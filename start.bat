@echo off
start "Cloudflare Tunnel" cmd /k "cd /d C:\invoice_assistant && .\cloudflared.exe tunnel --url http://localhost:8501"
start "Streamlit ERP" cmd /k "cd /d C:\invoice_assistant && .\venv\Scripts\python.exe -m streamlit run app.py"
