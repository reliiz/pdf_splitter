# pdf_splitter

指定したページで PDF を分割するツールです。CLI と GUI の両方を用意しています。

※ `python` コマンドが無い環境では、以下の例のとおり `python3` を使用してください。

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

---

## GUIアプリ（おすすめ）

起動:

```bash
python3 pdf_splitter_gui.py
```

### GUI機能

1. PDF を読み込み（ファイル選択）
2. ページプレビューを表示（テキストプレビュー）
3. 表示中ページを分割点に追加し、重複あり/なしを選択して分割

> macOS などで `tkinterdnd2` のネイティブ依存が合わない場合、
> ドラッグ&ドロップ機能のみ自動で無効化されます（アプリは落ちずに起動します）。
> その場合は「ファイル選択」ボタンを使用してください。

ドラッグ&ドロップを有効にしたい場合（任意）:

```bash
python3 -m pip install tkinterdnd2
```

### GUIの使い方

1. PDF を読み込む（D&D もしくは「ファイル選択」）。
2. 「前ページ / 次ページ」でプレビューし、分割したいページで「このページを分割点に追加」。
3. 必要なら「境界ページを重複させる」をON。
4. 「分割を実行」を押す。

`--split-at 3,5` の概念でいうと:
- 重複なし: `1-3`, `4-5`, `6-最終`
- 重複あり: `1-3`, `3-5`, `5-最終`

---

## CLI版

```bash
python3 pdf_splitter.py sample.pdf --split-at 3,5,10 --output-dir out
```

### 境界ページを重複させる場合

```bash
python3 pdf_splitter.py sample.pdf --split-at 3,5,10 --overlap-boundary
```

## CLI引数

- `input_pdf`（必須）: 分割対象の PDF ファイル
- `--split-at`（必須）: 分割位置（例: `3,5,10`）
- `--output-dir`（任意）: 出力先ディレクトリ（デフォルト: カレントディレクトリ）
- `--overlap-boundary`（任意）: 分割境界ページを重複して含める
