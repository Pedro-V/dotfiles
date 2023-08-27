#!/bin/python3
"""
Script for managing my git repositories.

I mantain all my repositories in ~/repos for an easy management.
"""

import sys
import re
from os import system

def adjust_commands(commands):
    clean_spaces = lambda st: re.sub(r'\s+', ' ', st)
    return {k: (x, clean_spaces(y)) for k, (x, y) in commands.items()}

commands = adjust_commands({
    'status': (
        'prints each repo status',
        """
        find -name .git
            -execdir pwd \;
            -execdir git status -s \;
        """,
    ),
    'pull': (
        'pulls recursively each repo and submodule',
        """
        find -name .git 
            -execdir pwd \;
            -execdir git pull --recurse-submodules \;
        """,
    ),
    'push': (
        'pushes every repo and submodule',
        """
        find -name .git
            -execdir pwd \;
            -execdir git push \;
        """,
    ),
    'submodule-checkout': (
        'makes each submodule checkout main',
        """
        find -name .gitmodules
            -execdir pwd \;
            -execdir git submodule foreach --recursive 
                'git checkout main &> /dev/null || git checkout master' \;
        """,
    ),
})

def main():
    if len(sys.argv) < 2:
        print(f'usage: {sys.argv[0]} [COMMAND]')
        for c in commands:
            print(f'\t{c}: {commands[c][0]}')
        return
    system(commands[sys.argv[1]][1])

if __name__ == '__main__':
    main()
