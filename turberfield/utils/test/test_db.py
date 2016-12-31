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

from collections import OrderedDict
import enum
import glob
import os.path
import tempfile
import unittest
import urllib.parse
import uuid


@enum.unique
class Ownershipstate(enum.IntEnum):
    lost = 0
    found = 1
 
class Connection:
    """
    * Find target database files
    * Load extensions
    * Attach databases (readonly?)

    * Attach in-memory database
    * Execute pragmas
    * Discover state tables
    * Create state tables
    """
    class CacheOptions(enum.Enum):
        shared = "cache=shared"
        private = "cache=private"

    class ImmutableOptions(enum.Enum):
        immutable = "immutable=1"
        mutable = "immutable=0"

    class ModeOptions(enum.Enum):
        read = "mode=ro"
        read_write = "mode=rw"
        read_write_create = "mode=rwc"
        memory = "mode=memory"

    @staticmethod
    def url(conn, options):
        return "file://{0}?{1}".format(
            conn, "&".join(i.value for i in options)
        )

    @staticmethod
    def options(paths=[]):
        if not paths:
            dbs = {
                ":memory:": [
                    Connection.CacheOptions.shared,
                    Connection.ModeOptions.memory
                ]
            }
        elif len(paths) == 1:
            dbs = {
                paths[0]: [Connection.ModeOptions.read_write_create]
            }
        else:
            dbs = OrderedDict({
                ":memory:": [
                    Connection.CacheOptions.private,
                    Connection.ModeOptions.memory
                ]
            })
            dbs.update(
                {i: [Connection.ModeOptions.read] for i in paths}
            )
        return {
            "attach": dbs
        }

    def __init__(self, attach=[]):
        self.attach = attach
        self.db = None
        for conn, options in self.attach.items():
            print(Connection.url(conn, options))

    def __enter__(self):
        self.db = sqlite3.connect(
            "file:path/to/database?mode=ro",
            uri=True
        )
        return self.db

    def __exit__(self, exc_type, exc_value, traceback):
        return False

class NeedsTempDirectory:

    def setUp(self):
        self.drcty = tempfile.TemporaryDirectory()

    def tearDown(self):
        if os.path.isdir(self.drcty.name):
            self.drcty.cleanup()
        self.assertFalse(os.path.isdir(self.drcty.name))
        self.drcty = None

class InMemoryTests(NeedsTempDirectory, unittest.TestCase):

    def test_one_db_in_memory(self):
        obj = Connection(**Connection.options())
        self.assertIsNone(obj.db)

class OptionTests(NeedsTempDirectory, unittest.TestCase):

    @staticmethod
    def make_db_files(tempdir, n):
        for i in range(n):
            fd, path = tempfile.mkstemp(
                dir=tempdir.name,
                suffix=".db"
            )
            yield fd, path

    @staticmethod
    def close_db_files(*items):
        for fd, path in items:
            os.close(fd)

    def test_one_db_in_memory(self):
        rv = Connection.options()
        self.assertIsInstance(rv, dict)
        self.assertEqual(1, len(rv["attach"]))
        self.assertIn(
            Connection.ModeOptions.memory,
            list(rv["attach"].values())[0]
        )

    def test_one_db_from_file(self):
        fd, path = next(OptionTests.make_db_files(self.drcty, 1))
        paths = glob.glob(os.path.join(self.drcty.name, "*.db"))
        self.assertEqual(1, len(paths)) 
        OptionTests.close_db_files((fd, path))
        rv = Connection.options(paths=paths)
        self.assertIsInstance(rv, dict)
        self.assertEqual(1, len(rv["attach"]))
        self.assertIn(
            Connection.ModeOptions.read_write_create,
            list(rv["attach"].values())[0]
        )

    def test_ten_db_from_file(self):
        items = list(OptionTests.make_db_files(self.drcty, 10))
        paths = glob.glob(os.path.join(self.drcty.name, "*.db"))
        self.assertEqual(10, len(paths)) 
        OptionTests.close_db_files(*items)
        rv = Connection.options(paths=paths)
        self.assertIsInstance(rv, dict)
        self.assertEqual(11, len(rv["attach"]))
        name, options = rv["attach"].popitem(last=False)
        self.assertEqual(":memory:", name)
        self.assertIn(Connection.ModeOptions.memory, options)
        self.assertTrue(all(
            Connection.ModeOptions.read in i
            for i in rv["attach"].values())
        )
