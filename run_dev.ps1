$venv = Join-Path $PWD '.venv'
if (-not (Test-Path $venv)) {
    python -m venv .venv
}

Write-Output "Activating venv..."
. .\.venv\Scripts\Activate.ps1

Write-Output "Installing requirements..."
pip install -r requirements.txt

Write-Output "Starting uvicorn (app-dir: src)..."
python -m uvicorn main:app --reload --port 8000 --app-dir src
