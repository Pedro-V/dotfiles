#Requires -RunAsAdministrator
<#
  Windows baseline provisioning - reproducible setup for a fresh (or existing) Windows box.
  Run elevated:  powershell -ExecutionPolicy Bypass -File .\apply.ps1
  Pick modules:  .\apply.ps1 -Modules search,wsl        (default: all)
  Every module is idempotent and safe to re-run.
#>
param(
  [ValidateSet('search','wsl','debloat','nvidia')]
  [string[]]$Modules = @('search','wsl','debloat','nvidia')
)

# ============ EDITABLE CONFIG ============
$WslMemory = '6GB'      # WSL2 RAM cap
$WslSwap   = '2GB'
$DebloatAppx = @(       # Store apps to remove + deprovision (edit freely)
  'YourPhone','CrossDevice','GamingApp','MicrosoftOfficeHub',
  'GetHelp','BingNews','BingWeather','SolitaireCollection','Clipchamp',
  'WindowsFeedbackHub','QuickAssist'
)
# =========================================

$ErrorActionPreference = 'Continue'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

function Step($m){ Write-Host "`n=== $m ===" -ForegroundColor Cyan }

function Invoke-Search {
  Step 'Search: disable web/Bing results in Start search'
  reg import "$here\search-no-web-results.reg" 2>&1 | Out-Null
  Get-Process SearchHost -EA SilentlyContinue | Stop-Process -Force -EA SilentlyContinue
  Write-Host "  applied (local search unaffected; run revert.reg to undo)"
}

function Invoke-Wsl {
  Step "WSL: cap memory ($WslMemory) + auto-reclaim"
  $content = @"
[wsl2]
memory=$WslMemory
swap=$WslSwap

[experimental]
autoMemoryReclaim=gradual
"@
  Set-Content -Path "$env:USERPROFILE\.wslconfig" -Value $content -Encoding ASCII
  Write-Host "  wrote $env:USERPROFILE\.wslconfig (takes effect on next 'wsl --shutdown')"
}

function Invoke-Debloat {
  Step 'Debloat: remove + deprovision Store bloat'
  foreach($pat in $DebloatAppx){
    Get-AppxPackage -AllUsers -Name "*$pat*" -EA SilentlyContinue | ForEach-Object {
      try { Remove-AppxPackage -Package $_.PackageFullName -AllUsers -EA Stop; Write-Host "  removed  $($_.Name)" } catch {}
    }
    Get-AppxProvisionedPackage -Online | Where-Object { $_.DisplayName -match $pat } | ForEach-Object {
      try { Remove-AppxProvisionedPackage -Online -PackageName $_.PackageName -AllUsers -EA Stop | Out-Null; Write-Host "  deprovisioned  $($_.DisplayName)" } catch {}
    }
  }
}

function Invoke-Nvidia {
  Step 'NVIDIA: clean driver-cache hoard + schedule weekly'
  & "$here\nvidia-cache-clean.ps1"
  $act = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$here\nvidia-cache-clean.ps1`""
  $trg = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 3am
  try {
    Register-ScheduledTask -TaskName 'NvidiaCacheClean' -Action $act -Trigger $trg -RunLevel Highest -Force -EA Stop | Out-Null
    Write-Host "  scheduled weekly cleanup task 'NvidiaCacheClean'"
  } catch { Write-Host "  (couldn't register scheduled task: $($_.Exception.Message))" }
}

if($Modules -contains 'search'){  Invoke-Search }
if($Modules -contains 'wsl'){     Invoke-Wsl }
if($Modules -contains 'debloat'){ Invoke-Debloat }
if($Modules -contains 'nvidia'){  Invoke-Nvidia }

Write-Host "`nBaseline applied. Some changes (WSL, search) take full effect after a reboot." -ForegroundColor Green
