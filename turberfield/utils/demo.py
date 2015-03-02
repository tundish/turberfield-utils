#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

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
from collections import OrderedDict
import decimal
import itertools
import logging
from logging.handlers import WatchedFileHandler
import os
import os.path
import random
import sys
import uuid

from turberfield.common.inventory import Inventory

from turberfield.utils import __version__
from turberfield.utils.company import Company
from turberfield.utils.homogeneous import point
from turberfield.utils.expert import Fixed
from turberfield.utils.expert import Mobile
from turberfield.utils.shifter import Shifter
from turberfield.utils.stage import Stage
from turberfield.utils.travel import steadypace
from turberfield.utils.travel import trajectory

DFLT_LOCN = os.path.expanduser(os.path.join("~", ".turberfield"))

__doc__ = """
Provides a demonstration of Turberfield stages.
"""

Item = namedtuple("Item", ["uuid", "label", "class_"])


class Simulation:

    # TODO: populate stages with bus driver and travellers

    path = "demo.json"
    posns = OrderedDict([
        ("nw", point(160, 100, 0)),
        ("ne", point(484, 106, 0)),
        ("se", point(478, 386, 0)),
        ("sw", point(160, 386, 0)),
    ])

    patterns = [
        (Item(uuid.uuid4().hex, "Bus", "platform"),
         itertools.cycle(
            zip(posns.values(),
            list(posns.values())[1:] + [posns["nw"]])
         ),
        itertools.repeat(decimal.Decimal(24))
        ),
    ]

    static = [
        (Item(uuid.uuid4().hex, "A", "zone"), point(285, 60, 0), 45),
        (Item(uuid.uuid4().hex, "B", "zone"), point(530, 245, 0), 50),
        (Item(uuid.uuid4().hex, "C", "zone"), point(120, 245, 0), 42),
    ]

    npcs = [Inventory.Character(i, uuid.uuid4().hex, random.random())
            for i in ["Andy Riley", "Desmond Coyle", "George Byrne",
            "David Nicholson", "Declan Lynch", "Ken Sweeney",
            "Neil Hannon", "Keith Cullen", "Ciaran Donnelly",
            "Mick McEvoy", "Jack White", "Henry Bigbigging",
            "Hank Tree", "Hiroshima Twinkie" "Stig Bubblecard",
            "Johnny Hellzapoppin", "Luke Duke", "Billy Ferry",
            "Chewy Louie", "John Hoop", "Hairycake Liner",
            "Rebulah Conundrum", "Peewee Stairmaster",
            "Jemima Racktool", "Jerry Twig", "Spodo Komodo",
            "Cannabranna Lammer", "Todd Unctious"]
           ]

def main(args):
    log = logging.getLogger("turberfield.demo.run")
    log.setLevel(args.log_level)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-7s %(name)s|%(message)s")
    ch = logging.StreamHandler()

    if args.log_path is None:
        ch.setLevel(args.log_level)
    else:
        fh = WatchedFileHandler(args.log_path)
        fh.setLevel(args.log_level)
        fh.setFormatter(formatter)
        log.addHandler(fh)
        ch.setLevel(logging.WARNING)

    ch.setFormatter(formatter)
    log.addHandler(ch)

    theatre = OrderedDict([
            (stage, Mobile(
                steadypace(trajectory(), routing, timing),
                10)
            )
            for stage, routing, timing in Simulation.patterns])
    theatre.update(
        OrderedDict([
            (stage, Fixed(posn, reach))
            for stage, posn, reach in Simulation.static]))

    kwargs = Shifter.options(parent=args.output)
    shifter = Shifter(theatre, **kwargs)

    positions = {
        p: random.choice([Stage(i.uuid) for i in theatre])
        for p in Simulation.npcs}
    pockets = defaultdict(Counter)

    kwargs = Company.options(parent=args.output)
    # TODO: args = (PipeQueue.pipequeue(path), )
    company = Company(positions, pockets, **kwargs)

    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.Task(shifter(
            0, decimal.Decimal("Infinity"), 1, loop=loop)
        ),
        asyncio.Task(company(loop=loop)),
    ]
    loop.run_until_complete(asyncio.wait(asyncio.Task.all_tasks(loop)))


def parser(descr=__doc__):
    rv = argparse.ArgumentParser(description=descr)
    rv.add_argument(
        "--version", action="store_true", default=False,
        help="Print the current version number")
    rv.add_argument(
        "-v", "--verbose", required=False,
        action="store_const", dest="log_level",
        const=logging.DEBUG, default=logging.INFO,
        help="Increase the verbosity of output")
    rv.add_argument(
        "--log", default=None, dest="log_path",
        help="Set a file path for log output")
    rv.add_argument(
        "--output", default=DFLT_LOCN,
        help="path to output directory [{}]".format(DFLT_LOCN))
    return rv


def run():
    p = parser()
    args = p.parse_args()
    if args.version:
        sys.stdout.write(__version__ + "\n")
        rv = 0
    else:
        try:
            os.mkdir(args.output)
        except OSError:
            pass
        rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
