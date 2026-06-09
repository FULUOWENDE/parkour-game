$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$env:UV_CACHE_DIR = Join-Path $ProjectRoot ".uv-cache"
$env:UV_PYTHON_INSTALL_DIR = Join-Path $ProjectRoot ".uv-python"

uv --cache-dir "$env:UV_CACHE_DIR" --system-certs run --no-project --default-index "https://pypi.org/simple" --python 3.12 --with "pygame-ce>=2.5.0" python -m src.main
