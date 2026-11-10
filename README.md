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
