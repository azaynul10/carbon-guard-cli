#!/usr/bin/env python3
"""Setup configuration for carbon-guard-cli."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="carbon-guard-cli",
    version="1.0.0",
    author="Carbon Guard Team",
    author_email="team@carbonguard.com",
    description="A CLI tool for carbon footprint monitoring and optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/carbonguard/carbon-guard-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "boto3>=1.26.0",
        "botocore>=1.29.0",
        "requests>=2.28.0",
        "pillow>=9.0.0",
        "pytesseract>=0.3.10",
        "pandas>=1.5.0",
        "pyyaml>=6.0",
        "rich>=12.0.0",
        "psutil>=5.9.0",
        "docker>=6.0.0",
        "moto>=4.2.0",  # Required for --mock flag functionality
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "carbon-guard=carbon_guard.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "carbon_guard": ["data/*.json", "templates/*.txt"],
    },
)
