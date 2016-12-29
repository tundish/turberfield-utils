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

import glob
import os.path
import tempfile
import unittest
import uuid

class Connection:
    """
    * Find target database files
    * Select module
    * Load extensions
    * Attach databases
    * Execute pragmas
    """
    @staticmethod
    def options():
        return {}

class NeedsTempDirectory:

    def setUp(self):
        self.drcty = tempfile.TemporaryDirectory()

    def tearDown(self):
        if os.path.isdir(self.drcty.name):
            self.drcty.cleanup()
        self.assertFalse(os.path.isdir(self.drcty.name))
        self.drcty = None

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

    def test_one_db_on_file(self):
        fd, path = next(OptionTests.make_db_files(self.drcty, 1))
        paths = glob.glob(os.path.join(self.drcty.name, "*.db"))
        self.assertEqual(1, len(paths)) 
        OptionTests.close_db_files((fd, path))

    def test_ten_db_on_file(self):
        items = list(OptionTests.make_db_files(self.drcty, 10))
        paths = glob.glob(os.path.join(self.drcty.name, "*.db"))
        self.assertEqual(10, len(paths)) 
        OptionTests.close_db_files(*items)
