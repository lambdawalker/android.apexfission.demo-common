# Publishing Demo Common

Only the `:demo-common` release AAR is published. Gradle runs on JDK 21 and
produces Java 17 bytecode.

## Owner setup

Install `python -m pip install -r scripts/requirements-setup.txt` and run
`python scripts/setup_github_environments.py`. Use a repository-scoped
GitHub token with the environment administration permissions shown by
the wizard. Review the changes before applying. Central requires
`MAVEN_CENTRAL_USERNAME`, `MAVEN_CENTRAL_PASSWORD`, `SIGNING_IN_MEMORY_KEY`,
and the signing password if applicable. Enter the exported signing key's
file path. Confirm namespace ownership in Central Portal. Public JitPack
has an empty environment and requires a public GitHub repository.

Use a 15-minute wait timer on `delayed-docs` where supported. In Settings →
Pages, select GitHub Actions. The release token must be able to push
release tags and confirmed documentation updates under the existing rules.

## Publish

Run **Publish Demo Common** on `main`. Choose Maven Central or JitPack and
leave **version** blank. The first release is `0.1.0`. Unchanged release
inputs reuse the latest immutable version and source. Changed inputs
advance the patch. An explicit stable version must be strictly newer than
the latest identity at that destination.

Central and JitPack can use the same semantic version from different commits.
Tags use `demo-common/vX.Y.Z-maven-central` and `demo-common/vX.Y.Z-jitpack`.
JitPack uses a tilde in the consumer version. The release fingerprint covers
library sources, packaged guides, toolchain, and shared release helpers.
Generated confirmation records and installation instructions are excluded.

The workflow validates local artifacts before reserving a version. Central
writes an upload marker before upload and verifies public hashes and signatures
after propagation. JitPack checks the build's source commit and public
artifacts. [IMPORT.md](../IMPORT.md) updates only after confirmation.

## Recovery

Keep canonical, pending, and upload-started tags if interrupted. Inspect
the publish log and the provider's status. Run **Finalize Demo Common
release** with the same destination and reserved version. It verifies and
finalizes without another upload. If branch protection rejects a final push,
keep the reservation and have a maintainer reconcile it.

A terminal JitPack failure with no public artifacts can be archived by a
new attempt from corrected source. For JitPack only, an explicit newer
version can opt into bypassing older pending attempts. The override retains
those journals and checks their source provenance. Central has no bypass.

GitHub may replace an older queued run with a newer one. The shared job
lock serializes mutation and is released during the propagation wait.
The reservation tags preserve release state independently of the queue.

## Verify without publishing

```sh
python -m pip install -r scripts/requirements-publishing.txt
python scripts/publishing_config.py check
PYTHONPATH=scripts python -m unittest discover -s scripts/tests -v
./gradlew verifyImportDocs :demo-common:lintRelease :demo-common:assembleRelease
```

CI also assembles unsigned local publications for both destinations and
validates the AAR, sources, documentation archive, POM, and Gradle metadata.
The Pages build runs on pull requests and deploys from main, including after
successful release finalization.
