#!/usr/bin/env python3
"""
Symlinks for dotfiles.
"""
import os
import argparse
import pathlib

def prompt_delete_file(file):
    while True:
        choice = input(f"Destination path '{file}' already exists. Do you want to overwrite it? (Y/n): ")
        if choice.lower() in ['y', 'yes', '']:
            return True
        elif choice.lower() in ['n', 'no']:
            return False
        else:
            print("Invalid choice. Please enter 'y' or 'n'.")

def make_symlink(origin, dest):
    os.symlink(origin, dest)
    print(f"Symbolic link created: {dest} -> {origin}")

def print_log(log_str, quiet):
    print(log_str) if quiet else None

def attempt_symlink_creation(
    origin,
    dest,
    overwrite_all=False,
    only_inexistent=False,
    quiet=False,
):
    try:
        if os.path.exists(dest):
            if only_inexistent:
                print_log(f"Symlink not created for {dest} as it already exists.", quiet)
                return
            if overwrite_all or prompt_delete_file(dest):
                print_log(f"Overwriting {dest}.", quiet)
                os.remove(dest)
        make_symlink(origin, dest)
    except Exception as e:
        print(f"Error creating symlink: {e}")

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
HOME_DIR = pathlib.Path.home()

# TODO look for a more robust, less verbose way of doing this

symlink_paths = {
    "shell/bashrc":         ".bashrc",
    "shell/gitconfig":      ".gitconfig",
    "shell/bash_profile":   ".bash_profile",
    "editor/vim":           ".vim",
    "editor/exrc":          ".exrc",
    "editor/emacs":         ".emacs",
    "gui/i3":               ".config/i3",
    "languages/ghc":        ".ghc",
}

def main():
    parser = argparse.ArgumentParser(description="Link maker")
    parser.add_argument('--overwrite-all',
                        action='store_true',
                        help='Overwrite all symlinks without prompting')
    parser.add_argument('--only-inexistent',
                        action='store_true',
                        help='Create symlink only if it doesn\'t exist')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress verbose output')
    args = parser.parse_args()
    for origin in symlink_paths:
        attempt_symlink_creation(SCRIPT_DIR / origin,
                                 HOME_DIR / symlink_paths[origin],
                                 args.overwrite_all,
                                 args.only_inexistent,
                                 args.quiet)

if __name__ ==  "__main__":
    main()
