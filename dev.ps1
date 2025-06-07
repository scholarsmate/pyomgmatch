# PowerShell development script for pyomgmatch
# Usage: .\dev.ps1 <command>

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "Available commands:"
    Write-Host "  install     - Install production dependencies"
    Write-Host "  install-dev - Install development dependencies"  
    Write-Host "  build       - Build native libraries and package"
    Write-Host "  test        - Run tests"
    Write-Host "  test-cov    - Run tests with coverage"
    Write-Host "  lint        - Run all linting checks"
    Write-Host "  format      - Format code with black and isort"
    Write-Host "  security    - Run security scans"
    Write-Host "  clean       - Clean build artifacts"
    Write-Host "  all         - Run format, lint, test, and build"
}

function Install-Dependencies {
    Write-Host "Installing production dependencies..."
    pip install -r requirements.txt
}

function Install-DevDependencies {
    Install-Dependencies
    Write-Host "Installing development dependencies..."
    pip install -r requirements-dev.txt
}

function Build-Package {
    Write-Host "Building native libraries and package..."
    & ./build.sh
}

function Run-Tests {
    Write-Host "Running tests..."
    pytest tests/ -v
}

function Run-TestsWithCoverage {
    Write-Host "Running tests with coverage..."
    pytest tests/ -v --cov=omg --cov-report=term --cov-report=html
}

function Run-Lint {
    Write-Host "Running flake8..."
    flake8 omg/ tests/
    Write-Host "Running mypy..."
    mypy omg/ --ignore-missing-imports
    Write-Host "Checking black formatting..."
    black --check omg/ tests/
    Write-Host "Checking isort..."
    isort --check-only omg/ tests/
}

function Format-Code {
    Write-Host "Formatting with black..."
    black omg/ tests/
    Write-Host "Sorting imports with isort..."
    isort omg/ tests/
}

function Run-Security {
    Write-Host "Running bandit..."
    bandit -r omg/
    Write-Host "Running safety..."
    safety check
}

function Clean-Artifacts {
    Write-Host "Cleaning build artifacts..."
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    if (Test-Path "*.egg-info") { Remove-Item -Recurse -Force "*.egg-info" }
    if (Test-Path "omg/native") { Remove-Item -Recurse -Force "omg/native" }
    if (Test-Path ".coverage") { Remove-Item -Force ".coverage" }
    if (Test-Path "htmlcov") { Remove-Item -Recurse -Force "htmlcov" }
    if (Test-Path ".pytest_cache") { Remove-Item -Recurse -Force ".pytest_cache" }
    
    # Remove __pycache__ directories
    Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" | ForEach-Object {
        Remove-Item -Recurse -Force $_.FullName
    }
    
    # Remove .pyc files
    Get-ChildItem -Path . -Recurse -File -Name "*.pyc" | ForEach-Object {
        Remove-Item -Force $_.FullName
    }
}

function Run-All {
    Format-Code
    Run-Lint
    Run-Tests
    Build-Package
}

switch ($Command.ToLower()) {
    "help" { Show-Help }
    "install" { Install-Dependencies }
    "install-dev" { Install-DevDependencies }
    "build" { Build-Package }
    "test" { Run-Tests }
    "test-cov" { Run-TestsWithCoverage }
    "lint" { Run-Lint }
    "format" { Format-Code }
    "security" { Run-Security }
    "clean" { Clean-Artifacts }
    "all" { Run-All }
    default { 
        Write-Host "Unknown command: $Command"
        Show-Help
    }
}
