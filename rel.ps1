#Requires -Version 7.0

<#
Run the release validation sequence.

The script echoes each exact command before running it.
#>

Clear-Host

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
# $PSNativeCommandUseErrorActionPreference = $true


function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Section,

        [Parameter(Mandatory = $true)]
        [string]$Command,

        [Parameter(Mandatory = $true)]
        [scriptblock]$Script
    )

    Write-Host ""
    Write-Host "============================================================"
    Write-Host $Section
    Write-Host "============================================================"
    Write-Host $Command
    & $Script
}


# ============================================================
# A) Toolchain refresh
# ============================================================

Invoke-Step "A0) Update lock file" "uv lock --upgrade" {
    uv lock --upgrade
}

Invoke-Step "A1) Sync Python tooling" "uv sync --extra dev --extra docs --upgrade" {
    uv sync --extra dev --extra docs --upgrade
}

Invoke-Step "A2) Install pre-commit hooks" "uvx pre-commit install" {
    uvx pre-commit install
}


# ============================================================
# B) Package command surface
# ============================================================

Invoke-Step "B1) Run dc-up dry-run command" "uv run dc-up" {
    uv run dc-up
}

Invoke-Step "B2) Run dc-up todo command" "uv run dc-up todo" {
    uv run dc-up todo
}

# Intentionally disabled for release validation because it modifies files.
# Invoke-Step "B3) Run dc-up write command" "uv run dc-up --write" {
#     uv run dc-up --write
# }


# ============================================================
# C) Pre-commit and Python tests
# ============================================================

Invoke-Step "C1) Stage all changes so pre-commit sees tracked/staged files" "git add -A" {
    git add -A
}

Invoke-Step "C2) Run pre-commit autofix pass" "uvx pre-commit run --all-files" {
    $oldNativePreference = $null
    $hadNativePreference = Test-Path Variable:\PSNativeCommandUseErrorActionPreference

    if ($hadNativePreference) {
        $oldNativePreference = $PSNativeCommandUseErrorActionPreference
        $PSNativeCommandUseErrorActionPreference = $false
    }

    uvx pre-commit run --all-files
    $exitCode = $LASTEXITCODE

    if ($hadNativePreference) {
        $PSNativeCommandUseErrorActionPreference = $oldNativePreference
    }

    if ($exitCode -ne 0) {
        Write-Host ""
        Write-Host "Pre-commit may have modified files. Staging changes and continuing to verification pass."
        git add -A
    }
}

Invoke-Step "C3) Run pre-commit verification pass" "uvx pre-commit run --all-files" {
    uvx pre-commit run --all-files
}

Invoke-Step "C4) Run Python tests" "uv run python -m pytest" {
    uv run python -m pytest
}

Invoke-Step "C5) Run Pyright" "uv run python -m pyright" {
    uv run python -m pyright
}

Invoke-Step "C6) Run final pre-commit check after tests/type checks" "uvx pre-commit run --all-files" {
    uvx pre-commit run --all-files
}


# ============================================================
# D) Documentation
# ============================================================

Invoke-Step "D1) Build documentation" "uv run python -m zensical build" {
    uv run python -m zensical build
}


# ============================================================
# E) Architectural and code-health checks
# ============================================================

Invoke-Step "E0) Check import layers" "uvx --python 3.14 --with-editable . --from import-linter lint-imports --config .github/.importlinter" {
    uvx --python 3.14 --with-editable . --from import-linter lint-imports --config .github/.importlinter
}

Invoke-Step "E1) Find dead code" "uvx --with-editable . vulture src/dc_up" {
    uvx --with-editable . vulture src/dc_up
}

Invoke-Step "E2) Check complexity; any output means C-or-worse complexity exists" "uvx radon cc src/dc_up -s -a -n C" {
    uvx radon cc src/dc_up -s -a -n C
}

Invoke-Step "E3) Report raw code metrics" "uvx radon raw src/dc_up -j | uv run python -c `"import json, sys; data=json.load(sys.stdin); keys=('loc','lloc','sloc','comments','multi','blank','single_comments'); totals={k:sum(file[k] for file in data.values()) for k in keys}; print('\n'.join(f'{k.upper()}: {v}' for k,v in totals.items()))`"" {
    uvx radon raw src/dc_up -j | uv run python -c "import json, sys; data=json.load(sys.stdin); keys=('loc','lloc','sloc','comments','multi','blank','single_comments'); totals={k:sum(file[k] for file in data.values()) for k in keys}; print('\n'.join(f'{k.upper()}: {v}' for k,v in totals.items()))"
}


# ============================================================
# F) Distribution artifacts and installed-package smoke tests
# ============================================================

Invoke-Step "F0) Clean distribution artifacts" "uv run python -c `"import shutil; from pathlib import Path; shutil.rmtree(Path('dist'), ignore_errors=True)`"" {
    uv run python -c "import shutil; from pathlib import Path; shutil.rmtree(Path('dist'), ignore_errors=True)"
}

Invoke-Step "F1) Build source and wheel distributions" "uv build" {
    uv build
}

Invoke-Step "F2) Check distribution metadata" "uvx twine check dist/*" {
    uvx twine check dist/*
}

Invoke-Step "F3) Confirm wheel was built" "Get-ChildItem dist -Filter *.whl" {
    $wheels = Get-ChildItem dist -Filter "*.whl" | Sort-Object LastWriteTime
    if (-not $wheels) {
        throw "No wheel found in dist/."
    }

    $wheel = $wheels[-1]
    Write-Host "Wheel: $($wheel.FullName)"
}

Invoke-Step "F4) Smoke test installed wheel command help" "uvx --from <built-wheel> dc-up --help" {
    $wheel = Get-ChildItem dist -Filter "*.whl" | Sort-Object LastWriteTime | Select-Object -Last 1
    if (-not $wheel) {
        throw "No wheel found in dist/."
    }

    uvx --from $wheel.FullName dc-up --help
}

Invoke-Step "F5) Smoke test installed wheel todo command" "uvx --from <built-wheel> dc-up todo --root ." {
    $wheel = Get-ChildItem dist -Filter "*.whl" | Sort-Object LastWriteTime | Select-Object -Last 1
    if (-not $wheel) {
        throw "No wheel found in dist/."
    }

    uvx --from $wheel.FullName dc-up todo --root .
}

Invoke-Step "F6) Smoke test installed wheel package metadata" "uvx --from <built-wheel> python -c `"from importlib.metadata import version; print(version('dc-up'))`"" {
    $wheel = Get-ChildItem dist -Filter "*.whl" | Sort-Object LastWriteTime | Select-Object -Last 1
    if (-not $wheel) {
        throw "No wheel found in dist/."
    }

    uvx --from $wheel.FullName python -c "from importlib.metadata import version; print(version('dc-up'))"
}
