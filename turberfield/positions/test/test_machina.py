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
from collections import OrderedDict
import unittest

from turberfield.positions.demo import Simulation
from turberfield.positions.machina import Fixed
from turberfield.positions.machina import Mobile
from turberfield.positions.machina import Props
from turberfield.positions.machina import Shifter
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

    def test_first_collision(self):
        shifter = Shifter(self.theatre, self.props)
        task = asyncio.Task(shifter(0, 0.3, 0.1))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(task)
        print(task.result())
        loop.close()
        print(self.theatre)
