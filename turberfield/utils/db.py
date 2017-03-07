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
import logging
import sqlite3


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
        self.cols = cols

    def sql_lines(self):
        yield "create table if not exists {0}(".format(self.name)
        pks = [i for i in self.cols if i.isPK]
        for col in self.cols:
            yield " ".join((
                col.name, self.declare_type(col),
                "PRIMARY KEY" if col.isPK and len(pks) == 1 else "",
                "NOT NULL" if not col.isNullable else "",
                "UNIQUE" if col.isUnique else "",
                "DEFAULT {0}".format(col.default) if col.default else "" 
            )).rstrip() + ("," if len(pks) >= 2 or col is not self.cols[-1] else "")
        if len(pks) >= 2:
            yield "PRIMARY KEY({0})".format(", ".join([i.name for i in pks]))
        yield(")")

schema = OrderedDict(
    (table.name, table) for table in [
    Table(
        "entity",
        cols=[
          Table.Column("name", str, True, False, None, None, []),
          Table.Column("session", str, True, False, None, None, []),
        ]
    )
])


class SQLOperation:

    @property
    def sql(self):
        raise NotImplementedError

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def run(self, con, log=None):
        """
        Execute the SQL defined by this class.
        Returns the cursor for data extraction.

        """
        log = log or logging.getLogger("SQLOperation")
        cur = con.cursor()
        try:
            cur.execute(*self.sql)
        except sqlite3.OperationalError:
            log.error(self.sql)
            con.rollback()
        except sqlite3.ProgrammingError:
            con.rollback()
        else:
            con.commit()
        return cur


class Creation(SQLOperation):

    @property
    def sql(self):
        return (";\n".join("\n".join(table.sql_lines()) for table in self.tables), )

    def __init__(self, *args, **kwargs):
        self.tables = args
        super().__init__(**kwargs)

    def run(self, con, log=None):
        cur = super().run(con)
        if cur is not None:
            cur.close()
            return self.tables


class Insertion(SQLOperation):

    @property
    def sql(self):
        lines = []
        for table in self.tables:
            params = [i for i in table.cols if i.name in self.kwargs]
            lines.append(
                "insert into {table.name} ({columns}) values ({values})".format(
                    table=table,
                    columns=", ".join(i.name for i in params),
                    values=", ".join(":{col.name}".format(col=col) for col in params)
                )
            )
        return (";\n".join(lines), self.kwargs)

    def __init__(self, *args, **kwargs):
        self.tables = args
        super().__init__(**kwargs)


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

    def __init__(self, attach=[], log=None):
        self.log = log or logging.getLogger("Connection")
        self.attach = attach
        self.db = None
        for conn, options in self.attach.items():
            self.log.debug(Connection.url(conn, options))

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
