#!/usr/bin/env python
# encoding: UTF-8

import ast
import os.path

from setuptools import setup


try:
    # Includes bzr revsion number
    from turberfield.positions.about import version
except ImportError:
    try:
        # For setup.py install
        from turberfield.positions import __version__ as version
    except ImportError:
        # For pip installations
        version = str(ast.literal_eval(
                    open(os.path.join(os.path.dirname(__file__),
                    "turberfield", "positions", "__init__.py"),
                    'r').read().split("=")[-1].strip()))

__doc__ = open(os.path.join(os.path.dirname(__file__), "README.txt"),
               'r').read()

setup(
    name="turberfield-positions",
    version=version,
    description="Semantic web-based movement for interactive storytelling.",
    author="D Haynes",
    author_email="tundish@thuswise.org",
    url="https://www.assembla.com/spaces/turberfield/messages",
    long_description=__doc__,
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: GNU Affero General Public License v3"
        " or later (AGPLv3+)"
    ],
    namespace_packages=["turberfield"],
    packages=[
        "turberfield.positions",
        "turberfield.positions.test",
        "turberfield.web",
    ],
    package_data={
        "turberfield.positions": [
            "doc/*.rst",
            "doc/_templates/*.css",
            "doc/html/*.html",
            "doc/html/*.js",
            "doc/html/_sources/*",
            "doc/html/_static/css/*",
            "doc/html/_static/font/*",
            "doc/html/_static/js/*",
            "doc/html/_static/*.css",
            "doc/html/_static/*.gif",
            "doc/html/_static/*.js",
            "doc/html/_static/*.png",
            ],
        "turberfield.web": [
            "static/css/*.css",
            "static/css/*/*.css",
            "static/img/*.jpg",
            "static/img/*.png",
            "static/js/*.js",
            "static/rson/*.rson",
            "templates/*.tpl",
        ]
    },
    install_requires=[
        "bottle>=0.12.7",
        "rson>=0.9",
        ],
    tests_require=[
        ],
    entry_points={
        "console_scripts": [
            "turberfield-demo = turberfield.web.main:run",
        ],
        "turberfield.component.task": [
        ],
    },
    zip_safe=False
)


