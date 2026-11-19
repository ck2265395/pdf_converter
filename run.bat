@echo off
cd /d "%~dp0"
python -c "import reportlab" >nul 2>nul
if errorlevel 1 (
  echo 首次运行，正在安装 PDF 组件...
  python -m pip install -r requirements.txt
)
python app.py
if errorlevel 1 pause

