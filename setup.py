#!/usr/bin/env python3
# MobilNumTrack — setup.py
# Run:  python3 setup.py install
#       pip3 install .

from setuptools import setup, find_packages

setup(
    name="MobilNumTrack",
    version="4.0",
    description="Advanced Mobile Number Address & OSINT Tracker — Zero Login, Zero Key",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="MobilNumTrack Project",
    url="https://github.com/yourusername/MobilNumTrack",
    license="MIT",
    py_modules=["MobilNumTrack"],
    python_requires=">=3.8",
    install_requires=[
        "phonenumbers>=8.13.0",
        "requests>=2.28.0",
        "pytz>=2023.3",
    ],
    entry_points={
        "console_scripts": [
            "mobilnumtrack=MobilNumTrack:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: Internet",
    ],
)
