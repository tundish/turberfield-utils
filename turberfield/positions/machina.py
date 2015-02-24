#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import asyncio
from collections import Counter
from collections import defaultdict
from collections import namedtuple
import contextlib
import decimal
import itertools
import json
import logging
import os
import re
import tempfile
import time
import uuid
import warnings

from turberfield.common.pipes import PipeQueue
from turberfield.positions import __version__
from turberfield.positions.travel import Impulse

__doc__ = """
Machina places an actor on a stage.
"""

Fixed = namedtuple("Fixed", ["posn", "reach"])
Mobile = namedtuple("Mobile", ["motion", "reach"])
Tick = namedtuple("Tick", ["start", "stop", "step", "ts"])


class TypesEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        if isinstance(obj, type(re.compile(""))):
            return obj.pattern

        try:
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        except AttributeError:
            return json.JSONEncoder.default(self, obj)


class Provider:

    Attribute = namedtuple("Attribute", ["name"])
    HATEOAS = namedtuple("HATEOAS", ["name", "attr", "dst"])
    JSON = namedtuple("JSON", ["name"])
    Page = namedtuple("Page", ["info", "nav", "items", "options"])
    RSON = namedtuple("RSON", ["name"])

    public = None

    @staticmethod
    @contextlib.contextmanager
    def endpoint(arg, suffix=".json"):
        if isinstance(arg, str):
            parent = os.path.dirname(arg)
            fD, fN = tempfile.mkstemp(suffix=suffix, dir=parent)
            try:
                rv = open(fN, 'w')
                yield rv
            except Exception as e:
                raise e
            rv.close()
            os.close(fD)
            os.replace(fN, arg)
        else:
            yield arg

    @staticmethod
    def options():
        raise NotImplementedError

    def __init__(self, *args, **kwargs):
        class_ = self.__class__
        self.log = logging.getLogger(class_.__name__)
        loop = kwargs.pop("loop", None)
        self.inputs = [
            i for i in args
            if isinstance(i, (asyncio.Queue, PipeQueue))
            # TODO: accept JobQueue, via hasattr duck typing?
        ]
        self._watchers = [
            asyncio.Task(self.watch(q, loop=loop), loop=loop)
            for q in self.inputs
        ]
        self._services = kwargs
        if kwargs:
            if class_.public is not None:
                warnings.warn("Re-initialisation of {}: {}".format(
                    class_.__name__, kwargs))

            attributes = [k for k, v in kwargs.items()
                          if isinstance(v, Provider.Attribute)]
            self.Interface = namedtuple(
                class_.__name__ + "Interface", attributes)

            class_.public = self.Interface._make(
                itertools.repeat(None, len(attributes)))
            
    @property
    def page(self):
        return Provider.Page(
            info = {
                "title": self.__class__.__name__,
                "version": __version__
            },
            nav = [],
            items = [],
            options = []
        )

    def provide(self, data):
        kwargs = defaultdict(None)
        class_ = self.__class__
        for name, service in self._services.items():
            if isinstance(service, Provider.Attribute):
                kwargs[service.name] = data[service.name]
            elif isinstance(service, Provider.HATEOAS):
                content = data[service.attr]
                with Provider.endpoint(service.dst) as output:
                    json.dump(
                        vars(content), output,
                        cls=TypesEncoder, indent=4
                    )

        class_.public = class_.public._replace(**kwargs)

    @asyncio.coroutine
    def watch(self, q, **kwargs):
        loop = kwargs.pop("loop", None)
        msg = object()
        while msg is not None:
            msg = yield from q.get()
