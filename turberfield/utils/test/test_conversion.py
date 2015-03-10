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


class AttributeConversionTests(unittest.TestCase):

    def test_itemise_single_type(self):
        # attribute
        Thing = namedtuple("Thing", ["value"])
        data = OrderedDict([
            (frozenset((1,2)), [Thing(0), Thing(1)]),
            (frozenset((1,3)), [Thing(2), Thing(5)]),
            (frozenset((2,3)), [Thing(3), Thing(4)]),
        ])

        # filtering
        output = [
            dict(_links=[], _type=t.__class__.__name__, **vars(t))
            for (a, b), things in data.items()
            for t in things if 2 < t.value < 5]

        self.assertEqual(
            len(output), len({id(i["_links"]) for i in output}))
        self.fail(output)
