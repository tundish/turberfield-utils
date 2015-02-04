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
import unittest

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
        self.props = Props()
        self.props._clear()
        self.theatre = OrderedDict([
                (stage, Mobile(
                    steadypace(trajectory(), routing, timing),
                    10)
                )
                for stage, routing, timing in Simulation.patterns])
        self.theatre.update(
            OrderedDict([
                (stage, Fixed(posn, reach))
                for stage, posn, reach in Simulation.static]))

    def test_has_provide(self):
        p = Provider()
        shifter = Shifter(self.theatre, self.props)
        self.assertIsInstance(shifter, Provider)
        self.assertTrue(hasattr(shifter, "provide"))

    def test_has_options(self):
        shifter = Shifter(self.theatre, self.props)
        self.assertIsInstance(shifter.options, argparse.Namespace)

    def test_has_services(self):
        p = Provider()
        shifter = Shifter(self.theatre, self.props)
        self.assertIsInstance(shifter, Provider)
        self.assertEqual(3, len(shifter.services))

    def test_tick_attribute_service(self):
        shifter = Shifter(self.theatre, self.props)
        task = asyncio.Task(shifter(0, 0.3, 0.1))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(task)
        rv = task.result()
        self.assertAlmostEqual(rv.stop, rv.ts + rv.step, places=10)
        self.assertEqual(rv, shifter.tick)

    def test_page_attribute_service(self):
        shifter = Shifter(self.theatre, self.props)
        task = asyncio.Task(shifter(0, 0.3, 0.1))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(task)
        self.assertIn("info", vars(shifter.page))
        self.assertIn("nav", vars(shifter.page))
        self.assertIn("items", vars(shifter.page))
        self.assertIn("options", vars(shifter.page))

    def test_first_collision(self):
        shifter = Shifter(self.theatre, self.props)
        task = asyncio.Task(shifter(0, 0.3, 0.1))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(task)
        rv = task.result()
