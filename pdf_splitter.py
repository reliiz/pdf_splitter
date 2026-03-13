#!/usr/bin/env python3
"""Split a PDF file at user-specified page numbers.

Example:
    python pdf_splitter.py input.pdf --split-at 3,5,10

The command above creates the following files:
    input_part1.pdf  (pages 1-3)
    input_part2.pdf  (pages 4-5)
    input_part3.pdf  (pages 6-10)
    input_part4.pdf  (pages 11-end)
"""

from __future__ import annotations

import argparse
from pathlib import Path

def parse_split_points(raw: str, total_pages: int) -> list[int]:
    """Parse comma-separated split points and validate them.

    Split points are 1-indexed inclusive page numbers where each part ends.
    """
    if not raw.strip():
        raise ValueError("--split-at にページ番号を指定してください (例: 3,5,10)")

    values: list[int] = []
    for chunk in raw.split(","):
        item = chunk.strip()
        if not item:
            continue
        if not item.isdigit():
            raise ValueError(f"不正なページ番号です: {item}")
        page = int(item)
        if page <= 0:
            raise ValueError(f"ページ番号は1以上で指定してください: {page}")
        if page >= total_pages:
            raise ValueError(
                f"ページ番号 {page} はPDF総ページ数({total_pages})未満である必要があります"
            )
        values.append(page)

    if not values:
        raise ValueError("有効なページ番号が見つかりませんでした")

    unique_sorted = sorted(set(values))
    return unique_sorted


def build_ranges(total_pages: int, split_points: list[int], overlap: bool) -> list[tuple[int, int]]:
    """Build 0-indexed page ranges as (start_inclusive, end_exclusive)."""
    ranges: list[tuple[int, int]] = []
    start = 0

    for split_point in split_points:
        end = split_point
        ranges.append((start, end))
        start = split_point - 1 if overlap else split_point

    ranges.append((start, total_pages))
    return ranges


def split_pdf(
    input_path: Path, split_points: list[int], output_dir: Path, overlap: bool
) -> list[Path]:
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(str(input_path))
    total_pages = len(reader.pages)
    stem = input_path.stem
    ranges = build_ranges(total_pages, split_points, overlap)

    output_files: list[Path] = []
    for idx, (start, end) in enumerate(ranges, start=1):
        writer = PdfWriter()
        for page_idx in range(start, end):
            writer.add_page(reader.pages[page_idx])

        output_path = output_dir / f"{stem}_part{idx}.pdf"
        with output_path.open("wb") as f:
            writer.write(f)
        output_files.append(output_path)

    return output_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="指定したページ数でPDFを分割します（ページ番号は1始まり）。"
    )
    parser.add_argument("input_pdf", type=Path, help="分割対象のPDFファイル")
    parser.add_argument(
        "--split-at",
        required=True,
        help="分割位置(各チャンクの終端ページ)をカンマ区切りで指定。例: 3,5,10",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("."),
        help="出力先ディレクトリ（デフォルト: カレントディレクトリ）",
    )
    parser.add_argument(
        "--overlap-boundary",
        action="store_true",
        help=(
            "分割境界ページを前後のファイルで重複させる。"
            " 例: split-at 3,5 のとき 1-3 / 3-5 / 5-最終ページ"
        ),
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    input_path: Path = args.input_pdf
    output_dir: Path = args.output_dir

    if not input_path.exists():
        parser.error(f"入力ファイルが見つかりません: {input_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        from pypdf import PdfReader
    except ModuleNotFoundError:
        parser.error(
            "pypdf がインストールされていません。`pip install -r requirements.txt` を実行してください"
        )

    reader = PdfReader(str(input_path))
    total_pages = len(reader.pages)
    if total_pages < 2:
        parser.error("2ページ以上のPDFを指定してください")

    try:
        split_points = parse_split_points(args.split_at, total_pages)
    except ValueError as exc:
        parser.error(str(exc))

    created = split_pdf(input_path, split_points, output_dir, args.overlap_boundary)

    print("分割が完了しました:")
    for output in created:
        print(f"- {output}")


if __name__ == "__main__":
    main()
