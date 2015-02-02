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
from collections import Counter
from collections import defaultdict

__doc__ = """
Machina places an actor on a stage.
"""

class Props:
    """
    TODO: Move a base class to turberfield.common.inventory
    """ 

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
        if not hasattr(self, "pockets"):
            self.places = defaultdict(list)
            self.pockets = defaultdict(Counter)

    def _clear(self):
        try:
            del self.places
        except AttributeError:
            pass

        try:
            del self.pockets
        except AttributeError:
            pass

class Placement:

    @staticmethod
    def queue(loop=None):
        return asyncio.Queue(loop=loop)

    def __init__(self, theatre, props):
        self.theatre = theatre
        self.props = props

    @asyncio.coroutine
    def __call__(self, start, stop, step):
        pass
