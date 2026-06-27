#!/usr/bin/env python3
"""
template.html + contents/about.css + contents/{page}.html -> {page}.html
CSS は全ページで about.css を共用。
"""

import re
import urllib.request
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

# 本番サイトから最新の CSS fingerprint URL を取得してテンプレート内の古い URL を差し替え
try:
    with urllib.request.urlopen("https://lab.corkagency.com/about", timeout=10) as resp:
        live_html = resp.read().decode("utf-8")
    m = re.search(
        r'href="(https://assets\.osiro\.it/assets/ui_2_0/front/application-[^"]+\.css)"',
        live_html,
    )
    if m:
        live_css_url = m.group(1)
        template = re.sub(
            r"https://assets\.osiro\.it/assets/ui_2_0/front/application-[^\"']+\.css",
            live_css_url,
            template,
        )
        print(f"CSS URL updated: {live_css_url}")
    else:
        print("Warning: could not find CSS URL in live page, using template as-is")
except Exception as e:
    print(f"Warning: could not fetch live CSS URL ({e}), using template as-is")

for page in PAGES:
    html = (CONTENTS / f"{page}.html").read_text(encoding="utf-8")

    result = template.replace(CSS_MARKER, f'<style id="block_page_css" type="text/css">\n{css}</style>', 1)
    result = result.replace(HTML_MARKER, f'<div class="page-1832 page-go-ahead">{html}</div>', 1)
    result = result.replace('<head>', '<head><base href="/web-about/">', 1)
    result = re.sub(r'<script\b[^>]*>.*?</script>', '', result, flags=re.DOTALL)
    # root-relative /images/ パスを絶対 URL に変換（GitHub Pages では解決できないため）
    result = re.sub(r'url\((/images/)', r'url(https://lab.corkagency.com\1', result)

    out = BASE / f"{page}.html"
    out.write_text(result, encoding="utf-8")
    print(f"Built: {out} ({out.stat().st_size:,} bytes)")
