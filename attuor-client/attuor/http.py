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

import http.client
import urllib.parse
from base64 import b64encode
from json import loads

class HTTPClient():
    """Create a HTTPClient object"""
    def __init__(self, cfg):
        self.master = urllib.parse.urlparse(cfg['master'])
        self.username = cfg['username']
        self.password = cfg['password']
        self.headers = dict()
        self.conn = None

    def auth(self):
        """Create the HTTP Authentication header"""
        authstr = b64encode(b"%s:%s" % (
            bytes(self.username, encoding="ascii"),
            bytes(self.password, encoding="ascii"))).decode("ascii")
        self.headers['Authorization'] = 'Basic %s' % (authstr)

    def publish(self, data):
        """POST the results to the master"""
        self.build_client()
        print(data)
        self.conn.request('POST', '/publish/', data, headers=self.headers)
        return self.process_response()

    def get_settings(self):
        """Download all the settings"""
        self.build_client()
        self.conn.request('GET', '/settings', headers=self.headers)
        return self.process_response()

    def get_subscription(self, subscription, data):
        """Get all info for a subscription"""
        self.build_client()
        self.conn.request('POST', '/subscription/%s' % (subscription), data, headers=self.headers)
        return self.process_response()

    def process_response(self):
        """Parse the response from the server, which is always JSON"""
        response = self.conn.getresponse()
        data = response.read()
        self.conn.close()
        return loads(data)

    def build_client(self):
        """Prepare the HTTP Client"""
        m = self.master

        self.headers["Content-type"] = "application/json"
        self.auth()

        if self.conn:
            return

        if m.scheme == 'http':
            self.conn = http.client.HTTPConnection(m.netloc)
        elif m.scheme == 'https':
            self.conn = http.client.HTTPSConnection(m.netloc)
