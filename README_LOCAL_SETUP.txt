
IMPORTANT: PLEASE READ

Your current Google Drive workspace is too slow for Python development (libraries like Gradio/CrewAI read 10,000+ files on startup).

I have automatically created a LOCAL copy of your project here:
C:\Projects\Agentic_Capstone

It is already set up and ready to run 100x faster.

=== HOW TO SWITCH ===
1. Close this VS Code window.
2. Open VS Code again.
3. Click "File" > "Open Folder" and select: C:\Projects\Agentic_Capstone

=== HOW TO RUN (IN THE NEW LOCAL FOLDER) ===

Terminal 1 (Backend):
.\venv-backend\Scripts\uvicorn.exe app.main:app --port 8000

Terminal 2 (Frontend):
.\venv-frontend\Scripts\python.exe ui\gradio_app.py

You will see the app start instantly.
