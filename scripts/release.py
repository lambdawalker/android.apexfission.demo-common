"""Signed Android release policy, durable attempt journal, and deterministic docs.

Standard library only. Network failures are never treated as an empty registry.
"""
import io
import json
import os
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

CENTRAL = 'https://repo.maven.apache.org/maven2'
SEMVER = r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)'
SUFFIXES = ('.pom', '.aar', '-sources.jar', '-javadoc.jar', '.module')


def version_key(value):
    if not re.fullmatch(SEMVER, value):
        raise ValueError(f'Expected stable X.Y.Z, got {value!r}')
    return tuple(map(int, value.split('.')))


def _parse_xml(data):
    raw = data.encode('utf-8') if isinstance(data, str) else bytes(data)
    upper = raw.upper()
    if b'<!DOCTYPE' in upper or b'<!ENTITY' in upper:
        raise ValueError('XML DTD and entity declarations are not allowed')
    return ET.fromstring(raw)


def fetch(url, missing=False, attempts=3):
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code == 404 and missing:
                return None
            if error.code != 429 and error.code < 500:
                raise
            if attempt == attempts - 1:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == attempts - 1:
                raise
        time.sleep(2 ** attempt)


def artifact_base(group, artifact):
    return f'{CENTRAL}/{group.replace(".", "/")}/{artifact}'


def published_versions(group, artifact):
    data = fetch(artifact_base(group, artifact) + '/maven-metadata.xml', missing=True)
    if data is None:
        return []
    xml = _parse_xml(data)
    if xml.tag != 'metadata' or xml.findtext('groupId') != group or xml.findtext('artifactId') != artifact:
        raise ValueError('Invalid Central metadata identity')
    versions = xml.findall('./versioning/versions/version')
    if not versions or any(not node.text for node in versions):
        raise ValueError('Malformed/empty Central metadata')
    return [node.text for node in versions]


def verify_pom(data, group, artifact, version):
    xml = _parse_xml(data)
    for node in xml.iter():
        node.tag = node.tag.split('}')[-1]
    if tuple(xml.findtext(k) for k in ('groupId', 'artifactId', 'version')) != (group, artifact, version):
        raise ValueError('POM coordinates/version mismatch')
    if xml.findtext('packaging') != 'aar':
        raise ValueError('Publication must be an Android AAR')
    for path in ('name', 'description', 'url', 'licenses/license/name', 'licenses/license/url',
                 'developers/developer/id', 'developers/developer/name', 'scm/url', 'scm/connection'):
        if not xml.findtext(path):
            raise ValueError(f'Missing POM metadata: {path}')
    dependencies = xml.findall('dependencies/dependency')
    expected = {'foundation', 'ui'}
    exported = {n.findtext('artifactId') for n in dependencies
                if n.findtext('scope', 'compile') == 'compile'}
    if not expected <= exported:
        raise ValueError('Compose Foundation and UI must be exported')
    if any(n.findtext('artifactId') == 'unspecified' or n.findtext('version') == 'unspecified'
           for n in dependencies):
        raise ValueError('Unresolved project dependency in POM')


def verify_artifact(data, suffix, group, artifact, version):
    if suffix == '.pom':
        verify_pom(data, group, artifact, version)
    elif suffix == '.module':
        module = json.loads(data)
        if tuple(module.get('component', {}).get(k) for k in ('group', 'module', 'version')) != (group, artifact, version):
            raise ValueError('Gradle module coordinates mismatch')
    else:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            if archive.testzip():
                raise ValueError('Corrupt JAR')
            names = archive.namelist()
            if suffix == '.aar':
                if 'AndroidManifest.xml' not in names or 'classes.jar' not in names:
                    raise ValueError('AAR is missing manifest or classes.jar')
                with zipfile.ZipFile(io.BytesIO(archive.read('classes.jar'))) as classes_jar:
                    classes = [n for n in classes_jar.namelist()
                               if n.endswith('.class') and n.startswith('com/apexfission/android/democommon/')]
                    if not classes or any(classes_jar.read(n)[:4] != b'\xca\xfe\xba\xbe' or
                                          int.from_bytes(classes_jar.read(n)[6:8], 'big') != 61 for n in classes):
                        raise ValueError('Missing library classes or unexpected JVM bytecode target')
                if any('DemoPreviews' in name for name in classes):
                    raise ValueError('Debug fixture must not be included')
            elif suffix == '-sources.jar' and not any(n.endswith('.kt') for n in names):
                raise ValueError('Sources JAR has no Kotlin source')
            elif suffix == '-javadoc.jar' and not any(n.endswith(('.md', '.html')) for n in names):
                raise ValueError('Documentation JAR has no documentation')


def outputs(values):
    text = ''.join(f'{k}={v}\n' for k, v in values.items())
    print(text, end='')
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as stream:
            stream.write(text)
    return values
