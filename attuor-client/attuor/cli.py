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

import threading
import subprocess
import time
import sys
import json

from attuor import http
from attuor import config
from attuor import publish

# pylint: disable=too-many-instance-attributes
class Check:
    """Configure a check object. We allow this object to be exported as a
    dictionary, to ease the json-reply to the server"""
    def __init__(self, cname, cdata):
        self.name = cname
        self.command = cdata['command']
        self.interval = cdata['interval']
        self.occurences = cdata['occurences']
        self.ttl = cdata['ttl']
        self.status = None
        self.duration = None
        self.executed = None
        self.issued = None
        self.output = None

    def ret(self):
        """Return this object as a dictionary"""
        ret = {}
        for dk, dv in vars(self).items():
            ret[dk] = dv
        return ret

    def __str__(self):
        return self.name

def Publish():
    """This thread always keeps running, ready to publish results"""
    pc = http.HTTPClient(config.cfg)
    while True:
        item = publish.pq.get()
        for t in item:
            item[t]['issued'] = time.time()
        pc.publish(json.dumps(item))
        publish.pq.task_done()

def Execute(test):
    """Execute a check, and push the results in the publish queue"""
    timer = time.time()
    p = subprocess.run(test.command.split(' '), capture_output=True)
    done = time.time()
    ret = test.ret()
    ret['output'] = p.stdout.strip().decode("utf-8")
    ret['executed'] = timer
    ret['duration'] = done-timer
    ret['status'] = p.returncode
    publish.pq.put({str(test): ret})

def CheckThread(check):
    """For each check, execute a check-thread. Afterwards, sleep the configured interval"""
    while True:
        # Create an execution thread
        et = threading.Thread(target=Execute, args=(check,), name=str(check))
        et.start()
        et.join()
        time.sleep(check.interval)

def main():
    """The main thread"""
    c = http.HTTPClient(config.cfg)
    settings = c.get_settings()

    checks = dict()
    # For each subscription, fetch the checks
    for s in settings['subscriptions']:
        for check in c.get_subscription(s)['checks']:
            for cname, cdata in check.items():
                checks[cname] = Check(cname, cdata)

    try:
        threads = []
        # Setup Publishing thread
        pt = threading.Thread(target=Publish, name="Publish")
        pt.daemon = True
        pt.start()
        threads.append(pt)

        # For each check, start a main thread
        for check in checks:
            tt = threading.Thread(target=CheckThread, args=(checks[check],), name=check)
            tt.daemon = True
            tt.start()
            threads.append(tt)

        for t in threads:
            t.join()

    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
