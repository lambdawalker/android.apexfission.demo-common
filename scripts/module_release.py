"""Journaled Demo Common releases for Central and JitPack. Never uploads packages."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.error
import zipfile

import documentation_history
import import_docs
import jitpack_release
from publishing_config import ID, load_config, validate_url
import release as common
import release_identity

ROOT = Path(__file__).resolve().parents[1]
MODULES = ('demo-common',)


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def repository():
    value = os.environ.get('RELEASE_REPOSITORY', 'maven-central')
    if value not in load_config():
        raise ValueError('Unknown release repository')
    return value


def repository_url():
    return jitpack_release.REPOSITORY if repository() == 'jitpack' else common.CENTRAL


def fetch(url, missing=False):
    if not url.startswith(repository_url() + '/'):
        raise ValueError('Unexpected repository request destination')
    return common.fetch(url, missing=missing)


def scope():
    return '' if repository() == 'maven-central' else repository() + '/'


def metadata_path(module):
    return f'docs/releases/{scope()}{module}.json'


def tag(module, version):
    return release_identity.canonical(module, version, repository())


def legacy_source_tags(module, version):
    return (
        release_identity.canonical(module, version),
        f'{repository()}/{module}/v{version}',
    )


def record_source_tag(record):
    explicit = release_identity.record_tag(record)
    if explicit:
        return explicit
    candidates = legacy_source_tags(record['module'], record['version'])
    return next(
        (
            name
            for name in candidates
            if remote_ref(name) and git('rev-parse', f'{name}^{{commit}}') == record['source']
        ),
        candidates[0],
    )


def pending(module, version):
    return f'release-pending/{scope()}{module}/{version}'


def uploading(module, version):
    return f'release-uploading/{scope()}{module}/{version}'


def failed(module, version):
    return f'release-failed/{scope()}{module}/{version}'


def artifact_base(group, artifact):
    return f'{repository_url()}/{group.replace(".", "/")}/{artifact}'


def refresh():
    git('fetch', 'origin', 'main', '--tags')


def remote_tags():
    return [
        line.split('refs/tags/', 1)[1]
        for line in git('ls-remote', '--refs', '--tags', 'origin').splitlines()
    ]


def remote_ref(name):
    result = git('ls-remote', '--refs', 'origin', f'refs/tags/{name}')
    return result.split()[0] if result else None


def properties():
    return dict(
        line.strip().split('=', 1)
        for line in (ROOT / 'gradle.properties').read_text(encoding='utf-8').splitlines()
        if '=' in line and not line.lstrip().startswith('#')
    )


def identity(module):
    props = properties()
    group = props['GROUP']
    artifact = props['POM_ARTIFACT_ID']
    if (
        not re.fullmatch(r'[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)+', group)
        or not re.fullmatch(r'[a-z][a-z0-9-]*', artifact)
    ):
        raise ValueError('Unexpected module coordinates')
    return group, artifact


def ensure_available(module, tags, *, pending_override=None):
    legacy = [
        t for t in tags if re.fullmatch(r'release-(?:pending|uploading)/' + common.SEMVER, t)
    ]
    if legacy and not scope():
        raise ValueError(
            'Unresolved legacy paired release; finalize it using the old workflow before independent releases'
        )
    own = [
        t
        for t in tags
        if t.startswith(
            (f'release-pending/{scope()}{module}/', f'release-uploading/{scope()}{module}/')
        )
    ]
    if pending_override and repository() == 'jitpack':
        version, source = pending_override
        prefix = f'release-pending/jitpack/{module}/'
        for name in own[:]:
            if not name.startswith(prefix):
                continue
            old_version = name[len(prefix):]
            if common.version_key(version) <= common.version_key(old_version):
                raise ValueError(
                    'JitPack override requires a version newer than every pending attempt'
                )
            journal = read_record(module, old_version)
            canonical = record_source_tag(journal)
            if (
                not remote_ref(canonical)
                or git('rev-parse', f'{canonical}^{{commit}}') != journal['source']
            ):
                raise ValueError('Pending JitPack canonical source does not match its journal')
            git('merge-base', '--is-ancestor', journal['source'], source)
            print(f'JitPack override: preserving {name} and proceeding with {version}')
            own.remove(name)
    if own:
        raise ValueError(f'Unresolved {module} attempt {own}; run finalization, never re-upload')


def validate_record(record, module, check_destination=True):
    target = record.get('repository', 'maven-central')
    if not isinstance(target, str) or not ID.fullmatch(target):
        raise ValueError('Invalid journal repository')
    if target != 'maven-central' or 'repository_url' in record:
        validate_url(record.get('repository_url', ''))
    if check_destination:
        if target != repository():
            raise ValueError('Journal repository differs from selection')
        if record.get('repository_url', common.CENTRAL) != repository_url():
            raise ValueError('Journal destination differs from configured URL')
    if (
        module not in MODULES
        or record.get('module') != module
        or (target != 'jitpack' and (record.get('group'), record.get('artifact')) != identity(module))
        or record.get('companions')
    ):
        raise ValueError('Journal must contain exactly the selected module')
    common.version_key(record['version'])
    if 'source_tag' in record and (
        record.get('legacy_tag')
        or record['source_tag'] != release_identity.canonical(module, record['version'], target)
    ):
        raise ValueError('Invalid destination source tag')
    if not re.fullmatch('[0-9a-f]{40}', record['source']):
        raise ValueError('Invalid source')
    expected = set(common.SUFFIXES)
    actual = set(record['sha256'])
    valid_hashes = actual == expected or (
        target == 'jitpack' and actual == expected - {'.module'}
    )
    if not valid_hashes or any(
        not re.fullmatch('[0-9a-f]{64}', v) for v in record['sha256'].values()
    ):
        raise ValueError('Incomplete publication hashes')
    if target == 'jitpack':
        jitpack_release.artifact_base(record)
    if record['phase'] not in ('reserved-before-upload', 'confirmed-public'):
        raise ValueError('Invalid phase')


def read_record(module, version):
    name = pending(module, version)
    if git('cat-file', '-t', f'refs/tags/{name}') != 'tag':
        raise ValueError('Journal must be annotated')
    if remote_ref(name) != git('rev-parse', f'refs/tags/{name}'):
        raise ValueError('Remote reservation differs')
    record = json.loads(git('cat-file', '-p', f'refs/tags/{name}').split('\n\n', 1)[1])
    validate_record(record, module)
    if record['version'] != version or git('rev-parse', f'{name}^{{commit}}') != record['source']:
        raise ValueError('Journal source/version mismatch')
    return record


def all_records(remote=False):
    if remote:
        paths = git(
            'ls-tree', '-r', '--name-only', 'origin/main', '--', 'docs/releases'
        ).splitlines()
        return [
            json.loads(git('show', f'origin/main:{p}'))
            for p in paths
            if p.endswith('.json') and not p.startswith('docs/releases/history/')
        ]
    return list(documentation_history.latest_records(ROOT))


def recover_failed_jitpack(module, tags, version, source):
    """Archive a terminal, artifact-free attempt before selecting newer source."""
    if repository() != 'jitpack':
        return
    prefix = f'release-pending/jitpack/{module}/'
    attempts = [name for name in tags if name.startswith(prefix)]
    if not attempts:
        return
    if len(attempts) != 1 or any(
        name.startswith(f'release-uploading/jitpack/{module}/') for name in tags
    ):
        raise ValueError(
            'Multiple or upload-started JitPack attempts require manual reconciliation'
        )
    name = attempts[0]
    old_version = name[len(prefix):]
    record = read_record(module, old_version)
    if (
        common.version_key(version) <= common.version_key(old_version)
        or source == record['source']
    ):
        raise ValueError('Failed JitPack recovery requires a newer version and corrected source')
    git('merge-base', '--is-ancestor', record['source'], source)
    canonical = record_source_tag(record)
    if (
        not remote_ref(canonical)
        or git('rev-parse', f'{canonical}^{{commit}}') != record['source']
    ):
        raise ValueError('Failed JitPack canonical source does not match its journal')
    current = confirmed_record(module, remote=True)
    if current and common.version_key(current['version']) >= common.version_key(old_version):
        raise ValueError('Confirmed JitPack history requires manual reconciliation')
    base = jitpack_release.artifact_base(record)

    def check_failure():
        status = json.loads(fetch(f'{jitpack_release.API_BASE}/{record["consumer_version"]}'))
        if str(status.get('status', '')).lower() not in ('error', 'failed'):
            raise ValueError(
                'JitPack attempt is not a proven terminal failure; preserve pending journal'
            )
        if status.get('commit') != record['source']:
            raise ValueError('JitPack failure source does not match the reserved source')
        expected = {
            'group': record['group'],
            'artifact': record['artifact'],
            'version': record['consumer_version'],
        }
        if any(key in status and status[key] != value for key, value in expected.items()):
            raise ValueError('JitPack failure identity differs from the reservation')

    check_failure()
    # Even a partial publication must keep its reservation for investigation.
    if any(fetch(base + suffix, missing=True) is not None for suffix in common.SUFFIXES):
        raise ValueError('JitPack attempt has public artifacts; preserve pending journal')
    check_failure()
    original = git('rev-parse', f'refs/tags/{name}')
    archive = f'release-failed/jitpack/{module}/{old_version}'
    if remote_ref(archive):
        raise ValueError('JitPack failure archive already exists; reconcile history')
    # Preserve the exact annotated journal object. Leases and an atomic push
    # prevent clearing a changed reservation or overwriting an existing archive.
    git(
        'push',
        '--atomic',
        f'--force-with-lease=refs/tags/{name}:{original}',
        f'--force-with-lease=refs/tags/{archive}:',
        'origin',
        f'{original}:refs/tags/{archive}',
        f':refs/tags/{name}',
    )
    git('update-ref', '-d', f'refs/tags/{name}', original)
    print(
        f'Archived failed JitPack {module} {old_version}; canonical tag retained; advancing to {version}'
    )


def abort_unconfirmed(module, version):
    """Archive stuck release-pending and release-uploading tags after verifying Central absence."""
    if repository() != "maven-central":
        raise ValueError("abort-unconfirmed supports Maven Central only")
    common.version_key(version)
    refresh()
    current = confirmed_record(module, remote=True)
    if current and current['version'] == version:
        raise ValueError('Version already finalized at destination; cannot abort')
    pending_name = pending(module, version)
    uploading_name = uploading(module, version)
    pending_oid = remote_ref(pending_name)
    uploading_oid = remote_ref(uploading_name)
    if not pending_oid and not uploading_oid:
        raise ValueError('No unconfirmed release attempt found for this version')
    record = read_record(module, version) if pending_oid else None
    if uploading_oid and record is not None:
        if git('rev-parse', f'{uploading_name}^{{commit}}') != record['source']:
            raise ValueError('Upload marker source differs from reservation')
    group, artifact = identity(module)
    published = common.published_versions(group, artifact)
    if version in published:
        raise ValueError(
            'Version is published on Maven Central; run finalize instead of aborting'
        )
    archive = failed(module, version)
    if remote_ref(archive):
        raise ValueError('Failure archive already exists; reconcile history')
    archive_oid = pending_oid or uploading_oid
    leases = [f'--force-with-lease=refs/tags/{archive}:']
    refspecs = [f'{archive_oid}:refs/tags/{archive}']
    if pending_oid:
        leases.append(f'--force-with-lease=refs/tags/{pending_name}:{pending_oid}')
        refspecs.append(f':refs/tags/{pending_name}')
    if uploading_oid:
        leases.append(f'--force-with-lease=refs/tags/{uploading_name}:{uploading_oid}')
        refspecs.append(f':refs/tags/{uploading_name}')
    git('push', '--atomic', *leases, 'origin', *refspecs)
    if pending_oid:
        git('update-ref', '-d', f'refs/tags/{pending_name}', pending_oid)
    if uploading_oid:
        git('update-ref', '-d', f'refs/tags/{uploading_name}', uploading_oid)
    print(f'Archived unconfirmed {module} {version} to {archive}')


def prepare(module, requested='', *, allow_pending_jitpack=False):
    refresh()
    tags = remote_tags()
    if repository() != 'jitpack':
        ensure_available(module, tags)
    source = git('rev-parse', 'HEAD')
    git('merge-base', '--is-ancestor', source, 'origin/main')
    records = all_records(remote=True)
    for record in records:
        if record:
            validate_record(record, record['module'], check_destination=False)
    if allow_pending_jitpack and not requested.strip():
        raise ValueError('JitPack override requires an explicit version (X.Y.Z)')
    head = source
    version, source = release_identity.select(
        module, source, git, tags, records, requested.strip(), destination=repository()
    )
    if repository() == 'jitpack':
        if allow_pending_jitpack:
            if source != head:
                raise ValueError(
                    'JitPack override requires a new version from the selected workflow source'
                )
            ensure_available(module, tags, pending_override=(version, source))
        else:
            recover_failed_jitpack(module, tags, version, source)
            ensure_available(module, remote_tags())
    current = confirmed_record(module, remote=True)
    if current and current['version'] == version:
        validate_record(current, module)
        if current['source'] != source:
            raise ValueError('Destination version has conflicting source')
        return common.outputs(dict(module=module, version=version, source=source, skip='true'))
    if repository() != 'jitpack':
        group, artifact = identity(module)
        published = common.published_versions(group, artifact)
        if version in published:
            raise ValueError(
                'Version exists at destination without a matching confirmed record; investigate before upload'
            )
        if any(
            re.fullmatch(common.SEMVER, v) and common.version_key(v) > common.version_key(version)
            for v in published
        ):
            raise ValueError('Destination has newer untracked releases; reconcile provenance')
    return common.outputs(dict(module=module, version=version, source=source, skip='false'))


def prepare_finalization(module, version, source=''):
    common.version_key(version)
    if source and not re.fullmatch('[0-9a-f]{40}', source):
        raise ValueError('Invalid source')
    refresh()
    if remote_ref(pending(module, version)):
        record = read_record(module, version)
        stable = record_source_tag(record)
        if record.get('source_tag') and (
            not remote_ref(stable)
            or git('rev-parse', f'{stable}^{{commit}}') != record['source']
        ):
            raise ValueError('Pending source tag differs from reservation')
        if source and source != record['source']:
            raise ValueError('Conflicting source')
        git('merge-base', '--is-ancestor', record['source'], 'origin/main')
        current = confirmed_record(module, remote=True)
        if current and common.version_key(current['version']) >= common.version_key(version):
            raise ValueError('Pending release would overwrite newer documentation')
        return common.outputs(
            dict(module=module, version=version, source=record['source'], skip='false')
        )
    current = confirmed_record(module, remote=True)
    if remote_ref(uploading(module, version)) or not current:
        raise ValueError('No matching pending or completed release')
    validate_record(current, module)
    if current['phase'] != 'confirmed-public' or common.version_key(
        current['version']
    ) < common.version_key(version):
        raise ValueError('Stable tag lacks confirmed docs')
    record = current
    if current['version'] != version:
        record = None
        for filename in (f'{version}-{repository()}.json', f'{version}.json'):
            path = documentation_history.HISTORY / module / filename
            if git('ls-tree', '--name-only', 'origin/main', '--', str(path)):
                entry = documentation_history.validate(
                    json.loads(git('show', f'origin/main:{path}'))
                )
                record = entry['destinations'].get(repository())
                if record:
                    break
        if not record or record['version'] != version:
            raise ValueError('No confirmed record for this destination and version')
        validate_record(record, module)
    stable = record_source_tag(record)
    if not remote_ref(stable) or git('rev-parse', f'{stable}^{{commit}}') != record['source']:
        raise ValueError('Confirmed source differs from stable tag')
    if source and source != record['source']:
        raise ValueError('Conflicting source')
    git('merge-base', '--is-ancestor', record['source'], current['source'])
    git('merge-base', '--is-ancestor', current['source'], 'origin/main')
    return common.outputs(
        dict(module=module, version=version, source=record['source'], skip='true')
    )


def verify_bytes(data, suffix, record):
    common.verify_artifact(
        data,
        suffix,
        record['group'],
        record['artifact'],
        record.get('consumer_version', record['version']),
    )


def verify_documentation_contents(data):
    # Apply to new local candidates only; historical releases may contain media.
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        unexpected = [
            entry.filename
            for entry in archive.infolist()
            if not entry.is_dir()
            and not entry.filename.endswith('.md')
            and entry.filename not in ('LICENSE', 'META-INF/MANIFEST.MF')
        ]
        if unexpected:
            raise ValueError(f'Unexpected documentation archive content: {unexpected}')


def local_record(module, version, source):
    common.version_key(version)
    if source != git('rev-parse', 'HEAD'):
        raise ValueError('Checkout differs from source')
    git('diff', '--exit-code', source, '--', '.')
    group, artifact = identity(module)
    record = dict(
        module=module,
        version=version,
        source=source,
        group=group,
        artifact=artifact,
        sha256={},
        phase='reserved-before-upload',
        workflow_run=os.environ.get('GITHUB_RUN_ID', 'local'),
    )
    record.update(
        repository=repository(),
        repository_url=repository_url(),
        source_tag=tag(module, version),
    )
    if repository() == 'jitpack':
        group, artifact, consumer = jitpack_release.coordinates(
            module, version, artifact, scoped=True
        )
        record.update(group=group, artifact=artifact, consumer_version=consumer)
    consumer = record.get('consumer_version', version)
    directory = (
        ROOT
        / 'build/verification-repository'
        / group.replace('.', '/')
        / artifact
        / consumer
    )
    for suffix in common.SUFFIXES:
        data = (directory / f'{artifact}-{consumer}{suffix}').read_bytes()
        verify_bytes(data, suffix, record)
        if suffix == '-javadoc.jar':
            verify_documentation_contents(data)
        record['sha256'][suffix] = hashlib.sha256(data).hexdigest()
    validate_record(record, module)
    return record


def reserve(module, version, source, *, allow_pending_jitpack=False):
    record = local_record(module, version, source)
    base = (
        f'{artifact_base(record["group"], record["artifact"])}'
        f'/{version}/{record["artifact"]}-{version}'
    )
    if repository() != 'jitpack' and any(
        fetch(base + suffix, missing=True) is not None for suffix in common.SUFFIXES
    ):
        raise ValueError('Immutable version already has public artifacts')
    refresh()
    ensure_available(
        module,
        remote_tags(),
        pending_override=(version, source) if allow_pending_jitpack else None,
    )
    git('merge-base', '--is-ancestor', source, 'origin/main')
    stable = tag(module, version)
    updates = []
    if remote_ref(stable):
        if git('rev-parse', f'{stable}^{{commit}}') != source:
            raise ValueError('Canonical tag has different source')
    else:
        git(
            'tag',
            '-a',
            stable,
            source,
            '-m',
            f'Module release {module} {version}; publication tracked separately',
        )
        updates.append(f'refs/tags/{stable}')
    name = pending(module, version)
    git('tag', '-a', name, source, '-m', json.dumps(record, sort_keys=True))
    git('push', '--atomic', 'origin', *updates, f'refs/tags/{name}')


def guard(module, version):
    common.version_key(version)
    record = read_record(module, version)
    if (
        record['source'] != git('rev-parse', 'HEAD')
        or (record['group'], record['artifact']) != identity(module)
    ):
        raise ValueError('Reservation differs from source/module')
    current = confirmed_record(module, remote=True)
    if current and current['version'] == version:
        raise ValueError('Version already finalized at destination')
    marker = uploading(module, version)
    if remote_ref(marker):
        raise ValueError('Upload already started; finalize without re-uploading')
    git(
        'tag',
        '-a',
        marker,
        record['source'],
        '-m',
        f'Upload may have started: {pending(module, version)}',
    )
    git('push', f'--force-with-lease=refs/tags/{marker}:', 'origin', f'refs/tags/{marker}')


def verify_public(record):
    if repository() == 'jitpack':
        # Requesting the artifact starts JitPack's build; API lookup alone does not.
        fetch(jitpack_release.artifact_base(record) + '.pom')
        return jitpack_release.verify(record, fetch)
    base = (
        f'{artifact_base(record["group"], record["artifact"])}'
        f'/{record["version"]}/{record["artifact"]}-{record["version"]}'
    )
    for suffix in common.SUFFIXES:
        data = fetch(base + suffix)
        verify_bytes(data, suffix, record)
        if hashlib.sha256(data).hexdigest() != record['sha256'][suffix]:
            raise ValueError('Public artifact hash mismatch')
        if b'BEGIN PGP SIGNATURE' not in fetch(base + suffix + '.asc'):
            raise ValueError('Missing signature')
    return record['sha256']


def confirm(module, version, timeout=2400, *, source=None):
    common.version_key(version)
    record = read_record(module, version)
    if record['source'] != (source or git('rev-parse', 'HEAD')):
        raise ValueError('Confirmation source differs from reservation')
    deadline = time.monotonic() + timeout
    last = None
    while True:
        try:
            hashes = verify_public(record)
            if repository() == 'jitpack':
                record['sha256'] = hashes
            break
        except urllib.error.HTTPError as error:
            if error.code not in (404, 429) and error.code < 500:
                raise
            last = error
        except (urllib.error.URLError, TimeoutError) as error:
            last = error
        if time.monotonic() >= deadline:
            raise TimeoutError(
                'Public artifacts not confirmed; preserve journal and retry finalization'
            ) from last
        time.sleep(min(20, max(0, deadline - time.monotonic())))
    record['phase'] = 'confirmed-public'
    path = ROOT / f'build/{scope()}confirmed-{module}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return record


def confirmed_record(module, remote=False):
    path = metadata_path(module)
    if remote:
        if not git('ls-tree', '--name-only', 'origin/main', '--', path):
            return None
        return json.loads(git('show', f'origin/main:{path}'))
    local = ROOT / path
    return json.loads(local.read_text(encoding='utf-8')) if local.exists() else None


def documentation(verify=False):
    # Preserve historical records even when a destination is later removed from the registry.
    targets = ['maven-central'] + sorted(
        {p.parent.name for p in (ROOT / 'docs/releases').glob('*/*.json')}
    )
    records = {
        (target, module): json.loads(path.read_text(encoding='utf-8'))
        for target in targets
        for module in MODULES
        if (
            path := ROOT
            / 'docs/releases'
            / ('' if target == 'maven-central' else target)
            / f'{module}.json'
        ).exists()
    }
    sections = import_docs.render(records, {module: identity(module) for module in MODULES})
    template = (ROOT / 'docs/templates/MODULE_IMPORT.md.template').read_text(encoding='utf-8')
    expected = template.replace('{{INSTALLATION}}', sections)
    if '{{' in expected:
        raise ValueError('Unknown template placeholder')
    path = ROOT / 'IMPORT.md'
    if verify:
        if path.read_text(encoding='utf-8') != expected:
            raise ValueError('IMPORT.md drift; run ./gradlew generateImportDocs')
    else:
        path.write_text(expected, encoding='utf-8')


def finalize(module, version, source):
    common.version_key(version)
    if not re.fullmatch('[0-9a-f]{40}', source):
        raise ValueError('Invalid source')
    record = json.loads(
        (ROOT / f'build/{scope()}confirmed-{module}.json').read_text(encoding='utf-8')
    )
    validate_record(record, module)
    if (record['version'], record['source'], record['phase']) != (
        version,
        source,
        'confirmed-public',
    ):
        raise ValueError('Confirmation mismatch')
    journal = read_record(module, version)
    expected = {**journal, 'phase': 'confirmed-public'}
    if repository() == 'jitpack':
        expected['sha256'] = record['sha256']
    if expected != record:
        raise ValueError('Confirmation differs from reservation')
    refresh()
    git('merge-base', '--is-ancestor', source, 'origin/main')
    # Artifact inputs may advance while a verified older release propagates.
    # Only changes to the executing protocol/renderer require reconciliation.
    git(
        'diff',
        '--exit-code',
        'HEAD',
        'origin/main',
        '--',
        'scripts',
        ':(exclude)scripts/tests',
        'publishing',
        'docs/templates/MODULE_IMPORT.md.template',
    )
    git('switch', '-C', f'finalize-{module}', 'origin/main')
    current = confirmed_record(module)
    if current and common.version_key(current['version']) >= common.version_key(version):
        raise ValueError('Refusing to replace same/newer module metadata')
    documentation_history.seed(ROOT)
    documentation_history.archive_record(ROOT, record)
    meta_file = ROOT / metadata_path(module)
    meta_file.parent.mkdir(parents=True, exist_ok=True)
    meta_file.write_text(
        json.dumps(record, indent=2, sort_keys=True) + '\n', encoding='utf-8'
    )
    documentation()
    git('config', 'user.name', 'github-actions[bot]')
    git('config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
    git('add', metadata_path(module), 'IMPORT.md', str(documentation_history.HISTORY))
    git('commit', '-m', f'docs: confirm {module} {version}')
    stable = record_source_tag(journal)
    updates = ['HEAD:refs/heads/main', f':refs/tags/{pending(module, version)}']
    if remote_ref(stable):
        if git('rev-parse', f'{stable}^{{commit}}') != source:
            raise ValueError('Stable tag source mismatch')
    else:
        git('tag', '-a', stable, source, '-m', f'Module release {module} {version}')
        updates.append(f'refs/tags/{stable}')
    if remote_ref(uploading(module, version)):
        if git('rev-parse', f'{uploading(module, version)}^{{commit}}') != source:
            raise ValueError('Upload marker source mismatch')
        updates.append(f':refs/tags/{uploading(module, version)}')
    git('push', '--atomic', 'origin', *updates)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'command',
        choices=[
            'prepare',
            'prepare-finalization',
            'check-local',
            'reserve',
            'guard',
            'confirm',
            'finalize',
            'abort-unconfirmed',
            'generate',
            'verify',
        ],
    )
    parser.add_argument('--module', choices=MODULES)
    parser.add_argument('--version')
    parser.add_argument('--source', default='')
    parser.add_argument('--timeout', type=int, default=2400)
    parser.add_argument('--allow-pending-jitpack', action='store_true')
    args = parser.parse_args()
    if args.command in ('generate', 'verify'):
        return documentation(args.command == 'verify')
    if not args.module:
        parser.error('--module is required')
    if args.allow_pending_jitpack and (
        args.command not in ('prepare', 'reserve') or repository() != 'jitpack'
    ):
        parser.error('--allow-pending-jitpack is only valid for JitPack prepare and reserve')
    if args.command == 'prepare':
        return prepare(
            args.module,
            args.version or '',
            allow_pending_jitpack=args.allow_pending_jitpack,
        )
    if not args.version:
        parser.error('--version is required')
    if args.command == 'prepare-finalization':
        return prepare_finalization(args.module, args.version, args.source)
    if args.command == 'abort-unconfirmed':
        return abort_unconfirmed(args.module, args.version)
    if args.command in ('check-local', 'reserve', 'finalize') and not args.source:
        parser.error('--source is required')
    if args.command == 'check-local':
        print(json.dumps(local_record(args.module, args.version, args.source), indent=2))
    elif args.command == 'reserve':
        reserve(
            args.module,
            args.version,
            args.source,
            allow_pending_jitpack=args.allow_pending_jitpack,
        )
    elif args.command == 'guard':
        guard(args.module, args.version)
    elif args.command == 'confirm':
        confirm(args.module, args.version, args.timeout, source=args.source)
    elif args.command == 'finalize':
        finalize(args.module, args.version, args.source)


if __name__ == '__main__':
    main()
