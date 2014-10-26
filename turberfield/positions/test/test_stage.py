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

from collections import namedtuple
from collections import OrderedDict
from collections.abc import MutableMapping
import unittest
import uuid

from altgraph.Graph import Graph
 
from turberfield.common.schema import Actor

class Stage(MutableMapping):

    Contact = namedtuple("Contact", ["view", "throw", "hear", "reach"])

    class Directions():

        def __init__(self, stage, obj):
            self.stage = stage
            self.obj = obj

        def reaches(self, *args, fact=True, mutual=False):
            for i in args:
                other = self.stage[i]
                self.stage.placement.add_edge(self.obj, other.obj)
                edge = self.stage.placement.edge_by_node(self.obj, other.obj)
                self.stage.placement.update_edge_data(
                    edge,
                    Stage.Contact(True, True, True, True)
                )

    @staticmethod
    def item():
        return

    def __init__(self):
        self.placement = Graph()

    def __len__(self):
        return len(self.placement)

    def __iter__(self):
        return self.placement.__iter__()

    def __delitem__(self, key):
        return self.placement.__delitem__(key)

    def __getitem__(self, key):
        if key not in self.placement:
            self.placement.add_node(key, Stage.Directions(self, key))
        return self.placement.describe_node(key)[1]

    def __setitem__(self, key, val):
        return self.placement.__setitem__(key, val)

class APIPrototyping(unittest.TestCase):

    def test_stage_stores_directions(self):
        s = Stage()
        rv = s[Actor(uuid.uuid4().hex, "Alice")]
        self.assertIsInstance(rv, Stage.Directions)

    def test_movement(self):
        alice = Actor(uuid.uuid4().hex, "Alice")
        bob = Actor(uuid.uuid4().hex, "Bob")
        stage = Stage()
        stage[alice].reaches(
            bob,
            fact=True, mutual=True)

        self.assertIn(alice, stage)
        self.assertIn(bob, stage)
