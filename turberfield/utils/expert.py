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
import contextlib
import decimal
import itertools
import json
import logging
import os
import re
import tempfile
import time
import warnings

from turberfield.utils import __version__
from turberfield.utils.pipes import PipeQueue
from turberfield.utils.travel import Impulse

__doc__ = """
Machina places an actor on a stage.
"""


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


class Expert:

    Attribute = namedtuple("Attribute", ["name"])
    Event = namedtuple("Event", ["name"])
    HATEOAS = namedtuple("HATEOAS", ["name", "attr", "dst"])
    JSON = namedtuple("JSON", ["name"])
    Page = namedtuple("Page", ["info", "nav", "items", "options"])
    RSON = namedtuple("RSON", ["name", "attr", "dst"])

    public = None

    @staticmethod
    @contextlib.contextmanager
    def declaration(arg, suffix=".json"):
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

    @classmethod
    def page(cls):
        return Expert.Page(
            info={
                "title": cls.__name__,
                "version": __version__
            },
            nav=[],
            items=[],
            options=[]
        )

    def __init__(self, *args, **kwargs):
        class_ = self.__class__
        self._log = logging.getLogger(
            "turberfield.expert." + class_.__name__.lower())
        loop = kwargs.pop("loop", None)
        inputs = [
            i for i in args
            if isinstance(i, (asyncio.Queue, PipeQueue))
            # TODO: accept JobQueue, via hasattr duck typing?
        ]
        self._watchers = [
            asyncio.Task(self.watch(q, loop=loop), loop=loop)
            for q in inputs
        ]
        self._services = kwargs
        if kwargs:
            if class_.public is not None:
                warnings.warn("Re-initialisation of {}: {}".format(
                    class_.__name__, kwargs))

            attributes = [
                k for k, v in kwargs.items()
                if isinstance(v, (Expert.Attribute, Expert.Event))
            ]
            self.Interface = namedtuple(
                class_.__name__ + "Interface", attributes)

            class_.public = self.Interface._make(
                itertools.repeat(None, len(attributes)))

    def declare(self, data, loop=None):
        class_ = self.__class__
        kwargs = defaultdict(None)
        for name, service in self._services.items():
            if isinstance(service, Expert.Attribute):
                kwargs[service.name] = data[service.name]
            elif isinstance(service, Expert.Event):
                event = kwargs[service.name] = (
                    getattr(class_.public, service.name)
                    or asyncio.Event(loop=loop))
                if data[service.name]:
                    event.set()
                else:
                    event.clear()
            elif isinstance(service, Expert.RSON):
                with Expert.declaration(service.dst) as output:
                    output.write(
                        "\n".join(json.dumps(
                            dict(_type=type(i).__name__, **vars(i)),
                            output, cls=TypesEncoder, indent=0
                            )
                            for i in data.get(service.attr, []))
                    )
            elif isinstance(service, Expert.HATEOAS):
                page = class_.page()
                page.info["ts"] = time.time()
                items = data.get(service.attr, [])
                page.items[:] = [dict(
                    _links=[],
                    _type=i.__class__.__name__, **vars(i))
                    for i in items]
                with Expert.declaration(service.dst) as output:
                    json.dump(
                        vars(page), output,
                        cls=TypesEncoder, indent=4
                    )

        class_.public = class_.public._replace(**kwargs)

    @asyncio.coroutine
    def watch(self, q, **kwargs):
        loop = kwargs.pop("loop", None)
        msg = object()
        while msg is not None:
            msg = yield from q.get()
