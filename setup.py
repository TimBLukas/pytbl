from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent
usage = here / "USAGE.md"

setup(
    name="pytbl",
    version="0.0.1",
    description="A personal library for stuff i got tired of doing again and again",
    long_description=open(usage).read(),
    long_description_content_type="text/markdown",
    author="TBL",
    author_email="tim.b.lukas@gmail.com",
    packages=find_packages(),
    install_requires=["pytest"],
    license="GPL-3.0-or-later",
    python_requires=">=3.10",
)
