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

import argparse
import asyncio
from collections import OrderedDict
from collections.abc import Callable
from collections.abc import Mapping
from io import StringIO
import json
import unittest
import uuid
import warnings

from turberfield.positions.demo import Simulation
from turberfield.positions.machina import Fixed
from turberfield.positions.machina import Mobile
from turberfield.positions.machina import Props
from turberfield.positions.machina import Provider
from turberfield.positions.machina import Tick
from turberfield.positions.shifter import Shifter
from turberfield.positions.travel import steadypace
from turberfield.positions.travel import trajectory


# Prototyping
from collections import defaultdict

def collision(pending=None):
    pending = defaultdict(set) if pending is None else pending
    while True:
        ts, theatre = (yield pending)
        for stage, push in theatre.items():
            gaps = [
                (other, (push.pos - fix.posn).magnitude, fix.reach)
                for other, fix in theatre.items()
                if isinstance(fix, Fixed) and stage is not other]
            [collisions[other].add(stage)
             for other, gap, rad in gaps if gap < rad]


class ShifterTests(unittest.TestCase):

    def create_theatre():
        rv = OrderedDict([
                (stage, Mobile(
                    steadypace(trajectory(), routing, timing),
                    10)
                )
                for stage, routing, timing in Simulation.patterns])
        rv.update(
            OrderedDict([
                (stage, Fixed(posn, reach))
                for stage, posn, reach in Simulation.static]))
        return rv

        
    def setUp(self):
        class_ = self.__class__
        class_.props = Props()
        class_.theatre = ShifterTests.create_theatre()

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        warnings.simplefilter("ignore")

        # Plug in a StringIO object to the positions endpoint
        self._services = Shifter.options()
        class_._output = StringIO()
        self._services["positions"] = (
            self._services["positions"]._replace(dst=class_._output)
        )
        class_.tick = Tick(0, 0.3, 0.1, None)

    def test_has_provide(self):
        p = Provider()
        shifter = Shifter(
            self.theatre, self.props,
            loop=self.loop, **self._services
        )
        self.assertIsInstance(shifter, Provider)
        self.assertTrue(hasattr(shifter, "provide"))

    def test_has_services(self):
        shifter = Shifter(
            self.theatre, self.props,
            loop=self.loop, **self._services
        )
        self.assertEqual(3, len(shifter._services))

    def test_first_instantiation_defines_services(self):
        shifter = Shifter(
            self.theatre, self.props,
            loop=self.loop, **self._services
        )
        self.assertIsInstance(Shifter.options, Callable)
        self.assertIsInstance(
            shifter._services, Mapping)
        self.assertIsInstance(
            shifter._services["positions"].dst, StringIO)

        self.assertIsNot(Shifter.public, None)

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            self.assertRaises(
                UserWarning,
                Shifter,
                ShifterTests.theatre, ShifterTests.props,
                loop=self.loop,
                **Shifter.options()
            )

    def test_tick_attribute_service(self):
        shifter = Shifter(
            self.theatre, self.props,
            loop=self.loop, **self._services
        )
        task = asyncio.Task(
            shifter(0, 0.3, 0.1, loop=self.loop), loop=self.loop
        )

        self.loop.run_until_complete(task)
        self.tick = task.result()
        self.assertAlmostEqual(
            self.tick.stop,
            self.tick.ts + self.tick.step, places=10
        )
        self.assertEqual(self.tick, Shifter.public.tick)

    def test_page_attribute_service(self):
        shifter = Shifter(
            self.theatre, self.props,
            loop=self.loop, **self._services
        )
        task = asyncio.Task(
            shifter(0, 0.3, 0.1, loop=self.loop), loop=self.loop
        )

        self.loop.run_until_complete(task)
        self.tick = task.result()
        self.assertIn("info", vars(Shifter.public.page))
        self.assertIn("nav", vars(Shifter.public.page))
        self.assertIn("items", vars(Shifter.public.page))
        self.assertIn("options", vars(Shifter.public.page))

    def test_hateoas_attribute_service(self):
        shifter = Shifter(
            self.theatre, self.props,
            loop=self.loop, **self._services
        )
        task = asyncio.Task(
            shifter(0, 0.3, 0.1, loop=self.loop), loop=self.loop
        )

        self.loop.run_until_complete(task)
        self.tick = task.result()
        history = ShifterTests._output.getvalue()
        data = "{" + history.rpartition("}{")[-1]
        output = json.loads(data)
        self.assertIn("info", output)
        self.assertIn("nav", output)
        self.assertIn("items", output)
        self.assertIn("options", output)


class TaskTests(unittest.TestCase):

    def setUp(self):
        class_ = self.__class__
        class_.props = Props()
        class_.theatre = ShifterTests.create_theatre()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def test_tasks_for_queues(self):
        q = asyncio.Queue(loop=self.loop)
        shifter = Shifter(
            self.theatre, self.props, q, loop=self.loop
        )

        self.assertEqual(1, len(shifter.inputs))
        self.assertTrue(
            all(isinstance(i, asyncio.Queue) for i in shifter.inputs)
        )

        self.assertEqual(1, len(shifter._watchers))
        self.assertTrue(
            all(isinstance(i, asyncio.Task) for i in shifter._watchers)
        )

    def test_watcher_consumes_queues(self):

        @asyncio.coroutine
        def one_shot(q):
            # Collision id, actor, stage
            obj = (id(None), uuid.uuid4().hex, uuid.uuid4().hex)
            yield from q.put(obj)
            yield from q.put(None)

        q = asyncio.Queue(loop=self.loop)
        shifter = Shifter(
            self.theatre, self.props, q, loop=self.loop
        )

        listener = shifter._watchers[0]
        self.assertIsInstance(listener, asyncio.Task)
        self.assertIs(shifter.inputs[0], q)
        self.loop.run_until_complete(asyncio.wait(
            [one_shot(shifter.inputs[0]), listener],
            loop=self.loop,
            timeout=1)
        )

    def test_shifter_collision(self):
        theatre = self.theatre.copy()
        stage, job = list(theatre.items())[-1]
        theatre[stage._replace(uuid=uuid.uuid4().hex, label="D")] = job

        collider = collision()
        collider.send(None)
        ts = 0
        collisions = list(collider.send((ts, theatre)))
        print(collisions)
        #self.loop.run_until_complete(asyncio.wait(
        #    [one_shot(shifter.inputs[0]), listener],
        #    loop=self.loop,
        #    timeout=1)
        #)
