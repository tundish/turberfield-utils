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
from collections.abc import MutableMapping
import unittest
import uuid

from turberfield.common.schema import Actor

class Stage(MutableMapping):
    """
    Vista
    Pitch
    Chamber
    Reach
    """

    @staticmethod
    def item():
        return

    def __init__(self):
        self.placement = OrderedDict()

    def __len__(self):
        return len(self.placement)

    def __iter__(self):
        return self.placement.__iter__()

    def __delitem__(self, key):
        return self.placement.__delitem__(key)

    def __getitem__(self, key):
        return self.placement.setdefault(key, None)

    def __setitem__(self, key, val):
        return self.placement.__setitem__(key, val)

class APIPrototyping(unittest.TestCase):

    def test_movement(self):
        s = Stage()
        s[Actor(uuid.uuid4().hex, "Alice")].reaches({
            Actor(uuid.uuid4().hex, "Bob")
        }, fact=True, mutual=True)
