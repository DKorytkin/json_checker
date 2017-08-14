
import codecs
from setuptools import setup

import checker


setup(
    name=checker.__name__,
    version=checker.__version__,
    author='Denis Korytkin',
    author_email='dkorytkin@gmail.com',
    description='Simple data validation library',
    keywords='Json checker from auto tests',
    url='https://github.com/DKorytkin/Checker',
    py_modules=['checker', 'checker_exceptions'],
    python_requires='=2.7, =3.3, =3.4, =3.5, =3.6',
    long_description=codecs.open('README.rst', 'r', 'utf-8').read(),
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
