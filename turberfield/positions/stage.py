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

from collections import namedtuple
from collections import OrderedDict
from collections.abc import MutableMapping

from altgraph.Graph import Graph
 

class Stage(MutableMapping):

    Contact = namedtuple("Contact", ["view", "throw", "hear", "reach"])

    class Directions():

        def __init__(self, stage, obj):
            self.stage = stage
            self.obj = obj

        def contact(self, field):
            graph = self.stage.placement
            return [graph.tail(e) for e in graph.out_edges(self.obj)
                    if getattr(graph.edge_data(e), field, None)]

        def can_contact(
            self,
            *args,
            fact=True, mutual=False,
            new=None, replace=None
        ):
            graph = self.stage.placement
            for i in args:
                other = self.stage[i]
                jobs = [(self.obj, other.obj)]
                if mutual:
                    jobs.append((other.obj, self.obj))

                for a, b in jobs:
                    edge = graph.edge_by_node(a, b)
                    if fact and edge is None:
                        graph.add_edge(a, b, new)
                    else:
                        data = graph.edge_data(edge)
                        update = data._replace(
                            **{k: fact for k in replace}
                        )
                        graph.update_edge_data(edge, update)

        @property
        def hearing(self):
            return self.contact("hear")

        @property
        def throw(self):
            return self.contact("throw")

        @property
        def reach(self):
            return self.contact("reach")

        @property
        def view(self):
            return self.contact("view")

        def can_hear(self, *args, fact=True, mutual=False):
            return self.can_contact(
                *args, fact=fact, mutual=mutual,
                new=Stage.Contact(False, False, True, False),
                replace=["throw", "hear"])

        def can_reach(self, *args, fact=True, mutual=False):
            return self.can_contact(
                *args, fact=fact, mutual=mutual,
                new=Stage.Contact(True, True, True, True),
                replace=["reach"])

        def can_see(self, *args, fact=True, mutual=False):
            return self.can_contact(
                *args, fact=fact, mutual=mutual,
                new=Stage.Contact(True, False, False, False),
                replace=["see"])

        def can_throw(self, *args, fact=True, mutual=False):
            return self.can_contact(
                *args, fact=fact, mutual=mutual,
                new=Stage.Contact(True, True, False, False),
                replace=["throw"])

    def __init__(self, boundary=None, scenes=None):
        self.placement = Graph()
        self.boundary = boundary

    def __len__(self):
        return self.placement.number_of_nodes()

    def __iter__(self):
        return self.placement.__iter__()

    def __delitem__(self, key):
        node, direction, in_, out_ = self.placement.describe_node(key)
        for edge in in_ + out_:
            contact = self.placement.edge_data(edge)
            del contact
        del direction
        self.placement.hide_node(node)

    def __getitem__(self, key):
        if key not in self.placement:
            self[key] = Stage.Directions(self, key)
        return self.placement.describe_node(key)[1]

    def __setitem__(self, key, val):
        if isinstance(val, Stage.Directions):
            self.placement.add_node(key, val)
