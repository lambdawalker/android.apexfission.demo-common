# Repository instructions

Keep public behavior, agent docs, and sample aligned. The consumer guide
starts at [docs/agents/index.md](docs/agents/index.md). Generate IMPORT.md
from confirmed release records. Keep screenshots and demo code out of the
library's publication, and use credential-free checks for release changes.


Documentation uses the opt-in Zola backend in `sites/zola.toml`. Read `sites/README.md` before changing the site. Run the pinned Rust CLI with `android-repo-setup build_docs --check` and Zola 0.23.6 on PATH. English guides are canonical in `docs/agents/`; Spanish translations in `docs/es/` must preserve code samples and heading structure. Record English SHA-256 hashes in `docs/es/translations.json` only after reviewing the translation. Do not rewrite historical release identities. Generated workflows belong to the shared CLI; change templates/inputs and regenerate instead of hand-editing managed files.

Validate Android string translations with `android-repo-setup check_localization`. The generated verify-localization workflow runs this check across app and library source sets.
