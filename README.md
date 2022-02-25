# Calligraphy
---
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Shell scripting for the modern age**

Calligraphy is a hybrid scripting language that allows you to mix Python and Bash code
in the same file. This gives you the advantages of bash when working with other
processes while also giving you the advantages of a modern language like Python.

It's a free software distributed under the MIT Licence unless
otherwise specified.

Development is hosted on GitHub: https://github.com/jfcarter2358/calligraphy/

Pull requests are amazing and most welcome.

## Install

Calligraphy can be simply installed by running

```
pip install calligraphy
```

If you want to install from a source distribution, extract the tarball and run
the following command (this requires poetry to be installed)

```
poetry install --no-dev
```

## Documentation

The documentation lives at https://calligraphy.readthedocs.io/.

## Testing

We use `pytest` and `pytest-cov` for running the test suite. You should be able to install them with

```
pip install pytest pytest-cov
```

or you can install calligraphy alongside those packages with

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
    - When using the explain flag the resulting annotated code isn't indented. This can make it hard to read considering that indentation matters in Python and Calligraphy, so we should include that in our output.
- [ ] Enable sourcing of other calligraphy scripts
    - In order to make Calligraphy more useful, we need to end the limitation of only one source file. A `source` directive should be introduced which allows other Calligraphy scripts to be imported.
- [ ] Token output flag
    - It's useful to be able to see the token representaion of a source file when debugging, therefore we should add a flag which outputs said representation.
- [ ] Windows shell support
    - Currently when a shell command is run it adds `printenv` at the end in order to capture environment changes. We need to detect which OS is being run on and use `set` in its place on Windows.



## License

Calligraphy is under the [MIT license](https://opensource.org/licenses/MIT).
