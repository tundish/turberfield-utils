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


import enum
from collections import deque
from collections import namedtuple
import itertools
import os.path
import textwrap
import unittest

# prototyping
from inspect import getmembers
import json

class Assembly:

    decoder = {}

    @staticmethod
    def register(*args, namespace=None):
        tmplt = "{module}.{name}" if namespace is None else "{namespace}.{module}.{name}"
        Assembly.decoder.update({
            tmplt.format(
                namespace=namespace,
                module=dict(getmembers(i)).get("__module__"),
                name=i.__name__): i for i in args})

    @staticmethod
    def object_hook(obj):
        typ = obj.pop("_type", None)
        cls = Assembly.decoder.get(typ, None)
        try:
            factory = getattr(cls, "factory", cls)
            return factory(**obj)
        except TypeError:
            return obj

    @staticmethod
    def loads(s):
        return json.loads(s, object_hook=Assembly.object_hook)

class Wheelbarrow:

    Bucket = namedtuple("Bucket", ["capacity"])
    Grip = namedtuple("Grip", ["length", "colour"])
    Handle = namedtuple("Handle", ["length", "grip"])
    Rim = namedtuple("Rim", ["dia"])
    Tyre = namedtuple("Tyre", ["dia", "pressure"])
    Wheel = namedtuple("Wheel", ["rim", "tyre"])

    class Colour(enum.Enum):
        red = (255, 0 , 0)
        green = (0, 255 , 0)
        blue = (0, 0 , 255)

        @classmethod
        def factory(cls, name=None, **kwargs):
            return cls[name]


    def __init__(self, bucket=None, wheel=None, handles=[]):
        self.bucket = bucket
        self.wheel = wheel
        self.handles = deque(handles, maxlen=2)

class AssemblyTester(unittest.TestCase):

    data = textwrap.dedent("""
    {
    "_type": "turberfield.utils.test.test_assembly.Wheelbarrow",
    "bucket": {
        "_type": "turberfield.utils.test.test_assembly.Bucket",
        "capacity": 45
        },
    "wheel": {
        "_type": "turberfield.utils.test.test_assembly.Wheel",
        "rim": {
            "_type": "turberfield.utils.test.test_assembly.Rim",
            "dia": 22.85
        },
        "tyre": {
            "_type": "turberfield.utils.test.test_assembly.Tyre",
            "dia": 22.85,
            "pressure": 30
        }
        },
    "handles": [
        {
            "_type": "turberfield.utils.test.test_assembly.Handle",
            "length": 80,
            "grip": {
                "_type": "turberfield.utils.test.test_assembly.Grip",
                "length": 15,
                "colour": {
                    "_type": "turberfield.utils.test.test_assembly.Colour",
                    "name": "green"
                }
            }
        },
        {
            "_type": "turberfield.utils.test.test_assembly.Handle",
            "length": 80,
            "grip": {
                "_type": "turberfield.utils.test.test_assembly.Grip",
                "length": 15,
                "colour": {
                    "_type": "turberfield.utils.test.test_assembly.Colour",
                    "name": "green"
                }
            }
        }
        ]
    }""")

    def setUp(self):
        types = Assembly.register(
            Wheelbarrow,
            Wheelbarrow.Bucket,
            Wheelbarrow.Colour,
            Wheelbarrow.Wheel,
            Wheelbarrow.Grip,
            Wheelbarrow.Handle,
            Wheelbarrow.Rim,
            Wheelbarrow.Tyre,
            Wheelbarrow.Wheel,
            namespace="turberfield"
        )

    def test_nested_object_dumps(self):
        rv = Assembly.loads(AssemblyTester.data)
        print(json.dumps(rv))
            
    def test_nested_object_loads(self):
        rv = Assembly.loads(AssemblyTester.data)
        self.assertIsInstance(rv, Wheelbarrow)
        self.assertEqual(45, rv.bucket.capacity)
        self.assertEqual(30, rv.wheel.tyre.pressure)
        self.assertIsInstance(rv.handles, deque)
        self.assertEqual(2, len(rv.handles))
        self.assertEqual(Wheelbarrow.Colour.green, rv.handles[0].grip.colour)

    def test_nested_object_extraloads(self):
        data = AssemblyTester.data[:-3] + textwrap.dedent("""
        ,{
            "_type": "turberfield.utils.test.test_assembly.Handle",
            "length": 80,
            "grip": {
                "_type": "turberfield.utils.test.test_assembly.Grip",
                "length": 15,
                "colour": {
                    "_type": "turberfield.utils.test.test_assembly.Colour",
                    "name": "red"
                }
            }
        }
        ]}""")
        rv = Assembly.loads(data)
        self.assertIsInstance(rv, Wheelbarrow)
        self.assertIsInstance(rv.handles, deque)
        self.assertEqual(2, len(rv.handles))
        self.assertEqual(Wheelbarrow.Colour.green, rv.handles[0].grip.colour)
        self.assertEqual(Wheelbarrow.Colour.red, rv.handles[1].grip.colour)