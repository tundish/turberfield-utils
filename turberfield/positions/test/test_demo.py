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
from collections import deque
from decimal import Decimal as Dl
from io import StringIO
import itertools
import json
import os.path
import shutil
import unittest

import turberfield.positions
from turberfield.positions.demo import Simulation
from turberfield.positions.homogeneous import point
from turberfield.positions.homogeneous import vector
from turberfield.positions.travel import ticks


class EndpointTests(unittest.TestCase):

    drcty = os.path.expanduser(os.path.join("~", ".turberfield"))
    node = "test.json"

    def setUp(self):
        try:
            os.mkdir(EndpointTests.drcty)
        except OSError:
            pass

    def tearDown(self):
        shutil.rmtree(EndpointTests.drcty, ignore_errors=True)

    def test_content_goes_to_named_file(self):
        fP = os.path.join(
                EndpointTests.drcty, EndpointTests.node)
        self.assertFalse(os.path.isfile(fP))
        with turberfield.positions.demo.endpoint(
            EndpointTests.node,
            parent=EndpointTests.drcty) as output:
            json.dump("Test string", output)

        self.assertTrue(os.path.isfile(fP))
        with open(fP, 'r') as check:
            self.assertEqual('"Test string"', check.read())

    def test_content_goes_to_file_object(self):
        fP = os.path.join(
                EndpointTests.drcty, EndpointTests.node)
        fObj = StringIO()
        self.assertFalse(os.path.isfile(fP))
        with turberfield.positions.demo.endpoint(
            fObj,
            parent=EndpointTests.drcty) as output:
            json.dump("Test string", output)

        self.assertFalse(os.path.isfile(fP))
        self.assertEqual('"Test string"', fObj.getvalue())

    def test_run(self):
        fP = os.path.join(
                EndpointTests.drcty, EndpointTests.node)
        print(turberfield.positions.demo.run(
            Simulation.patterns,
            options=argparse.Namespace(output=EndpointTests.drcty),
            node=EndpointTests.node,
            stop=6))
        with open(fP, 'r') as check:
            print(check.read())


class PositionTests(unittest.TestCase):

    def test_path_definition(self):
        sim = Simulation()
        self.assertEqual(
            (Simulation.posns["nw"], Simulation.posns["ne"]),
            sim.path)
        for n in range(22):
            with self.subTest(n=n):
                data = sim.positions()
        self.assertEqual(
            (Simulation.posns["ne"], Simulation.posns["se"]),
            sim.path)

    def test_path_calculation(self):
        sim = Simulation()
        for n in range(22):
            with self.subTest(n=n):
                data = sim.positions()
                if n == 0: continue
                x, y = data[0].pos
        self.assertEqual(Simulation.posns["ne"][:2], (x, y))
