from setuptools import setup, find_packages

setup(
    name='metar.py',
    version='1.0.dev2',
    description='Library allowing easy importing METAR data from NOAA\'s website.',
    author='Artur Michalek',
    packages=find_packages(),
    python_requires='>=3.8.5',
    install_requires=['requests'],
)