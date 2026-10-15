"""生成不依赖外部资源的单文件 HTML 演示。"""
import base64
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

from content import FRAMEWORK, SLIDES

ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parent
REVISION = (ROOT / 'source-revision.txt').read_text(encoding='utf-8').strip()
REPO_URL = f'https://github.com/danerlt/ontology-driven-dev/blob/{REVISION}'


def source_url(file):
    if not (REPOSITORY / file).is_file():
        raise ValueError(f'源码依据不存在：{file}')
    return f'{REPO_URL}/{quote(file, safe="/")}'


def render_slide(data, index):
    sources = [{'label': f'仓库依据：{file}', 'url': source_url(file)} for file in data['sources']]
    attrs = f'data-slide="{index}" data-title="{html.escape(data["title"])}" data-chapter="{data["chapter"]}" data-sources=\'{html.escape(json.dumps(sources, ensure_ascii=False), quote=True)}\''
    attrs += f' data-topic="{html.escape(data.get("topic", ""))}"'
    edit_key = data.get('topic') or data.get('edit_key') or str(index)
    body = data['body'].replace('@@REPO@@', REPO_URL).replace('@@FRAMEWORK@@', source_url(FRAMEWORK))
    if data['kind'] == 'cover':
        content = f'<div class="section-label"><span>本体驱动开发 · 原理与工程实践</span><span>2026.10</span></div>{body}'
    else:
        heading = f'<header><div class="section-label"><span>本体驱动开发 · {data["chapter"]}</span><span>{index:02d} / {len(SLIDES)}</span></div><h2 data-edit="title-{edit_key}" data-check="标题">{data["title"]}</h2>'
        lead = f'<p class="lead" data-edit="lead-{edit_key}" data-check="引言">{data["lead"]}</p>' if data['lead'] else ''
        content = f'{heading}{lead}</header><div class="body" data-check="主体安全区">{body}</div>'
    footer = f'<footer class="foot"><span>{data["footer"]}</span><span class="num">{index:02d} / {len(SLIDES)}</span></footer>'
    notes = f'<aside class="speaker-notes">{html.escape(data["notes"])}</aside>'
    return f'<section class="slide {data["kind"]} {"active visible" if index == 1 else ""}" {attrs}>{content}{footer}{notes}</section>'


def icon(paths):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths}</svg>'


def build():
    source = ROOT / 'src'
    font_css = '/* 字体许可与来源\n' + (ROOT/'fonts/LICENSES.txt').read_text(encoding='utf-8') + '\n*/\n'
    for subset in json.loads((ROOT/'fonts/manifest.json').read_text(encoding='utf-8')):
        family = subset['family']
        font = ROOT / 'fonts' / subset['filename']
        if not font.is_file():
            raise RuntimeError('缺少内嵌字体，请先运行 python presentation/fetch_fonts.py。')
        encoded = base64.b64encode(font.read_bytes()).decode('ascii')
        font_css += f"@font-face{{font-family:'{family}';font-style:normal;font-weight:400 800;font-display:swap;src:url(data:font/woff2;base64,{encoded}) format('woff2');unicode-range:{subset['unicode_range']};}}\n"
    parts = {
        'FONTS': font_css,
        'BASE': (source / 'viewport-base.css').read_text(encoding='utf-8'),
        'STYLES': (source / 'styles.css').read_text(encoding='utf-8') + '\n' + (source/'harness.css').read_text(encoding='utf-8'),
        'SLIDES': '\n'.join(render_slide(data, i + 1) for i, data in enumerate(SLIDES)),
        'SCRIPT': (source / 'app.js').read_text(encoding='utf-8') + '\n' + (source/'harness.js').read_text(encoding='utf-8'),
        'COUNT': str(len(SLIDES)),
        'ICON_LEFT': icon('<path d="m15 6-6 6 6 6"/>'),
        'ICON_RIGHT': icon('<path d="m9 6 6 6-6 6"/>'),
        'ICON_FULL': icon('<path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5"/>'),
        'ICON_DOWNLOAD': icon('<path d="M12 3v12m-4-4 4 4 4-4M4 17v4h16v-4"/>'),
        'ICON_PRINT': icon('<path d="M6 8V3h12v5M6 17H3V9h18v8h-3M6 14h12v7H6z"/>'),
    }
    page = (source / 'shell.html').read_text(encoding='utf-8')
    for name, value in parts.items():
        page = page.replace(f'@@{name}@@', value)
    if re.search(r'@@[A-Z_]+@@', page):
        raise ValueError('演示文件仍有未替换的模板标记。')
    (ROOT / 'index.html').write_text(page, encoding='utf-8')
    print(f'已生成 {len(SLIDES)} 页独立演示，包含内嵌字体、讲稿和源码依据。')


if __name__ == '__main__':
    build()
