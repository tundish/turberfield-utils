import asyncio
from collections import namedtuple
import datetime
import enum
import logging
import pathlib
from tempfile import TemporaryDirectory
import unittest


class Logger:

    Entry = namedtuple("Entry", ("level", "text", "metadata")) 
    Level = enum.Enum(
        "Level",
        [(label, getattr(logging, label, 15)) for label in [
            "NOTSET", "DEBUG", "NOTE", "INFO", "WARNING", "ERROR", "CRITICAL"
        ]]
    )

    def __init__(self, name):
        self.name = name
        self.templates = [
            "{now}", "{level.name:>8}", "{logger.name}", " {0}"
        ]

    @property
    def metadata(self):
        return {
            "logger": self,
            "now": datetime.datetime.utcnow()
        }

    def format(self, *args, **kwargs):
        for field in self.templates:
            try:
                yield field.format(*args, **kwargs)
            except (KeyError, IndexError):
                yield ""

    def render(self, words):
        return "|".join(words)

    def entry(self, level, *args, **kwargs):
        metadata = dict(self.metadata, level=level, **kwargs)
        text = self.render(self.format(*args, **metadata))
        return self.Entry(level, text, metadata)
        
    def log(self, level, *args, **kwargs):
        print(self.entry(level, *args, **kwargs))


class LogEndpoint:
    pass


class LogManager:

    registry = {}

    Route = namedtuple("Route", ("level", "endpoint"))

    def __init__(
        self, loop=None, executor=None, timeout=None, **kwargs
    ):
        self.loop = loop
        self.timeout = timeout
        self.executor = executor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    @property
    def loggers(self):
        return [i for i in self.registry.values() if isinstance(i, Logger)]

    def wait_for(self, func, *args, **kwargs):
        if self.loop:
            return self.loop.run_until_complete(
                asyncio.wait_for(
                    self.loop.run_in_executor(self.executor, func, *args),
                    self.timeout
                )
            )
        else:
            return func(*args, **kwargs)

    def get_logger(self, name, factory=Logger, **kwargs):
        return self.registry.setdefault(name, factory(name, **kwargs))


class LogLocation(LogManager):

    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.path = pathlib.Path(path)

    @property
    def stat(self):
        return self.wait_for(self.path.stat)


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
