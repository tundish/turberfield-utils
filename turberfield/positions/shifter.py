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
from collections import defaultdict
from collections import OrderedDict
import decimal
from operator import attrgetter
import os.path
import time
import warnings


from turberfield.positions.homogeneous import vector
from turberfield.positions.machina import Fixed
from turberfield.positions.machina import Mobile
from turberfield.positions.machina import Provider
from turberfield.positions.machina import Tick
from turberfield.positions.travel import Impulse


__doc__ = """
Shifter moves stages around
"""

class Shifter(Provider):

    @staticmethod
    def collision(theatre, pending=None):
        pending = defaultdict(int) if pending is None else pending
        while True:
            stage, impulse, expires = (yield pending)
            gaps = [
                (other, (impulse.pos - fix.posn).magnitude, fix.reach)
                for other, fix in theatre.items()
                if isinstance(fix, Fixed) and stage is not other]

            for other, gap, rad in gaps:
                if gap < rad:
                    pending[frozenset((stage, other))] = expires

    @staticmethod
    def movement(theatre, start, ts):
        infinity = decimal.Decimal("Infinity")
        for stage, job in theatre.items():
            if isinstance(job, Fixed):
                imp = Impulse(
                    start, infinity, vector(0, 0, 0), job.posn
                )
                yield (stage, imp)
            elif isinstance(job, Mobile):
                if ts == start:
                    job.motion.send(None)
                imp = job.motion.send(ts)
                if imp is not None:
                    yield (stage, imp)

    @staticmethod
    def options(
        parent=os.path.expanduser(os.path.join("~", ".turberfield"))
    ):
        return OrderedDict([
            ("tick", Provider.Attribute("tick")),
            ("collisions", Provider.Attribute("collisions")),
            ("movement", Provider.Attribute("movement")),
            ("bridging", Provider.HATEOAS(
                "bridging",
                "collisions",
                os.path.join(parent, "bridging.json"))
            ),
            ("positions", Provider.HATEOAS(
                "positions",
                "movement",
                os.path.join(parent, "positions.json"))
            ),
        ])

    def __init__(self, theatre, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theatre = theatre
        self._events = Shifter.collision(theatre)

    @asyncio.coroutine
    def __call__(self, start, stop, step, loop=None):
        ts = start
        self._events.send(None)
        while stop > ts:
            t = time.time()
            collisions = self.page
            collisions.info["ts"] = t
            movement = self.page
            movement.info["ts"] = t

            for stage, push in Shifter.movement(
                self.theatre, start, ts
            ):
                movement.items.append({
                    "uuid": stage.uuid,
                    "label": stage.label,
                    "class_": stage.class_,
                    "pos": push.pos[0:2],
                })
                bridging = self._events.send((stage, push, ts + 5))

            # TODO: create from a second endpoint: "rte"
            # provided by a TheatreCompany(Provider)
            # Web tier consumes, filters, adds to synchronous items.
            collisions.items[:] = [{
                "label": "{0.label} - {1.label}".format(a, b),
                "deadline": expires - ts
            } for (a, b), expires in bridging.items()]

            tick = Tick(start, stop, step, ts)
            self.provide(locals())

            ts += step
            yield from asyncio.sleep(max(step, 0.2), loop=loop)

        return tick
