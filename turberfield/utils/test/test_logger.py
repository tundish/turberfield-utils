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
import io
import os
import pathlib
from tempfile import TemporaryDirectory
import unittest

from turberfield.utils.logger import Logger
from turberfield.utils.logger import LogAdapter
from turberfield.utils.logger import LogLocation
from turberfield.utils.logger import LogManager


class LogTests(unittest.TestCase):

    def setUp(self):
        self.stream = io.StringIO()
        self.manager = LogManager(
            defaults=[LogManager.Route(Logger.Level.INFO, LogAdapter(), self.stream)]
        )

    def tearDown(self):
        self.stream.close()
        self.manager.routings.clear()

    def test_log_blocked(self):
        logger = self.manager.get_logger("unit.test.log")
        self.assertIn(logger, self.manager.loggers)
        logger.log(logger.Level.DEBUG, "Debug message")
        self.assertFalse(self.stream.getvalue())

    def test_log_printed(self):
        logger = self.manager.get_logger("unit.test.log")
        self.assertIn(logger, self.manager.loggers)
        logger.log(logger.Level.INFO, "Info message")
        self.assertIn("Info message", self.stream.getvalue())

    def test_log_newlines(self):
        logger = self.manager.get_logger("unit.test.log")
        self.assertIn(logger, self.manager.loggers)
        logger.log(logger.Level.INFO, "Message")
        logger.log(logger.Level.INFO, "Message")
        lines = self.stream.getvalue().splitlines()
        self.assertEqual(2, len(lines))


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
        self.assertIsInstance(l.path, pathlib.Path)
        self.assertIsInstance(l.stat, os.stat_result)


class LocationAsyncTests(LocationTests, unittest.TestCase):

    def test_stat_asyncio(self):
        loop = asyncio.new_event_loop()
        l = LogLocation(self.locn.name, loop=loop)
        with l:
            self.assertIs(l.loop, loop)
            self.assertIsInstance(l.stat, os.stat_result)
