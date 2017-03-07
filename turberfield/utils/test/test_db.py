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

import datetime
import glob
import os.path
import sqlite3
import tempfile
import unittest
import uuid

from turberfield.utils.db import Connection
from turberfield.utils.db import Creation
from turberfield.utils.db import Insertion
from turberfield.utils.db import Table
from turberfield.utils.db import schema


class SQLTests(unittest.TestCase):

    def test_create_entity(self):
        expected = "\n".join((
            "create table if not exists entity(",
            "name TEXT  NOT NULL,",
            "session TEXT  NOT NULL,",
            "PRIMARY KEY(name, session)",
            ")"
        ))
        rv = Creation(schema["entity"]).sql
        self.assertEqual(1, len(rv))
        self.assertEqual(expected, rv[0])

    def test_insert_entity(self):
        expected = (
            "insert into entity (name, session) values (:name, :session)",
            {"name": "qwerty", "session": "1234567890"}
        )
        rv = Insertion(
            schema["entity"],
            name="qwerty",
            session="1234567890",
        ).sql
        self.assertEqual(expected, rv)

class DBTests:

    @staticmethod
    def get_tables(con):
        cur = con.cursor()
        try:
            cur.execute("select * from sqlite_master where type='table'")
            return cur.fetchall()
        finally:
            cur.close()

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
            self.assertTrue(con.db)

    def test_not_null(self):
        con = Connection(**Connection.options())
        with con as db:
            rv = Creation(schema["entity"]).run(db)
            self.assertRaises(
                sqlite3.IntegrityError,
                Insertion(
                    schema["entity"],
                    session=uuid.uuid4().hex
                ).run,
                db
            )

    def test_primary_keys(self):
        con = Connection(**Connection.options())
        with con as db:
            rv = Creation(schema["entity"]).run(db)
            session=uuid.uuid4().hex
            rv = Insertion(
                schema["entity"],
                name="test",
                session=session
            ).run(db)
            self.assertRaises(
                sqlite3.IntegrityError,
                Insertion(
                    schema["entity"],
                    session=session
                ).run,
                db
            )

class TableTests(DBTests, unittest.TestCase):

    def test_creation_sql(self):
        table = Table(
            "records",
            cols=[
              Table.Column("id", int, True, False, None, None, []),
              Table.Column("ts", datetime.datetime, False, False, None, None, []),
              Table.Column("valid", bool, False, True, None, None, []),
              Table.Column("data", str, False, True, None, None, []),
            ]
        )
        con = Connection(**Connection.options())
        with con as db:
            rv = Creation(table).run(db)
            n = len(self.get_tables(db))
            self.assertEqual(1, n)

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
