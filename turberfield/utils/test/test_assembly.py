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
from collections import OrderedDict
from decimal import Decimal
from enum import Enum
from inspect import getmembers
import json
import re

from turberfield.utils.encoder import JSONEncoder

class Assembly:

    decoding = {}
    encoding = {}

    class Encoder(JSONEncoder):

        def default(self, obj):
            tag = Assembly.encoding.get(type(obj), None)
            if tag is not None:
                print(tag)
                rv = OrderedDict([("_type", tag)])
                try:
                    attribs = obj._asdict()
                except AttributeError:
                    if isinstance(obj, Enum):
                        attribs = {"name": obj.name, "value": obj.value}
                    else:
                        attribs = vars(obj)
                rv.update(attribs)
                return rv

            try:
                return JSONEncoder.default(self, obj)
            except TypeError as e:
                try:
                    return obj.strftime("%Y-%m-%d %H:%M:%S")
                except AttributeError:
                    if isinstance(obj, (deque,)):
                        return list(obj)
                    elif isinstance(obj, (Decimal, )):
                        return str(obj)
                    elif isinstance(obj, type(re.compile(""))):
                        return obj.pattern
                    else:
                        raise e

    @staticmethod
    def register(*args, namespace=None):
        tmplt = "{module}.{name}" if namespace is None else "{namespace}.{module}.{name}"
        for arg in args:
            module = dict(getmembers(arg)).get("__module__")
            tag = tmplt.format(
                    namespace=namespace,
                    module=module,
                    name=arg.__name__
            )
            Assembly.decoding[tag] = arg
            Assembly.encoding[arg] = tag

    @staticmethod
    def object_hook(obj):
        typ = obj.pop("_type", None)
        cls = Assembly.decoding.get(typ, None)
        try:
            factory = getattr(cls, "factory", cls)
            return factory(**obj)
        except TypeError:
            return obj

    @staticmethod
    def dumps(
        obj, skipkeys=False, ensure_ascii=True, check_circular=True,
        allow_nan=True, cls=None, indent=None, separators=None,
        default=None, sort_keys=False, **kwargs
    ):
        return Assembly.Encoder(
            skipkeys=skipkeys, ensure_ascii=ensure_ascii,
            check_circular=check_circular, allow_nan=allow_nan,
            indent=indent, separators=separators, default=default,
            sort_keys=sort_keys, **kwargs
        ).encode(obj)

    @staticmethod
    def loads(s):
        return json.loads(
            s, object_hook=Assembly.object_hook, parse_float=Decimal
        )

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
        print(Assembly.dumps(rv, indent=2))
            
    def test_nested_object_loads(self):
        rv = Assembly.loads(AssemblyTester.data)
        self.assertIsInstance(rv, Wheelbarrow)
        self.assertEqual(45, rv.bucket.capacity)
        self.assertIsInstance(rv.wheel.rim.dia, Decimal)
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
