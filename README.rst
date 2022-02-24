README for Caligraphy - https://caligraphy.readthedocs.io/
=============================================
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT

==========
Caligraphy
==========

**Shell scripting for the modern age**

Caligraphy is a hybrid scripting language that allows you to mix Python and Bash code
in the same file. This gives you the advantages of bash when working with other
processes while also giving you the advantages of a modern language like Python.

It's a free software distributed under the MIT Licence unless
otherwise specified.

Development is hosted on GitHub: https://github.com/jfcarter2358/caligraphy/

Pull requests are amazing and most welcome.

Install
-------

Pylint can be simply installed by running::

    pip install caligraphy

If you want to install from a source distribution, extract the tarball and run
the following command (this requires poetry to be installed)::

    poetry install --no-dev .

Documentation
-------------

The documentation lives at https://caligraphy.readthedocs.io/.

Pylint is shipped with following additional commands:

Testing
-------

We use _pytest_ and _coverage_ for running the test suite. You should be able to install them with::

    pip install pytest coverage


To run the test suite, you can do::

    make test

License
-------

caligraphy is under the `MIT <https://opensource.org/licenses/MIT>`_ license.
