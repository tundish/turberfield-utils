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
        self.proc = trajectory()
        self.state = (None, None)

    def positions(self, at=None):
        dt = Dl("0.2")
        accn = vector(0, 0, 0)
        items = []
        n, val = self.state
        if n is None:
            val = self.proc.send(None)
            self.state = (0, val)
        elif n == 0:
            val = self.proc.send(Impulse(
                Dl(0), Dl("0.2"),
                accn, Simulation.posns["nw"]
            ))
            self.state = (n + 1, val)
        elif n == 1:
            val = self.proc.send(Impulse(
                Dl("0.2"), Dl("0.4"),
                accn,
                Simulation.posns["nw"] +
                (Simulation.posns["ne"]
                - Simulation.posns["nw"]) / Dl(20)
                ))
            self.state = (n + 1, val)
        else:
            val = self.proc.send(Impulse(
                val.tEnd, val.tEnd + dt, accn, val.pos)
            )
            self.state = (n + 1, val)

        try:
            items.append(
                Item(
                    (int(val.pos[0]) % 800, int(val.pos[1]) % 600),
                    "platform"
                )
            )
        except AttributeError:
            pass

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
