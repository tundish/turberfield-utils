#!/usr/bin/env python3
#   encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.

import io
import textwrap
import unittest

from turberfield.utils.misc import config_parser


class ConfigTests(unittest.TestCase):

    def test_defaults(self):
        defaults = {"a": 1, "b": "two", "c": None}
        cfg = config_parser(**defaults)
        witness = io.StringIO()
        cfg.write(witness)
        for check in ["[DEFAULT]", "a = 1", "b = two", "c"]:
            with self.subTest(check=check):
                self.assertIn(check, witness.getvalue().splitlines())

    def test_section(self):
        section = textwrap.dedent("""
        [section.one]
        root = /home

        [section.two]
        path = ${section.one:root}/tmp
        """)
        cfg = config_parser(section)
        self.assertEqual("/home/tmp", cfg["section.two"]["path"])

    def test_sections(self):
        sections = [
            "[section.one]\nroot = /home",
            "[section.two]\npath = ${section.one:root}/tmp"
        ]
        cfg = config_parser(*sections)
        self.assertEqual("/home/tmp", cfg["section.two"]["path"])

    def test_defaults_and_sections(self):
        defaults = {"a": 1, "b": "two", "c": None}
        sections = [
            "[section.one]\nroot = /home",
            "[section.two]\npath = ${section.one:root}/tmp",
            "[section.three]\npath = ${section.two:path}.${b}"
        ]
        cfg = config_parser(*sections, **defaults)
        self.assertEqual("/home/tmp.two", cfg["section.three"]["path"])
