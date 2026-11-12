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
grep -Fq 'content="0;url=/central/en/"' "$fixture/public/index.html"
grep -Fq 'content="0;url=/central/es/"' "$fixture/public/es/index.html"
if grep -Fq 'scope-card' "$fixture/public/index.html"; then exit 1; fi
# A newer release available only on JitPack must win over an older Central release.
cat > "$fixture/scopes.json" <<'JSON'
[
 {"module":"demo-common","language":"en","version":"0.9.99-maven-central","development":false,"root":"/central-old/","pages":[]},
 {"module":"demo-common","language":"en","version":"0.10.0-jitpack","development":false,"root":"/new/","pages":[]}
]
JSON
render
grep -Fq 'content="0;url=/new/"' "$fixture/public/index.html"
# A shared canonical release has one bilingual route and provider availability.
cat > "$fixture/scopes.json" <<'JSON'
[
 {"module":"demo-common","language":"en","version":"0.1.11","development":false,"root":"/shared/en/","pages":[],"destinations":["jitpack","maven-central"]},
 {"module":"demo-common","language":"es","version":"0.1.11","development":false,"root":"/shared/es/","pages":[],"destinations":["jitpack","maven-central"]}
]
JSON
render
grep -Fq 'content="0;url=/shared/en/"' "$fixture/public/index.html"
grep -Fq 'content="0;url=/shared/es/"' "$fixture/public/es/index.html"
# Development is never presented as a confirmed release.
cat > "$fixture/scopes.json" <<'JSON'
[{"module":"demo-common","language":"en","version":"development","development":true,"root":"/dev/","pages":[]}]
JSON
render
grep -Fq 'content="0;url=/dev/"' "$fixture/public/index.html"
grep -Fq 'Documentación no disponible' "$fixture/public/es/index.html"

# Render the real documentation template: version families preserve original scope
# indices, choose the latest patch numerically, and expose only verified providers.
cp "$repository/sites/templates/page.html" "$repository/sites/templates/release_availability.html" "$fixture/templates/"
mkdir -p "$fixture/static"
cp "$repository/sites/static/release-equivalence.json" "$fixture/static/"
cat > "$fixture/templates/base.html" <<'TEMPLATE'
{% set scopes = load_data(path="scopes.json") %}
{% set language = "en" %}{% if section is defined %}{% set language = section.lang %}{% endif %}
{% if page is defined %}{% set scope = scopes[page.extra.scope_index] %}{% set language = scope.language %}{% endif %}
{% set spanish = language == "es" %}
<html lang="{{ language }}"><head><title>{% block title %}Docs{% endblock title %}</title></head><body>{% block content %}{% endblock content %}</body></html>
TEMPLATE
cat > "$fixture/content/guide.md" <<'PAGE'
+++
title = "Guide"
template = "page.html"
[extra]
scope_index = 1
guide = ""
fallback = false
+++
Documentation body.
PAGE
cat > "$fixture/scopes.json" <<'JSON'
[
 {"module":"demo-common","label":"Demo Common","language":"en","version":"development","development":true,"root":"/dev/","pages":[],"source":"dev","documentation_ref":"docs"},
 {"module":"demo-common","label":"Demo Common","language":"en","version":"0.1.2-maven-central","development":false,"root":"/central/","pages":[],"source":"11d3cdce31c481fe2204f00d25b5fd93e5f9a18c","documentation_ref":"docs","translation_tree":"retained-translation"},
 {"module":"demo-common","label":"Demo Common","language":"en","version":"0.1.2-jitpack","development":false,"root":"/jitpack/","pages":[],"source":"86b43bd7ee858ceb09642ec755f0dc99e7eb5a2f","documentation_ref":"docs"},
 {"module":"demo-common","label":"Demo Common","language":"en","version":"0.1.9","development":false,"root":"/nine/","pages":[],"source":"nine","documentation_ref":"docs","destinations":["jitpack"]},
 {"module":"demo-common","label":"Demo Common","language":"en","version":"0.1.10","development":false,"root":"/ten/","pages":[],"source":"ten","documentation_ref":"docs","destinations":["jitpack","maven-central"]}
]
JSON
render
html="$fixture/public/guide/index.html"
grep -Fq '<option value="4" selected>0.1.x</option>' "$html"
test "$(grep -o '>0.1.x</option>' "$html" | wc -l)" -eq 1
grep -Fq '>Development</option>' "$html"
grep -Fq 'href="/central/installation/">Maven Central</a>' "$html"
grep -Fq 'href="/jitpack/installation/">JitPack</a>' "$html"
grep -Fq 'AAR, sources and Javadoc archives are identical' "$html"
grep -Fq '<code>retained-translation</code>' "$html"
# Matching version numbers alone do not justify claiming equivalent publications.
sed 's/86b43bd7ee858ceb09642ec755f0dc99e7eb5a2f/unverified/' "$fixture/scopes.json" > "$fixture/changed.json"
mv "$fixture/changed.json" "$fixture/scopes.json"
render
if grep -Fq 'href="/jitpack/installation/">JitPack</a>' "$html"; then exit 1; fi
# Canonical metadata confirms both destinations without an equivalence override.
sed 's/scope_index = 1/scope_index = 4/' "$fixture/content/guide.md" > "$fixture/changed.md"
mv "$fixture/changed.md" "$fixture/content/guide.md"
render
grep -Fq '<strong>0.1.10</strong>' "$html"
grep -Fq 'href="/ten/installation/">Maven Central</a>' "$html"
grep -Fq 'href="/ten/installation/">JitPack</a>' "$html"
# Spanish controls, availability and direct latest-documentation link.
sed 's/"language":"en"/"language":"es"/g' "$fixture/scopes.json" > "$fixture/changed.json"
mv "$fixture/changed.json" "$fixture/scopes.json"
render
grep -Fq ' · Disponible en' "$html"
grep -Fq '>Desarrollo</option>' "$html"
grep -Fq 'https://example.test/es' "$html"
printf 'Direct documentation, numeric release selection, version families and verified availability pass.\n'
