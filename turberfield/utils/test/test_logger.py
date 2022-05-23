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

import asyncio
import logging
import pathlib
from tempfile import TemporaryDirectory
import unittest

from turberfield.utils.logger import Logger
from turberfield.utils.logger import LogLocation
from turberfield.utils.logger import LogManager


class LogTests(unittest.TestCase):

    def setUp(self):
        self.manager = LogManager()

    def test_get_logger(self):
        logger = self.manager.get_logger("unit.test.log")
        logger.log(logger.Level.DEBUG, "Simple message")
        self.assertIn(logger, self.manager.loggers)


class LocationTests:

    def setUp(self):
        self.locn = TemporaryDirectory()
        self.locn.__enter__()

    def tearDown(self):
        self.locn.__exit__(None, None, None)


class LocationSyncTests(LocationTests, unittest.TestCase):

    def test_empty_location_string(self):
        l = LogLocation(self.locn.name)
        self.assertIsInstance(l.path, pathlib.Path)

    def test_empty_location_path(self):
        l = LogLocation(pathlib.Path(self.locn.name))
        self.assertIsInstance(l.path, pathlib.Path)

    def test_stat_empty_location(self):
        l = LogLocation(self.locn.name)
        print(l.stat)
        self.assertIsInstance(l.path, pathlib.Path)


class LocationAsyncTests(LocationTests, unittest.TestCase):

    def test_stat_asyncio(self):
        loop = asyncio.new_event_loop()
        l = LogLocation(self.locn.name, loop=loop)
        with l:
            self.assertIs(l.loop, loop)
            print(l.stat)
