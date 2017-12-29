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

import unittest

from turberfield.utils.misc import config_parser

class Service:

    @classmethod
    def check_cfg(cls, cfg):
        """Check the consistency of a mapping object. """
        return cfg

    def __new__(cls, cfg=None):
        if getattr(cls, "_instance", None) is None:
            settings = cls.check_cfg(cfg)
            if settings is not None:
                cls._instance = super().__new__(cls)
                cls._instance.settings = settings
        return getattr(cls, "_instance", None)

class ServiceTests(unittest.TestCase):

    def tearDown(self):
        Service._instance = None

    def test_singleton(self):
        a = Service(config_parser())
        b = Service(config_parser())
        self.assertIs(b, a)

    def test_settings_bad(self):

        class Invalid(Service):
            @classmethod
            def check_cfg(cls, cfg):
                return None

        cfg = config_parser()
        rv = Invalid(cfg)
        self.assertIsNone(rv)

    def test_settings_good(self):
        cfg = config_parser()
        rv = Service(cfg)
        self.assertTrue(hasattr(rv, "settings"))
        self.assertIs(cfg, rv.settings)
