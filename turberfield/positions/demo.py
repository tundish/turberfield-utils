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

Item = namedtuple("Item", ["pos", "class_"])

class Simulation:

    posns = OrderedDict([
        ("nw", point(160, 100, 0)),
        ("ne", point(484, 106, 0)),
        ("se", point(478, 386, 0)),
        ("sw", point(160, 386, 0)),
    ])

    def __init__(self, args, debug=False):
        self.args = args
        self.debug = debug
        self.items = [
            Item((pos[0], pos[1]), "actor")
            for pos in Simulation.posns.values()]

    def positions(self):
        accns = itertools.repeat(Dl("-9.806"))
        x = int(50 + 4 * time.time() % 200)
        items = self.items + [
            Item((x, 80), "platform"),
            Item((x, 120), "actor"),
        ]
        return {
            "info": {
                "args": vars(self.args),
                "debug": self.debug,
                "interval": 200,
                "time": "{:.1f}".format(time.time()),
                "title": "Turberfield positions {}".format(__version__),
                "version": __version__
            },
            "items": [i._asdict() for i in items],
            
        }
