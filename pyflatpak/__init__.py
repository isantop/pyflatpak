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

This is the demo cli client implementing the API provided.
"""

import logging
import logging.handlers as handlers

from . import remotes as Remotes
from . import command as Command

VERSION = '0.0.0'

SYSTEMD_SUPPORT = False
try:
    from systemd.journal import JournalHandler
    SYSTEMD_SUPPORT = True

except ImportError:
    pass

log_file_path = '/tmp/pyflatpak.log'

level = {
    0 : logging.WARNING,
    1 : logging.INFO,
    2 : logging.DEBUG,
}

console_level = level[0]
file_level = level[0]

stream_fmt = logging.Formatter(
    '%(name)-21s: %(message)s')
file_fmt = logging.Formatter(
    '%(asctime)s - %(name)-21s: %(levelname)-8s %(message)s')
log = logging.getLogger('pyflatpak')

console_log = logging.StreamHandler()
console_log.setFormatter(stream_fmt)
console_log.setLevel(console_level)

file_log = handlers.RotatingFileHandler(
    log_file_path, maxBytes=(1048576*5), backupCount=5)
file_log.setFormatter(file_fmt)
file_log.setLevel(file_level)

log.addHandler(console_log)
#log.addHandler(file_log)

if SYSTEMD_SUPPORT:
    journald_log = JournalHandler()
    journald_log.setLevel(file_level)
    journald_log.setFormatter(stream_fmt)
    log.addHandler(journald_log)

log.setLevel(logging.DEBUG)

remotes = Remotes.Remotes()

def validate(url):
    valid_fp_url = url.endswith('.flatpakrepo')
    return valid_fp_url
