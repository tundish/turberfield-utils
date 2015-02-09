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

        # Plug in a StringIO object to the positions endpoint
        services = Shifter.options()
        hateoas = services["positions"]
        class_._output = StringIO()
        services["positions"] = (
            hateoas._replace(dst=class_._output)
        )
        class_._shifter = Shifter(
            class_.theatre, class_.props, **services
        )

        class_.tick = Tick(0, 0.3, 0.1, None)
        warnings.simplefilter("ignore")

    def test_has_provide(self):
        p = Provider()
        self.assertIsInstance(ShifterTests._shifter, Provider)
        self.assertTrue(hasattr(ShifterTests._shifter, "provide"))

    def test_has_services(self):
        self.assertEqual(3, len(ShifterTests._shifter._services))

    def test_first_instantiation_defines_services(self):
        self.assertIsInstance(Shifter.options, Callable)
        self.assertIsInstance(
            ShifterTests._shifter._services, Mapping)
        self.assertIsInstance(
            ShifterTests._shifter._services["positions"].dst, StringIO)

        self.assertIsNot(Shifter.public, None)

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            self.assertRaises(
                UserWarning,
                Shifter,
                ShifterTests.theatre, ShifterTests.props,
                **Shifter.options()
            )

    def test_tick_attribute_service(self):
        task = asyncio.Task(ShifterTests._shifter(0, 0.3, 0.1))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(task)
        self.tick = task.result()
        self.assertAlmostEqual(
            self.tick.stop,
            self.tick.ts + self.tick.step, places=10
        )
        self.assertEqual(self.tick, Shifter.public.tick)

    def test_page_attribute_service(self):
        task = asyncio.Task(ShifterTests._shifter(0, 0.3, 0.1))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(task)
        self.tick = task.result()
        self.assertIn("info", vars(Shifter.public.page))
        self.assertIn("nav", vars(Shifter.public.page))
        self.assertIn("items", vars(Shifter.public.page))
        self.assertIn("options", vars(Shifter.public.page))

    def test_hateoas_attribute_service(self):
        task = asyncio.Task(ShifterTests._shifter(0, 0.3, 0.1))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(task)
        self.tick = task.result()
        history = ShifterTests._output.getvalue()
        data = "{" + history.rpartition("}{")[-1]
        output = json.loads(data)
        self.assertIn("info", output)
        self.assertIn("nav", output)
        self.assertIn("items", output)
        self.assertIn("options", output)

    def test_first_collision(self):
        task = asyncio.Task(ShifterTests._shifter(0, 0.3, 0.1))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(task)
        self.tick = task.result()
