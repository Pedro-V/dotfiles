# Utility functions
# ----------------------------------------------------------
function Add-LineNumber {
  param(
    [Parameter(ValueFromPipeline=$true)]
    [object]$InputObject
  )

  begin { $i = 0 }

  process {
    "{0,6}: {1}" -f $i++, $InputObject
  }
}

# Aliases
# ----------------------------------------------------------

Set-Alias nl Add-LineNumber

# User prompt
# ----------------------------------------------------------

$esc    = [char]27
$reset  = "$esc[0m"
$bold   = "$esc[1m"
$red    = "$esc[31m"
$green  = "$esc[32m"
$yellow = "$esc[33m"
$cyan   = "$esc[36m"
$gray   = "$esc[90m"
$white  = "$esc[97m"

function prompt {
    $lastOk = $?  # must be first — any other expression resets it

    $p     = $ExecutionContext.SessionState.Path.CurrentLocation
    $short = $p -replace [regex]::Escape($HOME), '~'

    $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator
    )
    $adminPart = if ($isAdmin) { "${red}${bold}[ADMIN]${reset} " } else { '' }

    $gitPart = ''
    git rev-parse --git-dir 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $branch = git symbolic-ref --short HEAD 2>$null
        if ($LASTEXITCODE -ne 0) {
            $branch = git rev-parse --short HEAD 2>$null
        }
        $dirty = git status --porcelain 2>$null
        if ($dirty) {
            $gitPart = " (${yellow}${branch}*${reset})"
        } else {
            $gitPart = " (${green}${branch}${reset})"
        }
    }

    $venvPart = ''
    if ($env:VIRTUAL_ENV) {
        $venvPart = " ${gray}[$(Split-Path $env:VIRTUAL_ENV -Leaf)]${reset}"
    }

    $arrow = if ($lastOk) { "${white}>${reset}" } else { "${red}>${reset}" }

    "$adminPart${gray}PS${reset} ${cyan}${short}${reset}$gitPart$venvPart $arrow "
}

