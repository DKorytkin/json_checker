# -*- coding: utf-8 -*-

import codecs
from setuptools import setup, find_packages


setup(
    name="json_checker",
    version='1.2.3',
    author='Denis Korytkin',
    author_email='dkorytkin@gmail.com',
    description='Simple data validation library',
    keywords=['Json checker', 'API testing', 'requests testing'],
    url='https://github.com/DKorytkin/json_checker',
    platforms=['linux'],
    packages=find_packages(),
    license='MIT license',
    py_modules=[
        'json_checker.app',
        'json_checker.exceptions'
    ],
    install_requires=['six>=1.10.0'],
    python_requires='>=2.7',
    long_description=codecs.open('README.rst', 'r', 'utf-8').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ],
)
