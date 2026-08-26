# windows-config

Version-controlled Windows tweaks, reproducible across machines. "Dotfiles for Windows."

## Contents
| File | What |
|---|---|
| `search-no-web-results.reg` | Disables Bing/web results in Start-menu search (local search unaffected) |
| `revert.reg` | Undoes the above (back to stock search) |
| `apply.ps1` | Idempotent applier — sets the keys **and** restarts SearchHost so it takes effect now |

## Use it on another machine
```powershell
git clone <your-repo> ; cd windows-config
# either:
powershell -ExecutionPolicy Bypass -File .\apply.ps1        # (elevated) applies + restarts SearchHost
# or just the registry:
reg import "search-no-web-results.reg"                       # (elevated), then reboot / restart SearchHost
```
To undo: `reg import "revert.reg"` (elevated) then reboot.

## Versioning
```powershell
cd C:\Users\minga\windows-config
git init && git add -A && git commit -m "windows search: no web results"
# push to your GitHub/GitLab; clone on any other Windows box
```

## Three ways to version Windows config (ranked for this use)
1. **`.reg` files** (this folder) — registry settings are plain text; commit to git, `reg import` anywhere. Simplest for pure registry tweaks. Needs admin for HKLM keys.
2. **PowerShell script** (`apply.ps1`) — when you need logic beyond registry (restart a service, conditionals, file copies, appx removals). One script per machine class; most flexible.
3. **winget Configuration (DSC YAML)** — Microsoft's modern declarative option: `winget configure .\config.dsc.yaml` can set registry, install packages, and enforce state idempotently. Best if you want full machine provisioning as code, not just a few tweaks.

> Note: HKLM policy keys require elevation. HKCU tweaks don't. Machine-specific things
> (pagefile size, per-app startup entries) are intentionally NOT in here — they don't
> port cleanly between machines.
