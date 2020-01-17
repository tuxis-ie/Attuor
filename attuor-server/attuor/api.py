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

from flask import request, jsonify
from attuor import app
from attuor import auth
from attuor import version
from attuor import config
from attuor import publish

@app.route('/', defaults={'path': ''})
@app.route('/', methods=['GET'])
@auth.login_required
def req_root():
    """This path currently only identifies the server and the version running on the
    server. Also, a minimal required version of the client may be sent. If a
    client has a too low version, it may publish keepalives with an "I'm too old"
    message."""
    return jsonify({
        "name": version.NAME,
        "version": version.VERSION,
        "hostname": version.HOSTNAME,
        "min_required": version.MIN_REQ_CLI
    })

@app.route('/settings')
@app.route('/settings', methods=['GET'])
@auth.login_required
def req_settings():
    """After authenticating, the client will request it's settings. These settings
    include the nodename of the client (auth username), the publishing endpoints,
    and the channels a client should subscribe to. Also, specific checks may be
    sent. If a client is too old, only the publishing endpoint are used. This
    value always works."""
    username = auth.username()
    subscriptions = config.GetClientSubscriptions(username)
    publishnodes = config.GetPublisherConfig(username)

    return jsonify(
        {
            "nodename": username,
            "publishnodes": publishnodes,
            "subscriptions": subscriptions
        })

@app.route('/subscription/')
@app.route('/subscription/<subscription>', methods=['GET'])
@auth.login_required
def req_subscription(subscription):
    """After receiving it's settings, the client will request the info about the
    given subscriptions. This will result in the client having all the checks he
    needs to run, and the publishing data it needs."""
    checks = config.GetSubscriptionChecks(subscription)
    return jsonify(
        {
            "subscription": subscription,
            "checks": checks
        })


@app.route('/publish/', methods=['POST'])
@auth.login_required
def req_publish():
    """After the client runs a check, it will publish the results here."""
    return jsonify(publish.publish(request.json))
