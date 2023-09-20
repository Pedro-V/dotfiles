#!/usr/bin/env python3
"""
Symlinks for dotfiles.
"""
import os
import pathlib

def prompt_delete_file(file):
    while True:
        choice = input(f"Destination path '{file}' already exists. Do you want to delete it? (Y/n): ")
        if choice.lower() in ['y', 'yes', '']:
            return True
        elif choice.lower() in ['n', 'no']:
            return False
        else:
            print("Invalid choice. Please enter 'y' or 'n'.")

def make_symlink(origin, dest):
    try:
        os.symlink(origin, dest)
        print(f"Symbolic link created: {dest} -> {origin}")
    except FileExistsError:
        if prompt_delete_file(dest):
            try:
                os.remove(dest)
                os.symlink(origin, dest)
                print(f"Symbolic link created: {dest} -> {origin}")
            except Exception as e:
                print(f"Error creating symlink: {e}")
        else:
            print("Symlink creation aborted.")

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

for origin in symlink_paths:
    make_symlink(SCRIPT_DIR / origin,
                 HOME_DIR / symlink_paths[origin])

