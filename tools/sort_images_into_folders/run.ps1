# Auto-setup and run script for sort_images_into_folders
$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPath = Join-Path $scriptDir ".venv"
$pythonScript = Join-Path $scriptDir "sort_images_into_folders.py"
$requirementsFile = Join-Path $scriptDir "requirements.txt"

try {
    # Check if venv exists, create if not
    if (-not (Test-Path $venvPath)) {
        Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
        python -m venv $venvPath
        Write-Host "Virtual environment created." -ForegroundColor Green
    }

    # Activate virtual environment
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & $activateScript

    # Install/update dependencies
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    pip install --quiet -r $requirementsFile

    # Run the Python script
    Write-Host "Running sort_images_into_folders..." -ForegroundColor Cyan
    python $pythonScript
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
finally {
    # Deactivate virtual environment
    if (Get-Command deactivate -ErrorAction SilentlyContinue) {
        Write-Host "Deactivating virtual environment..." -ForegroundColor Cyan
        deactivate
    }
}
