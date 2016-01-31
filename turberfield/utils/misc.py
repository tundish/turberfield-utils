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


def gather_installed(key):
    for i in pkg_resources.iter_entry_points(key):
        try:
            ep = i.resolve()
        except Exception as e:
            continue
        else:
            yield (i.name, ep)
