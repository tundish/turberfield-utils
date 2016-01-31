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


from collections import deque
from collections import OrderedDict
from decimal import Decimal
from enum import Enum
from inspect import getmembers
import json
import re

from turberfield.utils.encoder import JSONEncoder

class Assembly:

    decoding = {}
    encoding = {}

    class Encoder(JSONEncoder):

        def default(self, obj):
            tag = Assembly.encoding.get(type(obj), None)
            if tag is not None:
                rv = OrderedDict([("_type", tag)])
                try:
                    attribs = obj._asdict()
                except AttributeError:
                    if isinstance(obj, Enum):
                        attribs = {"name": obj.name, "value": obj.value}
                    else:
                        attribs = vars(obj)
                rv.update(attribs)
                return rv

            try:
                return JSONEncoder.default(self, obj)
            except TypeError as e:
                try:
                    return obj.strftime("%Y-%m-%d %H:%M:%S")
                except AttributeError:
                    if isinstance(obj, (deque,)):
                        return list(obj)
                    elif isinstance(obj, (Decimal, )):
                        return float(obj)
                    elif isinstance(obj, type(re.compile(""))):
                        return obj.pattern
                    else:
                        raise e

    @staticmethod
    def register(*args, namespace=None):
        tmplt = "{module}.{name}" if namespace is None else "{namespace}.{module}.{name}"
        for arg in args:
            module = dict(getmembers(arg)).get("__module__")
            tag = tmplt.format(
                    namespace=namespace,
                    module=module,
                    name=arg.__name__
            )
            Assembly.decoding[tag] = arg
            Assembly.encoding[arg] = tag

        return list(Assembly.encoding.keys())

    @staticmethod
    def object_hook(obj):
        typ = obj.pop("_type", None)
        cls = Assembly.decoding.get(typ, None)
        try:
            factory = getattr(cls, "factory", cls)
            return factory(**obj)
        except TypeError:
            return obj

    @staticmethod
    def dump(
        obj, fp, skipkeys=False, ensure_ascii=True, check_circular=True,
        allow_nan=True, cls=None, indent=None, separators=None,
        default=None, sort_keys=False, **kwargs
    ):
        dumper = Assembly.Encoder(
            skipkeys=skipkeys, ensure_ascii=ensure_ascii,
            check_circular=check_circular, allow_nan=allow_nan,
            indent=indent, separators=separators, default=default,
            sort_keys=sort_keys, **kwargs
        ).iterencode(obj)
        for chunk in dumper:
            fp.write(chunk)

    @staticmethod
    def dumps(
        obj, skipkeys=False, ensure_ascii=True, check_circular=True,
        allow_nan=True, cls=None, indent=None, separators=None,
        default=None, sort_keys=False, **kwargs
    ):
        return Assembly.Encoder(
            skipkeys=skipkeys, ensure_ascii=ensure_ascii,
            check_circular=check_circular, allow_nan=allow_nan,
            indent=indent, separators=separators, default=default,
            sort_keys=sort_keys, **kwargs
        ).encode(obj)

    @staticmethod
    def loads(s):
        return json.loads(
            s, object_hook=Assembly.object_hook, parse_float=Decimal
        )
