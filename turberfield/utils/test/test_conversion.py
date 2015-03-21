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

from collections import namedtuple
from collections import OrderedDict
import json
import unittest


def obj2str(obj):
    """
    Serialise a single data object to a (JSON) string.
    """
    data = vars(obj)
    data["_type"] = type(obj).__name__
    return "\n".join(
        (json.dumps(data, cls=TypeEncoder, indent=0), "")
    )


# TODO: Goes in machina because of rson dependency
def rson2objs(text, types):
    """
    Read an RSON string and return a sequence of data objects.
    """
    which = {i.__name__: i for i in types}
    things = rson.loads(text)
    things = things if isinstance(things, list) else [things]
    return [which.get(i.pop("_type", None), dict)(**i) for i in things]


class AttributeConversionTests(unittest.TestCase):

    def test_itemise_single_type(self):
        # attribute
        Thing = namedtuple("Thing", ["a", "b", "value"])
        Thong = namedtuple("Thong", ["colour"])
        data = OrderedDict([
            (frozenset((1, 2)), [0, 1]),
            (frozenset((1, 3)), [2, 5]),
            (frozenset((2, 3)), [3, 4]),
        ])

        # filtering
        filtered = [
            Thing(a, b, val)
            for (a, b), values in data.items()
            for val in values if 2 < val < 5
        ]

        static = [Thong("blue")]

        # filtered, static saved as RSON, then loaded into web tier
        things = [dict(
            _links=["/{}".format(i.value)],
            _type=i.__class__.__name__, **vars(i))
            for i in filtered]

        thongs = [dict(
            _links=["#"],
            _type=i.__class__.__name__, **vars(i))
            for i in static]

        page = {
            "info": {},
            "items": things + thongs
        }

        # check _links lists are not refs to same object
        self.assertEqual(
            len(things), len({id(i["_links"]) for i in things}))
        self.assertTrue(json.dumps(page))
