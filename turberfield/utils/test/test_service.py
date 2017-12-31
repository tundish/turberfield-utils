#!/usr/bin/env python
# encoding: UTF-8

# This file is part of Turberfield.
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
# along with Turberfield.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import unittest

from turberfield.utils.misc import config_parser
from turberfield.utils.service import Service

class ServiceTests(unittest.TestCase):

    def tearDown(self):
        Service._instance = None

    def test_singleton(self):
        a = Service(cfg=config_parser())
        b = Service.instance()
        self.assertIs(b, a)

    def test_settings_bad(self):

        class Invalid(Service):
            @classmethod
            def check_cfg(cls, cfg):
                return None

        rv = Invalid(cfg=config_parser())
        self.assertIsNone(rv.settings)

    def test_settings_good(self):
        cfg = config_parser()
        rv = Service(cfg=cfg)
        self.assertTrue(hasattr(rv, "settings"))
        self.assertIs(cfg, rv.settings)

    def test_events(self):

        class Clock(Service):

            @property
            @classmethod
            def value(cls):
                return cls._instance.val

            def __init__(self, *args, start=None, **kwargs):
                self.val = start

            def advance(self):
                self.val += datetime.timedelta(seconds=30)

        a = Clock(start=datetime.datetime.now(), cfg=config_parser())
        start = a.val
        a.advance()
        self.assertGreater(a.val, start)

        b = Clock.instance()
        self.assertGreater(b.val, start)
