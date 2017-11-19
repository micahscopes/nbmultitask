# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = ""

setup(
    name="nbmultitask",
    version="0.1.0",
    description="ipywidget controls for multitasking in Jupyter notebooks",
    license="MIT",
    author="Micah Fitch",
    packages=find_packages(),
    install_requires=[],
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
    ],
    py_modules=['nbmultitask']

)
