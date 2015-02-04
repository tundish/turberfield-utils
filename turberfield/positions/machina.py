#!/usr/bin/env python3
# encoding: UTF-8

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

import asyncio
from collections import Counter
from collections import defaultdict
from collections import namedtuple
import decimal
import time

from turberfield.positions.travel import Impulse

__doc__ = """
Machina places an actor on a stage.
"""

Fixed = namedtuple("Fixed", ["posn", "reach"])
Mobile = namedtuple("Mobile", ["motion", "reach"])
Page = namedtuple("Page", ["info", "nav", "items", "options"])


class Props:
    """
    TODO: Move a base class to turberfield.common.inventory
    """ 

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
        if not hasattr(self, "pockets"):
            self.places = defaultdict(list)
            self.pockets = defaultdict(Counter)

    def _clear(self):
        try:
            del self.places
        except AttributeError:
            pass

        try:
            del self.pockets
        except AttributeError:
            pass

class Shifter:

    @staticmethod
    def queue(loop=None):
        return asyncio.Queue(loop=loop)

    @staticmethod
    def movement(ops, start, ts):
        infinity = decimal.Decimal("Infinity")
        for stage, job in ops.items():
            if isinstance(job, Fixed):
                imp = Impulse(start, 0, infinity, job.posn)
                yield (stage, imp)
            elif isinstance(job, Mobile):
                if ts == start:
                    job.motion.send(None)
                imp = job.motion.send(ts)
                if imp is not None:
                    yield (stage, imp)

    def __init__(self, theatre, props):
        self.theatre = theatre
        self.props = props

    @asyncio.coroutine
    def __call__(self, start, stop, step):
        ts = start
        while ts < stop:
            now = time.time()
            for stage, push in Shifter.movement(
                self.theatre, start, ts
            ):
                pass
            #self.ticks.send(ts) # Game clock
            ts += step
            yield from asyncio.sleep(step)

        return "Hi"
