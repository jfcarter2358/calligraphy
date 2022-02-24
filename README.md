# Caligraphy
---
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Shell scripting for the modern age**

Caligraphy is a hybrid scripting language that allows you to mix Python and Bash code
in the same file. This gives you the advantages of bash when working with other
processes while also giving you the advantages of a modern language like Python.

It's a free software distributed under the MIT Licence unless
otherwise specified.

Development is hosted on GitHub: https://github.com/jfcarter2358/caligraphy/

Pull requests are amazing and most welcome.

## Install

Caligraphy can be simply installed by running

```
pip install caligraphy
```

If you want to install from a source distribution, extract the tarball and run
the following command (this requires poetry to be installed)

```
poetry install --no-dev
```

## Documentation

The documentation lives at https://caligraphy.readthedocs.io/.

## Testing

We use `pytest` and `pytest-cov` for running the test suite. You should be able to install them with

```
pip install pytest pytest-cov
```

or you can install caligraphy alongside those packages with

```
poetry install
```

To run the test suite, you can do

```
make test
```

This will produce an html coverage report under the `htmlcov` directory.

## To Do

- [x] Add indentation to explain output
- [ ] Enable sourcing of other caligraphy scripts
- [ ] Token output flag

## License

Caligraphy is under the [MIT license](https://opensource.org/licenses/MIT).
