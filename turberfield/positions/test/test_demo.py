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

from collections import deque
from decimal import Decimal as Dl
import itertools
import unittest

from turberfield.positions.demo import Simulation
from turberfield.positions.homogeneous import point
from turberfield.positions.homogeneous import vector
from turberfield.positions.travel import ticks


class PositionTests(unittest.TestCase):

    def test_path_calculation(self):
        sim = Simulation()
        for n in range(5):
            with self.subTest(n=n):
                data = sim.positions()
                print(data)
                x, y = data[0].pos
        self.assertEqual(Simulation.posns["ne"][:2], (x, y))
