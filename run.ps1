# Auto-setup and run script for photo_and_video_tools
$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$launcherScript = Join-Path $scriptDir "launcher.py"

try {
    # Sync dependencies (creates/updates the uv-managed virtual environment)
    Write-Host "Syncing dependencies..." -ForegroundColor Cyan
    uv sync --quiet

    # Run the launcher
    Write-Host "Running launcher..." -ForegroundColor Cyan
    uv run python $launcherScript
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
