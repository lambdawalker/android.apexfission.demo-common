# Publishing Demo Common

Only the `:demo-common` release AAR is published. Gradle runs on JDK 21 and
produces Java 17 bytecode.

## Owner setup

The CLI is pinned to released `v0.1.20` in `.project/setup/config.yaml`.
The Gradle plugin remains at released `v0.1.9`. The documentation site requires Zola 0.23.6.

Run `setup.bat` on Windows or `sh ./setup.sh` on Linux/macOS. The generated
launchers install and validate the configured CLI, cache it under
`.project/setup/cache/`, and forward arguments. Release pins download verified
binaries; full commit pins build with Cargo. Run `setup check` to validate setup.
See [shared setup](shared-setup.md) for regeneration and pin updates.

The interactive wizard supports Tab/Shift+Tab navigation, Space to toggle
checkboxes, and Enter to activate buttons. Password fields are masked.

Use a repository-scoped
GitHub token with the environment administration permissions shown by
the wizard. Review the changes before applying. Central requires
`MAVEN_CENTRAL_USERNAME`, `MAVEN_CENTRAL_PASSWORD`, `SIGNING_IN_MEMORY_KEY`,
and the signing password if applicable. Create a Maven signing key in the
wizard or select an existing key from the local GnuPG keyring. Confirm namespace ownership in Central Portal. Public JitPack
has an empty environment and requires a public GitHub repository.

Use a 15-minute wait timer on `delayed-docs` where supported. In Settings →
Pages, select GitHub Actions. The release token must be able to push
release tags and confirmed documentation updates under the existing rules.
The Maven Central guard also updates its `release-pending/*` tag when
recording the upload marker.

## Publish

Run **Publish Demo Common** on `main`. Choose Maven Central or JitPack and
leave **version** blank. New releases share one immutable source commit and
build-input fingerprint across destinations. Matching inputs reuse that module
version and its exact source; changed inputs advance the patch. An explicit
existing shared version is accepted only when the inputs match. A new explicit
version must be newer than the module's existing release history.

The first publication atomically reserves
`release-identity/demo-common/X.Y.Z` with its destination journal. Publishing
the same version to the other destination reuses this identity. Provider tags
`demo-common/vX.Y.Z-maven-central` and `demo-common/vX.Y.Z-jitpack` and their
publication statuses remain independent. JitPack uses a tilde in the consumer
version. Signing and provider metadata can differ, so matching artifact bytes
are not required across destinations.

The release fingerprint covers library sources, packaged guides, toolchain,
tracked build configuration and shared release helpers. Generated confirmation
records and installation instructions are excluded. Failed attempts keep their
immutable shared version; they never free it for different source code.

Historical releases such as `0.1.2` retain their original provider-specific
source identities. They are not merged retroactively. New shared versions start
above the existing module history, and confirmed destinations appear together
under one documentation version.

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

Generated publishing workflows reconcile the selected module and destination
before choosing a version and after a reserved attempt fails. For manual
recovery, preview the exact version, review the report, then apply eligible
changes. Maven Central is the default destination; set
`RELEASE_REPOSITORY=jitpack` for JitPack. Run under the repository release
concurrency lock, with no other release operation running. Applying changes
requires permission to push journal refs and verified release metadata to `main`.

```sh
android-repo-setup module_release reconcile --module demo-common --version X.Y.Z
android-repo-setup module_release reconcile --module demo-common --version X.Y.Z --apply
```

Reconciliation archives an abandoned Central reservation only when the new
upload protocol proves its upload guard never ran and no artifacts exist. An
upload-started Central attempt requires `FAILED` status for the matching
deployment receipt and no public artifacts; JitPack requires a terminal failure
for the reserved commit and no public artifacts. Provider status is checked
again before archiving. Fully verified public artifacts are finalized without
another upload. Active or uncertain attempts remain pending. A missing receipt
or deployment, absence from a public version listing, age, or an Actions failure
is not proof of provider failure. See the
[shared reconciliation guide](https://github.com/lambdawalker/gradle.android-repo-setup/blob/v0.1.20/docs/release-reconciliation.md)
for evidence requirements and report states.

For JitPack only, an explicit newer
version can opt into bypassing older pending attempts. The override retains
those journals and checks their source provenance. For Central, the
recovery override only skips the public version listing and requires an
explicit newer version.

GitHub may replace an older queued run with a newer one. The shared job
lock serializes mutation and is released during the propagation wait.
The reservation tags preserve release state independently of the queue.

## Verify without publishing

```sh
android-repo-setup publishing_config check
android-repo-setup import_docs --check
android-repo-docs build --check
android-repo-setup workflows --check
./gradlew verifyImportDocs :demo-common:testDebugUnitTest :demo-common:lintRelease :demo-common:assembleRelease
```

CI also assembles unsigned local publications for both destinations and
validates the AAR, sources, documentation archive, POM, and Gradle metadata.
The Pages build runs on pull requests and deploys from main, including after
successful release finalization.


## Prepare signing for a demo APK

Run this from a private terminal with a JDK. Use `./setup.sh` on Linux or
macOS, or `setup.bat` on Windows. Both launchers use the configured `tooling_ref`
and follow the installation and cache rules above; the `.project/setup/cache/` directory is
ignored by Git. The CLI opens your existing encrypted vault in place. To open
the signing wizard directly, run `./setup.sh signing` or `setup.bat signing`.

In the terminal wizard, choose keystore creation, GitHub setup with an existing key, or both.
The first run defaults to both. Later runs default to the incomplete steps,
or Exit after both steps are complete. Non-secret prompts use a 20-second countdown until you type, paste, or click a field.
After interacting, confirm manually. If untouched, the displayed default applies. Upload, reset, and password-reveal confirmations
default to cancelling or preserving the current state. Password and token
prompts wait for input.

The per-repository vault in `~/.projects/android.apexfission.demo-common/secrets/` encrypts setup
progress, keystore details, and verified signing passwords. It can
remember a GitHub token if you explicitly opt in. Unlock the vault with
your separate vault password on each run. Losing that password means
losing access to the saved answers. Resetting local setup clears those
answers while preserving the keystore and GitHub secrets.

Use a fine-grained GitHub token scoped to this repository with
**Administration: read/write** and **Environments: read/write**.
The script prepares `demo-apk-release` for the `main` branch and prompts
for review before writing to GitHub. It defaults to the `demo-common`
alias and a repository-specific keystore filename in the project secrets folder. Keep the keystore
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
android-repo-setup workflows --check
```

## Local setup configuration

Repository setup configuration lives in `.project/setup/`:

- `config.yaml`: project identity and shared tooling version.
- `repositories.yml`: publishing destinations.
- `repositories.properties`: generated Gradle publishing settings.
- `workflow-generation.json`: generated workflow hashes (created by setup).

Commit these files with the generated `.github/workflows/` files. The transient
`workflow-generation.lock` is ignored. Signing keys and the encrypted vault stay
outside the checkout under `~/.projects/<project>/secrets/`.


## Documentation website

The website uses Zola 0.23.6 and the pinned Rust CLI; it requires neither Python nor Node.js. Install both tools on PATH and run `android-repo-docs build --check` from the repository root. The opt-in backend is configured in `sites/zola.toml`; [the website guide](../sites/README.md) covers content ownership, versioned English/Spanish pages, reviewed translation hashes, local preview and Pages deployment. Confirmed release metadata remains authoritative; documentation builds never publish an Android artifact or change historical source identities.
