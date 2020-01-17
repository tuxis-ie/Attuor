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

import json
import redis
from flask import g
from attuor import app

# This file handles all the Redis interaction

@app.before_request
def ConfigConnect():
    """Set up a connection to the configuration caching database"""
    if 'config_db' not in g:
        g.config_db = redis.StrictRedis(host=app.config['REDIS_HOST'],
                                        port=app.config['REDIS_PORT'],
                                        db=app.config['REDIS_CFG_DB'])

@app.before_request
def PublishConnect():
    """Set up a connection for publishing"""
    if 'publish_db' not in g:
        g.publish_db = redis.StrictRedis(host=app.config['REDIS_HOST'],
                                         port=app.config['REDIS_PORT'])

def PublishCheck(data):
    """Publish the data"""
    g.publish_db.publish('checks', json.dumps(data))

def StoreConfig(pfx, n, v):
    """Store stuff in Redis, with the configured TTL"""
    ttl = app.config['CFG_CACHE_TTL']
    g.config_db.setex('%s_%s' % (pfx, n), ttl, json.dumps(v))

def StoreClientConfig(client, cfg):
    """Store through StoreConfig"""
    StoreConfig('cli', client, cfg)

def StoreSubscriptionChecks(subscription, cfg):
    """Store through StoreConfig"""
    StoreConfig('sub', subscription, cfg)

def StorePublisherConfig(client, cfg):
    """Store through StoreConfig"""
    StoreConfig('pub', client, cfg)

def StoreFullConfig(cfg):
    """Store through StoreConfig"""
    StoreConfig('full', 'full', cfg)

def GetConfig(pfx, n):
    """Get configuration from Redis"""
    cfg = g.config_db.get('%s_%s' % (pfx, n))
    if not cfg:
        raise ValueError

    return json.loads(cfg)

def GetSubscriptionChecks(subscription):
    """Get configuration though GetConfig"""
    return GetConfig('sub', subscription)

def GetClientConfig(client):
    """Get configuration though GetConfig"""
    return GetConfig('cli', client)

def GetPublisherConfig(client):
    """Get configuration though GetConfig"""
    return GetConfig('pub', client)

def GetFullConfig():
    """Get configuration though GetConfig"""
    return GetConfig('full', 'full')
