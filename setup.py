from setuptools import setup, find_packages

setup(
    name='metar.py',
    version='1.0.dev1',
    description='Library allowing easy importing METAR data from NOAA\'s website.',
    author='Artur Michalek',
    package_dir={'': 'metar'},
    packages=find_packages(where='src'),
    python_requires='>=3.8.5',
    install_requires=['requests'],
)