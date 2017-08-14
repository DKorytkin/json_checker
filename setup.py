
import codecs
from setuptools import setup

import checker


setup(
    name=checker.__name__,
    version=checker.__version__,
    author="Denis Korytkin",
    author_email="dkorytkin@gmail.com",
    description="Simple data validation library",
    keywords="Json checker from auto tests",
    url="https://github.com/DKorytkin/Checker",
    py_modules=[checker.__name__],
    long_description=codecs.open('README.rst', 'r', 'utf-8').read(),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
    ],
)
