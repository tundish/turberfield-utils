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
import concurrent.futures
import datetime
from decimal import Decimal as Dl
import json
import logging
from logging.handlers import WatchedFileHandler
import operator
import os
import os.path
import sys
import time

import bottle
from bottle import Bottle
import pkg_resources

from turberfield.positions import __version__
import turberfield.positions.demo
#import turberfield.project


DFLT_LOCN = os.path.expanduser(os.path.join("~", ".turberfield"))

__doc__ = """
Serves a graphical web interface for Turberfield positions.
"""

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
    # TODO: get data endpoints from job in config and
    #       pass to template as items.
    return {
        "info": {
            "args": app.config.get("args"),
            "debug": bottle.debug,
            "interval": 200,
            "time": "{:.1f}".format(time.time()),
            "title": "Turberfield positions {}".format(__version__),
            "version": __version__
        },
    # TODO: "items": actor RTEs
        
    }

@app.route("/css/<filename>")
def serve_css(filename):
    locn = os.path.join(os.path.dirname(__file__), "static", "css")
    return bottle.static_file(filename, root=locn)

@app.route("/js/<filename>")
def serve_js(filename):
    locn = os.path.join(os.path.dirname(__file__), "static", "js")
    return bottle.static_file(filename, root=locn)

@app.route("/data/<filename>")
def serve_data(filename):
    bottle.request.environ["HTTP_IF_MODIFIED_SINCE"] = None
    locn = app.config["args"].output
    response  = bottle.static_file(filename, root=locn)
    response.expires = os.path.getmtime(locn)
    response.set_header("Cache-control", "max-age=0")
    return response

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

    # TODO: discover endpoints from each publisher
    # TODO: positions, collisions, accounts, inventory, relationships
    # TODO: standardise call (remove special parameters)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future = executor.submit(
            turberfield.positions.demo.run,
        )
        app.config.update({
            "args": args,
            "jobs": set([future]),
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
