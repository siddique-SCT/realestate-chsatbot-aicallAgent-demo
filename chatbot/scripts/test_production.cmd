@echo off
echo Testing the application with gunicorn (production server)...

REM Check if gunicorn is installed
pip show gunicorn > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing gunicorn...
    pip install gunicorn
)

REM Run the application with gunicorn
echo Starting the application with gunicorn...
cd ..
gunicorn --chdir flask_app app:create_app() --bind 0.0.0.0:8000

pause