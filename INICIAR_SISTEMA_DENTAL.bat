@echo off
title Clinica Dental Coba MTY - Servidor Unificado & WAF
cd /d "%~dp0"
echo =====================================================================
echo    CLINICA DENTAL COBA MONTERREY ^& GUADALUPE - MVP FULL-STACK
echo    Escudo WAF Militar + Telemetria + WhatsApp Cloud Bot + SQLite ACID
echo =====================================================================
echo.
echo Iniciando servidor en http://localhost:8090 ...
start "" "http://localhost:8090"
python server.py
pause
