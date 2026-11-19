# Local PDF Converter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个离线 Windows 桌面工具，将 TXT、DOC、DOCX 批量转换为 PDF。

**Architecture:** `converter` 包负责格式识别、输出命名和具体转换后端，`app.py` 只负责 Tkinter 交互。TXT 使用 ReportLab；Word 使用可发现的 LibreOffice 或 Microsoft Word。

**Tech Stack:** Python 3.11+、Tkinter、ReportLab、pytest

**Spec:** `docs/superpowers/specs/2026-11-19-local-pdf-converter-design.md`

## Global Constraints

- 仅本地转换，不上传文件。
- 支持 `.txt`、`.doc`、`.docx`。
- 已存在输出文件时不得覆盖。
- 单文件失败不得终止整个批次。

## Review Focus

- 中文 TXT 的字体与编码探测。
- 超长行换行和多页输出。
- 重名 PDF 的安全命名。
- Office/LibreOffice 缺失时的可理解错误。
- 批处理中部分文件失败时继续执行。

---

### Task 1: 核心文件模型与安全输出命名

**Files:**
- Create: `converter/models.py`
- Create: `converter/paths.py`
- Test: `tests/test_paths.py`

**Interfaces:**
- Produces: `unique_pdf_path(source: Path, output_dir: Path | None) -> Path`

- [ ] 先写重名与默认目录测试并确认失败。
- [ ] 实现最小安全命名逻辑并确认测试通过。

### Task 2: TXT 转 PDF

**Files:**
- Create: `converter/text_pdf.py`
- Test: `tests/test_text_pdf.py`

**Interfaces:**
- Produces: `convert_text(source: Path, destination: Path) -> None`

- [ ] 先写 UTF-8/GBK、中文、换行和 PDF 有效性测试并确认失败。
- [ ] 实现编码探测、字体选择、换行与分页并确认测试通过。

### Task 3: Word 转 PDF 后端

**Files:**
- Create: `converter/word_pdf.py`
- Test: `tests/test_word_pdf.py`

**Interfaces:**
- Produces: `find_word_backend() -> WordBackend | None`、`convert_word(source, destination, backend) -> None`

- [ ] 先写后端发现、命令构造和缺失错误测试并确认失败。
- [ ] 实现 LibreOffice/Word 后端并确认测试通过。

### Task 4: 批处理服务

**Files:**
- Create: `converter/service.py`
- Test: `tests/test_service.py`

**Interfaces:**
- Produces: `convert_files(sources, output_dir, progress) -> list[ConversionResult]`

- [ ] 先写格式分派、继续失败任务和结果汇总测试并确认失败。
- [ ] 实现服务并确认测试通过。

### Task 5: Windows 桌面界面与交付说明

**Files:**
- Create: `app.py`
- Create: `requirements.txt`
- Create: `README.md`
- Create: `run.bat`
- Test: `tests/test_app_helpers.py`

**Interfaces:**
- Consumes: `convert_files(...)`

- [ ] 先写界面辅助逻辑测试并确认失败。
- [ ] 实现文件选择、输出目录、后台转换、进度和结果列表。
- [ ] 运行完整测试、启动冒烟测试并记录打包方式。

