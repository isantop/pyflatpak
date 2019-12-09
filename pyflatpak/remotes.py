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
import os
import pathlib

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
    fp_user_config_filepath = os.path.join(
        pathlib.Path.home(),
        '.local/share/flatpak'
    )
    fp_config_filename = 'repo/config'

    def __init__(self):
        self.log = logging.getLogger('pyflatpak.Remotes')
        self.log.debug('Loaded!')
        self.remotes = {}
        self.get_remotes()
    
    def get_remote(self, loc='~/.local/share/flatpak', option='user'):
        """
        Get a remote, given the LOC config path
        """

        current_remotes = {}
        config = ConfigParser()
        fp_config = os.path.join(loc, self.fp_config_filename)
        self.log.debug('Looking for %s remotes in %s', option, fp_config)

        with open(fp_config) as config_file:
            config.read_file(config_file)
        raw_config = config._sections

        for section in raw_config:
            if 'remote' in section:
                remote_name = section.split('"')[1]
                current_remotes[remote_name] = {}
                remote_title = remote_name
                try:
                    if bool(raw_config[section]['xa.title-is-set']):
                        remote_title = raw_config[section]['xa.title']
                except KeyError:
                    pass
                remote_url = raw_config[section]['url']
                current_remotes[remote_name]['name'] = remote_name
                current_remotes[remote_name]['title'] = remote_title
                current_remotes[remote_name]['url'] = remote_url
                current_remotes[remote_name]['option'] = option
        
        return (option, current_remotes)
    
    def get_remotes(self):
        """
        Update system and user remotes
        """
        try:
            self.system_remotes = self.get_remote(
                loc=self.fp_sys_config_filepath, 
                option='system'
            )[1]
        except FileNotFoundError:
            self.system_remotes = {}
        
        try:
            self.user_remotes = self.get_remote(
                loc=self.fp_user_config_filepath,
                option='user'
            )[1]
        except FileNotFoundError:
            self.user_remotes = {}
        self.remotes['system'] = self.system_remotes
        self.remotes['user'] = self.user_remotes

    
    def delete_remote(self, remote_name):
        """
        Delete a configured remote.

        Argument:
            remote_name: The 'name' of the remote to delete
        """
        self.get_remotes()
        if remote_name not in self.user_remotes and remote_name not in self.system_remotes:
            self.log.exception('Remote %s not configured!' % remote_name)
            raise NoRemoteExistsError
        
        rm_command = command.Command(['remote-delete', '--force', remote_name])
        rm_command.run()
        self.get_remotes()
    
    def add_remote(self, remote_name, remote_url, user=True):
        """
        Add a new remote.

        Arguments:
            remote_name: the name to use for the new remote
            remote_url: the URL of the .flatpakrepo file
        """
        cmd = ['remote-add', '--if-not-exists', remote_name, remote_url]

        if user:
            cmd.append("--user")

        add_command = command.Command(cmd)
        add_command.run()
        self.get_remotes()
        
