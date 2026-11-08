import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

import documentation_history
import github_environment_api
import import_docs
import jitpack_build
import module_release
import publishing_config
import release
import release_identity
import setup_github_environments


class ReleaseTests(unittest.TestCase):
    def test_registry_has_only_implemented_destinations(self):
        self.assertEqual(set(publishing_config.load_config()), {'maven-central', 'jitpack'})
        self.assertEqual(publishing_config.generate(check=True), [])

    def test_first_version_and_invalid_explicit_version(self):
        select = release_identity.select
        self.assertEqual(select('demo-common', 'source', None, [], []), ('0.1.0', 'source'))
        with self.assertRaises(ValueError):
            select('demo-common', 'source', None, [], [], '1.0.0-SNAPSHOT')

    def test_destination_scoping_and_explicit_reuse(self):
        tag = 'demo-common/v0.1.9-maven-central'

        def git(*args):
            return {
                'rev-parse': 'original',
                'merge-base': '',
                'ls-tree': '',
                'show': 'original'
                if (args[1] if len(args) > 1 else '').startswith('original:')
                else 'changed',
            }[args[0]]

        select = release_identity.select
        self.assertEqual(select('demo-common', 'original', git, [tag], []), ('0.1.9', 'original'))
        self.assertEqual(select('demo-common', 'head', git, [tag], []), ('0.1.10', 'head'))
        self.assertEqual(
            select('demo-common', 'head', git, [tag], [], destination='jitpack'),
            ('0.1.0', 'head'),
        )
        with self.assertRaisesRegex(ValueError, 'newer'):
            select('demo-common', 'original', git, [tag], [], '0.1.9')

    def test_jitpack_builder_accepts_only_its_scoped_tags(self):
        self.assertEqual(
            jitpack_build.selection('demo-common~v0.1.0-jitpack'),
            ('demo-common', '0.1.0'),
        )
        with self.assertRaises(ValueError):
            jitpack_build.selection('demo-common/v0.1.0-maven-central')

    def test_documentation_requires_public_confirmation(self):
        identities = {'demo-common': module_release.identity('demo-common')}
        record = dict(
            module='demo-common',
            repository='maven-central',
            phase='reserved-before-upload',
            source='a' * 40,
            version='0.1.0',
            group=identities['demo-common'][0],
            artifact='demo-common',
            source_tag='demo-common/v0.1.0-maven-central',
        )
        records = {('maven-central', 'demo-common'): record}
        self.assertIn('No confirmed release', import_docs.render(records, identities))
        record['phase'] = 'confirmed-public'
        self.assertIn('demo-common:0.1.0', import_docs.render(records, identities))
        with tempfile.TemporaryDirectory() as folder:
            path = documentation_history.archive_record(Path(folder), record)
            self.assertEqual(path.name, '0.1.0-maven-central.json')
            self.assertEqual(len(documentation_history.load_catalog(Path(folder))), 1)

    def test_release_xml_entity_guard_blocks_doctype_and_entity(self):
        malicious_metadata = (
            b'<?xml version="1.0"?>'
            b'<!DOCTYPE metadata [<!ENTITY xxe "expanded">]>'
            b'<metadata><groupId>com.apexfission.android</groupId>'
            b'<artifactId>demo-common</artifactId>'
            b'<versioning><versions><version>&xxe;</version></versions></versioning></metadata>'
        )
        with patch.object(release, 'fetch', return_value=malicious_metadata):
            with self.assertRaisesRegex(ValueError, 'XML DTD and entity declarations'):
                release.published_versions('com.apexfission.android', 'demo-common')

        malicious_pom = (
            b'<?xml version="1.0"?>'
            b'<!ENTITY boom "x">'
            b'<project><groupId>com.apexfission.android</groupId></project>'
        )
        with self.assertRaisesRegex(ValueError, 'XML DTD and entity declarations'):
            release.verify_pom(malicious_pom, 'com.apexfission.android', 'demo-common', '0.1.0')

        valid_metadata = (
            b'<metadata><groupId>com.apexfission.android</groupId>'
            b'<artifactId>demo-common</artifactId>'
            b'<versioning><versions><version>0.1.0</version></versions></versioning></metadata>'
        )
        with patch.object(release, 'fetch', return_value=valid_metadata):
            self.assertEqual(
                release.published_versions('com.apexfission.android', 'demo-common'),
                ['0.1.0'],
            )

    def test_documentation_history_spanish_translation_verification(self):
        identities = {'demo-common': module_release.identity('demo-common')}
        record = dict(
            module='demo-common',
            repository='maven-central',
            phase='confirmed-public',
            source='a' * 40,
            version='0.1.0',
            group=identities['demo-common'][0],
            artifact='demo-common',
            source_tag='demo-common/v0.1.0-maven-central',
        )
        entry = dict(
            schema=1,
            module='demo-common',
            version='0.1.0',
            source='a' * 40,
            documentation_ref='a' * 40,
            destinations={'maven-central': record},
        )
        spanish = documentation_history.installation(entry, 'es')
        self.assertIn('#### Catálogo de versiones', spanish)
        self.assertNotIn('#### Version catalog', spanish)

        with patch.object(import_docs, '_examples', return_value='#### Drift without expected headings'):
            with self.assertRaisesRegex(ValueError, 'Missing Spanish translation source phrase'):
                documentation_history.installation(entry, 'es')

    @patch.dict("os.environ", {"RELEASE_REPOSITORY": "jitpack"})
    def test_abort_unconfirmed_rejects_jitpack_before_accessing_release_state(self):
        with patch.object(module_release, 'git') as git:
            with patch.object(release, 'published_versions') as published:
                with self.assertRaisesRegex(ValueError, "Maven Central only"):
                    module_release.abort_unconfirmed('demo-common', '0.1.0')
                git.assert_not_called()
                published.assert_not_called()

    @patch.dict("os.environ", {"RELEASE_REPOSITORY": "maven-central"})
    def test_module_release_guard_and_abort_unconfirmed(self):
        source_sha = 'b' * 40
        journal = dict(
            module='demo-common',
            version='0.1.0',
            source=source_sha,
            group='com.apexfission.android',
            artifact='demo-common',
            repository='maven-central',
            repository_url=release.CENTRAL,
            source_tag='demo-common/v0.1.0-maven-central',
            phase='reserved-before-upload',
            sha256={suffix: 'c' * 64 for suffix in release.SUFFIXES},
        )
        calls = []

        def fake_git(*args):
            calls.append(args)
            if args == ('cat-file', '-t', 'refs/tags/release-pending/demo-common/0.1.0'):
                return 'tag'
            if args == ('cat-file', '-p', 'refs/tags/release-pending/demo-common/0.1.0'):
                return 'header\n\n' + json.dumps(journal)
            if args[0] == 'ls-remote':
                ref = args[-1]
                if ref == 'refs/tags/release-pending/demo-common/0.1.0':
                    return f'pending-oid\t{ref}'
                if ref == 'refs/tags/release-uploading/demo-common/0.1.0':
                    return f'uploading-oid\t{ref}'
                return ''
            if args[0] == 'rev-parse':
                if args[1] == 'refs/tags/release-pending/demo-common/0.1.0':
                    return 'pending-oid'
                return source_sha
            if args[0] == 'ls-tree':
                return ''
            return ''

        with patch.object(module_release, 'git', side_effect=fake_git):
            with patch.object(module_release, 'remote_ref', side_effect=lambda name: 'pending-oid' if name == 'release-pending/demo-common/0.1.0' else None):
                module_release.guard('demo-common', '0.1.0')
                self.assertIn(
                    (
                        'push',
                        '--force-with-lease=refs/tags/release-uploading/demo-common/0.1.0:',
                        'origin',
                        'refs/tags/release-uploading/demo-common/0.1.0',
                    ),
                    calls,
                )

            with patch.object(release, 'published_versions', return_value=['0.1.0']):
                with self.assertRaisesRegex(ValueError, 'published on Maven Central'):
                    module_release.abort_unconfirmed('demo-common', '0.1.0')

            calls.clear()
            with patch.object(release, 'published_versions', return_value=[]):
                module_release.abort_unconfirmed('demo-common', '0.1.0')
            push_calls = [c for c in calls if c[0] == 'push']
            self.assertEqual(len(push_calls), 1)
            push_cmd = push_calls[0]
            self.assertIn('--atomic', push_cmd)
            self.assertIn('--force-with-lease=refs/tags/release-failed/demo-common/0.1.0:', push_cmd)
            self.assertIn('pending-oid:refs/tags/release-failed/demo-common/0.1.0', push_cmd)
            self.assertIn(':refs/tags/release-pending/demo-common/0.1.0', push_cmd)
            self.assertIn(':refs/tags/release-uploading/demo-common/0.1.0', push_cmd)


class GitHubEnvironmentSetupTests(unittest.IsolatedAsyncioTestCase):
    async def test_github_environment_api_validation_and_pagination(self):
        for invalid in ('../repo', 'owner/..', './repo', 'owner/.', '.', '..', 'owner/repo/extra', 'owner'):
            with self.assertRaises(github_environment_api.SetupError):
                github_environment_api.GitHubAPI(invalid, 'token')

        seen_params = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen_params.append(dict(request.url.params))
            page = int(request.url.params.get('page', '1'))
            if page == 1:
                items = [{'name': f'SEC_{i}'} for i in range(100)]
            else:
                items = [{'name': 'SEC_100'}]
            return httpx.Response(200, json={'total_count': 101, 'secrets': items})

        transport = httpx.MockTransport(handler)
        async with github_environment_api.GitHubAPI(
            'lambdawalker/android.apexfission.demo-common', 'test-token', transport=transport
        ) as api:
            values = await api.list_values('maven-central', 'secrets')
        self.assertEqual(len(values), 101)
        self.assertEqual(seen_params[0].get('per_page'), '100')
        self.assertEqual(seen_params[1].get('page'), '2')

    async def test_setup_github_environments_clears_secret_on_error_and_locks(self):
        setting = setup_github_environments.Setting(
            environment='maven-central',
            name='MAVEN_CENTRAL_PASSWORD',
            kind='secret',
            required=True,
        )
        wizard = setup_github_environments.SetupWizard(
            'lambdawalker/android.apexfission.demo-common',
            [setting],
        )
        async with wizard.run_test() as pilot:
            wizard.stage = 'settings'
            wizard.index = 0
            wizard.show_setting()
            entry = wizard.query_one('#value', setup_github_environments.Input)
            entry.value = '   '
            await wizard.advance()
            await pilot.pause()
            self.assertEqual(entry.value, '')
            self.assertEqual(wizard.changes, {})
            self.assertEqual(wizard.index, 0)

        with tempfile.TemporaryDirectory() as folder:
            with setup_github_environments.setup_lock(
                'lambdawalker/android.apexfission.demo-common', directory=folder
            ):
                with self.assertRaises(github_environment_api.SetupError):
                    with setup_github_environments.setup_lock(
                        'lambdawalker/android.apexfission.demo-common', directory=folder
                    ):
                        self.fail('Expected second lock acquisition to fail')

    async def test_apply_changes_handles_409_conflict_and_pre_apply_drift(self):
        var_setting = setup_github_environments.Setting(
            environment='maven-central',
            name='CUSTOM_VAR',
            kind='variable',
            required=True,
            existing=False,
        )

        class ConflictAPI:
            async def snapshot(self, environment):
                return True, {}, set()

            async def write_variable(self, environment, name, value, exists=False):
                raise github_environment_api.SetupError('GitHub request failed (HTTP 409).')

        result = await setup_github_environments.apply_changes(
            ConflictAPI(),
            {'maven-central': True},
            [var_setting],
            {0: 'value'},
        )
        self.assertEqual(result.failed, 'maven-central / CUSTOM_VAR')
        self.assertIn('409 Conflict', result.message)

        class DriftAPI:
            async def snapshot(self, environment):
                return True, {'CUSTOM_VAR': 'already-created'}, set()

        drift_result = await setup_github_environments.apply_changes(
            DriftAPI(),
            {'maven-central': True},
            [var_setting],
            {0: 'value'},
        )
        self.assertEqual(drift_result.failed, 'pre-apply environment check')
        self.assertIn('changed concurrently', drift_result.message)


if __name__ == '__main__':
    unittest.main()
