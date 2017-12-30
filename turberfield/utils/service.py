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


class ConfiguredSettings:

    @classmethod
    def check_cfg(cls, cfg):
        """Check the consistency of a mapping object. """
        return cfg

    def __init__(self, *args, **kwargs):
        self.settings = self.check_cfg(kwargs.pop("cfg"))
        super().__init__(*args, **kwargs)

class Service:

    @classmethod
    def instance(cls):
        return getattr(cls, "_instance", None)

    def __new__(cls, *args, **kwargs):
        if getattr(cls, "_instance", None) is None:
            cls._instance = super().__new__(cls)
        return cls.instance()
