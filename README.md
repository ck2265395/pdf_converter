# 轻松转 PDF

一个免费、离线的 Windows 桌面转换工具。文件不会上传到任何服务器。

## 当前支持

- TXT → PDF：内置转换，支持 UTF-8、UTF-16、GBK/GB18030 和中文自动换行分页。
- DOC/DOCX → PDF：自动使用 LibreOffice（推荐、免费）或本机 Microsoft Word。
- 多文件批量转换、输出目录选择、重名文件保护、单文件失败后继续。

## 运行

需要 Python 3.11 或更高版本。在 Windows 上双击 `run.bat`，首次运行会自动安装 ReportLab。

也可以在终端运行：

```powershell
python -m pip install -r requirements.txt
python app.py
```

若要转换 Word 文件，推荐安装免费的 [LibreOffice](https://www.libreoffice.org/download/download-libreoffice/)。也可使用已安装的 Microsoft Word。TXT 转换不依赖办公软件。

## 测试

```powershell
python -m pytest -q
```

## 打包为 EXE

```powershell
python -m pip install pyinstaller
pyinstaller --noconfirm --windowed --name "轻松转PDF" --collect-all reportlab app.py
```

生成文件位于 `dist/轻松转PDF/`。LibreOffice 或 Microsoft Word 仍需用户本机安装，才能转换 DOC/DOCX。

