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
import itertools
import json
import logging
from logging.handlers import WatchedFileHandler
import re
import tempfile
import time
import os.path
import uuid

from turberfield.positions import __version__
from turberfield.positions.homogeneous import point
from turberfield.positions.travel import steadypace
from turberfield.positions.travel import trajectory


Item = namedtuple("Item", ["pos", "class_"])
Actor = namedtuple("Actor", ["uuid", "label", "class_"])
Travel = namedtuple("Travel", ["path", "step", "proc"])


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
        itertools.repeat(Dl(6))
        ),
    ]

    static = [
        (Actor(uuid.uuid4().hex, "A", "zone"), point(285, 60, 0)),
        (Actor(uuid.uuid4().hex, "B", "zone"), point(530, 245, 0)),
        (Actor(uuid.uuid4().hex, "C", "zone"), point(120, 245, 0)),
    ]

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
    options=argparse.Namespace(
        output=".", log_level=logging.INFO, log_path=None
    ),
    node="demo.json",
    start=0, stop=Dl("Infinity"),
    dt=1
    ):
    log = logging.getLogger("turberfield.demo.run")
    log.setLevel(options.log_level)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-7s %(name)s|%(message)s")
    ch = logging.StreamHandler()

    if options.log_path is None:
        ch.setLevel(options.log_level)
    else:
        fh = WatchedFileHandler(options.log_path)
        fh.setLevel(options.log_level)
        fh.setFormatter(formatter)
        log.addHandler(fh)
        ch.setLevel(logging.WARNING)

    ch.setFormatter(formatter)
    log.addHandler(ch)

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
                "items": [{
                    "uuid": obj.uuid,
                    "label": obj.label,
                    "class_": obj.class_,
                    "pos": pos[0:2],
                } for obj, pos in Simulation.static],
                "options": []
            }
            for item, imp in movement(ops, start, ts):
                page["items"].append({
                    "uuid": item.uuid,
                    "label": item.label,
                    "class_": item.class_,
                    "pos": imp.pos[0:2],
                })
                page["options"].extend([{
                    "label": obj.label,
                    "value": (imp.pos - pos).magnitude
                } for obj, pos in Simulation.static])
            json.dump(
                page, output,
                cls=TypesEncoder,
                indent=4
            )
            # for colln in collisions:
            #     yield from transfer queue
        ts += dt
        time.sleep(dt)
    return stop
