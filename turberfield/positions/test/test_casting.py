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

import abc
from collections import namedtuple
import enum
import unittest
import uuid

from turberfield.common.schema import NPC
from turberfield.common.schema import Player

@enum.unique
class Commodity(enum.Enum):
    COIN = "coin"
    SCRP = "scrip"

@enum.unique
class TradePosition(enum.Enum):

    buying = "buying"
    selling = "selling"

Role = namedtuple("Role", ["name", "description"])

class Scene(metaclass=abc.ABCMeta):

    def __init__(self):
        pass

    @property
    @abc.abstractmethod
    def casting(self):
        pass

class PayingOff(Scene):
    """
    This scene can be played every time a worker in a scrip system wants
    to cash in his tokens for coin.
    """

    sellout = Role("sellout", None)
    broker = Role("broker", None)

    @property
    def casting(self):
        return {
            frozenset([
            (Commodity.COIN, frozenset([TradePosition.buying])),
            (Commodity.SCRP, frozenset([TradePosition.selling]))]): PayingOff.sellout,
            frozenset([
            (Commodity.COIN, frozenset([TradePosition.selling])),
            (Commodity.SCRP, frozenset([TradePosition.buying]))]): PayingOff.broker,
        }

    def __call__(self, sellout, broker):
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

actors = {
    NPC(uuid.uuid4().hex, "worker #01", 0, 0, 0, 0.1): {
        Commodity.COIN: [TradePosition.buying],
        Commodity.SCRP: [TradePosition.selling],
    },
    NPC(uuid.uuid4().hex, "worker #02", 0, 0, 0, 0.2): {},
    NPC(uuid.uuid4().hex, "worker #03", 0, 0, 0, 0.3): {},
    NPC(uuid.uuid4().hex, "worker #04", 0, 0, 0, 0.4): {},
    NPC(uuid.uuid4().hex, "worker #05", 0, 0, 0, 0.5): {},
    NPC(uuid.uuid4().hex, "worker #06", 0, 0, 0, 0.6): {},
    NPC(uuid.uuid4().hex, "worker #07", 0, 0, 0, 0.7): {},
    Player(uuid.uuid4().hex, "Alice", 0, 0, 0, "alice@wonderland.com"): {
    },
    Player(uuid.uuid4().hex, "Bob", 0, 0, 0, "bob.cratchet@mail.me"): {
    },
    Player(uuid.uuid4().hex, "Carl", 0, 0, 0, "carl@buttonmasher.net"): {
    },
}

class PrototypeCasting(unittest.TestCase):

    def test_role_discovery(self):
        self.assertIsInstance(PayingOff().casting, dict)

    def test_playing_the_scene(self):
        scene = PayingOff()
        with scene(sellout=None, broker=None) as performance:
            dialogue = list(performance)
            self.assertTrue(performance)
