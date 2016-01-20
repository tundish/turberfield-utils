#!/usr/bin/env python3
#   encoding: UTF-8

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

import collections
import decimal
import inspect
import json
import re
import warnings

import pkg_resources


class SavesAsDict:

    @classmethod
    def from_json(cls, data):
        return cls(**json.loads(data))

    def __json__(self):
        return json.dumps(vars(self), indent=0, ensure_ascii=False, sort_keys=False)
 
class SavesAsList:

    @classmethod
    def from_json(cls, data):
        return cls(json.loads(data))

    def __json__(self):
        return json.dumps(self, indent=0, ensure_ascii=False, sort_keys=False)

class BetterTypesEncoder(json.JSONEncoder):

    def default(self, obj):
        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError as e:
            try:
                return obj.strftime("%Y-%m-%d %H:%M:%S")
            except AttributeError:
                if isinstance(obj, (collections.deque,)):
                    return list(obj)
                elif isinstance(obj, (decimal.Decimal, )):
                    return str(obj)
                elif isinstance(obj, type(re.compile(""))):
                    return obj.pattern
                else:
                    raise e


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


def obj_to_odict(obj):
    rv = collections.OrderedDict([
        ("_type", ".".join((dict(inspect.getmembers(obj)).get(
            "__module__",
            type(obj).__name__
        ),
        obj.__class__.__name__))),
    ])
    try:
        rv.update(obj._asdict())
    except AttributeError:
        try:
            rv.update(vars(obj))
        except TypeError:
            warnings.warn("{} not surviving.".format(obj))
    return rv


def type_dict(*args, namespace=None):
    """
    Returns a dictionary of types stored by their fully-qualified name. This
    can be used to de-serialise a stored mapping to its declared type.

    Such types must support call semantics with keyword arguments. If this is
    not possible (as in the case of Enums), then define a classmethod called `factory`
    which will be registered instead.

    """
    tmplt = "{module}.{name}" if namespace is None else "{namespace}.{module}.{name}"
    return {
        tmplt.format(
            namespace=namespace,
            module=dict(inspect.getmembers(i)).get("__module__"),
            name=i.__name__): getattr(i, "factory", i) for i in args}

def gather_installed(key):
    for i in pkg_resources.iter_entry_points(key):
        try:
            ep = i.resolve()
        except Exception as e:
            continue
        else:
            yield (i.name, ep)
