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

from flask import jsonify
from attuor import app

# pylint: disable=pointless-string-statement
"""These are all the HTTP errors we can return"""

@app.errorhandler(500)
def internal_error(error):
    """Internal Server Error"""
    return jsonify({"error": "Internal server error: %s" % (error)}), 500

@app.errorhandler(404)
def page_not_found(error):
    """Path not found"""
    return jsonify({"error": "Path not found: %s" % (error)}), 404

@app.errorhandler(401)
def auth_failed(error):
    """Authentication required"""
    return jsonify({"error": "Authentication required: %s" % (error)}), 401
