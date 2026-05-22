$ErrorActionPreference = "Stop"

git config core.hooksPath .githooks

Write-Host "Git hooks path set to .githooks" -ForegroundColor Green
Write-Host "The pre-push hook is now active for this repository." -ForegroundColor Green
