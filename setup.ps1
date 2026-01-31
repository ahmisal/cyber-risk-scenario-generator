# Setup script for Cyber Risk Scenario Generator
$projectRoot = "G:\My Drive\DPhil\Atomcamp Bootcamps\Agentic AI Bootcamp\Drafts\final"
cd $projectRoot

Write-Host "Creating backend venv..." -ForegroundColor Green
py -3.11 -m venv venv-backend
.\venv-backend\Scripts\Activate.ps1
pip install --upgrade pip --quiet
pip install -r requirements-backend.txt
deactivate

Write-Host "Creating frontend venv..." -ForegroundColor Green
py -3.11 -m venv venv-frontend
.\venv-frontend\Scripts\Activate.ps1
pip install --upgrade pip --quiet
pip install -r requirements-frontend.txt
deactivate

Write-Host "`nSetup complete! Use these commands to start:" -ForegroundColor Yellow
Write-Host "Backend:  .\venv-backend\Scripts\Activate.ps1 ; uvicorn app.main:app --reload --port 8000" -ForegroundColor Cyan
Write-Host "Frontend: .\venv-frontend\Scripts\Activate.ps1 ; python ui\gradio_app.py" -ForegroundColor Cyan