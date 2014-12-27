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

from collections import namedtuple
from collections import OrderedDict
from decimal import Decimal as Dl
import itertools
import time

from turberfield.positions import __version__
from turberfield.positions.homogeneous import point
from turberfield.positions.homogeneous import vector
from turberfield.positions.travel import Impulse
from turberfield.positions.travel import trajectory

Item = namedtuple("Item", ["pos", "class_"])


class Simulation:

    posns = OrderedDict([
        ("nw", point(160, 100, 0)),
        ("ne", point(484, 106, 0)),
        ("se", point(478, 386, 0)),
        ("sw", point(160, 386, 0)),
    ])

    def __init__(self, args=None, debug=False):
        self.args = vars(args) if args is not None else None
        self.debug = debug
        self.items = [
            Item((pos[0], pos[1]), "actor")
            for pos in Simulation.posns.values()]
        self.path = itertools.cycle(Simulation.posns.values())
        self.procs = OrderedDict([
            (trajectory(), (None, None))
        ])

    def positions(self, at=None):
        dt = Dl("0.5")
        accn = vector(0, 0, 0),
        items = []
        for proc in self.procs:
            n, val = self.procs[proc]
            if n is None:
                proc.send(None)
                self.procs[proc] = (0, val)
                continue
            elif n == 0:
                self.procs[proc] = (
                    n + 1,
                    proc.send(Impulse(Dl(0), Dl("0.5"),
                    accn,
                    Simulation.posns["nw"]))
                )
            elif n == 1:
                self.procs[proc] = (
                    n + 1,
                    proc.send(Impulse(Dl("0.5"), Dl(1),
                    accn,
                    (Simulation.posns["ne"]
                    - Simulation.posns["nw"]) / Dl("2.0")))
                )
            else:
                self.procs[proc] = (
                    n + 1,
                    proc.send(Impulse(val.tEnd, val.tEnd + dt, accn, val.pos)))


            print(self.procs[proc])
            if val is not None:
                items.append(
                    Item(
                        (int(val.pos[0]) % 800, int(val.pos[1]) % 600),
                        "platform"
                    )
                )
        return items

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
                "args": self.args,
                "debug": self.debug,
                "interval": 200,
                "time": "{:.1f}".format(now),
                "title": "Turberfield positions {}".format(__version__),
                "version": __version__
            },
            "items": [i._asdict() for i in items],
            
        }
