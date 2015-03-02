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

import asyncio
from collections import OrderedDict
import os

from turberfield.utils.expert import Expert

class Company(Expert):
    """
            # TODO:
            # 1. Look up collision by id
            # 2. Check timeframe acceptable
            # 3. Check actor is on stage
            # 4. Check destination valid
            # 5. Perform move to destination
    """

    @staticmethod
    def options(
        parent=os.path.expanduser(os.path.join("~", ".turberfield"))
    ):
        return OrderedDict([
            ("players", Expert.Attribute("players")),
            ("company", Expert.HATEOAS(
                "company",
                "players",
                os.path.join(parent, "company.json"))
            ),
        ])

    def __init__(self, positions, pockets, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._positions = positions # Actor: turberfield.utils.Stage
        self._pockets = pockets  # Actor: (Commodity: n)

    @asyncio.coroutine
    def __call__(self, loop=None):
        pass

    @asyncio.coroutine
    def watch(self, q, **kwargs):
        loop = kwargs.pop("loop", None)
