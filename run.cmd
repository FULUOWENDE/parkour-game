@echo off
setlocal

cd /d "%~dp0"
set "UV_CACHE_DIR=%CD%\.uv-cache"
set "UV_PYTHON_INSTALL_DIR=%CD%\.uv-python"

uv --cache-dir "%UV_CACHE_DIR%" --system-certs run --no-project --default-index "https://pypi.org/simple" --python 3.12 --with "pygame-ce>=2.5.0" python -m src.main
