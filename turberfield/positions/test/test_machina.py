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
from turberfield.positions.machina import Placement
from turberfield.positions.machina import Props
from turberfield.positions.travel import steadypace
from turberfield.positions.travel import trajectory

class PlacementTests(unittest.TestCase):

    def setUp(self):
        self.props = Props()
        self.props._clear()
        self.theatre = OrderedDict(
            [(stage, steadypace(trajectory(), routing, timing))
            for stage, routing, timing in Simulation.patterns])
        # TODO: Add static stages to theatre


    def test_first_collision(self):
        op = Placement(None, self.props)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(op(0, 60, 1))
        loop.close()
