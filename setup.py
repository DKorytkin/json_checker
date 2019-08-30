# -*- coding: utf-8 -*-

import codecs
from setuptools import setup, find_packages


setup(
    name="json_checker",
    version='2.0.0',
    author='Denis Korytkin',
    author_email='dkorytkin@gmail.com',
    description='Simple schema validation library',
    keywords=[
        'Json checker',
        'API testing',
        'requests testing',
        'json schema validation'
    ],
    url='https://github.com/DKorytkin/json_checker',
    platforms=['linux'],
    packages=find_packages(),
    license='MIT license',
    py_modules=[
        'json_checker.app',
        'json_checker.core.checkers',
        'json_checker.core.exceptions',
        'json_checker.core.reports',
    ],
    python_requires='>=3.6',
    long_description=codecs.open('README.rst', 'r', 'utf-8').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ],
)
