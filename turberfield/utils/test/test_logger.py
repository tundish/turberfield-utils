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
import sys
from tempfile import TemporaryDirectory
import unittest
import uuid

from turberfield.utils.logger import Logger
from turberfield.utils.logger import LogAdapter
from turberfield.utils.logger import LogLocation
from turberfield.utils.logger import LogManager


class EndpointRegistrationTests(unittest.TestCase):

    def setUp(self):
        self.manager = LogManager()
        self.assertIn(sys.stderr, self.manager.registry.values())

    def tearDown(self):
        self.manager.registry.clear()

    def test_register_stderr(self):
        d = {}
        rv = self.manager.register_endpoint(sys.stderr, registry=d)
        self.assertEqual(d, {sys.stderr.name: sys.stderr})

    def test_register_stream(self):
        stream = io.StringIO()
        d = {}
        rv = self.manager.register_endpoint(stream, registry=d)
        self.assertEqual(d, {id(stream): stream})


class LogStreamTests(unittest.TestCase):

    def setUp(self):
        self.stream = io.StringIO()
        self.stream.name = "test stream"
        self.manager = LogManager(
            defaults=[LogManager.Route(None, Logger.Level.INFO, LogAdapter(), self.stream)]
        )

    def tearDown(self):
        self.stream.close()
        self.manager.registry.clear()

    def test_log_blocked(self):
        logger = self.manager.get_logger("unit.test.log")
        logger.log(logger.Level.DEBUG, "Debug message")
        self.assertFalse(self.stream.getvalue())

    def test_log_printed(self):
        logger = self.manager.get_logger("unit.test.log")
        logger.log(logger.Level.INFO, "Info message")
        self.assertIn("Info message", self.stream.getvalue())

    def test_log_newlines(self):
        logger = self.manager.get_logger("unit.test.log")
        logger.log(logger.Level.INFO, "Message")
        logger.log(logger.Level.INFO, "Message")
        lines = self.stream.getvalue().splitlines()
        self.assertEqual(2, len(lines))

    def test_bad_default_level(self):
        manager = LogManager(
            defaults=[LogManager.Route(None, None, LogAdapter(), self.stream)]
        )
        logger = manager.get_logger("unit.test.log")
        logger.log(logger.Level.INFO, "Info message")
        self.assertFalse(self.stream.getvalue())

    def test_bad_adapter(self):
        manager = LogManager(
            defaults=[LogManager.Route(None, Logger.Level.INFO, None, self.stream)]
        )
        logger = manager.get_logger("unit.test.log")
        logger.log(logger.Level.INFO, "Info message")
        self.assertFalse(self.stream.getvalue())

    def test_bad_endpoint(self):
        manager = LogManager(
            defaults=[LogManager.Route(None, Logger.Level.INFO, LogAdapter(), None)]
        )
        logger = manager.get_logger("unit.test.log")
        logger.log(logger.Level.INFO, "Info message")
        self.assertFalse(self.stream.getvalue())


class LocationTests:

    def setUp(self):
        self.locn = TemporaryDirectory()
        self.locn.__enter__()

    def tearDown(self):
        self.locn.__exit__(None, None, None)


class LogPathTests(LocationTests, unittest.TestCase):

    def setUp(self):
        super().setUp()
        uid = uuid.uuid4()
        self.path = pathlib.Path(self.locn.name, f"{uid.hex}.log")
        self.manager = LogManager(
            self.path,
            defaults=[LogManager.Route(None, Logger.Level.INFO, LogAdapter(), self.path)]
        )
        self.manager.__enter__()

    def tearDown(self):
        super().tearDown()
        self.manager.__exit__(None, None, None)

    def test_log_written(self):
        logger = self.manager.get_logger("unit.test.log")
        logger.log(logger.Level.INFO, "Info message")
        self.assertIn(self.path, self.manager.registry)
        self.assertTrue(self.path.exists())
        self.assertIn("Info message", self.path.read_text())
        self.assertTrue(any(
            self.path.resolve() == k.endpoint_name for k, v in self.manager.pairings
        ), self.manager.pairings)


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
