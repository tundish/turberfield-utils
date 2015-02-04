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
from functools import singledispatch
import time

from turberfield.positions import __version__
from turberfield.positions.travel import Impulse

__doc__ = """
Machina places an actor on a stage.
"""

Fixed = namedtuple("Fixed", ["posn", "reach"])
Mobile = namedtuple("Mobile", ["motion", "reach"])
Page = namedtuple("Page", ["info", "nav", "items", "options"])
Tick = namedtuple("Tick", ["start", "stop", "step", "ts"])


class Borg:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class Props(Borg):
    """
    TODO: Move a base class to turberfield.common.inventory
    """ 

    def __init__(self):
        super().__init__()
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

class Provider:

    Attribute = namedtuple("Attribute", ["name"])
    JSON = namedtuple("JSON", ["name"])
    RSON = namedtuple("RSON", ["name"])
    HATEOAS = namedtuple("HATEOAS", ["name"])

    @property
    def services(self):
        raise NotImplementedError

    @property
    def template(self):
        return {
            "info": {
                "interval": 800,
                "title": self.__class__.__name__,
                "version": __version__
            },
            "nav": [],
            "items": [],
            "options": [],
        }

    def provide(self, service, data):
        if isinstance(service, Provider.Attribute):
            setattr(self, service.name, data[service.name])

        #with endpoint(node, parent=options.output) as output:
        #    json.dump(
        #        page, output,
        #        cls=TypesEncoder,
        #        indent=4
        #    )

class Shifter(Borg, Provider):

    @staticmethod
    def queue(loop=None):
        return asyncio.Queue(loop=loop)

    @staticmethod
    def movement(theatre, start, ts):
        infinity = decimal.Decimal("Infinity")
        for stage, job in theatre.items():
            if isinstance(job, Fixed):
                imp = Impulse(start, 0, infinity, job.posn)
                yield (stage, imp)
            elif isinstance(job, Mobile):
                if ts == start:
                    job.motion.send(None)
                imp = job.motion.send(ts)
                if imp is not None:
                    yield (stage, imp)

    @property
    def services(self):
        return [
            Provider.Attribute("tick"),
            Provider.Attribute("page"),
        ]

    def __init__(self, theatre, props):
        super().__init__()
        self.theatre = theatre
        self.props = props

    @asyncio.coroutine
    def __call__(self, start, stop, step):
        ts = start
        while ts < stop:
            now = time.time()
            collisions = defaultdict(set)
            page = self.template
            for stage, push in Shifter.movement(
                self.theatre, start, ts
            ):
                page["items"].append({
                    "uuid": stage.uuid,
                    "label": stage.label,
                    "class_": stage.class_,
                    "pos": push.pos[0:2],
                })
                gaps = [
                    (other, (push.pos - fix.posn).magnitude, fix.reach)
                    for other, fix in self.theatre.items()
                    if isinstance(fix, Fixed)]
            #gaps = [
            #    (obj, (push.pos - pos).magnitude, rad)
            #    for obj, pos, rad in Simulation.static]
            #[collisions[obj].add(item) for obj, gap, rad in gaps
            # if gap < rad]

            #page["options"].extend([{
            #    "label": obj.label,
            #    "value": str(hits)
            #} for obj, hits in collisions.items() for h in hits])

            tick = Tick(start, stop, step, ts)
            for i in self.services:
                self.provide(i, locals())
            #self.ticks.send(tick) # Game clock
            ts += step
            yield from asyncio.sleep(step)

        return tick
