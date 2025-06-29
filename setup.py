#!/usr/bin/env python3
"""
Setup configuration for Paguro Boost
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="paguro-boost",
    version="2.0.0",
    author="Paguro Team",
    author_email="team@paguroboost.com",
    description="Cross-platform system optimizer with retro GUI interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/paguro-team/paguro-boost",
    packages=find_packages(exclude=['tests*', 'scripts*']),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: System Shells",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "paguro-boost=paguro_boost.app:main",
            "paguro-boost-gui=paguro_boost.gui:main",
            "paguro-boost-cli=paguro_boost.app:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="system optimizer performance ram disk startup retro gui",
    test_suite='tests.test_paguro_boost',
)