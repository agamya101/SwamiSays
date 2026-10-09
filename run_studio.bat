@echo off
title SwamiSays Studio
echo ==================================================
echo   SwamiSays - Timeless Wisdom for Gen Z ^& Alpha
echo ==================================================
echo.
echo Starting server on port 8000 (accessible on Phone ^& Laptop)...
set PYTHONPATH=%~dp0backend
python -m uvicorn server:app --app-dir "%~dp0backend" --host 0.0.0.0 --port 8000
pause
