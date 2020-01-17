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

from flask import g
from werkzeug.exceptions import InternalServerError
from attuor import redis

def publish(data):
    """Publish the data in Redis"""
    req_fields = [
        'command',
        'interval',
        'occurences',
        'ttl',
        'status',
        'duration',
        'executed',
        'issued',
        'output']

    for c in data:
        for f in req_fields:
            if not f in data[c]:
                raise InternalServerError(description={"error":"Missing required field %s" % (f)})
        if 'metrics' in data:
            publish_metrics(data['metrics'])

    data['nodename'] = g.username
    redis.PublishCheck(data)
    return {"result": "accepted"}

def publish_metrics(data):
    """This is useless, for now"""
    if data:
        return True

    return None
