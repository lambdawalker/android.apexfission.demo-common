"""Destination-independent module source identities. Git tags are never moved."""
import hashlib
import json
import re
import subprocess

SEMVER = r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)'

def key(version):
    if not re.fullmatch(SEMVER,version): raise ValueError('Expected X.Y.Z')
    return tuple(map(int,version.split('.')))

def canonical(module, version, destination=None):
    key(version)
    suffix = '-' + destination if destination else ''
    return f'{module}/v{version}{suffix}'

def fingerprint(module, source, git):
    paths = [f'{module}/src/main',f'{module}/build.gradle.kts',f'{module}/README.md',
             f'{module}/docs',f'{module}/consumer-rules.pro',f'{module}/proguard-rules.pro',
             'build.gradle.kts','settings.gradle.kts','gradle','gradlew','gradlew.bat',
             'LICENSE','jitpack.yml','scripts','publishing','docs/agents','docs/releases.md','.github/workflows/publish-library.yml','.github/workflows/publish-jitpack.yml']
    entries=git('ls-tree','-r',source,'--',*paths).splitlines()
    # Generated registry dropdowns/history are not source inputs. Shared scripts
    # are deliberately conservative: build protocol changes require a new tag.
    entries=[e for e in entries if not e.split('\t',1)[-1].startswith('scripts/tests/')]
    props=git('show',f'{source}:gradle.properties')
    return hashlib.sha256(('\n'.join(entries)+'\n'+props).encode()).hexdigest()

def record_tag(record):
    return record.get('source_tag') or record.get('legacy_tag')


def history(module, git, tags, records, destination):
    found = {}
    scope = '' if destination == 'maven-central' else destination + '/'
    scoped = re.compile(re.escape(module) + r'/v(' + SEMVER + r')-' + re.escape(destination))
    pending = re.compile(r'release-(?:pending|uploading|failed)/' + re.escape(scope + module) + r'/(' + SEMVER + r')')
    old_scoped = re.compile(re.escape(destination + '/' + module) + r'/v(' + SEMVER + r')')

    def add(version, name):
        found.setdefault(version, set()).add(git('rev-parse', f'{name}^{{commit}}'))

    for name in tags:
        match = scoped.fullmatch(name) or pending.fullmatch(name) or old_scoped.fullmatch(name)
        if match:
            add(match[1], name)
    for record in records:
        if record and record['module'] == module and record.get('repository', 'maven-central') == destination:
            version = record['version']
            key(version)
            explicit = record_tag(record)
            candidates = [explicit] if explicit else [canonical(module, version), f'{destination}/{module}/v{version}']
            name = next((name for name in candidates if name in tags and git('rev-parse', f'{name}^{{commit}}') == record['source']), None)
            if name is None:
                raise ValueError('Confirmed release is missing its source tag')
            add(version, name)
    for version,sources in found.items():
        if len(sources)!=1:raise ValueError(f'Conflicting source identities for {module} {version}; reconcile history before publishing')
    return {v:next(iter(s)) for v,s in found.items()}

def select(module,source,git,tags,records,requested='', *, destination='maven-central'):
    releases=history(module,git,tags,records,destination)
    if requested:key(requested)
    if not releases:return requested or '0.1.0',source
    latest=max(releases,key=key);original=releases[latest]
    try:git('merge-base','--is-ancestor',original,source)
    except subprocess.CalledProcessError:
        raise ValueError('Latest module release must be an ancestor of selected source') from None
    same=fingerprint(module,source,git)==fingerprint(module,original,git)
    if requested:
        if key(requested)<=key(latest):
            raise ValueError('Explicit version must be newer than the latest identity; use Finalize for recovery')
        return requested,source
    if same:return latest,original
    x,y,z=key(latest)
    return f'{x}.{y}.{z+1}',source
