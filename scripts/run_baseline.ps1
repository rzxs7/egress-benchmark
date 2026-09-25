$ErrorActionPreference = "Stop"
& .\.venv\Scripts\Activate.ps1

egress-bench --config config.yaml --output results
