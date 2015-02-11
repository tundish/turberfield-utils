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

import asyncio
from collections import OrderedDict
from io import StringIO
import json
import os
import shutil
import unittest

from turberfield.positions.machina import Provider

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
        with Provider.endpoint(fP) as output:
            json.dump("Test string", output)

        self.assertTrue(os.path.isfile(fP))
        with open(fP, 'r') as check:
            self.assertEqual('"Test string"', check.read())

    def test_content_goes_to_file_object(self):
        fP = os.path.join(
                EndpointTests.drcty, EndpointTests.node)
        fObj = StringIO()
        self.assertFalse(os.path.isfile(fP))
        with Provider.endpoint(fObj) as output:
            json.dump("Test string", output)

        self.assertFalse(os.path.isfile(fP))
        self.assertEqual('"Test string"', fObj.getvalue())

class ProviderTests(unittest.TestCase):

    def test_subclassing_provider(self):

        class Subclass(Provider):

            @staticmethod
            def options():
                return OrderedDict([
                    ("tick", Provider.Attribute("tick")),
                    ("page", Provider.Attribute("page")),
                ])

        self.assertTrue(hasattr(Subclass, "public"))
        options = Subclass.options()
        sub = Subclass(**options)
        self.assertTrue(hasattr(sub, "Interface"))
        self.assertIs(None, Provider.public)
        self.assertIsInstance(Subclass.public, sub.Interface)


class TaskTests(unittest.TestCase):

    def test_task_from_queue(self):
        q = asyncio.Queue()
        p = Provider(q)
        self.assertEqual(1, len(p._watchers))
