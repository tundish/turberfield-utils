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

import decimal
from decimal import Decimal as Dl
import itertools
import unittest

from turberfield.positions.homogeneous import point
from turberfield.positions.homogeneous import vector
from turberfield.positions.travel import ticks
from turberfield.positions.travel import trajectory


class ProjectileTests(unittest.TestCase):

    def test_scalar_calculation(self):
        expected = [
            Dl("0"), Dl("29.41800004"), Dl("56.38450008"),
            Dl("80.89950012"), Dl("102.96300016"), Dl("122.5750002"),
            Dl("139.73550024"), Dl("154.44450028"), Dl("166.70200032"),
            Dl("176.50800036"), Dl("183.8625004"), Dl("188.76550044"),
            Dl("191.21700048"), Dl("191.21700052"), Dl("188.76550056"),
            Dl("183.8625006"), Dl("176.50800064"), Dl("166.70200068"),
            Dl("154.44450072"), Dl("139.73550076"), Dl("122.5750008"),
            Dl("102.96300084"), Dl("80.89950088"), Dl("56.38450092"),
            Dl("29.41800096"), Dl("0.000001")
        ]

        dt = Dl("0.5")
        g = Dl("-9.806")
        vel = Dl("61.28750008")
        posns = (0, vel * dt + Dl("0.5") * g * dt * dt)
        samples = (Dl(i.t / 10) for i in ticks(0, 130, 5))
        for n, x in enumerate(
            trajectory(
                samples, posns=posns, accns=itertools.repeat(g))
        ):
            with self.subTest(n=n):
                self.assertEqual(expected[n], x.pos)

    def test_point_calculation(self):
        expected = [point(i, 0, 0) for i in [
            Dl("0"), Dl("29.41800004"), Dl("56.38450008"),
            Dl("80.89950012"), Dl("102.96300016"), Dl("122.5750002"),
            Dl("139.73550024"), Dl("154.44450028"), Dl("166.70200032"),
            Dl("176.50800036"), Dl("183.8625004"), Dl("188.76550044"),
            Dl("191.21700048"), Dl("191.21700052"), Dl("188.76550056"),
            Dl("183.8625006"), Dl("176.50800064"), Dl("166.70200068"),
            Dl("154.44450072"), Dl("139.73550076"), Dl("122.5750008"),
            Dl("102.96300084"), Dl("80.89950088"), Dl("56.38450092"),
            Dl("29.41800096"), Dl("0.000001")]
        ]

        dt = Dl("0.5")
        g = vector(Dl("-9.806"), 0, 0)
        vel = vector(Dl("61.28750008"), 0, 0)
        posns = (
            point(0, 0, 0),
            point(0, 0, 0) + vel * dt + Dl("0.5") * g * dt * dt
        )
        samples = (Dl(i.t / 10) for i in ticks(0, 130, 5))
        for n, x in enumerate(
            trajectory(
                samples, posns=posns, accns=itertools.repeat(g))
        ):
            with self.subTest(n=n):
                self.assertEqual(expected[n], x.pos)


class PolynomialTests(unittest.TestCase):

    def test_scalar_calculation(self):
        expected = [
            Dl("0"), Dl("0.502656"), Dl("0.824448"), Dl("0.986112"),
            Dl("1.008384"), Dl("0.912"), Dl("0.717696"),
            Dl("0.446208"), Dl("0.118272"), Dl("-0.245376"),
            Dl("-0.624"), Dl("-0.996864"), Dl("-1.343232"),
            Dl("-1.642368"), Dl("-1.873536"), Dl("-2.016"),
            Dl("-2.049024"), Dl("-1.951872"), Dl("-1.703808"),
            Dl("-1.284096"), Dl("-0.672"), Dl("0.153216"),
            Dl("1.212288"), Dl("2.525952"), Dl("4.114944"), Dl("6")
        ]

        samples = (Dl(i.t / 100) for i in ticks(0, 300, 12))
        accns = [
            Dl("-14"), Dl("-12.56"), Dl("-11.12"), Dl("-9.68"),
            Dl("-8.24"), Dl("-6.8"), Dl("-5.36"), Dl("-3.92"),
            Dl("-2.48"), Dl("-1.04"), Dl("0.4"), Dl("1.84"),
            Dl("3.28"), Dl("4.72"), Dl("6.16"), Dl("7.6"), Dl("9.04"),
            Dl("10.48"), Dl("11.92"), Dl("13.36"), Dl("14.8"),
            Dl("16.24"), Dl("17.68"), Dl("19.12"), Dl("20.56"),
            Dl("22")
        ]

        posns = (Dl(0), Dl("0.502656"))
        for n, x in enumerate(
            trajectory(
                samples, posns=posns, accns=iter(accns))
        ):
            with self.subTest(n=n):
                self.assertEqual(
                    expected[n],
                    x.pos.quantize(Dl("0.00000000000001"))
                )

    def test_point_calculation(self):
        expected = [point(i, 0, 0) for i in [
            Dl("0"), Dl("0.502656"), Dl("0.824448"), Dl("0.986112"),
            Dl("1.008384"), Dl("0.912"), Dl("0.717696"),
            Dl("0.446208"), Dl("0.118272"), Dl("-0.245376"),
            Dl("-0.624"), Dl("-0.996864"), Dl("-1.343232"),
            Dl("-1.642368"), Dl("-1.873536"), Dl("-2.016"),
            Dl("-2.049024"), Dl("-1.951872"), Dl("-1.703808"),
            Dl("-1.284096"), Dl("-0.672"), Dl("0.153216"),
            Dl("1.212288"), Dl("2.525952"), Dl("4.114944"), Dl("6")]
        ]

        samples = (Dl(i.t / 100) for i in ticks(0, 300, 12))
        accns = [vector(i, 0, 0) for i in [
            Dl("-14"), Dl("-12.56"), Dl("-11.12"), Dl("-9.68"),
            Dl("-8.24"), Dl("-6.8"), Dl("-5.36"), Dl("-3.92"),
            Dl("-2.48"), Dl("-1.04"), Dl("0.4"), Dl("1.84"),
            Dl("3.28"), Dl("4.72"), Dl("6.16"), Dl("7.6"), Dl("9.04"),
            Dl("10.48"), Dl("11.92"), Dl("13.36"), Dl("14.8"),
            Dl("16.24"), Dl("17.68"), Dl("19.12"), Dl("20.56"),
            Dl("22")]
        ]

        posns = (
            point(Dl(0), Dl(0), Dl(0)),
            point(Dl("0.502656"), Dl(0), Dl(0))
        )

        with decimal.localcontext() as ctx:
            ctx.prec = 15
            for n, x in enumerate(
                trajectory(
                    samples, posns=posns, accns=iter(accns))
            ):
                with self.subTest(n=n):
                    self.assertEqual(expected[n], x.pos)
