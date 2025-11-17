$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvActivate = Join-Path $scriptDir '.venv\Scripts\Activate.ps1'
$launcher = Join-Path $scriptDir 'launch_merge_subtitles.py'

if (-not (Test-Path $venvActivate)) {
    Write-Error "Virtual environment not found at $venvActivate. Create it with 'python -m venv .venv'"
}

. $venvActivate

& python $launcher
$exitCode = $LASTEXITCODE

Write-Host ""
Read-Host "Press Enter to close this window"

exit $exitCode
