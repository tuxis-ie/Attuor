# -*- coding: utf-8 -*-

# pylint: disable=invalid-name, wrong-import-position

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

from flask import Flask
from flask import g
from flask_httpauth import HTTPBasicAuth

# Initialize the app
app = Flask('tuxismonitoring_server', instance_relative_config=True)
# Load the config file
app.config.from_object('config')

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    """Verify the password"""
    if username:
        if config.GetClientPassword(username) == password:
            g.username = username
            return True

    return False

from attuor import config
from attuor import redis
from attuor import errors
from attuor import api
