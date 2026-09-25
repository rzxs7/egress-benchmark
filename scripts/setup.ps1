$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    py -m venv .venv
}

& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

if (-not (Test-Path "config.yaml")) {
    Copy-Item config.example.yaml config.yaml
}

Write-Host "Setup complete."
Write-Host "Terminal A: python scripts\lab_server.py"
Write-Host "Terminal B: egress-bench --config config.yaml --output results"
