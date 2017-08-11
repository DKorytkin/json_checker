from setuptools import setup

import codecs


setup(
    name="Checker",
    version="1.0",
    author="Denis Korytkin",
    author_email="dkorytkin@gmail.com",
    description="Simple data validation library",
    keywords="Json checker from auto tests",
    url="https://github.com/DKorytkin/Checker",
    py_modules=['checker'],
    long_description=codecs.open('README.rst', 'r', 'utf-8').read(),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
    ],
)
