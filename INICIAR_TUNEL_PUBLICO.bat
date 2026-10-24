@echo off
title Tunel Cloudflare - Clinica Dental Coba MTY
cd /d "%~dp0"
echo =====================================================================
echo    CLOUDFLARE TUNNEL - ACCESO PUBLICO GLOBAL Y WEBHOOK WHATSAPP
echo =====================================================================
echo.
python run_tunnel.py
pause
