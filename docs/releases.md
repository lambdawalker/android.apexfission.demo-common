# Publishing Demo Common

Only the `:demo-common` release AAR is published. Gradle runs on JDK 21 and
produces Java 17 bytecode.

## Owner setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and run
`uv run scripts/setup_github_environments.py`. Use a repository-scoped
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

If an interrupted Central attempt was never published and Central Portal
confirms no deployment exists, archive the unconfirmed `release-pending` and
`release-uploading` markers to `release-failed/` with
`python3 scripts/module_release.py abort-unconfirmed --module demo-common --version X.Y.Z`
(which verifies `published_versions` on Maven Central before archiving).

A terminal JitPack failure with no public artifacts can be archived by a
new attempt from corrected source. For JitPack only, an explicit newer
version can opt into bypassing older pending attempts. The override retains
those journals and checks their source provenance. Central has no bypass.

GitHub may replace an older queued run with a newer one. The shared job
lock serializes mutation and is released during the propagation wait.
The reservation tags preserve release state independently of the queue.

## Verify without publishing

```sh
python3 -m pip install -r scripts/requirements-setup.txt -r sites/requirements.txt
python3 scripts/publishing_config.py check
python3 scripts/import_docs.py --check
python3 sites/build.py --check
PYTHONPATH=scripts python3 -m unittest discover -s scripts/tests -v
./gradlew verifyImportDocs :demo-common:testDebugUnitTest :demo-common:lintRelease :demo-common:assembleRelease
```

CI also assembles unsigned local publications for both destinations and
validates the AAR, sources, documentation archive, POM, and Gradle metadata.
The Pages build runs on pull requests and deploys from main, including after
successful release finalization.


## Prepare signing for a demo APK

Run this from a private terminal with a JDK and uv.

Run `./setup.sh` on Linux or macOS, or `setup.bat` on Windows.
Both launchers use pinned revision `b3294108af351fd5ee8a7743fa641b2fc6143617` of the shared
[Android Repository Setup wizard](https://github.com/lambdawalker/python.android-repo-setup).
The launcher opens your existing encrypted vault in place.

In the terminal wizard, choose keystore creation, GitHub setup with an existing key, or both.
The first run defaults to both. Later runs default to the incomplete steps,
or Exit after both steps are complete. The wizard shows a 20-second countdown on non-secret prompts. Timeout
uses the displayed default. Upload, reset, and password-reveal confirmations
default to cancelling or preserving the current state. Password and token
prompts wait for input.

The per-repository vault in `~/.demo-common-signing/` encrypts setup
progress, keystore details, and verified signing passwords. It can
remember a GitHub token if you explicitly opt in. Unlock the vault with
your separate vault password on each run. Losing that password means
losing access to the saved answers. Resetting local setup clears those
answers while preserving the keystore and GitHub secrets.

Use a fine-grained GitHub token scoped to this repository with
**Administration: read/write** and **Environments: read/write**.
The script prepares `demo-apk-release` for the `main` branch and prompts
for review before writing to GitHub. It defaults to the `demo-common`
alias and `~/.demo-common-signing/demo-common.jks`. Keep the keystore
outside the checkout and back it up securely.

Enter separate keystore and key passwords or press Enter at either
prompt to generate a 25-character password. Save generated passwords
in a password manager when prompted. They are displayed only after
you opt in, so use a terminal without session recording. Existing
signing secrets are preserved. If an upload stops partway through,
rerun with the original keystore, alias, and passwords.

This setup prepares the signing environment. Building and attaching
a signed APK to a GitHub Release is a separate workflow.

The wizard allows one local process per repository to prevent concurrent
vault updates. This does not coordinate different devices: run remote
environment setup from one device at a time. Completed environments are
checked again for main-only deployment rules. Unexpected setup failures
use a generic error message to avoid printing credential-bearing tracebacks.

Credential-free regression checks:
```sh
PYTHONPATH=scripts python3 -m unittest discover -s scripts/tests -v
```
