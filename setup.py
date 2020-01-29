#!/usr/bin/python3

"""
Copyright (c) 2019, Ian Santopietro
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


from distutils.core import setup
from distutils.cmd import Command
import os
import subprocess
import sys

TREE = os.path.dirname(os.path.abspath(__file__))
DIRS = [
    'python3-flatpak',
    'bin'
]

version = {}
with open ('pyflatpak/__version__.py') as fp:
    exec(fp.read(), version)

def run_under_same_interpreter(opname, script, args):
    """Re-run with the same as current interpreter."""
    print('\n** running: {}...'.format(script), file=sys.stderr)
    if not os.access(script, os.R_OK | os.X_OK):
        print(
            'ERROR: cannot read and execute: {!r}'.format(script),
            file=sys.stderr
        )
        print(
            'Consider running `setup.py test --skip-{}`'.format(opname),
            file=sys.stderr
        )
        sys.exit(3)
    cmd = [sys.executable, script] + args
    print('check_call:', cmd, file=sys.stderr)
    subprocess.check_call(cmd)
    print('** PASSED: {}\n'.format(script), file=sys.stderr)

def run_pyflakes3():
    """Run a round of pyflakes3."""
    script = '/usr/bin/pyflakes3'
    names = [
        'setup.py',
    ] + DIRS
    args = [os.path.join(TREE, name) for name in names]
    run_under_same_interpreter('flakes', script, args)

class Release(Command):
    """ Generate a release and push it to git."""
    description = "Generate a release and push it to git."

    user_options = [
        ('dry-run', None, 'Skip the actual release and do a dry run instead.'),
        ('prerelease', None, 'Release this version as a pre-release.'),
        ('skip-deb', None, 'Skip doing a debian update for this release.'),
        ('force-version=', None, 'Force the version to update to the given value.')
    ]

    def initialize_options(self):
        self.dry_run = False
        self.prerelease = False
        self.skip_deb = False
        self.force_version = None
    
    def finalize_options(self):
        if self.force_version:
            if not isinstance(self.force_version, str):
                raise Exception('Please specify the test version to release')

    def run(self):
        command = ['npx', 'standard-version']
        if self.dry_run:
            command.append('--dry-run')
        if self.prerelease:
            command.append('--prerelease')
        if self.force_version:
            # See https://github.com/conventional-changelog/standard-version#release-as-a-target-type-imperatively-npm-version-like
            command.append('--release-as')
            command.append(self.force_version)
        print(command)
        subprocess.run(command)
        if not self.dry_run:
            subprocess.run(
                ['git', 'push', '--follow-tags']
            )
        
        if not self.skip_deb:
            deb_command = ['dch', '-v']
            version = {}
            with open ('pyflatpak/__version__.py') as fp:
                exec(fp.read(), version)

            if self.force_version:
                deb_command.append(self.force_version)
            else:
                deb_command.append(version['__version__'])
                
            deb_r_command = ['dch', '-r', '""']
            print(deb_command)
            print(deb_r_command)
            if not self.dry_run:
                subprocess.run(deb_command)
                subprocess.run(deb_r_command)
            
            deb_git_command = ['git', 'commit', '-a', '-m']
            if self.force_version:
                deb_git_command.append(self.force_version)
            else:
                v = version['__version__']
                deb_git_command.append(f'chore(deb): Deb Release {v}')
            
            print(deb_git_command)
            if not self.dry_run:
                subprocess.run(deb_git_command)

class Test(Command):
    """Basic sanity checks on our code."""
    description = 'run pyflakes3'

    user_options = [
        ('skip-flakes', None, 'do not run pyflakes static checks'),
    ]

    def initialize_options(self):
        self.skip_sphinx = 0
        self.skip_flakes = 0

    def finalize_options(self):
        pass

    def run(self):
        if not self.skip_flakes:
            run_pyflakes3()

setup(
    name='pyflatpak',
    version=version['__version__'],
    description='Basic python wrapper for managing flatpak',
    url='https://github.com/isantop/pyflatpak',
    author='Ian Santopietro',
    author_email='isantop@gmail.com',
    license='BSD-2',
    packages=['pyflatpak'],
    cmdclass={
        'test': Test,
        'release': Release
    },
)
