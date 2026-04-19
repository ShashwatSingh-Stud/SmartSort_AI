@echo off
echo Starting Smart Waste Sorter App...

:: Check if venv exists, if not, wait and let user know
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please wait...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo Starting Flask server...
python app.py
pause
