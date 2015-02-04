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

from collections import OrderedDict
import unittest

import turberfield.positions
from turberfield.positions.demo import Simulation
from turberfield.positions.shifter import Shifter
from turberfield.positions.travel import Impulse
from turberfield.positions.travel import steadypace
from turberfield.positions.travel import trajectory


class SimulationTests(unittest.TestCase):

    def test_movement(self):
        ops = OrderedDict(
            [(obj, steadypace(trajectory(), routing, timing))
            for obj, routing, timing in Simulation.patterns])
        ts = start = 0
        stop = 6
        while ts < stop:
            for obj, imp in Shifter.movement(ops, start, ts):
                self.assertIn(obj, ops)
                self.assertIsInstance(imp, Impulse)
            ts += 1
