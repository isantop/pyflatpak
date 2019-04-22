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

Queries information about flatpak remotes
"""

from configparser import ConfigParser
import logging
from os import path

import pyflatpak.command as command

class NoRemoteExistsError(Exception):
    pass

class Remotes():
    """
    Queries information about flatpak remotes.
    
    Returns:
        A remote object.
    """

    fp_sys_config_filepath = '/var/lib/flatpak/'
    fp_user_config_filepath = '~/.local/share/flatpak'
    fp_config_filename = 'repo/config'

    def __init__(self):
        self.log = logging.getLogger('pyflatpak.Remotes')
        self.log.debug('Loaded!')

    def get_remotes(self):
        """
        Gets a dict of the current remotes, which have attributes.
        """
        config = ConfigParser()
        remotes = {}
        fp_sys_config = path.join(
            self.fp_sys_config_filepath,
            self.fp_config_filename
        )
        self.log.debug(fp_sys_config)
        with open(fp_sys_config) as config_file:
            config.read_file(config_file)
        raw_config =  config._sections
        for section in raw_config:
            if 'core' not in section:
                remote_name = section.split('"')[1]
                remotes[remote_name] = {}
                remote_title = remote_name
                if raw_config[section]['xa.title-is-set'] == 'true':
                    remote_title = raw_config[section]['xa.title']
                remote_url = raw_config[section]['url']
                remotes[remote_name]['name'] = remote_name
                remotes[remote_name]['title'] = remote_title
                remotes[remote_name]['url'] = remote_url
                remotes[remote_name]['option'] = 'system'
        
        self.remotes = remotes
        return remotes
    
    def delete_remote(self, remote_name):
        """
        Delete a configured remote.
        """
        if remote_name not in self.remotes:
            self.log.exception('Remote %s not configured!' % remote_name)
            raise NoRemoteExistsError
        
        rm_command = command.Command(['remote-delete', remote_name])
        try:
            rm_command.run()
        except subprocess.CalledProcessError:
            raise NoRemoteExistsError

        self.get_remotes()
    
    def add_remote(self, remote_name, remote_url):
        add_command = command.Command(
            ['remote-add', '--if-not-exists', remote_name, remote_url]
        )
        add_command.run()
        
