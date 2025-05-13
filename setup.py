from setuptools import setup, find_packages

setup(
    name="heimdall",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyside6>=6.5.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "rpy2>=3.5.0",
        "pluggy>=1.0.0",
    ],
)