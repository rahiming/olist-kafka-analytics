$ErrorActionPreference = "Stop"

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Action
    )

    Write-Host ""
    Write-Host "==> $Name" -ForegroundColor Cyan
    & $Action

    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Name"
    }
}

function Invoke-AdvisoryStep {
    param(
        [string]$Name,
        [scriptblock]$Action
    )

    Write-Host ""
    Write-Host "==> $Name" -ForegroundColor DarkYellow
    & $Action

    if ($LASTEXITCODE -ne 0) {
        Write-Warning "$Name reported differences. This check is advisory only because the project uses Ruff as the source-of-truth formatter."
        $global:LASTEXITCODE = 0
    }
}

function Assert-Command {
    param([string]$CommandName)

    if (-not (Get-Command $CommandName -ErrorAction SilentlyContinue)) {
        throw "Required command '$CommandName' was not found. Run: pip install -e `".[dev]`""
    }
}

Assert-Command "ruff"
Assert-Command "black"
Assert-Command "bandit"
Assert-Command "pytest"

$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Invoke-Step "Ruff lint" {
    ruff check .
}

Invoke-Step "Ruff format check" {
    ruff format --check .
}

Invoke-AdvisoryStep "Black format compatibility check" {
    black --check --quiet producer processor dashboard tests
}

Invoke-Step "Bandit security scan" {
    bandit -c pyproject.toml -r producer processor dashboard
}

Invoke-Step "Pytest unit tests" {
    python -m pytest tests -q
}

Write-Host ""
Write-Host "All pre-push checks passed." -ForegroundColor Green
