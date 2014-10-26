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

import unittest
import uuid

from turberfield.common.schema import Actor
from turberfield.positions.stage import Stage


class APIPrototyping(unittest.TestCase):

    def test_stage_stores_directions(self):
        s = Stage()
        rv = s[Actor(uuid.uuid4().hex, "Alice")]
        self.assertIsInstance(rv, Stage.Directions)

    def test_add_stage_direction(self):
        alice = Actor(uuid.uuid4().hex, "Alice")
        bob = Actor(uuid.uuid4().hex, "Bob")
        stage = Stage()
        stage[alice].can_reach(
            bob,
            fact=True, mutual=False)

        self.assertIn(alice, stage)
        self.assertIn(bob, stage)

        self.assertIs(alice, stage[alice].obj)
        self.assertIs(bob, stage[bob].obj)

        self.assertIn(bob, stage[alice].reach)
        self.assertNotIn(alice, stage[bob].reach)

    def test_add_stage_direction_mutual(self):
        alice = Actor(uuid.uuid4().hex, "Alice")
        bob = Actor(uuid.uuid4().hex, "Bob")
        stage = Stage()
        stage[alice].can_reach(
            bob,
            fact=True, mutual=True)

        self.assertIn(alice, stage)
        self.assertIn(bob, stage)

        self.assertIs(alice, stage[alice].obj)
        self.assertIs(bob, stage[bob].obj)

        self.assertIn(bob, stage[alice].reach)
        self.assertIn(alice, stage[bob].reach)

    def test_add_stage_direction_untrue(self):
        alice = Actor(uuid.uuid4().hex, "Alice")
        bob = Actor(uuid.uuid4().hex, "Bob")
        stage = Stage()
        stage[alice].can_reach(
            bob,
            fact=True, mutual=True)

        self.assertIn(alice, stage)
        self.assertIn(bob, stage)

        self.assertIs(alice, stage[alice].obj)
        self.assertIs(bob, stage[bob].obj)

        self.assertIn(bob, stage[alice].reach)
        self.assertIn(alice, stage[bob].reach)

        stage[alice].can_reach(
            bob,
            fact=False, mutual=False)

        self.assertNotIn(bob, stage[alice].reach)
        self.assertIn(alice, stage[bob].reach)

    def test_add_and_remove_stage_direction(self):
        alice = Actor(uuid.uuid4().hex, "Alice")
        bob = Actor(uuid.uuid4().hex, "Bob")
        stage = Stage()
        stage[alice].can_reach(
            bob,
            fact=True, mutual=True)

        self.assertIn(alice, stage)
        self.assertIn(bob, stage)
        self.assertIn(alice, stage.placement)
        self.assertIn(bob, stage.placement)
        self.assertEqual(2, len(stage))
        self.assertEqual(2, len(list(stage.placement)))

        del stage[bob]
        self.assertNotIn(bob, stage)
        self.assertNotIn(bob, stage.placement)
        self.assertEqual(1, len(stage))
        self.assertEqual(1, len(list(stage.placement)))

class TestHearing(unittest.TestCase):

    def test_add_hearing(self):
        alice = Actor(uuid.uuid4().hex, "Alice")
        bob = Actor(uuid.uuid4().hex, "Bob")
        stage = Stage()
        stage[alice].can_hear(
            bob,
            fact=True, mutual=False)

        self.assertIn(bob, stage[alice].hearing)
        self.assertNotIn(alice, stage[bob].hearing)

    def test_block_hearing(self):
        alice = Actor(uuid.uuid4().hex, "Alice")
        bob = Actor(uuid.uuid4().hex, "Bob")
        stage = Stage()
        stage[alice].can_hear(
            bob,
            fact=True, mutual=False)

        self.assertIn(bob, stage[alice].hearing)
        self.assertNotIn(bob, stage[alice].throw)
        self.assertNotIn(alice, stage[bob].hearing)


        stage[alice].can_throw(
            bob,
            fact=True, mutual=False)

        self.assertIn(bob, stage[alice].hearing)
        self.assertIn(bob, stage[alice].throw)

        stage[alice].can_hear(
            bob,
            fact=False, mutual=False)
        self.assertNotIn(bob, stage[alice].hearing)
        self.assertNotIn(bob, stage[alice].throw)

