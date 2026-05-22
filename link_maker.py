#!/usr/bin/env python3
"""
Symlinks for dotfiles.
"""

import argparse
import pathlib
import shutil
import sys
from dataclasses import dataclass

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
HOME_DIR = pathlib.Path.home()

_ANY = "any"

# Values are either a plain string (same dest on all OSes) or a dict mapping
# sys.platform keys ("linux", "darwin", "win32") to dest paths.
# Use _ANY as a fallback when no platform-specific entry matches.
SYMLINK_PATHS: dict[str, str | dict[str, str]] = {
    "shell/bashrc":         {"linux": ".bashrc", "darwin": ".bashrc"},
    "shell/bash_profile":   {"linux": ".bash_profile", "darwin": ".bash_profile"},
    "shell/Microsoft.Powershell_profile.ps1": {"win32": "Documents/PowerShell"},
    "shell/gitconfig":      ".gitconfig",
    "editor/vim":           {_ANY: ".vim", "win32": "vimfiles"},
    "editor/exrc":          ".exrc",
    "editor/emacs":         ".emacs",
    "editor/vscode":        {"linux": ".config/Code/User",
                             "darwin": "Library/Application Support/Code/User",
                             "win32":  "AppData/Roaming/Code/User"},
    "gui/i3":               {"linux": ".config/i3"},
    "languages/ghc":        {_ANY: ".ghc", "win32": "AppData/Roaming/ghc"},
}

def resolve_dest(entry: str | dict[str, str]) -> str | None:
    if isinstance(entry, str):
        return entry
    return entry.get(sys.platform) or entry.get(_ANY)


@dataclass
class Options:
    overwrite_all: bool = False
    only_inexistent: bool = False
    quiet: bool = False


def prompt_overwrite(dest: pathlib.Path) -> bool:
    while True:
        choice = (
            input(f"Destination '{dest}' already exists. Overwrite? (Y/n): ")
            .strip()
            .lower()
        )
        if choice in ("y", "yes", ""):
            return True
        if choice in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'.")


def delete(dest: pathlib.Path) -> None:
    if dest.is_dir() and not dest.is_symlink():
        shutil.rmtree(dest)
    else:
        dest.unlink()


def make_symlink(origin: pathlib.Path, dest: pathlib.Path) -> None:
    dest.symlink_to(origin, target_is_directory=origin.is_dir())
    print(f"Symbolic link created: {dest} -> {origin}")


def log(msg: str, quiet: bool) -> None:
    if not quiet:
        print(msg)


def attempt_symlink_creation(
    origin: pathlib.Path, dest: pathlib.Path, opts: Options
) -> None:
    try:
        if dest.exists() or dest.is_symlink():
            if opts.only_inexistent:
                log(f"Skipping '{dest}': already exists.", opts.quiet)
                return
            if opts.overwrite_all or prompt_overwrite(dest):
                log(f"Overwriting '{dest}'.", opts.quiet)
                delete(dest)
                make_symlink(origin, dest)
        else:
            make_symlink(origin, dest)
    except OSError as e:
        if sys.platform == "win32" and e.winerror == 1314:
            print(
                f"Error creating symlink for '{dest}': insufficient privileges.\n"
                "On Windows, symlink creation requires either Administrator rights or "
                "Developer Mode (Settings > System > For developers)."
            )
        else:
            print(f"Error creating symlink for '{dest}': {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Dotfile symlink manager")
    parser.add_argument(
        "--overwrite-all",
        action="store_true",
        help="Overwrite existing targets without prompting",
    )
    parser.add_argument(
        "--only-inexistent", action="store_true", help="Skip targets that already exist"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress informational output"
    )
    args = parser.parse_args()

    opts = Options(
        overwrite_all=args.overwrite_all,
        only_inexistent=args.only_inexistent,
        quiet=args.quiet,
    )

    for origin_rel, entry in SYMLINK_PATHS.items():
        dest_rel = resolve_dest(entry)
        if dest_rel is None:
            log(
                f"Skipping '{origin_rel}': no destination defined for '{sys.platform}'.",
                opts.quiet,
            )
            continue
        attempt_symlink_creation(SCRIPT_DIR / origin_rel, HOME_DIR / dest_rel, opts)


if __name__ == "__main__":
    main()
