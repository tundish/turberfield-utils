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
Configuration
-------------

To configure a new Expert of a certain class, first call the
:py:meth:`options <turberfield.utils.expert.Expert.options>` method of
that class. Call it with values defined at runtime by your
controlling process. Typically these will be command line arguments or
configuration file settings.

Let's suppose an Expert subclass requires a `data` argument to tell
it where to look for application data files::

    options = SomeExpertSubclass.options(data="/var/experts")

What you get back is a Python dictionary compatible with the keyword
argument parameters of the Expert subclass. The keys of this dictionary
are the names of attributes which your object will publish publicly.
The corresponding value of a key shows the way that attribute will be
published, as follows:

.. autoattribute:: turberfield.utils.expert.Expert.Attribute
   :annotation: (name). A regular public attribute.

.. autoattribute:: turberfield.utils.expert.Expert.Event
   :annotation: (name). A public attribute which is an asyncio.Event.

.. autoattribute:: turberfield.utils.expert.Expert.HATEOAS
   :annotation: (name, attr, dst). A sequence of items in a
        JSON-formatted web page, publicly readable as a local file.

.. autoattribute:: turberfield.utils.expert.Expert.RSON
   :annotation: (name, attr, dst). A sequence of items in
        RSON format, publicly readable as a local file.

Instantiation
-------------

Some Experts will define positional parameters specific to their
operation. Aside from those, you can also pass unnamed positional
arguments and keyword arguments.

Unnamed positional arguments must be objects compatible with the
`asyncio.Queue`_ interface. The Expert will watch them for messages you
pass in to them. 

::

    wiring = (asyncio.Queue(), PipeQueue.pipequeue("/tmp/pq.fifo"))
    expert = SomeExpertSubclass(*wiring, **options)

Invocation
----------

Experts are active objects which run in an event loop. So they all
support Python call semantics. The result of calling an Expert is a
coroutine you can pass to asyncio for use as a Task_:

.. code-block:: python
   :emphasize-lines: 2

   loop = asyncio.get_event_loop()
   task = asyncio.Task(expert(loop=loop))
   loop.run_until_complete(asyncio.wait(asyncio.Task.all_tasks(loop)))

Inspection
----------

Experts either publish the data they generate to local file, or to the
*public* attribute of their class. Exactly what ends up where will
depend on the class and can be discovered from the
:py:meth:`options <turberfield.utils.expert.Expert.options>` call.

For example, should SomeExpertSubclass define an
:py:class:`Event <turberfield.utils.expert.Expert.Event>` called
`someEvent`, you'd use it like this::

    yield from SomeExpertSubclass.public.someEvent.wait()

.. _asyncio.Queue: https://docs.python.org/3/library/asyncio-queue.html
.. _Task: https://docs.python.org/3/library/asyncio-task.html
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
    """
    A base class for *Information Experts*.
    """

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
        """
        Subclasses must override the base class implementation.

        The method returns an `ordered dictionary`_. Each key is the
        name of a piece of public data to be managed by the Expert
        class. The object mapped to that key configures how the data
        is to be published. See the
        :py:meth:`declare <turberfield.utils.expert.Expert.declare>`
        method for details.

        .. _ordered dictionary: https://docs.python.org/3/library/collections.html#collections.OrderedDict
        """
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
        """
        ::

            super().__init__(*args, **kwargs)

        Unnamed positional arguments must be compatible with
        `asyncio.Queue`_.
        """
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

    @asyncio.coroutine
    def __call__(self, loop=None):
        """
        Subclasses must override the base class implementation.

        This method makes the object callable. It is a coroutine
        to be launched as an `asyncio.Task`_.

        .. _asyncio.Task: https://docs.python.org/3/library/asyncio-task.html
        """ 
        raise NotImplementedError

    def declare(self, data, loop=None):
        """
        :param data: data to be published
        :type data: a dictionary

        Invoke this method from within
        :py:meth:`__call__ <turberfield.utils.expert.Expert.__call__>`
        to publish data via the class-defined interface.

        The table shows how the different mechanisms work, depending what
        options are supplied on Instantiation_:

        +-------------------------------------------------------------------+-------------------------------------------------------------------+
        | Interface type                                                    | Publishing mechanism                                              |
        +===================================================================+===================================================================+
        | :py:class:`Attribute <turberfield.utils.expert.Expert.Attribute>` | ``<Subclass>.public.<name>`` mirrors the data value.              |
        +-------------------------------------------------------------------+-------------------------------------------------------------------+
        | :py:class:`Event <turberfield.utils.expert.Expert.Event>`         | ``<Subclass>.public.<name>`` is set or cleared by the data value. |
        +-------------------------------------------------------------------+-------------------------------------------------------------------+
        | :py:class:`RSON <turberfield.utils.expert.Expert.RSON>`           | ``RSON.dst`` is the file path to the data in RSON format.         |
        +-------------------------------------------------------------------+-------------------------------------------------------------------+
        | :py:class:`HATEOAS <turberfield.utils.expert.Expert.HATEOAS>`     | ``HATEOAS.dst`` is the file path to the data as a JSON web page.  |
        +-------------------------------------------------------------------+-------------------------------------------------------------------+
        """
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
        """
        Subclasses may override the base class implementation.

        This method is used to create one coroutine for each queue of
        input. The job of the method is to watch the queue for messages
        and dispatch them appropriately.

        """
        loop = kwargs.pop("loop", None)
        msg = object()
        while msg is not None:
            msg = yield from q.get()


Expert.Attribute.__doc__ = "Attribute docstring".format(Expert.Attribute.__doc__)
print(Expert.Attribute.__doc__)
