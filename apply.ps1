#Requires -RunAsAdministrator
# Idempotent applier for Windows config in this folder. Run elevated on any machine:
#   powershell -ExecutionPolicy Bypass -File .\apply.ps1

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Applying: disable web results in Start search..."
$explorer = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\Explorer'
$search   = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search'
foreach($k in $explorer,$search){ if(-not (Test-Path $k)){ New-Item -Path $k -Force | Out-Null } }
New-ItemProperty -Path $explorer -Name 'DisableSearchBoxSuggestions' -Value 1 -PropertyType DWord -Force | Out-Null
New-ItemProperty -Path $search   -Name 'DisableWebSearch'           -Value 1 -PropertyType DWord -Force | Out-Null
New-ItemProperty -Path $search   -Name 'ConnectedSearchUseWeb'      -Value 0 -PropertyType DWord -Force | Out-Null
New-ItemProperty -Path $search   -Name 'AllowCloudSearch'           -Value 0 -PropertyType DWord -Force | Out-Null

# Restart SearchHost so the change takes effect without a reboot
Get-Process SearchHost -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Done. Verify:" -ForegroundColor Green
Get-ItemProperty $explorer -Name DisableSearchBoxSuggestions | Select-Object DisableSearchBoxSuggestions
