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
from turberfield.positions.travel import trajectory


class PositionTests(unittest.TestCase):

    def test_path_calculation(self):
        sim = Simulation()

    def test_point_calculation(self):
        expected = [point(i, 0, 0) for i in [
            Dl("0"), Dl("29.41800004"), Dl("56.38450008"),
            Dl("80.89950012"), Dl("102.96300016"), Dl("122.5750002"),
            Dl("139.73550024"), Dl("154.44450028"), Dl("166.70200032"),
            Dl("176.50800036"), Dl("183.8625004"), Dl("188.76550044"),
            Dl("191.21700048"), Dl("191.21700052"), Dl("188.76550056"),
            Dl("183.8625006"), Dl("176.50800064"), Dl("166.70200068"),
            Dl("154.44450072"), Dl("139.73550076"), Dl("122.5750008"),
            Dl("102.96300084"), Dl("80.89950088"), Dl("56.38450092"),
            Dl("29.41800096"), Dl("0.000001")]
        ]

        dt = Dl("0.5")
        vel = vector(Dl("61.28750008"), 0, 0)
        samples = deque([Dl(i.t / 10) for i in ticks(0, 130, 5)])
        accns = deque([vector(Dl("-9.806"), 0, 0)] * len(samples))
        posns = deque([
            point(0, 0, 0),
            point(0, 0, 0) + vel * dt + Dl("0.5") * accns[0] * dt * dt
        ])
        for n, x in enumerate(
            trajectory(
                samples, posns=posns, accns=accns)
        ):
            with self.subTest(n=n):
                self.assertEqual(expected[n], x.pos)
