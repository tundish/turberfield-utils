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
from turberfield.positions.shifter import Shifter
from turberfield.positions.travel import steadypace
from turberfield.positions.travel import trajectory


class ShifterTests(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter("error")
        props = Props()
        theatre = OrderedDict([
                (stage, Mobile(
                    steadypace(trajectory(), routing, timing),
                    10)
                )
                for stage, routing, timing in Simulation.patterns])
        theatre.update(
            OrderedDict([
                (stage, Fixed(posn, reach))
                for stage, posn, reach in Simulation.static]))

        if not hasattr(ShifterTests, "_shifter"):
            services = Shifter.options()
            hateoas = services["positions"]
            services["positions"] = (
                hateoas._replace(dst=StringIO())
            )
            ShifterTests._shifter = Shifter(
                theatre, props, **services)

    def test_has_provide(self):
        p = Provider()
        shifter = Shifter()
        self.assertIsInstance(shifter, Provider)
        self.assertTrue(hasattr(shifter, "provide"))

    def test_has_services(self):
        p = Provider()
        shifter = Shifter()
        self.assertIsInstance(shifter, Provider)
        self.assertEqual(3, len(shifter._services))

    def test_first_instantiation_defines_services(self):
        p = Provider()
        self.assertIsInstance(Shifter.options, Callable)
        self.assertIsInstance(
            ShifterTests._shifter._services, Mapping)
        self.assertIsInstance(
            self._shifter._services["positions"].dst, StringIO)

        borg = Shifter()
        self.assertIsInstance(borg._services, Mapping)
        self.assertIsInstance(
            borg._services["positions"].dst, StringIO)

    def test_tick_attribute_service(self):
        shifter = Shifter()
        task = asyncio.Task(shifter(0, 0.3, 0.1))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(task)
        rv = task.result()
        self.assertAlmostEqual(rv.stop, rv.ts + rv.step, places=10)
        self.assertEqual(rv, shifter.tick)

    def test_page_attribute_service(self):
        shifter = Shifter()
        task = asyncio.Task(shifter(0, 0.3, 0.1))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(task)
        self.assertIn("info", vars(shifter.page))
        self.assertIn("nav", vars(shifter.page))
        self.assertIn("items", vars(shifter.page))
        self.assertIn("options", vars(shifter.page))

    def test_gateoas_attribute_service(self):
        shifter = Shifter()
        task = asyncio.Task(self._shifter(0, 0.3, 0.1))
        loop = asyncio.get_event_loop()
        rv = loop.run_until_complete(task)
        history = shifter._services["positions"].dst.getvalue()
        data = "{" + history.rpartition("}{")[-1]
        output = json.loads(data)
        self.assertIn("info", output)
        self.assertIn("nav", output)
        self.assertIn("items", output)
        self.assertIn("options", output)

    def test_hateoas_attribute_service(self):
        shifter = Shifter()
        print(vars(shifter))
        task = asyncio.Task(shifter(0, 0.3, 0.1))
        loop = asyncio.get_event_loop()
        rv = loop.run_until_complete(task)
        print(rv)
        history = shifter._services["positions"].dst.getvalue()
        data = "{" + history.rpartition("}{")[-1]
        output = json.loads(data)
        self.assertIn("info", output)
        self.assertIn("nav", output)
        self.assertIn("items", output)
        self.assertIn("options", output)

    def test_first_collision(self):
        shifter = Shifter()
        task = asyncio.Task(shifter(0, 0.3, 0.1))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(task)
        rv = task.result()
