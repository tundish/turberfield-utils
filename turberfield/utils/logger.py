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
from collections import defaultdict
from collections import namedtuple
import datetime
import enum
import logging
import pathlib
import sys


class Logger:

    Entry = namedtuple("Entry", ("origin", "level", "text", "metadata"))
    Level = enum.Enum(
        "Level",
        [(label, getattr(logging, label, 15)) for label in [
            "NOTSET", "DEBUG", "NOTE", "INFO", "WARNING", "ERROR", "CRITICAL"
        ]]
    )

    def __init__(self, name, manager):
        self.name = name
        self.manager = manager
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
        return self.Entry(self, level, text, metadata)
        
    def log(self, level, *args, **kwargs):
        entry = self.entry(level, *args, **kwargs)
        try:
            self.manager.queue.put_nowait(entry)
        except asyncio.QueueFull:
            pass
        finally:
            self.manager.notify(self)


class LogEndpoint:
    pass


class LogManager:

    registry = {}
    routings = defaultdict(set)

    Route = namedtuple("Route", ("level", "endpoint"))

    def __init__(
        self, defaults: list=None, queue=None, loop=None, executor=None, timeout=None, **kwargs
    ):
        self.defaults = defaults or [self.Route(Logger.Level.INFO, sys.stderr)]
        self.queue = queue or asyncio.Queue()
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
        if name not in self.routings:
            self.routings[name].update(self.defaults)

        return self.registry.setdefault(name, factory(name, self, **kwargs))

    def notify(self, client):
        rv = self.queue.qsize()
        while self.queue.qsize():
            entry = self.queue.get_nowait()
            try:
                for route in self.routings[entry.origin.name]:
                    self.emit(entry, route)
            finally:
                self.queue.task_done()

        return rv

    def emit(self, entry, route):
        if entry.level.value >= route.level.value:
            route.endpoint.write(entry.text)


class LogLocation(LogManager):

    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.path = pathlib.Path(path)

    @property
    def stat(self):
        return self.wait_for(self.path.stat)
