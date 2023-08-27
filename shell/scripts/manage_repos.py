#!/bin/python3
"""
Script for updating my git repositories.

I mantain all my repositories in ~/repos for an easy pull in all of them
with `~/repos/update_repos.py {repo}`.
This may take a while, maybe there is a more efficient way of doing it.
"""

import sys
from os import system

commands = {
    'checkout': (
        'prints each repo status',
        'find -name .git -execdir pwd \; -execdir git status -s \;',
    ),
    'update': (
        'pulls recursively each repo',
        'find -name .git -execdir pwd \; -execdir git pull --recurse-submodules \;',
    ),
}

def main():
    if len(sys.argv) < 2:
        print(f'usage: {sys.argv[0]} [COMMAND]')
        for c in commands:
            print(f'\t{c}: {commands[c][0]}')
        return
    system(commands[sys.argv[1]][1])

if __name__ == '__main__':
    main()
