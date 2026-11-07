"""Build the static English/Spanish docs and immutable release routes."""
import argparse
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import markdown

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import documentation_history

DEST = ROOT / 'sites/dist'
GITHUB = 'https://github.com/lambdawalker/android.apexfission.demo-common'
GUIDES = {'index': 'Overview', 'quickstart': 'Quickstart', 'api': 'API'}


def source(ref, path):
    if ref is None:
        return (ROOT / path).read_text(encoding='utf-8')
    return subprocess.check_output(['git', 'show', f'{ref}:{path}'], cwd=ROOT, text=True)


def write(path, body):
    path = DEST / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding='utf-8')


def render(text):
    return markdown.markdown(text, extensions=['fenced_code', 'tables', 'toc'])


def layout(lang, title, nav, body, base):
    return (
        f'<!doctype html><html lang="{lang}"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{html.escape(title)} · Demo Common</title>'
        f'<link rel="stylesheet" href="{base}/style.css">'
        f'<header><a href="{base}/">Demo Common</a><nav>{nav}</nav></header>'
        f'<main>{body}</main></html>\n'
    )


def guide_links(text, base, ref, *, raw):
    def link(match):
        target = match[1]
        if target.startswith(('#', 'http://', 'https://')):
            return match[0]
        if target.endswith('IMPORT.md'):
            return f']({base}/' + ('IMPORT.md)' if raw else 'install.html)')
        if target.split('#')[0] in {f'{name}.md' for name in GUIDES}:
            return '](' + (target if raw else target.replace('.md', '.html', 1)) + ')'
        return f']({GITHUB}/blob/{ref or "main"}/{target.removeprefix("../../")})'
    # Leave fenced snippets untouched.
    return ''.join(
        part if index % 2 else re.sub(r'\]\(([^)]+)\)', link, part)
        for index, part in enumerate(re.split(r'(```[\s\S]*?```)', text))
    )


def build(base):
    shutil.rmtree(DEST, ignore_errors=True)
    DEST.mkdir(parents=True)
    shutil.copy(ROOT / 'sites/style.css', DEST / 'style.css')
    documentation_history.verify(ROOT)
    entries = documentation_history.load_catalog(ROOT)
    versions = [('development', None, None)]
    versions.extend((documentation_history.route_version(e), e['documentation_ref'], e) for e in entries)
    latest = versions[-1][0]
    for name, ref, entry in versions:
        for lang in ('en', 'es'):
            folder = f'{name}/{lang}'
            url = f'{base}/{folder}'
            other = 'es' if lang == 'en' else 'en'
            install = (documentation_history.installation(entry, lang) if entry else
                       source(None, 'IMPORT.md'))
            write(f'{folder}/IMPORT.md', install)
            for page, title in {**GUIDES, 'install': 'Installation', 'releases': 'Publishing'}.items():
                versions_menu = ' '.join(
                    f'<a href="{base}/{v}/{lang}/{page}.html">{html.escape(v)}</a>'
                    for v, _, _ in versions
                )
                nav = ' '.join(f'<a href="{url}/{p}.html">{label}</a>' for p, label in
                               {**GUIDES, 'install': 'Installation', 'releases': 'Publishing'}.items())
                nav += f' <a href="../{other}/{page}.html">{other.upper()}</a>'
                fallback = ('<p>Guía en inglés para esta versión.</p>' if lang == 'es'
                            and (page != 'install' or entry is None) else '')
                path = f'docs/agents/{page}.md' if page in GUIDES else 'docs/releases.md'
                text = install if page == 'install' else source(ref, path)
                body = f'<p>Version: {html.escape(name)} · {versions_menu}</p>{fallback}'
                body += render(guide_links(text, url, ref, raw=False))
                if page == 'index' and name == 'development':
                    body += ('<div class="gallery"><img src="' + base +
                             '/media/catalog-light.png" alt="Populated light catalog"><img src="' +
                             base + '/media/catalog-dark.png" alt="Populated dark catalog"></div>')
                write(f'{folder}/{page}.html', layout(lang, title, nav, body, base))
                if page in GUIDES:
                    write(f'{folder}/agents/{page}.md', guide_links(text, url, ref, raw=True))
    write('index.html', layout('en', 'Documentation', '',
          f'<meta http-equiv="refresh" content="0;url={base}/{latest}/en/index.html">'
          f'<a href="{base}/{latest}/en/index.html">Open Demo Common documentation</a>', base))
    shutil.copyfile(DEST / f'{latest}/en/IMPORT.md', DEST / 'IMPORT.md')
    shutil.copytree(DEST / f'{latest}/en/agents', DEST / 'agents')
    write('llms.txt', f'# Demo Common\n\n- [Integration guide]({base}/agents/index.md)\n'
          f'- [Installation]({base}/IMPORT.md)\n')
    media = DEST / 'media'
    media.mkdir()
    for image in sorted((ROOT / 'docs/screenshots').glob('*.png')):
        shutil.copy(image, media / image.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='/android.apexfission.demo-common')
    build(parser.parse_args().base.rstrip('/'))
