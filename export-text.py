#!/usr/bin/env python3
"""
contents/about.html から HTML タグを除去してテキストを about.md に出力
"""

from html.parser import HTMLParser
from pathlib import Path
import re

BASE = Path(__file__).parent

HEADINGS   = {'h1': '#', 'h2': '##', 'h3': '###', 'h4': '####', 'h5': '#####'}
SKIP_TAGS  = {'script', 'style'}  # img は void element のため除外
BLOCK_TAGS = {'p', 'div', 'ul', 'ol', 'dl', 'blockquote'}


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._skip = 0
        self._buf  = []

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self._skip += 1
        elif tag in HEADINGS:
            self._buf.append('\n' + HEADINGS[tag] + ' ')
        elif tag == 'li':
            self._buf.append('\n- ')
        elif tag == 'dt':
            self._buf.append('\n')
        elif tag == 'dd':
            self._buf.append('\n  ')
        elif tag == 'br':
            self._buf.append('\n')
        elif tag in BLOCK_TAGS:
            self._buf.append('\n')

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            self._skip = max(0, self._skip - 1)
        elif tag in HEADINGS or tag in ('li', 'dt', 'dd', 'p'):
            self._buf.append('\n')

    def handle_data(self, data):
        if self._skip == 0:
            self._buf.append(data)

    def result(self):
        text  = ''.join(self._buf)
        lines = [re.sub(r'[ \t]+', ' ', ln).strip() for ln in text.splitlines()]
        text  = '\n'.join(lines)
        text  = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()


src = BASE / 'contents' / 'about.html'
out = BASE / 'about.md'

ex = TextExtractor()
ex.feed(src.read_text(encoding='utf-8'))

out.write_text(ex.result() + '\n', encoding='utf-8')
print(f'Exported: {out} ({out.stat().st_size:,} bytes)')
