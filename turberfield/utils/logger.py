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
from collections import namedtuple
import datetime
import enum
import logging
import pathlib


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
