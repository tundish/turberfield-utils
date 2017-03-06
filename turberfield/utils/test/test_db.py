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
import datetime
import enum
import glob
import os.path
import sqlite3
import textwrap
import tempfile
import unittest
import urllib.parse
import uuid


class Table:

    Column = namedtuple(
        "Column",
        ["name", "type", "isPK", "isNullable", "isUnique", "default", "refs"]
    )

    @staticmethod
    def declare_type(col):
        if isinstance(col.type, str):
            return "INTEGER" if "int" in col.type.lower() and col.isPK else col.type
        elif col.type is int:
            return "INTEGER"
        elif col.type is str:
            return "TEXT"
        elif col.type is bool:
            return ""
        elif col.type is bytes:
            return "BLOB"
        elif col.type is datetime.date:
            return "date"
        elif col.type is datetime.datetime:
            return "timestamp"
        elif "__conform__" in dir(col.type):
            return "BLOB"
        else:
            return ""

    def __init__(self, name, cols=[]):
        self.name = name
        self.cols=cols

    def sql_lines(self):
        yield "create table if not exists {0}(".format(self.name)
        for col in self.cols:
            yield " ".join((
                col.name, self.declare_type(col),
                "PRIMARY KEY" if col.isPK else "",
                "NOT NULL" if not col.isNullable else "",
                "UNIQUE" if col.isUnique else "",
                "DEFAULT {0}".format(col.default) if col.default else "" 
            )).rstrip() + ("," if col is not self.cols[-1] else "")
        yield(")")

schema = OrderedDict(
    (table.name, table) for table in [
    Table(
        "responses",
        cols=[
          Table.Column("id", int, True, False, None, None, []),
          Table.Column("ts", datetime.datetime, False, False, None, None, []),
          Table.Column("valid", bool, False, True, None, None, []),
          Table.Column("data", str, False, True, None, None, []),
        ]
    )
])

class SQLOperation:

    @property
    def sql(self):
        raise NotImplementedError

    def __init__(self, **kwargs):
        pass

    def run(self, con, log=None):
        """
        Execute the SQL defined by this class.
        Returns the cursor for data extraction.

        """
        cur = con.cursor()
        try:
            cur.execute(self.sql)
        except sqlite3.ProgrammingError:
            con.rollback()
        else:
            con.commit()
        return cur

class Creation(SQLOperation):

    @property
    def sql(self):
        return ";\n".join("\n".join(table.sql_lines()) for table in self.tables)

    def __init__(self, *args, **kwargs):
        self.tables = args
        super().__init__(**kwargs)

    def run(self, con, log=None):
        cur = super().run(con)
        cur.close()

@enum.unique
class Ownershipstate(enum.IntEnum):
    lost = 0
    acquired = 1
 
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
        return "file:{0}?{1}".format(
            conn, "&".join(i.value for i in options)
        )

    @staticmethod
    def options(name=None, paths=[]):
        if not paths:
            if name is None:
                dbs = {
                    ":memory:": [
                        Connection.CacheOptions.shared,
                    ]
                }
            else:
                dbs = {
                    name: [
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
        conn, options = list(self.attach.items())[0]
        self.db = sqlite3.connect(
            self.url(conn, options), uri=True,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        self.db.row_factory = sqlite3.Row
        return self.db

    def __exit__(self, exc_type, exc_value, traceback):
        return False

class SQLTests(unittest.TestCase):

    def test_create_entity(self):
        expected = (
            "create table entity ( "
            "name not none, "
            "session not none, "
            "primary key(name, session) )"
        )
        self.assertEqual(expected, schema["entity"].sql)

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
        con = Connection(**Connection.options())
        self.assertIsNone(con.db)
        with con as db:
            print(db)

    def test_foreign_keys(self):
        con = Connection(**Connection.options())
        self.assertIsNone(con.db)
        with con as db:
            rv = Creation(list(schema.values())[0]).run(db)
            cur = db.cursor()
            try:
                cur.execute(
                    "select count(*) from sqlite_master "
                    "where type='table' and name='responses'"
                )
                self.assertEqual((1,), tuple(cur.fetchone()))
            finally:
                cur.close()

class TableTests(unittest.TestCase):

    def test_creation_sql(self):
        print("\n".join(list(schema.values())[0].sql_lines()))

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
            Connection.CacheOptions.shared,
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
