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

要件に合わせて、以下の機能を実装しています。

1. PDF をドラッグ&ドロップで読み込み（ボタン選択も可）
2. ページプレビューを表示
3. プレビュー中のページを分割点として追加し、重複あり/なしを選択して分割

起動:

```bash
python3 pdf_splitter_gui.py
```

### GUIの使い方

1. 画面上部に PDF をドラッグ&ドロップ（または「ファイル選択」）。
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
