# windows-config

Version-controlled, reproducible Windows baseline. "Dotfiles for Windows." Clone on any box, run one elevated command, get your setup.

## Quick start
```powershell
git clone <your-repo-url> ; cd windows-config
powershell -ExecutionPolicy Bypass -File .\apply.ps1          # elevated — runs all modules
# or pick modules:
.\apply.ps1 -Modules search,wsl
```
Every module is idempotent (safe to re-run). Some changes (WSL, search) fully apply after a reboot.

## Modules (`apply.ps1`)
| Module | What it does | Portable? |
|---|---|---|
| `search` | Disables Bing/web results in Start-menu search (local search unaffected) | ✅ any Win11 |
| `wsl` | Writes `~/.wslconfig` — caps WSL2 RAM (`6GB`) + auto memory-reclaim | ✅ any machine w/ WSL |
| `debloat` | Removes **and deprovisions** a list of Store bloat apps (Xbox app, Phone Link, Office nag, Get Help, Bing News/Weather, Solitaire, Clipchamp, Feedback Hub, Quick Assist) | ✅ list is editable |
| `nvidia` | Cleans the NVIDIA App driver-cache hoard now **and** schedules a weekly cleanup (it rebuilds ~750MB/update) | ✅ if NVIDIA present |

Edit the config block at the top of `apply.ps1` (`$WslMemory`, `$DebloatAppx`, …) to taste.

## Files
| File | |
|---|---|
| `apply.ps1` | Master orchestrator (modular, idempotent, elevated) |
| `nvidia-cache-clean.ps1` | Standalone NVIDIA cache cleaner (also run by the weekly task) |
| `search-no-web-results.reg` | The search registry keys (imported by the `search` module) |
| `revert.reg` | Undo the search tweak → stock Windows search |

## Versioning
```powershell
cd C:\Users\minga\windows-config
git add -A && git commit -m "..."
git remote add origin <your-repo-url> && git push -u origin master
```

## What is intentionally NOT here (machine-specific — don't port blindly)
- **Pagefile size** — depends on the box's RAM/SSD.
- **Per-app startup disables** (Steam/Discord/EA/Epic/Check Point) — depends on what's installed.
- **App uninstalls** (Warsaw/Zoom/Citrix) and **WSL docker.service disable** — specific to this machine's software.

## Three ways to version Windows config (general)
1. **`.reg` files** — registry is plain text; `git` + `reg import`. Simplest for pure settings.
2. **PowerShell script** (this repo) — when you need logic (restart a service, remove appx, conditionals). Most flexible.
3. **winget Configuration (DSC YAML)** — Microsoft's declarative provisioning: `winget configure config.yaml` sets registry + installs packages idempotently. Best for codifying a *whole* machine.
