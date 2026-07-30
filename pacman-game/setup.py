"""Setup script for Hello Kitty Maze Game."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="hello-kitty-maze",
    version="1.0.0",
    description="A cute Hello Kitty-themed Pac-Man game "
    "built with Python and Pygame",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Egjinaj Shajdar",
    author_email="student@42school.fr",
    url="https://github.com/42school/hello-kitty-maze",
    license="MIT",
    python_requires=">=3.9",
    install_requires=[
        "pygame>=2.1.0",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "hello-kitty-maze=game.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment",
    ],
)
