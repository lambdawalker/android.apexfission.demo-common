# Apexfission Demo Common

Build demo catalogs with three Material 3 Compose components. `DemoScreen`
provides a welcome header and scrolling list. `DemoCard` holds custom
content, and `CardTitle` adds a heading and optional icon.

- [Documentation website](https://lambdawalker.github.io/android.apexfission.demo-common/)
- [Confirmed installation](IMPORT.md)
- [Quickstart and Compose example](docs/agents/quickstart.md)
- [Agent integration guide](docs/agents/index.md)
- [Publishing and recovery](docs/releases.md)

Android API 28+ with Compose Material 3. The repository includes light and dark
previews and an executable screenshot suite.

The `demo-common` module contains the published library. The `app` module runs
the demo catalog with `./gradlew :app:installDebug`. Shared dependency and plugin
versions are defined in `gradle/libs.versions.toml`.


## Documentation tooling

Documentation is maintained by the independently pinned `android-repo-docs` executable.
Use `sh ./docs.sh check` on Linux/macOS or `docs.bat check` on Windows.
The launcher installs the configured release or immutable source revision on first use;
source pins require Rust and Git. No setup credentials are needed.

- `sh ./docs.sh sources check` verifies reviewed Kotlin inputs and examples.
- `sh ./docs.sh sources update` intentionally refreshes generated references and examples; review the diff.
- `sh ./docs.sh build --check` builds the existing documentation site locally.
- `sh ./docs.sh bootstrap check` verifies the launcher files against their independent pin.

Configuration and project-specific introductory Markdown live in `.project/docs/`.
Confirmed release records and archived source identities remain authoritative.
Documentation checks do not accept images, publish artifacts, or deploy the site.
