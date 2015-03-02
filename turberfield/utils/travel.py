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


from collections import deque
from collections import namedtuple
import decimal
from decimal import Decimal as Dl
import itertools
import logging
import warnings

from turberfield.utils.homogeneous import vector


Impulse = namedtuple("Impulse", ["tBegin", "tEnd", "accn", "pos"])
Tick = namedtuple("Tick", ["t", "priority"])
Stop = namedtuple("Stop", ["t", "priority"])

"""
A Simple
Time-Corrected Verlet
Integration Method
Jonathan "lonesock" Dummer
http://lonesock.net/article/verlet.html
"""


def ticks(start, end, interval):
    """
    Returns a generator of
    :py:class:`Ticks <turberfield.dynamics.types.Tick>` which will
    end with a
    :py:class:`Stop <turberfield.dynamics.types.Stop>`.

    """
    return itertools.chain(
        (Tick(i, 0) for i in range(start, end, interval)),
        [Stop(end, 0)])


def time_correct_verlet(state, t, accn, mass=1):
    imp0, imp_1 = state
    dt0, dt_1 = (
        Dl(imp0.tBegin - imp0.tEnd),
        Dl(imp_1.tBegin - imp_1.tEnd)
    )
    leap = imp0.accn * dt0 * dt0
    try:
        pos = imp0.pos + (imp0.pos - imp_1.pos) * dt0 / dt_1 + leap
    except (ZeroDivisionError, decimal.InvalidOperation):
        pos = imp0.pos + (imp0.pos - imp_1.pos) + leap
    rv = Impulse(imp0.tEnd, t, accn, pos)
    return (rv, imp0)


def trajectory(limits=None):
    state = deque([], maxlen=2)
    if len(state) == 0:
        imp = yield None
        state.appendleft(imp)
        imp = yield state[0]
        state.appendleft(imp)
        imp = yield state[0]
        state = time_correct_verlet(state, imp.tEnd, imp.accn)
        imp = yield state[0]
    while True:
        if imp.pos != state[0].pos:
            state = (imp, state[0])
        else:
            state = time_correct_verlet(state, imp.tEnd, imp.accn)
        imp = yield state[0]


# TODO: Move out of utils to turberfield.machina
def steadypace(integrator, routing, timing, tol=1):
    log = logging.getLogger("turberfield.utils.travel.steadypace")
    accn = vector(0, 0, 0)
    integrator.send(None)
    tBegin = yield None
    tEnd = yield None
    origin, destn = next(routing)
    tTransit = next(timing)
    imp = integrator.send(Impulse(tBegin, tEnd, accn, origin))
    hop = (destn - origin) * Dl(tEnd - tBegin) / tTransit
    tBegin, tEnd = tEnd, (yield imp)
    imp = integrator.send(Impulse(tBegin, tEnd, accn, origin + hop))
    while True:
        tBegin, tEnd = tEnd, (yield imp)
        dist = (destn - imp.pos).magnitude
        if dist < tol:
            origin, destn = next(routing)
            tTransit = next(timing)
            hop = (destn - origin) * (tEnd - tBegin) / tTransit
            imp = integrator.send(
                Impulse(tBegin, tEnd, accn, origin + hop)
            )
        else:
            imp = integrator.send(
                Impulse(tBegin, tEnd, accn, imp.pos)
            )
