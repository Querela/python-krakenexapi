import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ) as fh:
        return fh.read()


setup(
    name="krakenexapi",
    version="0.0.0",
    license="MIT",
    description="A Kraken Exchange API adapter.",
    long_description="%s\n%s"
    % (
        re.compile("^.. start-badges.*^.. end-badges", re.M | re.S).sub(
            "", read("README.rst")
        ),
        re.sub(":[a-z]+:`~?(.*?)`", r"``\1``", read("CHANGELOG.rst")),
    ),
    long_description_content_type="text/x-rst",
    author="Erik Körner",
    author_email="ekdev@live.de",
    url="https://github.com/Querela/python-krakenexapi",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Utilities",
    ],
    project_urls={
        "Documentation": "https://python-krakenexapi.readthedocs.io/",
        "Changelog": "https://python-krakenexapi.readthedocs.io/en/latest/changelog.html",
        "Issue Tracker": "https://github.com/Querela/python-krakenexapi/issues",
    },
    keywords=[
        "kraken",
        "crypto",
        "api",
    ],
    python_requires=">=3.6",
    extras_require={},
)
