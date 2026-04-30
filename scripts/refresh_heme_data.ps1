param(
    [string[]]$Drug,
    [switch]$SkipPdf,
    [switch]$SkipNtuh
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$updater = Join-Path $PSScriptRoot "update_nhi_open_data.py"
$ntuhUpdater = Join-Path $PSScriptRoot "update_ntuh_prices.py"
$builder = Join-Path $repoRoot "build_html.py"

$args = @($updater)
if ($Drug) {
    foreach ($name in $Drug) {
        $args += @("--drug", $name)
    }
}
if ($SkipPdf) {
    $args += "--skip-pdf"
}

Write-Host "Updating heme data from NHI open data..."
python @args

if (-not $SkipNtuh) {
    $ntuhArgs = @($ntuhUpdater)
    if ($Drug) {
        foreach ($name in $Drug) {
            $ntuhArgs += @("--drug", $name)
        }
    }
    Write-Host "Updating NTUH self-pay prices..."
    python @ntuhArgs
}

Write-Host "Rebuilding static HTML..."
python $builder
