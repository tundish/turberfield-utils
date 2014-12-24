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

from collections import deque
from collections import namedtuple
from collections import OrderedDict
from decimal import Decimal as Dl
import itertools
import time

from turberfield.positions import __version__
from turberfield.positions.homogeneous import point
from turberfield.positions.homogeneous import vector
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
        dt = Dl("0.5")
        vel = (Simulation.posns["ne"] - Simulation.posns["nw"]) / Dl("2.0")
        self.accns = deque([vector(0, 0, 0)])
        self.samples = deque([0, 0.2, 0.4])
        posns = deque([
            Simulation.posns["nw"],
            (Simulation.posns["nw"] + vel * dt
            + Dl("0.5") * self.accns[0] * dt * dt)
        ])
        self.proc = enumerate(
            trajectory(
                self.samples, posns=posns, accns=self.accns)
        )

    def positions(self):
        path = itertools.cycle(Simulation.posns.values())
        x = int(50 + 4 * time.time() % 200)
        items = self.items + [
            Item((x, 80), "platform"),
            Item((x, 120), "actor"),
        ]
        return {
            "info": {
                "args": self.args,
                "debug": self.debug,
                "interval": 200,
                "time": "{:.1f}".format(time.time()),
                "title": "Turberfield positions {}".format(__version__),
                "version": __version__
            },
            "items": [i._asdict() for i in items],
            
        }
