# pdf_splitter

指定したページ番号で PDF を分割するシンプルな Python ツールです。

※ `python` コマンドが無い環境では、README の例のとおり `python3` を使用してください。

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## 使い方

```bash
python3 pdf_splitter.py sample.pdf --split-at 3,5,10 --output-dir out
```

- `--split-at` は **各分割ファイルの終端ページ番号（1始まり）** をカンマ区切りで指定します。
- 上記例では以下の 4 ファイルが出力されます。
  - `sample_part1.pdf` (1-3ページ)
  - `sample_part2.pdf` (4-5ページ)
  - `sample_part3.pdf` (6-10ページ)
  - `sample_part4.pdf` (11ページ以降)

### 境界ページを重複させる場合

```bash
python3 pdf_splitter.py sample.pdf --split-at 3,5,10 --overlap-boundary
```

- `--overlap-boundary` を付けると、境界ページを前後のファイルで重複して含めます。
- 例: `--split-at 3,5` の場合
  - 重複なし（デフォルト）: `1-3`, `4-5`, `6-最終`
  - 重複あり: `1-3`, `3-5`, `5-最終`

## 引数

- `input_pdf`（必須）: 分割対象の PDF ファイル
- `--split-at`（必須）: 分割位置（例: `3,5,10`）
- `--output-dir`（任意）: 出力先ディレクトリ（デフォルト: カレントディレクトリ）
- `--overlap-boundary`（任意）: 分割境界ページを重複して含める
