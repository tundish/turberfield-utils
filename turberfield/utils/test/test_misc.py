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
import functools
import inspect
import unittest

from turberfield.utils.misc import type_dict


class TShirt(enum.Enum):

    small = 28
    medium = 36
    large = 42

    @classmethod
    def factory(cls, name=None, **kwargs):
        return cls[name]

class TypeDictTester(unittest.TestCase):

    def test_namespace_typing(self):
        reg = type_dict(TypeDictTester, namespace="turberfield")
        self.assertIn("turberfield.utils.test.test_misc.TypeDictTester", reg)

    def test_enum_factory(self):
        reg = type_dict(TShirt, namespace="turberfield")
        rv = reg["turberfield.utils.test.test_misc.TShirt"](name="medium")
        self.assertIs(TShirt.medium, rv)
