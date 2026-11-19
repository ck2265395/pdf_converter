from __future__ import annotations

from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from converter.models import ConversionResult
from converter.service import convert_files

SUPPORTED_EXTENSIONS = {".txt", ".doc", ".docx"}


def filter_supported_files(files: list[Path]) -> list[Path]:
    result: list[Path] = []
    seen: set[str] = set()
    for file in files:
        key = str(file).casefold()
        if file.suffix.lower() in SUPPORTED_EXTENSIONS and key not in seen:
            seen.add(key)
            result.append(file)
    return result


def format_result_line(result: ConversionResult) -> str:
    if result.success and result.destination:
        return f"✓ {result.source.name}  →  {result.destination.name}"
    return f"✗ {result.source.name}  —  {result.message}"


class PdfConverterApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("轻松转 PDF")
        self.geometry("820x610")
        self.minsize(700, 520)
        self.configure(bg="#f5f7fb")
        self.files: list[Path] = []
        self.output_dir = tk.StringVar(value="与源文件相同")
        self.status = tk.StringVar(value="请选择要转换的文件")
        self.events: queue.Queue[tuple] = queue.Queue()
        self._configure_style()
        self._build_ui()
        self.after(100, self._poll_events)

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("vista" if "vista" in style.theme_names() else "clam")
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 22, "bold"), background="#f5f7fb", foreground="#172033")
        style.configure("Sub.TLabel", font=("Microsoft YaHei UI", 10), background="#f5f7fb", foreground="#667085")
        style.configure("Accent.TButton", font=("Microsoft YaHei UI", 11, "bold"), padding=(20, 10))
        style.configure("TButton", font=("Microsoft YaHei UI", 10), padding=(12, 7))

    def _build_ui(self) -> None:
        header = tk.Frame(self, bg="#f5f7fb")
        header.pack(fill="x", padx=34, pady=(28, 18))
        ttk.Label(header, text="轻松转 PDF", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="文件只在本机处理 · 支持 TXT、DOC、DOCX · 完全离线", style="Sub.TLabel").pack(anchor="w", pady=(6, 0))

        toolbar = tk.Frame(self, bg="#f5f7fb")
        toolbar.pack(fill="x", padx=34, pady=(0, 12))
        ttk.Button(toolbar, text="＋ 添加文件", command=self._add_files).pack(side="left")
        ttk.Button(toolbar, text="移除选中", command=self._remove_selected).pack(side="left", padx=8)
        ttk.Button(toolbar, text="清空", command=self._clear).pack(side="left")

        list_frame = tk.Frame(self, bg="white", highlightthickness=1, highlightbackground="#dfe3eb")
        list_frame.pack(fill="both", expand=True, padx=34)
        self.file_list = tk.Listbox(
            list_frame, selectmode=tk.EXTENDED, borderwidth=0, highlightthickness=0,
            font=("Microsoft YaHei UI", 10), activestyle="none", bg="white", fg="#273142",
            selectbackground="#dbeafe", selectforeground="#1d4ed8",
        )
        scrollbar = ttk.Scrollbar(list_frame, command=self.file_list.yview)
        self.file_list.configure(yscrollcommand=scrollbar.set)
        self.file_list.pack(side="left", fill="both", expand=True, padx=14, pady=12)
        scrollbar.pack(side="right", fill="y")

        output = tk.Frame(self, bg="#f5f7fb")
        output.pack(fill="x", padx=34, pady=15)
        tk.Label(output, text="输出位置：", bg="#f5f7fb", fg="#344054", font=("Microsoft YaHei UI", 10, "bold")).pack(side="left")
        tk.Label(output, textvariable=self.output_dir, bg="#f5f7fb", fg="#667085", font=("Microsoft YaHei UI", 10), anchor="w").pack(side="left", fill="x", expand=True)
        ttk.Button(output, text="选择目录", command=self._choose_output).pack(side="right")

        bottom = tk.Frame(self, bg="#f5f7fb")
        bottom.pack(fill="x", padx=34, pady=(0, 26))
        self.progress = ttk.Progressbar(bottom, mode="determinate")
        self.progress.pack(fill="x", pady=(0, 8))
        tk.Label(bottom, textvariable=self.status, bg="#f5f7fb", fg="#667085", font=("Microsoft YaHei UI", 9)).pack(side="left")
        self.convert_button = ttk.Button(bottom, text="开始转换", style="Accent.TButton", command=self._start_conversion)
        self.convert_button.pack(side="right")

    def _add_files(self) -> None:
        selected = filedialog.askopenfilenames(title="选择文件", filetypes=[("支持的文件", "*.txt *.doc *.docx"), ("所有文件", "*.*")])
        combined = filter_supported_files(self.files + [Path(item) for item in selected])
        self.files = combined
        self._refresh_list()

    def _remove_selected(self) -> None:
        selected = set(self.file_list.curselection())
        self.files = [item for index, item in enumerate(self.files) if index not in selected]
        self._refresh_list()

    def _clear(self) -> None:
        self.files.clear()
        self._refresh_list()

    def _refresh_list(self) -> None:
        self.file_list.delete(0, tk.END)
        for item in self.files:
            self.file_list.insert(tk.END, f"  {item.name}    —    {item.parent}")
        self.status.set(f"已选择 {len(self.files)} 个文件" if self.files else "请选择要转换的文件")

    def _choose_output(self) -> None:
        selected = filedialog.askdirectory(title="选择 PDF 输出目录")
        if selected:
            self.output_dir.set(selected)

    def _start_conversion(self) -> None:
        if not self.files:
            messagebox.showinfo("提示", "请先添加 TXT、DOC 或 DOCX 文件。")
            return
        self.convert_button.configure(state="disabled")
        self.progress.configure(maximum=len(self.files), value=0)
        output = None if self.output_dir.get() == "与源文件相同" else Path(self.output_dir.get())
        threading.Thread(target=self._convert_worker, args=(self.files.copy(), output), daemon=True).start()

    def _convert_worker(self, files: list[Path], output: Path | None) -> None:
        def on_progress(current: int, total: int, result: ConversionResult) -> None:
            self.events.put(("progress", current, total, result))
        try:
            results = convert_files(files, output, on_progress)
            self.events.put(("done", results))
        except Exception as exc:
            self.events.put(("fatal", str(exc)))

    def _poll_events(self) -> None:
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == "progress":
                    _, current, total, result = event
                    self.progress.configure(value=current)
                    mark = "成功" if result.success else "失败"
                    self.status.set(f"{current}/{total}  {result.source.name}：{mark}")
                    self.file_list.delete(current - 1)
                    self.file_list.insert(current - 1, format_result_line(result))
                elif event[0] == "done":
                    results = event[1]
                    self.convert_button.configure(state="normal")
                    succeeded = sum(item.success for item in results)
                    failed = len(results) - succeeded
                    failures = "\n".join(f"• {item.source.name}：{item.message}" for item in results if not item.success)
                    text = f"转换完成：成功 {succeeded} 个，失败 {failed} 个。"
                    if failures:
                        text += f"\n\n{failures}"
                    messagebox.showinfo("转换结果", text)
                elif event[0] == "fatal":
                    self.convert_button.configure(state="normal")
                    self.status.set("转换意外中断")
                    messagebox.showerror("转换失败", event[1])
        except queue.Empty:
            pass
        self.after(100, self._poll_events)


if __name__ == "__main__":
    PdfConverterApp().mainloop()

