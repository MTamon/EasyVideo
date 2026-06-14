# -*- coding: utf-8 -*-

import re
from os import path
from setuptools import setup

NAME = "easy_video"
PACKAGES = ["easy_video"]
DESCRIPTION = "Wrap OpenCV package for make accessing video-file easier."
KEYWORDS = "opencv, wrapper, video I/O, video processing"

root_dir = path.abspath(path.dirname(__file__))


def _read_meta(name: str) -> str:
    """Read a metadata constant from the package __init__ without importing it
    (avoids requiring runtime dependencies such as cv2 at build time)."""
    init_path = path.join(root_dir, "easy_video", "__init__.py")
    with open(init_path, encoding="utf-8") as f:
        content = f.read()
    match = re.search(rf'^{name}\s*=\s*["\'](.+?)["\']', content, re.MULTILINE)
    if match is None:
        raise RuntimeError(f"Unable to find {name} in {init_path}")
    return match.group(1)


VERSION = _read_meta("VERSION")
LICENCE = _read_meta("LICENCE")
AUTHOR = _read_meta("AUTHOR")
EMAIL = _read_meta("EMAIL")
GIT_URL = _read_meta("GIT_URL")


def _requirements():
    return [
        name.rstrip()
        for name in open(
            path.join(root_dir, "requirements.txt"), encoding="utf-8"
        ).readlines()
    ]


def _test_requirements():
    return [
        name.rstrip()
        for name in open(
            path.join(root_dir, "test-requirements.txt"), encoding="utf-8"
        ).readlines()
    ]


assert VERSION
assert LICENCE
assert AUTHOR
assert EMAIL
assert GIT_URL

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()


setup(
    name=NAME,
    packages=PACKAGES,
    version=VERSION,
    license=LICENCE,
    install_requires=_requirements(),
    tests_require=_test_requirements(),
    author=AUTHOR,
    author_email=EMAIL,
    url=GIT_URL,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=KEYWORDS,
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
