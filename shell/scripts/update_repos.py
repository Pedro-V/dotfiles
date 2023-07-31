#!/bin/python3
import sys
from os import listdir, chdir, system, getcwd
from os.path import join, isdir

COMMAND = 'git pull --recurse-submodules'

def update_repos(path):
    dirs = list(filter(isdir,
                       map(lambda x: join(path, x), listdir(path))))
    if join(path, '.git') in dirs:
        try:
            print(f'Updating {path}')
            chdir(path)
            system(COMMAND)
        except Exception as e:
            print(f'Error while running command in {dir}: {e}')
    else:
        for directory in dirs:
            update_repos(directory)

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else getcwd()
    update_repos(path)
