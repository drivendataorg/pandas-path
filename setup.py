#!/usr/bin/env python
from pathlib import Path

import setuptools
from setuptools import setup


def load_reqs(path):
    reqs = []
    with open(path, "r") as f:
        for line in f.readlines():
            if line.startswith("-r"):
                reqs += load_reqs(line.split(" ")[1].strip())
            else:
                req = line.strip()
                if req and not req.startswith("#"):
                    reqs.append(req)
    return reqs


req_path = Path(__file__).parent / "requirements.txt"
requirements = load_reqs(req_path)

long_description = open(Path(__file__).parent / "README.md").read()


setup(
    name="pandas_path",
    url="https://github.com/drivendataorg/pandas-path",
    project_urls={
        "Source Code": "https://github.com/drivendataorg/pandas-path",
        "DrivenData": "http://drivendata.co",
    },
    version="0.3.0",
    author="DrivenData",
    author_email="info@drivendata.org",
    include_package_data=True,
    description="Pathlib functionality for pandas.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=setuptools.find_packages(),
    keywords=["data science"],
    python_requires=">=3.6",
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
