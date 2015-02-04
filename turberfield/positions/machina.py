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
from functools import singledispatch
import json
import logging
import os
import re
import tempfile
import time

from turberfield.positions import __version__
from turberfield.positions.travel import Impulse

__doc__ = """
Machina places an actor on a stage.
"""

Fixed = namedtuple("Fixed", ["posn", "reach"])
Mobile = namedtuple("Mobile", ["motion", "reach"])
Tick = namedtuple("Tick", ["start", "stop", "step", "ts"])


class Borg:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class Props(Borg):
    """
    TODO: Move a base class to turberfield.common.inventory
    """ 

    def __init__(self):
        super().__init__()
        if not hasattr(self, "pockets"):
            self.places = defaultdict(list)
            self.pockets = defaultdict(Counter)

    def _clear(self):
        try:
            del self.places
        except AttributeError:
            pass

        try:
            del self.pockets
        except AttributeError:
            pass


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

    @property
    def template(self):
        return Provider.Page(
            info = {
                "interval": 200,
                "title": self.__class__.__name__,
                "version": __version__
            },
            nav = [],
            items = [],
            options = []
        )

    def provide(self, service, data):
        if isinstance(service, Provider.Attribute):
            setattr(self, service.name, data[service.name])
        elif isinstance(service, Provider.HATEOAS):
            content = data[service.attr]
            with Provider.endpoint(service.dst) as output:
                json.dump(
                    vars(content), output, cls=TypesEncoder, indent=4
                )
