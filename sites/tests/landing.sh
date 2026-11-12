#!/bin/sh
# Render the actual landing template against isolated release metadata.
set -eu
repository=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
fixture=$(mktemp -d)
trap 'rm -rf "$fixture"' EXIT
mkdir -p "$fixture/templates" "$fixture/content"
cp "$repository/sites/templates/index.html" "$fixture/templates/index.html"
cat > "$fixture/templates/base.html" <<'TEMPLATE'
{% set scopes = load_data(path="scopes.json") %}
{% set language = section.lang %}{% set spanish = language == "es" %}
<html lang="{{ language }}"><body>{% block content %}{% endblock content %}</body></html>
TEMPLATE
cat > "$fixture/zola.toml" <<'CONFIG'
base_url = "https://example.test/"
title = "Demo Common"
default_language = "en"
[languages.es]
[extra]
repository = "lambdawalker/android.apexfission.demo-common"
CONFIG
for locale in en es; do
    name=_index.md
    if [ "$locale" = es ]; then name=_index.es.md; fi
    printf '+++\ntemplate = "index.html"\n+++\n' > "$fixture/content/$name"
done
render() { zola --root "$fixture" --config zola.toml build > "$fixture/build.log" 2>&1 || { cat "$fixture/build.log"; exit 1; }; }
cat > "$fixture/scopes.json" <<'JSON'
[
 {"module":"demo-common","language":"en","version":"development","development":true,"root":"/dev/","pages":[]},
 {"module":"demo-common","language":"en","version":"0.1.9-jitpack","development":false,"root":"/old/","pages":[]},
 {"module":"demo-common","language":"en","version":"0.1.10-jitpack","development":false,"root":"/jitpack/en/","pages":[]},
 {"module":"demo-common","language":"es","version":"0.1.10-jitpack","development":false,"root":"/jitpack/es/","pages":[]},
 {"module":"demo-common","language":"en","version":"0.1.10-maven-central","development":false,"root":"/central/en/","pages":[]},
 {"module":"demo-common","language":"es","version":"0.1.10-maven-central","development":false,"root":"/central/es/","pages":[]},
 {"module":"another-module","language":"en","version":"99.0.0-jitpack","development":false,"root":"/other/","pages":[]}
]
JSON
render
grep -Fq 'data-latest-version="0.1.10"' "$fixture/public/index.html"
grep -Fq 'class="hero-source primary-docs" href="/central/en/"' "$fixture/public/index.html"
grep -Fq 'class="hero-source primary-docs" href="/central/es/"' "$fixture/public/es/index.html"
grep -Fq 'href="/jitpack/es/"' "$fixture/public/index.html"
grep -Fq 'Última versión publicada' "$fixture/public/es/index.html"
grep -Fq '<details class="other-versions">' "$fixture/public/index.html"
grep -Fq 'href="/old/"' "$fixture/public/index.html"
# A newer release available only on JitPack must win over an older Central release.
cat > "$fixture/scopes.json" <<'JSON'
[
 {"module":"demo-common","language":"en","version":"0.9.99-maven-central","development":false,"root":"/central-old/","pages":[]},
 {"module":"demo-common","language":"en","version":"0.10.0-jitpack","development":false,"root":"/new/","pages":[]}
]
JSON
render
grep -Fq 'data-latest-version="0.10.0"' "$fixture/public/index.html"
grep -Fq 'class="hero-source primary-docs" href="/new/"' "$fixture/public/index.html"
grep -Fq 'href="/central-old/"' "$fixture/public/index.html"
# Development is never presented as a confirmed release.
cat > "$fixture/scopes.json" <<'JSON'
[{"module":"demo-common","language":"en","version":"development","development":true,"root":"/dev/","pages":[]}]
JSON
render
grep -Fq 'No confirmed release yet' "$fixture/public/index.html"
grep -Fq 'href="/dev/"' "$fixture/public/index.html"
if grep -Fq 'class="hero-source primary-docs"' "$fixture/public/index.html"; then exit 1; fi
printf 'Landing release selection, destination links, localization and unreleased fallback pass.\n'
