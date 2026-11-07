import tempfile
import unittest
from pathlib import Path

import documentation_history
import import_docs
import jitpack_build
import module_release
import publishing_config
import release_identity


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
            return {'rev-parse': 'original', 'merge-base': '', 'ls-tree': '',
                    'show': 'original' if (args[1] if len(args) > 1 else '').startswith('original:') else 'changed'}[args[0]]

        select = release_identity.select
        self.assertEqual(select('demo-common', 'original', git, [tag], []), ('0.1.9', 'original'))
        self.assertEqual(select('demo-common', 'head', git, [tag], []), ('0.1.10', 'head'))
        self.assertEqual(select('demo-common', 'head', git, [tag], [], destination='jitpack'), ('0.1.0', 'head'))
        with self.assertRaisesRegex(ValueError, 'newer'):
            select('demo-common', 'original', git, [tag], [], '0.1.9')

    def test_jitpack_builder_accepts_only_its_scoped_tags(self):
        self.assertEqual(jitpack_build.selection('demo-common~v0.1.0-jitpack'), ('demo-common', '0.1.0'))
        with self.assertRaises(ValueError):
            jitpack_build.selection('demo-common/v0.1.0-maven-central')

    def test_documentation_requires_public_confirmation(self):
        identities = {'demo-common': module_release.identity('demo-common')}
        record = dict(module='demo-common', repository='maven-central', phase='reserved-before-upload',
                      source='a' * 40, version='0.1.0', group=identities['demo-common'][0],
                      artifact='demo-common', source_tag='demo-common/v0.1.0-maven-central')
        records = {('maven-central', 'demo-common'): record}
        self.assertIn('No confirmed release', import_docs.render(records, identities))
        record['phase'] = 'confirmed-public'
        self.assertIn('demo-common:0.1.0', import_docs.render(records, identities))
        with tempfile.TemporaryDirectory() as folder:
            path = documentation_history.archive_record(Path(folder), record)
            self.assertEqual(path.name, '0.1.0-maven-central.json')
            self.assertEqual(len(documentation_history.load_catalog(Path(folder))), 1)
