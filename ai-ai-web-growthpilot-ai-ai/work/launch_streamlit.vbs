Set shell = CreateObject("WScript.Shell")
shell.CurrentDirectory = "C:\Users\A\Documents\Codex\2026-07-19\ai-ai-web-growthpilot-ai-ai"
shell.Run """C:\Users\A\Documents\Codex\2026-07-19\ai-ai-web-growthpilot-ai-ai\.venv\Scripts\python.exe"" -m streamlit run """C:\Users\A\Documents\Codex\2026-07-19\ai-ai-web-growthpilot-ai-ai\app.py"" --server.port=8502 --server.address=127.0.0.1 --server.headless=true", 0, False
