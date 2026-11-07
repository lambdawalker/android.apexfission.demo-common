"""Verify independently consumed, unsigned JitPack artifacts against build provenance.

A successful API response alone is insufficient: exact artifact URLs, coordinates,
JVM target, and public dependencies must all be confirmed. JitPack uses repository coordinates.
"""
import hashlib
import json
import re
import urllib.error

import release

GROUP = 'com.github.lambdawalker'
ARTIFACT = 'android.apexfission.demo-common'
API_BASE = 'https://jitpack.io/api/builds/com.github.lambdawalker/android.apexfission.demo-common'
REPOSITORY = 'https://jitpack.io'
ARTIFACTS = {'demo-common': 'demo-common'}
class NotReady(urllib.error.URLError):
    """Public build is pending; confirmation may retry without releasing its journal."""


REQUIRED_SUFFIXES = ('.pom', '.aar', '-sources.jar', '-javadoc.jar')


def coordinates(module, semantic_version, artifact, *, scoped=False):
    release.version_key(semantic_version)
    if module not in ARTIFACTS or artifact not in (ARTIFACTS[module], ARTIFACT):
        raise ValueError('Unexpected JitPack module/artifact identity')
    suffix = '-jitpack' if scoped else ''
    return GROUP, ARTIFACT, f'{module}~v{semantic_version}{suffix}'


def artifact_base(record):
    group, artifact, version = coordinates(record['module'], record['version'], record['artifact'], scoped='source_tag' in record)
    if record['group'] != group or record['artifact'] != artifact or record['consumer_version'] != version:
        raise ValueError('JitPack record coordinates mismatch')
    return f'{REPOSITORY}/{group.replace(".", "/")}/{artifact}/{version}/{artifact}-{version}'


def verify(record, fetch_bytes):
    base = artifact_base(record)
    if not re.fullmatch('[0-9a-f]{40}', record['source']):
        raise ValueError('Expected full source commit SHA')
    provenance = json.loads(fetch_bytes(f'{API_BASE}/{record["consumer_version"]}'))
    raw_status = provenance.get('status')
    status = raw_status.lower() if isinstance(raw_status, str) else raw_status
    if status in ('none', 'queued', 'pending', 'building', 'running'):
        raise NotReady(f'JitPack build is not ready: {status}')
    if status != 'ok':
        raise ValueError(f'JitPack build failed or returned an unknown status: {status!r}')
    if provenance.get('commit') != record['source']:
        raise ValueError('JitPack build is not successful at the reserved source commit')
    # Some API versions expose these identity fields; reject contradictions.
    expected_api = {'group': 'com.github.lambdawalker', 'artifact': 'android.apexfission.demo-common',
                    'version': record['consumer_version']}
    if any(key in provenance and provenance[key] != value for key, value in expected_api.items()):
        raise ValueError('JitPack build API identity mismatch')
    hashes = {}
    for suffix in (*REQUIRED_SUFFIXES, '.module'):
        data = fetch_bytes(base + suffix, missing=True) if suffix == '.module' else fetch_bytes(base + suffix)
        if data is None:
            if suffix != '.module':
                raise NotReady(f'JitPack artifact is not ready: {suffix}')
            continue
        release.verify_artifact(data, suffix, record['group'], record['artifact'], record['consumer_version'])
        hashes[suffix] = hashlib.sha256(data).hexdigest()
    return hashes
