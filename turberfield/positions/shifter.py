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
import decimal
import time


from turberfield.positions.machina import Borg  # TODO: common
from turberfield.positions.machina import Fixed
from turberfield.positions.machina import Mobile
from turberfield.positions.machina import Provider
from turberfield.positions.machina import Tick
from turberfield.positions.travel import Impulse


__doc__ = """
Shifter moves stages around
"""

class Shifter(Provider, Borg):

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

    @staticmethod
    def services():
        return [
            Provider.Attribute("tick"),
            Provider.Attribute("page"),
            Provider.HATEOAS("positions", "page", "positions.json"),
        ]

    def __init__(self, theatre, props, **kwargs):
        Borg.__init__(self)
        self.services = kwargs.pop("services", Shifter.services())
        super().__init__(**kwargs)
        self.theatre = theatre
        self.props = props

    @asyncio.coroutine
    def __call__(self, start, stop, step):
        ts = start
        while ts < stop:
            collisions = defaultdict(set)
            page = self.template
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
                    if isinstance(fix, Fixed)]
                [collisions[other].add(stage)
                 for other, gap, rad in gaps
                 if gap < rad]

            page.options.extend([{
                "label": obj.label,
                "value": str(hits)
            } for obj, hits in collisions.items() for h in hits])

            tick = Tick(start, stop, step, ts)
            for i in self.services:
                self.provide(i, locals())

            ts += step
            yield from asyncio.sleep(step)

        return tick
