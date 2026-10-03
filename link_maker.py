#!/usr/bin/env python3
"""Link dotfiles from this repository into the home directory."""

from __future__ import annotations

import argparse
import datetime
import os
import pathlib
import shutil
import stat
import sys
from dataclasses import dataclass

REPO_DIR = pathlib.Path(__file__).resolve().parent
HOME_DIR = pathlib.Path.home()
IS_WINDOWS = sys.platform == "win32"
ERROR_PRIVILEGE_NOT_HELD = 1314

ANY = "any"

# Keys are paths relative to the repository; values are destinations relative to
# the home directory. A value is either a string (same on all platforms) or a
# dict keyed by sys.platform ("linux", "darwin", "win32"), with ANY as fallback.
LINKS: dict[str, str | dict[str, str]] = {
    "shell/bashrc": {"linux": ".bashrc", "darwin": ".bashrc"},
    "shell/bash_profile": {"linux": ".bash_profile", "darwin": ".bash_profile"},
    "shell/Microsoft.Powershell_profile.ps1": {
        "win32": "Documents/PowerShell/Microsoft.PowerShell_profile.ps1"
    },
    "git/gitconfig": ".gitconfig",
    "editor/vim": {ANY: ".vim", "win32": "vimfiles"},
    "editor/exrc": ".exrc",
    "editor/emacs": ".emacs",
    "editor/vscode": {
        "linux": ".config/Code/User",
        "darwin": "Library/Application Support/Code/User",
        "win32": "AppData/Roaming/Code/User",
    },
    "gui/i3": {"linux": ".config/i3"},
    "languages/ghc": {ANY: ".ghc", "win32": "AppData/Roaming/ghc"},
}

STYLES = {
    "linked": "1;32",
    "current": "90",
    "skip": "90",
    "backup": "33",
    "restored": "33",
    "would": "36",
    "fail": "1;31",
}
STDERR_LEVELS = {"fail", "restored"}
TAG_WIDTH = max(len(level) for level in STYLES) + 3


@dataclass(frozen=True)
class Options:
    overwrite_all: bool = False
    only_inexistent: bool = False
    quiet: bool = False
    dry_run: bool = False
    backup: bool = True
    junctions: bool = True
    hardlinks: bool = False
    color: str = "auto"


def enable_windows_ansi() -> None:
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        enable_virtual_terminal_processing = 0x0004
        for std_handle in (-11, -12):
            handle = kernel32.GetStdHandle(std_handle)
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(
                    handle, mode.value | enable_virtual_terminal_processing
                )
    except (AttributeError, OSError):
        pass


def wants_color(stream, opts: Options) -> bool:
    if opts.color == "always":
        return True
    if opts.color == "never" or "NO_COLOR" in os.environ:
        return False
    return stream.isatty()


def report(level: str, msg: str, opts: Options) -> None:
    stream = sys.stderr if level in STDERR_LEVELS else sys.stdout
    if opts.quiet and stream is sys.stdout:
        return
    tag = f"[{level}]".ljust(TAG_WIDTH)
    if wants_color(stream, opts):
        tag = f"\033[{STYLES[level]}m{tag}\033[0m"
    print(f"{tag}{msg}", file=stream)


def resolve_dest(entry: str | dict[str, str]) -> pathlib.Path | None:
    rel = entry if isinstance(entry, str) else entry.get(sys.platform) or entry.get(ANY)
    return HOME_DIR / rel if rel else None


def prompt_overwrite(dest: pathlib.Path) -> bool:
    while True:
        try:
            choice = input(f"'{dest}' already exists. Replace it? (Y/n): ")
        except EOFError:
            return False
        match choice.strip().lower():
            case "y" | "yes" | "":
                return True
            case "n" | "no":
                return False
        print("Please enter 'y' or 'n'.")


def is_linked(origin: pathlib.Path, dest: pathlib.Path) -> bool:
    try:
        return os.path.samefile(origin, dest)
    except OSError:
        return False


def is_junction(path: pathlib.Path) -> bool:
    if not IS_WINDOWS:
        return False
    attrs = getattr(os.lstat(path), "st_file_attributes", 0)
    return bool(attrs & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def remove(path: pathlib.Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif is_junction(path):
        os.rmdir(path)
    else:
        shutil.rmtree(path)


def move_aside(dest: pathlib.Path) -> pathlib.Path:
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = dest.with_name(f"{dest.name}.bak-{stamp}")
    counter = 0
    while os.path.lexists(backup):
        counter += 1
        backup = dest.with_name(f"{dest.name}.bak-{stamp}-{counter}")
    dest.rename(backup)
    return backup


def is_privilege_error(e: OSError) -> bool:
    return IS_WINDOWS and getattr(e, "winerror", None) == ERROR_PRIVILEGE_NOT_HELD


def create_link(origin: pathlib.Path, dest: pathlib.Path, opts: Options) -> str:
    try:
        dest.symlink_to(origin, target_is_directory=origin.is_dir())
        return "symlink"
    except OSError as e:
        if not is_privilege_error(e):
            raise
        if origin.is_dir() and opts.junctions:
            import _winapi

            _winapi.CreateJunction(str(origin), str(dest))
            return "junction"
        if origin.is_file() and opts.hardlinks:
            os.link(origin, dest)
            return "hardlink"
        raise


def describe_kind(kind: str) -> str:
    if kind == "hardlink":
        return "hardlink; breaks if a tool replaces the file, re-run to relink"
    return kind


def describe_error(e: OSError, origin: pathlib.Path, opts: Options) -> str:
    if not is_privilege_error(e):
        return str(e)
    msg = "no symlink privilege (needs Administrator or Developer Mode)"
    if origin.is_file() and not opts.hardlinks:
        msg += "; retry with --hardlinks"
    return msg


def link_one(origin: pathlib.Path, dest: pathlib.Path, opts: Options) -> bool:
    if not os.path.lexists(origin):
        report("fail", f"{origin}: source does not exist", opts)
        return False

    occupied = os.path.lexists(dest)
    if occupied:
        if is_linked(origin, dest):
            report("current", str(dest), opts)
            return True
        if opts.only_inexistent:
            report("skip", f"{dest}: already exists", opts)
            return True

    if opts.dry_run:
        verb = "replace" if occupied else "create"
        report("would", f"{verb} {dest} -> {origin}", opts)
        return True

    if occupied and not (opts.overwrite_all or prompt_overwrite(dest)):
        report("skip", f"{dest}: kept", opts)
        return True

    backup: pathlib.Path | None = None
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if occupied:
            if opts.backup:
                backup = move_aside(dest)
                report("backup", f"{dest} -> {backup}", opts)
            else:
                remove(dest)
        kind = create_link(origin, dest, opts)
    except OSError as e:
        report("fail", f"{dest}: {describe_error(e, origin, opts)}", opts)
        if backup is not None:
            try:
                backup.rename(dest)
                report("restored", f"{dest} from {backup}", opts)
            except OSError as restore_error:
                report("fail", f"{dest}: could not restore from '{backup}': {restore_error}", opts)
        return False

    report("linked", f"{dest} -> {origin} ({describe_kind(kind)})", opts)
    return True


def parse_args() -> Options:
    parser = argparse.ArgumentParser(description="Dotfile link manager")
    parser.add_argument(
        "--overwrite-all",
        action="store_true",
        help="replace existing targets without prompting",
    )
    parser.add_argument(
        "--only-inexistent", action="store_true", help="skip targets that already exist"
    )
    parser.add_argument(
        "-n", "--dry-run", action="store_true", help="show what would be done"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="delete replaced targets instead of moving them aside",
    )
    parser.add_argument(
        "--no-junctions",
        action="store_true",
        help="on Windows, do not fall back to junctions for directories",
    )
    parser.add_argument(
        "--hardlinks",
        action="store_true",
        help="on Windows, fall back to hard links for files when symlinks are not allowed",
    )
    parser.add_argument(
        "--color",
        choices=("auto", "always", "never"),
        default="auto",
        help="colorize output (default: auto; NO_COLOR is respected)",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="suppress informational output"
    )
    args = parser.parse_args()
    return Options(
        overwrite_all=args.overwrite_all,
        only_inexistent=args.only_inexistent,
        quiet=args.quiet,
        dry_run=args.dry_run,
        backup=not args.no_backup,
        junctions=not args.no_junctions,
        hardlinks=args.hardlinks,
        color=args.color,
    )


def main() -> int:
    opts = parse_args()
    if IS_WINDOWS:
        enable_windows_ansi()

    failures = 0
    for origin_rel, entry in LINKS.items():
        dest = resolve_dest(entry)
        if dest is None:
            report("skip", f"{origin_rel}: no destination for '{sys.platform}'", opts)
            continue
        if not link_one(REPO_DIR / origin_rel, dest, opts):
            failures += 1

    if failures:
        report("fail", f"{failures} link(s) failed", opts)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
