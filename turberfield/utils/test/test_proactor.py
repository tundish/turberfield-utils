import configparser
import datetime
import jwt
import multiprocessing
import signal


import io
import itertools
import textwrap
import unittest
"""
try:
    jwt.decode(token, secret, algorithms=['HS256'])
except jwt.ExpiredSignatureError:
    # Signature has expired
"""

def worker(config, token=None):
    pass

def config_parser(*sections, **defaults):
    rv = configparser.ConfigParser(
        defaults=defaults,
        allow_no_value=True,
        interpolation=configparser.ExtendedInterpolation()
    )

    if sections:
        rv.read_string("\n".join(sections))
    return rv

def create_token(key, session=None):
    now = datetime.datetime.utcnow()
    return jwt.encode(
        {
            "exp": now + datetime.timedelta(days=30),
            "iat": now,
            "session": session
        },
        key=key,
        algorithm="HS256"
    )

class ConfigTests(unittest.TestCase):

    def test_defaults(self):
        defaults = {"a": 1, "b": "two", "c": None}
        cfg = config_parser(**defaults)
        witness = io.StringIO()
        cfg.write(witness)
        for n, check, line in zip(
            itertools.count(),
            ["[DEFAULT]", "a = 1", "b = two", "c"],
            witness.getvalue().splitlines()
        ):
            with self.subTest(check=check):
                self.assertEqual(check, line)
        self.assertEqual(3, n)

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

class TokenTests(unittest.TestCase):

    def test_create(self):
        self.fail(create_token("testsecret"))

if __name__ == "__main__":
    pass
