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

from collections import defaultdict
import itertools
import decimal
import inspect
import json
import logging
import logging.handlers
import os
import re
import warnings

import pkg_resources

_recordFactory = logging.getLogRecordFactory()

def record_factory(*args, **kwargs):
    record = _recordFactory(*args, **kwargs)
    record.pid = os.getpid()
    return record

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

def group_by_type(items):
    return defaultdict(list,
        {k: list(v) for k, v in itertools.groupby(items, key=type)}
    )

def gather_installed(key, log=None):
    for i in pkg_resources.iter_entry_points(key):
        try:
            ep = i.resolve()
        except Exception as e:
            if log is not None:
                log.warning(getattr(e, "args", e) or e)
        else:
            yield (i.name, ep)

def log_setup(args, name="turberfield", loop=None):
    logging.setLogRecordFactory(record_factory)
    log = logging.getLogger(name)

    log.setLevel(int(args.log_level))
    logging.getLogger("asyncio").setLevel(int(args.log_level))

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-7s|%(pid)s|%(name)s|%(message)s"
    )
    ch = logging.StreamHandler()

    if args.log_path is None:
        ch.setLevel(int(args.log_level))
    else:
        fh = logging.handlers.WatchedFileHandler(args.log_path)
        fh.setLevel(int(args.log_level))
        fh.setFormatter(formatter)
        log.addHandler(fh)
        ch.setLevel(logging.WARNING)

    if loop is not None and args.log_level == logging.DEBUG:
        try:
            loop.set_debug(True)
        except AttributeError:
            log.info("Upgrade to Python 3.4.2 for asyncio debug mode")
        else:
            log.info("Event loop debug mode is {}".format(loop.get_debug()))
    ch.setFormatter(formatter)
    log.addHandler(ch)
    return name
