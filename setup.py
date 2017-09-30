"""
neoasynchttpy
------


"""
import sys
from setuptools import setup, find_packages


install_requires = [
    'aiohttp',
]

# get the version information
exec(open('neoasynchttpy/version.py').read())

setup(
    name = 'vertex',
    packages = find_packages(),
    version = __version__,
    description = 'Async REST client for Neo4j',
    url = 'https://github.com/emehrkay/neoasynchttpy',
    author = 'Mark Henderson',
    author_email = 'emehrkay@gmail.com',
    long_description = __doc__,
    install_requires = install_requires,
    classifiers = [
    ],
    test_suite = 'vertex.test',
)
