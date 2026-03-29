# From repo root: .\scripts\push-to-github.ps1
# Prerequisite: gh auth login
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
Set-Location $RepoRoot

$gh = if (Get-Command gh -ErrorAction SilentlyContinue) { "gh" } elseif (Test-Path "C:\Program Files\GitHub CLI\gh.exe") {
    "C:\Program Files\GitHub CLI\gh.exe"
} else {
    throw "Install GitHub CLI: winget install GitHub.cli"
}

& $gh auth status 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not logged in. Run: gh auth login"
    exit 1
}

git remote get-url origin 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    & $gh repo create Overcharge-Alert --public --source=. --remote=origin --push
} else {
    git push -u origin master
}
