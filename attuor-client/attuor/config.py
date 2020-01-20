# -*- coding: utf-8 -*-

# pylint: disable=invalid-name

"""
Attuor, observing your services
Copyright (C) 2020  Mark Schouten, Tuxis B.V. <mark@tuxis.nl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from os import path
import platform
from yaml import load, YAMLError

def LoadConfig():
    """Load the config from the Yaml-file."""
    cfg_files = ['/etc/tuxis-monitoring/client.yml',
                 'etc/client.yml', 'client.yml']

    for cfg_file in cfg_files:
        if path.isfile(cfg_file):
            real_cfg = cfg_file

    if not real_cfg:
        raise ValueError("No configuration file!")

    try:
        d = open(real_cfg, "rb")
    except Exception as e:
        raise e

    try:
        document = load(d.read())
    except YAMLError as exc:
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark # pylint: disable=no-member
            raise ValueError("YAML Error in configuration; Error on line %s, position %s)" \
                % (mark.line+1, mark.column+1))
    except:
        raise ValueError("YAML Error in configuration")

    return document

def DetectOS():
    """Detect the OS we are running on"""
    our_os = platform.system().lower()
    if our_os == "":
        our_os = 'unknown'

    return our_os
cfg = LoadConfig()
cfg['os'] = DetectOS()