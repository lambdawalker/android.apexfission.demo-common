# Documentation website

The shared Rust CLI prepares versioned content and Zola 0.23.6 renders it with the bundled Apexfission documentation theme. No Python or Node.js is required to build this website. Use the immutable CLI commit pinned in `.project/setup/config.yaml` through `./setup.sh` or `setup.bat`; Cargo compiles a source pin once and caches it. Install [Zola 0.23.6](https://github.com/getzola/zola/releases/tag/v0.23.6) on PATH and verify its archive checksum. CI installs its checksum-pinned Zola automatically.

With Zola on PATH, run the pinned CLI from the repository root:

```sh
./setup.sh build_docs --check
```

Output is `sites/dist/`, including search indexes and raw Markdown. To inspect it locally, serve the repository root with any static HTTP server and open `/sites/dist/`; use a build with `--base /sites/dist` for that preview. Production uses `/android.apexfission.demo-common` as its URL base. The base path must match the directory your server exposes.

## Content ownership

| Content | Source |
| --- | --- |
| English consumer guides | `docs/agents/`, including nested Markdown files |
| Spanish guides | Matching `docs/es/` files |
| Reviewed translation freshness | `docs/es/translations.json`, SHA-256 of each exact English source |
| Confirmed releases and provenance | `docs/releases/history/demo-common/` |
| Current installation | Generated `IMPORT.md`, using `docs/templates/MODULE_IMPORT.md.template` |
| Build configuration | `sites/zola.toml` |
| Shared layout, styling and browser controls | `gradle.android-repo-setup/cli/site-theme/` |

The CLI stages Markdown and theme files in a temporary directory. Builds never execute historical scripts or rewrite canonical guides. Historical code and documentation revisions remain visible separately. Provider-specific installation instructions come only from that release's confirmed destinations. Development is explicitly unreleased, and missing/stale translations show English from the selected revision with a visible fallback notice. Corrections may use a retained translation tree without changing the release's code identity.

Canonical pages use `/en/demo-common/<version>/` and `/es/demo-common/<version>/`, with `/raw/*.md` companions. `versions.json` describes scopes for selectors and integrations. Previous `/<version>/<language>/*.html` links remain available. Root `IMPORT.md`, `llms.txt` and `agents/*.md` remain available to tools.

The Documentation workflow builds and checks PRs and publishes only main through GitHub Pages. Release completion also triggers documentation. Never publish a new Android artifact merely to retry a website build. Keep Pages configured to use GitHub Actions.

`build_docs --check` validates local generated links, anchors, images and raw Markdown endpoints; it does not verify external network availability or render Android UI. Site controls provide theme preference, scoped search and version/language switching that preserves the guide when available. If a guide is missing in the target scope, the selector explains the index fallback.

Do not edit generated output. For repository-specific layout changes, override bundled template files under `sites/templates/` or static assets under `sites/static/` and rerun the complete build/check.

## Direct documentation and release versions

The home URL opens the latest released documentation immediately, without a
catalog or presentation cards. `/es/` opens the Spanish release. Selection uses
numeric versions, so `0.1.10` follows `0.1.9`; canonical releases take precedence,
then Maven Central when both historical destinations have the newest patch.
Development is used only when that language has no confirmed release.

The version selector shows exact releases, such as **0.1.2**, with one entry
for equivalent Maven Central and JitPack publications of that patch. Older
patch releases remain individually selectable. **Development** remains a separate, unreleased entry.
The exact patch and confirmed repositories appear above every guide; publication
source commits remain available under **Publication details**. Language switching,
search and guide navigation keep using the original scopes and routes.

`sites/templates/` contains the home, guide and availability overrides;
`sites/static/release-docs.css` styles the availability line. Historical 0.1.2
publications are grouped using the explicitly verified sources and matching
artifact hashes in `sites/static/release-equivalence.json`. Version equality
alone never establishes equivalence. Future canonical releases read their
confirmed repositories directly from the shared release metadata. Existing
provider-specific deep links, raw Markdown and historical records stay valid.

Run the template regressions with Zola on `PATH`:

```sh
sh sites/tests/landing.sh
```

## Corrected documentation for 0.1.2

Maven Central 0.1.2 comes from `11d3cdce31c481fe2204f00d25b5fd93e5f9a18c`;
JitPack's `demo-common~v0.1.2-jitpack` comes from
`86b43bd7ee858ceb09642ec755f0dc99e7eb5a2f`. The commits differ only in
generated installation instructions and JitPack confirmation records. Their
public AAR, sources and Javadoc archives have matching verified SHA-256 hashes.

Both historical archives select a reviewed bilingual documentation revision via
`documentation_ref`. It corrects the pre-release/snapshot instructions, explains
the original publication provenance and retains the 0.1.2 API behavior. Catalog
screenshots come from the exact release source in CI run 42577067647; earlier
pre-release images were replaced. Source commits, provider tags, artifact hashes and confirmation
records remain unchanged. Development documentation continues to describe the
current implementation, including its newer Settings-button placement.

The illustrated documentation revision is retained on `docs/demo-common-0.1.2-catalog` so a full
history fetch can obtain it even if the integration PR is squash-merged. Keep
that documentation branch available; its immutable commit, rather than the
branch name, is what the archives reference.

The Compose API guide includes reviewed light/dark images for the screen, both
card overloads and title. Component screenshot provenance and reproduction steps
are in `docs/screenshots/README.md`.
