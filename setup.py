# -*- coding: utf-8 -*-

import codecs
from setuptools import setup, find_packages

import json_checker


setup(
    name="json_checker",
    version=json_checker.__version__,
    author=json_checker.__author__,
    author_email='dkorytkin@gmail.com',
    description='Simple data validation library',
    keywords='Json checker, API testing',
    url='https://github.com/DKorytkin/json_checker',
    packages=find_packages(),
    py_modules=[
        'json_checker.app',
        'json_checker.exceptions'
    ],
    install_requires=['six==1.11.0'],
    python_requires='>=2.7',
    long_description=codecs.open('README.rst', 'r', 'utf-8').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
