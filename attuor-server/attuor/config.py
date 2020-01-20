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

# Read the configuration for a client from a yaml-file. We try to cache the
# config for a minute or so, to prevent a lot of disk-io.

from yaml import safe_load, YAMLError
from attuor import app
from attuor import redis

def ReloadConfig():
    """ Load the config from the Yaml-file."""
    cfg = app.config['CLIENTCONFIG']

    try:
        document = redis.GetFullConfig()
    except ValueError:
        try:
            f = open(cfg)
        except Exception as e:
            raise e

        try:
            document = safe_load(f.read())
        except YAMLError as exc:
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark # pylint: disable=no-member
                raise ValueError("YAML Error in configuration; Error on line %s, position %s)" \
                    % (mark.line+1, mark.column+1))
        except:
            raise ValueError("YAML Error in configuration")

        redis.StoreFullConfig(document)

    return document



def GetClientConfig(client):
    """Load the config for a specific client"""
    # First, try to load the config from redis
    try:
        cfg = redis.GetClientConfig(client)
    # We return ValueError if there is nothing in redis
    except ValueError:
        fullconfig = ReloadConfig()
        cfg = fullconfig['clients'][client]
        redis.StoreClientConfig(client, cfg)

    return cfg

def GetClientSubscriptions(client):
    """First, try to load the config from redis"""
    cfg = GetClientConfig(client)

    return cfg['subscriptions']

def GetClientPassword(client):
    """Load the client password"""
    cfg = GetClientConfig(client)

    return cfg['password']

def GetPublisherConfig(client='default'):
    """Get the publishers for this client. If we have no specific publishers,
    return the default publishers"""
    try:
        cfg = redis.GetPublisherConfig(client)
    except ValueError:
        fullconfig = GetClientConfig(client)

        if 'publishers' in fullconfig:
            cfg = fullconfig['publishers']
        else:
            fullconfig = ReloadConfig()
            cfg = fullconfig['defaults']['publishers']

        redis.StorePublisherConfig(client, cfg)

    return cfg


def GetCheckDefaults():
    """Load the default config for all checks."""
    fullconfig = ReloadConfig()
    return fullconfig['defaults']['check']


def GetSubscriptionChecks(subscription, clientos):
    """Load the config for a subscription"""
    # First, try to load the config from redis

    if not clientos:
        clientos = 'any'

    cache_name = '%s_%s' % (subscription, clientos)
    try:
        cfg = redis.GetSubscriptionChecks(cache_name)
    # We return ValueError if there is nothing in redis
    except ValueError:
        checks = []
        fullconfig = ReloadConfig()
        defaults = GetCheckDefaults()
        for n, c in fullconfig['checks'].items():
            if subscription in c['subscribers']:
                for d in defaults:
                    if d not in c:
                        c[d] = defaults[d]
                if clientos in c['os'] or 'any' in c['os']:
                    checks.append({n: c})

        redis.StoreSubscriptionChecks(cache_name, checks)
        cfg = checks

    return cfg
