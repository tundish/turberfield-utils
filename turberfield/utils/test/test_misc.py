#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.

from collections import Counter
from collections import deque
from datetime import datetime
from decimal import Decimal
import enum
import functools
import inspect
import json
import re
import unittest

from turberfield.utils.misc import type_dict
from turberfield.utils.misc import TypesEncoder


class TShirt(enum.Enum):

    small = 28
    medium = 36
    large = 42

    @classmethod
    def factory(cls, name=None, **kwargs):
        return cls[name]

class TestTypesEncoder(unittest.TestCase):

    def test_dumps_counter(self):
        obj = Counter("aspidistra") 
        text = json.dumps(
            obj, cls=TypesEncoder, indent=0
        )
        self.assertEqual(obj, json.loads(text))
        cntr = Counter(json.loads(text))
        self.assertEqual(obj, cntr)

    def test_dumps_datetime(self):
        obj = datetime.utcnow()
        text = json.dumps(
            obj, cls=TypesEncoder, indent=0
        )
        rv = obj - datetime.strptime(
            json.loads(text), "%Y-%m-%d %H:%M:%S"
        )
        self.assertEqual(0, rv.days)
        self.assertEqual(0, rv.seconds)

    def test_dumps_decimal(self):
        obj = Decimal("3.1415269") 
        text = json.dumps(
            obj, cls=TypesEncoder, indent=0
        )
        self.assertEqual(obj, Decimal(json.loads(text)))

    def test_dumps_deque(self):
        obj = deque("aspidistra") 
        text = json.dumps(
            obj, cls=TypesEncoder, indent=0
        )
        seq = deque(json.loads(text))
        self.assertEqual(obj, seq)

    def test_dumps_regex(self):
        pattern = "[a-zA-Z0-9]+"
        regex = re.compile(pattern)
        text = json.dumps(
            regex, cls=TypesEncoder, indent=0
        )
        self.assertEqual(regex, re.compile(json.loads(text)))

class TypeDictTester(unittest.TestCase):

    def test_namespace_typing(self):
        reg = type_dict(TypeDictTester, namespace="turberfield")
        self.assertIn("turberfield.utils.test.test_misc.TypeDictTester", reg)

    def test_enum_factory(self):
        reg = type_dict(TShirt, namespace="turberfield")
        rv = reg["turberfield.utils.test.test_misc.TShirt"](name="medium")
        self.assertIs(TShirt.medium, rv)
