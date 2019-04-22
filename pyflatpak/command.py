#!/usr/bin/env python3

"""
 pyflatpak
 A simple python3 wrapper for managing the flatpak system

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

This is a command library that issues commands to flatpak and returns 
the results.
"""

import logging
import subprocess

class Command():
    """
    This is a command library that issues commands to flatpak and returns 
    the results.

    arguments:
        command - The command to run.
    
    Returns:
        The output of the command provided, or an error.
    """

    def __init__(self, command):
        self.log = logging.getLogger('pyflatpak.Command')
        self.log.debug('Loaded!')
        self.command = command
        self.log.info('Got command, {}'.format(self.command))
    
    def run(self):
        """
        Runs COMMAND and returns the output completed process.
        """
        this_command = ['flatpak'] + self.command
        complete_command = subprocess.run(
            this_command,
            check=True,
        )
        return complete_command
