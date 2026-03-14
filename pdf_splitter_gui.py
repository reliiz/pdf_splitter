#!/usr/bin/env python3
"""GUI app for splitting PDFs with drag & drop and page preview."""

from __future__ import annotations

import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from pdf_splitter import split_pdf


def parse_drop_files(raw: str) -> list[Path]:
    """Parse tkdnd raw drop string into Path objects."""
    files: list[Path] = []
    for token in re.findall(r"\{[^}]+\}|[^\s]+", raw):
        cleaned = token[1:-1] if token.startswith("{") and token.endswith("}") else token
        if cleaned:
            files.append(Path(cleaned))
    return files


class PdfSplitterGui:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PDF Splitter GUI")
        self.root.geometry("900x680")

        self.pdf_path: Path | None = None
        self.total_pages = 0
        self.current_page = 1
        self.split_points: set[int] = set()
        self.preview_photo = None
        self.pdf_doc = None

        self.output_dir = tk.StringVar(value=str(Path.cwd()))
        self.overlap_boundary = tk.BooleanVar(value=False)

        self._build_ui()

    def _build_ui(self) -> None:
        top = ttk.Frame(self.root, padding=12)
        top.pack(fill="both", expand=True)

        drop_frame = ttk.LabelFrame(top, text="1) PDFを読み込む", padding=10)
        drop_frame.pack(fill="x")

        self.drop_label = ttk.Label(
            drop_frame,
            text="ここにPDFをドラッグ&ドロップ（またはボタンで選択）",
            anchor="center",
            relief="solid",
            padding=16,
        )
        self.drop_label.pack(fill="x", pady=4)

        self.file_label = ttk.Label(drop_frame, text="未選択")
        self.file_label.pack(anchor="w", pady=(6, 0))

        button_row = ttk.Frame(drop_frame)
        button_row.pack(fill="x", pady=(8, 0))
        ttk.Button(button_row, text="ファイル選択", command=self.choose_pdf).pack(side="left")
        ttk.Button(button_row, text="リセット", command=self.reset_selection).pack(side="left", padx=8)

        self._bind_drop_events()

        preview_frame = ttk.LabelFrame(top, text="2) プレビュー / 分割点選択", padding=10)
        preview_frame.pack(fill="both", expand=True, pady=12)

        nav_row = ttk.Frame(preview_frame)
        nav_row.pack(fill="x")
        ttk.Button(nav_row, text="◀ 前ページ", command=self.prev_page).pack(side="left")
        ttk.Button(nav_row, text="次ページ ▶", command=self.next_page).pack(side="left", padx=8)

        self.page_info = ttk.Label(nav_row, text="ページ: -")
        self.page_info.pack(side="left", padx=12)

        self.preview_canvas = tk.Canvas(preview_frame, bg="#f3f3f3", height=340)
        self.preview_canvas.pack(fill="both", expand=True, pady=8)

        split_row = ttk.Frame(preview_frame)
        split_row.pack(fill="x")
        ttk.Button(split_row, text="このページを分割点に追加", command=self.add_current_split).pack(side="left")
        ttk.Button(split_row, text="選択した分割点を削除", command=self.remove_selected_split).pack(
            side="left", padx=8
        )

        self.split_list = tk.Listbox(preview_frame, height=5, exportselection=False)
        self.split_list.pack(fill="x", pady=(8, 0))

        options = ttk.LabelFrame(top, text="3) 分割オプション", padding=10)
        options.pack(fill="x")

        ttk.Checkbutton(
            options,
            text="境界ページを重複させる（例: 1-3 / 3-5 / 5-...）",
            variable=self.overlap_boundary,
        ).pack(anchor="w")

        out_row = ttk.Frame(options)
        out_row.pack(fill="x", pady=(8, 0))
        ttk.Label(out_row, text="出力先:").pack(side="left")
        ttk.Entry(out_row, textvariable=self.output_dir).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(out_row, text="選択", command=self.choose_output_dir).pack(side="left")

        ttk.Button(top, text="分割を実行", command=self.run_split).pack(fill="x", pady=(12, 0))

    def _bind_drop_events(self) -> None:
        try:
            from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore
        except ModuleNotFoundError:
            self.drop_label.configure(text="ドラッグ&ドロップを使うには tkinterdnd2 が必要です。下のボタンで選択できます。")
            return

        if not isinstance(self.root, TkinterDnD.Tk):
            return

        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind("<<Drop>>", self.on_drop)

    def choose_pdf(self) -> None:
        selected = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if selected:
            self.load_pdf(Path(selected))

    def reset_selection(self) -> None:
        self.pdf_path = None
        self.total_pages = 0
        self.current_page = 1
        self.split_points.clear()
        self.file_label.configure(text="未選択")
        self.split_list.delete(0, tk.END)
        self.page_info.configure(text="ページ: -")
        self.preview_canvas.delete("all")
        self._close_doc()

    def on_drop(self, event) -> None:  # type: ignore[no-untyped-def]
        files = parse_drop_files(event.data)
        if not files:
            return
        pdf_candidates = [f for f in files if f.suffix.lower() == ".pdf"]
        if not pdf_candidates:
            messagebox.showerror("エラー", "PDFファイルをドロップしてください。")
            return
        self.load_pdf(pdf_candidates[0])

    def load_pdf(self, path: Path) -> None:
        if not path.exists():
            messagebox.showerror("エラー", f"ファイルが見つかりません: {path}")
            return

        self._close_doc()
        try:
            from pypdf import PdfReader
            import pypdfium2 as pdfium
        except ModuleNotFoundError as exc:
            messagebox.showerror(
                "依存不足",
                "必要な依存関係が不足しています。\n"
                "python3 -m pip install -r requirements.txt\n"
                f"({exc})",
            )
            return

        try:
            reader = PdfReader(str(path))
            self.total_pages = len(reader.pages)
            self.pdf_doc = pdfium.PdfDocument(str(path))
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("エラー", f"PDFの読み込みに失敗しました:\n{exc}")
            return

        if self.total_pages < 2:
            messagebox.showerror("エラー", "2ページ以上のPDFを指定してください。")
            self._close_doc()
            return

        self.pdf_path = path
        self.current_page = 1
        self.split_points.clear()
        self.file_label.configure(text=f"読み込み: {path}")
        self.refresh_split_list()
        self.show_page(1)

    def _close_doc(self) -> None:
        self.pdf_doc = None

    def show_page(self, page_number: int) -> None:
        if not self.pdf_doc or self.total_pages == 0:
            return
        page_number = max(1, min(self.total_pages, page_number))
        self.current_page = page_number

        try:
            from PIL import Image, ImageTk

            page = self.pdf_doc.get_page(page_number - 1)
            pil_image = page.render(scale=0.8).to_pil()
            page.close()
            max_w, max_h = 820, 330
            pil_image.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
            self.preview_photo = ImageTk.PhotoImage(pil_image)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("エラー", f"プレビュー生成に失敗しました:\n{exc}")
            return

        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(410, 170, image=self.preview_photo)
        self.page_info.configure(text=f"ページ: {self.current_page} / {self.total_pages}")

    def prev_page(self) -> None:
        self.show_page(self.current_page - 1)

    def next_page(self) -> None:
        self.show_page(self.current_page + 1)

    def add_current_split(self) -> None:
        if not self.pdf_path:
            return
        page = self.current_page
        if page >= self.total_pages:
            messagebox.showwarning("注意", "最終ページは分割点にできません。")
            return
        self.split_points.add(page)
        self.refresh_split_list()

    def remove_selected_split(self) -> None:
        selected = self.split_list.curselection()
        if not selected:
            return
        value = self.split_list.get(selected[0])
        page = int(value.split()[0])
        self.split_points.discard(page)
        self.refresh_split_list()

    def refresh_split_list(self) -> None:
        self.split_list.delete(0, tk.END)
        for page in sorted(self.split_points):
            self.split_list.insert(tk.END, f"{page} ページ")

    def choose_output_dir(self) -> None:
        selected = filedialog.askdirectory()
        if selected:
            self.output_dir.set(selected)

    def run_split(self) -> None:
        if not self.pdf_path:
            messagebox.showerror("エラー", "先にPDFを読み込んでください。")
            return

        split_points = sorted(self.split_points)
        if not split_points:
            messagebox.showerror("エラー", "分割点を1つ以上選択してください。")
            return

        output_dir = Path(self.output_dir.get()).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            outputs = split_pdf(self.pdf_path, split_points, output_dir, self.overlap_boundary.get())
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("エラー", f"分割に失敗しました:\n{exc}")
            return

        created = "\n".join(str(p) for p in outputs)
        messagebox.showinfo("完了", f"分割が完了しました。\n\n{created}")


def main() -> None:
    try:
        from tkinterdnd2 import TkinterDnD  # type: ignore

        root = TkinterDnD.Tk()
    except ModuleNotFoundError:
        root = tk.Tk()
    app = PdfSplitterGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
