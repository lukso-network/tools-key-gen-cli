from setuptools import find_packages, setup

"""
THIS IS A STUB FOR RUNNING THE APP
"""

setup(
    name="staking_deposit",
    version='2.3.1-develop.1',
    py_modules=["staking_deposit"],
    packages=find_packages(exclude=('tests', 'docs')),
    python_requires=">=3.8,<4",
)
