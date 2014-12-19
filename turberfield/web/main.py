#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-
#

import argparse
from collections import namedtuple
from collections import OrderedDict
import datetime
import glob
import json
import logging
import operator
import os
import os.path
import sys
import tempfile
import time

import bottle
from bottle import Bottle
import pkg_resources

from turberfield.positions import __version__
#import turberfield.project


DFLT_LOCN = os.path.expanduser(os.path.join("~", ".turberfield"))

__doc__ = """
Serves a graphical web interface for Turberfield positions.
"""

Item = namedtuple("Item", ["pos", "name"])

bottle.TEMPLATE_PATH.append(
    pkg_resources.resource_filename("turberfield.web", "templates")
)

app = Bottle()

@app.route("/", "GET")
@bottle.view("simulation")
def simulation_get():
    log = logging.getLogger("turberfield.web.home")

    data = pkg_resources.resource_string(
        "turberfield.web", "static/rson/demo.rson"
    )
    log.info("Loading demo data")

    #steps = list(turberfield.project.load(data))
    return {
        "info": {
            "args": app.config.get("args"),
            "debug": bottle.debug,
            "interval": 200,
            "time": "{:.1f}".format(time.time()),
            "title": "Turberfield positions {}".format(__version__),
            "version": __version__
        },
    #    "items": OrderedDict([(str(id(i)), i) for i in steps]),
        
    }

@app.route("/positions")
def positions():
    x = int(50 + 4 * time.time() % 200)
    items = [
        Item((x, 80), "Alice"),
        Item((x, 120), "Bobby"),
    ]
    return {
        "info": {
            "args": app.config.get("args"),
            "debug": bottle.debug(),
            "interval": 200,
            "time": "{:.1f}".format(time.time()),
            "title": "Turberfield positions {}".format(__version__),
            "version": __version__
        },
        "items": [i._asdict() for i in items],
        
    }

@app.route("/css/<filename>")
def server_static(filename):
    locn = os.path.join(os.path.dirname(__file__), "static", "css")
    return bottle.static_file(filename, root=locn)

@app.route("/js/<filename>")
def server_static(filename):
    locn = os.path.join(os.path.dirname(__file__), "static", "js")
    return bottle.static_file(filename, root=locn)

def main(args):
    log = logging.getLogger("turberfield.web")
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

    bottle.debug(True)
    bottle.TEMPLATES.clear()
    log.debug(bottle.TEMPLATE_PATH)
    app.config.update({
        "args": vars(args)
    })
    bottle.run(app, host="localhost", port=8080)


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
