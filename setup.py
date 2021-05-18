import sys
from pkg_resources import VersionConflict, require
from setuptools import setup, find_packages

try:
    require('setuptools>=38.3')
except VersionConflict:
    print("Error: version of setuptools is too old (<38.3)!")
    sys.exit(1)

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="pycoornet",
    version="0.6.0",
    description="Using Python Given a set of URLs, this packages detects coordinated link sharing behavior on social media and outputs the network of entities that performed such behaviour.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author = 'Camilo Andres Soto Montoya, Jose R. Zapata',
    author_email = 'camilo.soto@outlook.com, jjrzg@hotmail.com',

    url="https://github.com/UPB-SS1/PyCooRnet",
    packages=find_packages(where='src' ,exclude=["tests", "*.test", "*.tes.*"]),
    package_dir={
        '': 'src',
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    keywords="pyCooRnet",
    license="MIT",
    test_suite="tests",
    install_requires=[
          'pandas>=1.0.5',
          'PyCrowdTangle>=0.5.0',
          'tqdm>=4.47.0',
          'networkx>=2.4',
          'python-louvain>=0.14',
          'tldextract>=3.1.0',
          'pyarrow>=4.0.0',
          'ratelimiter>= 1.2.0'
      ],
)
