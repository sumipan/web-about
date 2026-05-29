# web-about

コルクラボ about ページの入稿ソース管理リポジトリ。

## ファイル構成

| ファイル | 用途 |
|---|---|
| `contents/about.css` | カスタム CSS（入稿用・全ページ共用） |
| `contents/about.html` | 「コルクラボはこんなところ」ページの入稿 HTML |
| `contents/go-ahead.html` | 「となりにどうぞ」ページの入稿 HTML |
| `contents/template.html` | CMS から取得したページの雛形 |
| `about.html` / `go-ahead.html` | ビルド成果物（ローカルプレビュー用） |
| `scripts/build.py` | template + CSS + 各 HTML を結合してプレビュー用 HTML を生成 |
| `scripts/export-text.py` | 各 contents/*.html からテキストを抽出して *.md に出力 |
| `about.md` / `go-ahead.md` | 各 HTML のテキスト抽出結果 |

ページを追加する場合は `scripts/build.py` と `scripts/export-text.py` の `PAGES` リストにスラッグを追加する。

## ローカルプレビュー

```sh
python3 scripts/build.py
python3 -m http.server 8765
# → http://localhost:8765/about.html
# → http://localhost:8765/go-ahead.html
```

## CMS 入稿

OSIRO の管理画面から以下を更新する。

1. **CSS**（全ページ共通） → `contents/about.css` の内容をそのままペースト
2. **HTML**（ページごと） → `contents/{page}.html` の内容をそのままペースト

---

## CMS が入稿 HTML に加える変換

入稿した HTML/CSS が CMS（OSIRO）によってどう変換されてレンダリングされるかの分析結果。
CSS 記述・HTML 構造設計時に考慮が必要。

### 1. CSS の注入先が変わる

**入稿時**: `<style id="block_page_css">` に CSS を書く  
**レンダリング後**: CMS が CSS 内容を別の無名 `<style>` 要素に移す。`id="block_page_css"` の要素は空のまま残る

```
入稿: <style id="block_page_css">/* our CSS */</style>
出力: <style>/* our CSS */</style>   ← 別要素に移動
      <style id="block_page_css"></style>  ← 空になる
```

影響: なし（CSS は正常に適用される）

---

### 2. `<dl>` 内の `<img>` がDL外に移動する（HTML5 パーサーの正規化）

`<dl>` の直下に `<img>` を置くと、HTML5 パーサーが不正な構造と判断して正規化する。

**入稿 HTML:**
```html
<dl class="join_us">
  <dt>事前登録</dt>
  <dd>...</dd>
  <img src="arrow.png" />       ← dl の子
  <dt>応募フォーム提出</dt>
  <dd>...</dd>
  <img src="arrow.png" />
</dl>
```

**レンダリング後:**
```html
<dl class="join_us"><dt>事前登録</dt><dd>...</dd></dl>
<img src="arrow.png">            ← dl の兄弟要素に昇格
<dl class="join_us"><dt>応募フォーム提出</dt><dd>...</dd></dl>
<img src="arrow.png">
```

**CSS セレクタ: `.box_area > dl.join_us + img`**（dl.join_us の直後の兄弟 img）

**ソース HTML の書き方**: `<img>` を最初から `<dl>` の外に書くことで、ローカル・CMS 両方で同じ DOM 構造になる。→ `contents/about.html` の「入会の流れ」セクションを参照。

---

### 3. `<dl>` が複数の `<dl>` に分割される

同じく HTML5 パーサーの正規化。1 つの `<dl>` に複数の `<dt>/<dd>` セットがあると、
`<dt>/<dd>` の間に来た `<img>` を起点に `<dl>` が分割される。

入稿時に 1 つだった `<dl class="join_us">` が、`<dt>/<dd>` のペア数だけの `<dl>` に分かれる。
**`class` 属性は各 `<dl>` に引き継がれる。**

---

### 4. CMS がブロック要素に自動でクラスを付与する

入稿 HTML を CMS のブロックエディタで保存すると、各ブロック要素に以下のクラスが付加される。

| クラス | 付与先 |
|---|---|
| `block_element` | 各コンテンツブロック |
| `top_center` / `bottom_center` | 各コンテンツブロック（配置設定） |

---

### 5. `heading_level_block` に空の div が挿入される

見出しブロック（`heading_level_block`）の直下に空の div が自動挿入される。

```html
<div class="heading_level_block block_element top_center h2-overlay">
  <div class="block_element-attachment_fixed top_center"></div>  ← CMS が追加
  <div>
    <h2>...</h2>
  </div>
</div>
```

この div は背景画像の固定表示に使われる。CSS で `> div:not(.block_element-attachment_fixed)` と書く理由はここにある。

---

### 6. `all_background_layer` div が先頭に挿入される

`.block_page_base` の最初の子要素として、ページ全体の背景画像コンテナが挿入される。

```html
<div class="block_page_base top_center">
  <div class="all_background_layer top_center"></div>  ← CMS が追加
  <!-- 以下 html_block, heading_level_block... -->
```

---

### 7. 入稿 HTML 内のカスタムクラスは保持される

`class` 属性に書いたカスタムクラスは CMS に保持される。

| クラス | 用途 |
|---|---|
| `h2-overlay` | h2 に白背景ボックスを適用 |
| `join_us` | 入会の流れの dl に設定（保持される） |
| `qa` | Q&A の dl に設定 |
| `li-normal` | リストの太字を解除 |
| `box_wrap` / `box_area` / `box_column1` / `box_column2` | ボックスレイアウト |

---

### 8. 相対 URL が絶対 URL に変換される

`fixed_footer_block` 内のリンクなど、相対 URL は CMS がサイトのベース URL を付加して絶対 URL に変換する。

```
入稿: <a href="/join_us">
出力: <a href="https://lab.corkagency.com/join_us">
```

---

### 9. 画像 URL は書き換えられない

`staging.image.osiro.it` の URL を入稿しても、CMS はそのままにする（プロダクション URL に変換しない）。CMS の UI からアップロードした画像は `image.osiro.it` の URL になる。

---

## 矢印画像サイズの問題（解決済み）

「入会の流れ」の矢印画像が CMS 上で全幅（829px）で表示される問題。

**原因**: 上記 #2・#3 の変換により `<img>` が `<dl>` 外の `.box_area` 直下に移動するため、
`dl img` や `.join_us img` セレクタが一切マッチしない。

**解決策**: CSS セレクタを `.box_area > dl.join_us + img` に変更。
