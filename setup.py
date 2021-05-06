#!/usr/bin/env python

from setuptools import setup, find_packages

desc = """StoryGraph Bot (description coming...)"""

__appversion__ = None

#__appversion__, defined here
exec(open('storygraph_bot/version.py').read())

setup(
    name='storygraph_bot',
    version=__appversion__,
    description=desc,
    long_description='See: https://github.com/oduwsdl/storygraphbot',
    author='Kritika Garg and Alexander C. Nwala',
    author_email='kgarg.kritika@gmail.com',
    url='https://github.com/oduwsdl/storygraphbot',
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        'tweepy'
    ],
    scripts=[
        'bin/sgbot'
    ]
)
