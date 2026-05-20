#!/usr/bin/env python3
"""
template.html + contents/about.css + contents/about.html -> about-2.html
"""

from pathlib import Path

BASE = Path(__file__).parent.parent  # scripts/ の親 = プロジェクトルート
CONTENTS = BASE / "contents"

template = (CONTENTS / "template.html").read_text(encoding="utf-8")
css      = (CONTENTS / "about.css").read_text(encoding="utf-8")
html     = (CONTENTS / "about.html").read_text(encoding="utf-8")

# CSS を <style id="block_page_css"> タグに挿入
result = template.replace(
    '<style id="block_page_css" type="text/css"></style>',
    f'<style id="block_page_css" type="text/css">\n{css}</style>',
    1,
)

# HTML を <div class="page-1834 page-20260520-about-2"> に挿入
result = result.replace(
    '<div class="page-1834 page-20260520-about-2"></div>',
    f'<div class="page-1834 page-20260520-about-2">{html}</div>',
    1,
)

out = BASE / "about.html"
out.write_text(result, encoding="utf-8")
print(f"Built: {out} ({out.stat().st_size:,} bytes)")
