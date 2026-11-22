@echo off
TITLE Secure IoT Data Backup System - Vasani Jeel (24UG00241)
COLOR 0B

echo =====================================================================
echo  SECURE IOT DATA BACKUP SYSTEM - CLOUD COMPUTING ASSIGNMENT 18
echo  Student: Vasani Jeel ^| Reg No: 24UG00241
echo =====================================================================
echo.
echo Starting Flask Application Server & IoT Ingestion Gateway...
echo Dashboard will be available at: http://127.0.0.1:5000
echo.

start "" "http://127.0.0.1:5000"
python app.py

pause
