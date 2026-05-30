#!/usr/bin/env python3
"""
template.html + contents/about.css + contents/{page}.html -> {page}.html
CSS は全ページで about.css を共用。
"""

from pathlib import Path

BASE = Path(__file__).parent.parent  # scripts/ の親 = プロジェクトルート
CONTENTS = BASE / "contents"

PAGES = ["about", "go-ahead", "sake-awai"]

template = (CONTENTS / "template.html").read_text(encoding="utf-8")
css      = (CONTENTS / "about.css").read_text(encoding="utf-8")

for page in PAGES:
    html = (CONTENTS / f"{page}.html").read_text(encoding="utf-8")

    # CSS を <style id="block_page_css"> タグに挿入
    result = template.replace(
        '<style id="block_page_css" type="text/css"></style>',
        f'<style id="block_page_css" type="text/css">\n{css}</style>',
        1,
    )

    # HTML を <div class="page-1832 page-go-ahead"> に挿入
    result = result.replace(
        '<div class="page-1832 page-go-ahead"></div>',
        f'<div class="page-1832 page-go-ahead">{html}</div>',
        1,
    )

    out = BASE / f"{page}.html"
    out.write_text(result, encoding="utf-8")
    print(f"Built: {out} ({out.stat().st_size:,} bytes)")
