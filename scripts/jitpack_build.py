"""JitPack entry point: only canonical module tags may publish one library.

Keep this standalone script compatible with Python 3.5 on JitPack's default
image. Other release tooling runs on the modern Python configured in Actions.
"""
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TAG = re.compile(r'(demo-common)[/~]v((?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*))-jitpack')


def selection(value):
    match = TAG.fullmatch(value)
    if not match:
        raise ValueError('VERSION must be a canonical demo-common/vX.Y.Z-jitpack tag (slash or ~)')
    return match.group(1), match.group(2)


def run(*args):
    return subprocess.check_output(args, cwd=str(ROOT), universal_newlines=True).strip()




def command(module, version, scoped=False):
    selection('{}/v{}-jitpack'.format(module, version))
    return ['./gradlew', '--no-daemon', ':{}:publishToMavenLocal'.format(module),
            '-PjitpackBuild=true', '-PreleaseModule={}'.format(module), '-PreleaseVersion={}'.format(version),
            '-PjitpackScopedTag={}'.format(str(scoped).lower())]


def main():
    requested_tag = os.environ.get('VERSION', '')
    module, version = selection(requested_tag)
    tag = requested_tag.replace('~', '/')
    source = run('git', 'rev-parse', 'HEAD')
    if run('git', 'rev-parse', 'refs/tags/{}^{{commit}}'.format(tag)) != source:
        raise ValueError('Canonical tag does not identify checkout')
    if os.environ.get('GIT_COMMIT', source) != source:
        raise ValueError('JitPack GIT_COMMIT differs from checkout')
    subprocess.run(command(module, version, tag.endswith('-jitpack')), cwd=str(ROOT), check=True)


if __name__ == '__main__':
    main()
