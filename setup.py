#!/usr/bin/env python

from setuptools import setup

install_requires = [
    'six>=1.6.1',
    'requests>=2.9.1',
    'responses>=0.5.0',
    'pydub>=0.16.0',
    'apscheduler>=3.0.5'
]

setup(
    name="typecaster",
    version="0.1.0",
    author="Neil Bedi",
    author_email="neilbedi@gmail.com",
    description=("Dynamically generate podcasts from text."),
    license="MIT",
    keywords="podcast",
    url="https://github.com/nbedi/typecaster",
    packages=['typecaster'],
    long_description=open('README.rst').read(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    install_requires=install_requires
)
