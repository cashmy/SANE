param(
    [string]$Root = $PSScriptRoot,
    [switch]$IncludeLockFiles,
    [switch]$Details
)

$ErrorActionPreference = "Stop"

$excludeDirs = @(
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    ".vite",
    "coverage",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache"
)

$includeExtensions = @(
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".css",
    ".html",
    ".json",
    ".toml",
    ".ini",
    ".md",
    ".yml",
    ".yaml",
    ".example"
)

$includeNames = @(
    ".env.example",
    ".gitignore"
)

$lockFiles = @(
    "package-lock.json",
    "npm-shrinkwrap.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "uv.lock",
    "Pipfile.lock"
)

$resolvedRoot = (Resolve-Path -LiteralPath $Root).Path

$files = Get-ChildItem -LiteralPath $resolvedRoot -Recurse -File -Force | Where-Object {
    $relativePath = $_.FullName.Substring($resolvedRoot.Length).TrimStart("\", "/")
    $pathParts = $relativePath.Split([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    $isExcludedDir = [bool]($pathParts | Where-Object { $excludeDirs -contains $_ })
    $isIncludedType = ($includeExtensions -contains $_.Extension) -or ($includeNames -contains $_.Name)
    $isSecretEnv = $_.Name -eq ".env"
    $isLockFile = $lockFiles -contains $_.Name

    -not $isExcludedDir -and
        $isIncludedType -and
        -not $isSecretEnv -and
        ($IncludeLockFiles -or -not $isLockFile)
}

$lineItems = $files | ForEach-Object {
    $lineCount = (Get-Content -LiteralPath $_.FullName -ErrorAction SilentlyContinue | Measure-Object -Line).Lines
    [pscustomobject]@{
        Extension = if ($_.Extension) { $_.Extension } else { $_.Name }
        Lines = $lineCount
        File = $_.FullName.Substring($resolvedRoot.Length).TrimStart("\", "/")
    }
}

Write-Host "SANE project line count"
Write-Host "Root: $resolvedRoot"
Write-Host ""

$lineItems |
    Group-Object Extension |
    Sort-Object Name |
    ForEach-Object {
        [pscustomobject]@{
            Extension = $_.Name
            Files = $_.Count
            Lines = ($_.Group | Measure-Object Lines -Sum).Sum
        }
    } |
    Format-Table -AutoSize

Write-Host "---"

[pscustomobject]@{
    Files = $files.Count
    Lines = ($lineItems | Measure-Object Lines -Sum).Sum
} | Format-Table -AutoSize

if ($Details) {
    Write-Host "---"
    $lineItems |
        Sort-Object -Property @{ Expression = "Lines"; Descending = $true }, @{ Expression = "File"; Ascending = $true } |
        Format-Table -AutoSize
}
