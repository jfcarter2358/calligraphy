# Calligraphy
---
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/jfcarter2358/calligraphy/actions/workflows/makefile.yml/badge.svg)](https://github.com/jfcarter2358/calligraphy/actions/workflows/makefile.yml)
![Coverage Badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/jfcarter2358/a5b95abd1dc360c13da66165ff482d5e/raw/calligraphy__heads_main.json)

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
pip install calligraphy-scripting
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

## Roadmap

You can find the Calligraphy roadmap [here](https://jfcarter2358.notion.site/5081d4214297401db15a43e47a974521?v=9858c59c7ecd4eefa09bf75158c47448)

## License

Calligraphy is under the [MIT license](https://opensource.org/licenses/MIT).

## Contact

If you have any questions or concerns please reach out to me (John Carter) at [jfcarter2358@gmail.com](mailto:jfcarter2358@gmail.com)
