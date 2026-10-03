# Deletes hoarded NVIDIA App driver-download packages (ota-artifacts), keeping only the newest.
# The NVIDIA App accumulates ~750MB per driver update and never cleans up (was 47GB on this machine).
# Safe: these are download caches; the installed driver is unaffected and packages re-download if needed.
# Run standalone anytime, or let apply.ps1 register it as a weekly scheduled task.
# NOTE: ASCII-only on purpose so it parses under Windows PowerShell 5.1 (used by scheduled tasks).

$grd = "$env:ProgramData\NVIDIA Corporation\NVIDIA App\UpdateFramework\ota-artifacts\grd"
if (-not (Test-Path $grd)) { Write-Host "No NVIDIA ota-artifacts folder - nothing to do."; return }

$before = [math]::Round((Get-ChildItem $grd -Recurse -File -Force -EA SilentlyContinue | Measure-Object Length -Sum).Sum/1GB, 2)
$dirs = Get-ChildItem $grd -Directory -Force -EA SilentlyContinue | Sort-Object LastWriteTime -Descending
$dirs | Select-Object -Skip 1 | ForEach-Object { Remove-Item $_.FullName -Recurse -Force -EA SilentlyContinue }
$after = [math]::Round((Get-ChildItem $grd -Recurse -File -Force -EA SilentlyContinue | Measure-Object Length -Sum).Sum/1GB, 2)
Write-Host ("NVIDIA cache: {0} GB -> {1} GB (kept newest driver package)" -f $before, $after)
