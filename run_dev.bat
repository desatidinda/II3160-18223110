@echo off
IF NOT EXIST .venv ( 
    echo Creating virtual environment...
    python -m venv .venv
)
echo Activating virtual environment...
call .venv\Scripts\activate.bat
echo Installing requirements...
pip install -r requirements.txt
echo Starting server on http://127.0.0.1:8000
python -m uvicorn src.main:app --reload --port 8000
