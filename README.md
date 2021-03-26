# Metar-py

Metar.py is a simple python library that simplifies downloading METAR data from NOAA's [Aviation Weather Center](https://www.aviationweather.gov/metar). METAR's are partially decoded and presented as python dictionaries allowing for easy use in other aplications.

## Installation

Clone repository and run in `metar-py` directory.

```
python -m pip install .
```

## Usage

Import and create `Metar()` object.

```python
from metar.metar import Metar

m = Metar()
r = m.get_metar('ICAO') # ICAO airport code, eg. EPKK
print(r)
```

## Running the tests

Test only require python's default test `unittest` package. Run with following command

```
python -m unittest tests/tests.py
```
