#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.

import argparse
from collections import namedtuple
from collections import OrderedDict
import contextlib
from decimal import Decimal as Dl
import glob
import itertools
import json
import logging
import re
import stat
import tempfile
import time
import operator
import os.path
import uuid

from turberfield.positions import __version__
from turberfield.positions.homogeneous import point
from turberfield.positions.homogeneous import vector
from turberfield.positions.travel import Impulse
from turberfield.positions.travel import steadypace
from turberfield.positions.travel import trajectory

import turberfield.web.main

Item = namedtuple("Item", ["pos", "class_"])
Actor = namedtuple("Actor", ["uuid", "label", "class_"])
Travel = namedtuple("Travel", ["path", "step", "proc"])

class TypesEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Dl):
            return str(obj)
        if isinstance(obj, type(re.compile(""))):
            return obj.pattern

        try:
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        except AttributeError:
            return json.JSONEncoder.default(self, obj)

# TODO: turberfield.common
@contextlib.contextmanager
def endpoint(node, parent=None, suffix=".json"):
    if isinstance(node, str):
        fD, fN = tempfile.mkstemp(suffix=suffix, dir=parent)
        try:
            rv = open(fN, 'w')
            yield rv
        except Exception as e:
            raise e
        rv.close()
        os.close(fD)
        os.replace(fN, os.path.join(parent, node))
    else:
        yield node

def movement(ops, start, ts):
    for obj, op in ops.items():
        if ts == start:
            op.send(None)
        imp = op.send(ts)
        if imp is not None:
            yield (obj, imp)

def run(
    options=argparse.Namespace(output="."),
    node="demo.json",
    start=0, stop=Dl("Infinity"),
    dt=1
    ):
    log = logging.getLogger("turberfield.demo.run")
    ts = start
    ops = OrderedDict(
        [(obj, steadypace(trajectory(), routing, timing))
        for obj, routing, timing in Simulation.patterns])
    
    while ts < stop:
        now = time.time()
        with endpoint(node, parent=options.output) as output:
            page = {
                "info": {
                    "args": vars(options),
                    "interval": 800,
                    "time": "{:.1f}".format(now),
                    "title": "Turberfield positions {}".format(__version__),
                    "version": __version__
                },
                "items": [],
            }
            for obj, imp in movement(ops, start, ts):
                page["items"].append({
                    "uuid": obj.uuid,
                    "label": obj.label,
                    "class_": obj.class_,
                    "pos": imp.pos[0:2],
                })
            json.dump(
                page, output,
                cls=TypesEncoder,
                indent=4
            )
        ts += dt
        time.sleep(dt)
    return stop

class Simulation:

    path = "demo.json"
    posns = OrderedDict([
        ("nw", point(160, 100, 0)),
        ("ne", point(484, 106, 0)),
        ("se", point(478, 386, 0)),
        ("sw", point(160, 386, 0)),
    ])

    patterns = [
        (Actor(uuid.uuid4().hex, "Bus", "platform"),
         itertools.cycle(
            zip(posns.values(),
            list(posns.values())[1:] + [posns["nw"]])
         ),
        itertools.repeat(Dl(30))
        ),
    ]

    def hateoas(self):
        #x = int(50 + 4 * time.time() % 200)
        #items = self.items + [
        #    Item((x, 80), "platform"),
        #    Item((x, 120), "actor"),
        #]
        now = time.time()
        items = self.positions(at=now)
        return {
            "info": {
                "args": vars(self.args),
                "debug": self.debug,
                "interval": 200,
                "time": "{:.1f}".format(now),
                "title": "Turberfield positions {}".format(__version__),
                "version": __version__
            },
            "items": [i._asdict() for i in items],
            
        }
