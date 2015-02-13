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
            ("page", Provider.Attribute("page")),
            ("positions", Provider.HATEOAS(
                "positions",
                "page",
                os.path.join(parent, "positions.json"))
            ),
        ])

    def __init__(self, theatre, props, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theatre = theatre
        self.props = props

    @asyncio.coroutine
    def __call__(self, start, stop, step):
        ts = start
        while stop > ts:
            collisions = defaultdict(set)
            page = self.page
            page.info["ts"] = time.time()
            for stage, push in Shifter.movement(
                self.theatre, start, ts
            ):
                page.items.append({
                    "uuid": stage.uuid,
                    "label": stage.label,
                    "class_": stage.class_,
                    "pos": push.pos[0:2],
                })
                gaps = [
                    (other, (push.pos - fix.posn).magnitude, fix.reach)
                    for other, fix in self.theatre.items()
                    if isinstance(fix, Fixed) and stage is not other]
                [collisions[other].add(stage)
                 for other, gap, rad in gaps if gap < rad]

            # TODO: collisions are Real Time Events (RTEs)
            # TODO: store and send deadline ts for each collision
            page.options.extend([{
                "label": obj.label,
                "value": str(hits)
            } for obj, hits in collisions.items()])

            tick = Tick(start, stop, step, ts)
            self.provide(locals())
            # TODO: calculate sum wait time dispatched collisions
            # TODO: sleep for that time.

            ts += step
            yield from asyncio.sleep(max(step, 0.2))

        return tick
