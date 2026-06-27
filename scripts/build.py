#!/usr/bin/env python3
"""
template.html + contents/about.css + contents/{page}.html -> {page}.html
CSS は全ページで about.css を共用。
"""

from pathlib import Path
from pages import PAGES

BASE = Path(__file__).parent.parent  # scripts/ の親 = プロジェクトルート
CONTENTS = BASE / "contents"

CSS_MARKER  = '<style id="block_page_css" type="text/css"></style>'
HTML_MARKER = '<div class="page-1832 page-go-ahead"></div>'

template = (CONTENTS / "template.html").read_text(encoding="utf-8")
css      = (CONTENTS / "about.css").read_text(encoding="utf-8")

assert CSS_MARKER in template, \
    f"CSS マーカーが template.html に見つかりません: {CSS_MARKER!r}"
assert HTML_MARKER in template, \
    f"HTML マーカーが template.html に見つかりません: {HTML_MARKER!r}"

for page in PAGES:
    html = (CONTENTS / f"{page}.html").read_text(encoding="utf-8")

    result = template.replace(CSS_MARKER, f'<style id="block_page_css" type="text/css">\n{css}</style>', 1)
    result = result.replace(HTML_MARKER, f'<div class="page-1832 page-go-ahead">{html}</div>', 1)
    result = result.replace('<head>', '<head><base href="/web-about/">', 1)

    out = BASE / f"{page}.html"
    out.write_text(result, encoding="utf-8")
    print(f"Built: {out} ({out.stat().st_size:,} bytes)")
