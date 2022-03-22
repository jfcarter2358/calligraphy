Reference
=========

File Format
-----------

Calligraphy uses the ``.script`` file extension. While this doesn't *actually* matter 
for single-file scripts, it is enforced when sourcing other Calligraphy scripts into a 
larger program.

Language Detection
------------------

Calligraphy language detection operates under the following rules:

1. If a line starts with a Python keyword then it's a Python (or mixed) line.

   This gives rise to the need for the inline-bash marker, but ultimately keeps the 
   syntax and parsing simpler than it otherwise would need to be.

2. If a line follows the pattern ``<something> = <something>`` then it's a Python (or mixed) line.
   
   By disallowing setting environment variables from within Bash we can use assignment 
   detection as a rule for if a line is Python or not.

3. If a line starts with ``<already found variable or import name>.`` then it's a Python (or mixed) line.
   
   This is to handle things like having imported ``matplotlib.pyplot as plt`` and then 
   having a line that is ``plt.show()``.

4. If a line starts with ``source ...`` then it's a Calligraphy (to be converted to Python).

   This is a hard rule coming from the decided upon syntax for Calligraphy imports.

5. If a line contains ``$(...)`` or ``?(...)`` then it's a mixed line with that section being Bash.

   This works in conjunction with the first rule in the list. In addition, other markers 
   of ``<some symbol>(...)`` will be added in the future to expand the functionality.

6. Any lines that don't have a language assigned are then considered to be Bash.

Inline Bash
-----------

Inline Bash commands take two forms:

$(...)
~~~~~~

This executes the bash while printing/capturing stdout and returning it. If this is used
within an if statement then the captured stdout will not be returned and instead the
command's return code will be returned.

?(...)
~~~~~~

This operates the exact same way as ``$(...)`` except it does **NOT** print to stdout.

Program Arguments
-----------------

To make things more readable and more inline with teh purpose of being scripts run from 
a terminal for automation/devops purposes, Calligraphy uses the same syntax as Bash when
accessing the system arguments. For example, given the arguments:

- foo
- bar
- baz

``$1`` will give you ``foo``.  Please note that while in bash function arguments are 
also accessed this way, that is not the case in Calligraphy and they are instead 
accessed by their name in the normal Pythonic manner.

Environment Variables
---------------------

To keep a consistent method of accessing/setting environment variables in Calligraphy, 
they are only set from Python lines via the ``env`` variable. For example,

.. code-block:: python
   
   env.FOOBAR = "baz"

will set the environment variable ``FOOBAR`` to ``baz``. Any environment variables set 
from Python will have the same value if accessed from Bash. In addition, any environment
variables set as a consequence to running a Bash command will have their new values 
reflected when accessed from Python. You can access environment variables via the same 
``env`` variable in the following manner:

.. code-block:: python

   print(env.FOOBAR)

Bash Return Codes
-----------------

While Python gives us the ability to use ``try`` and ``except`` blocks to handle errors,
Bash forces us to make do with return codes. In the future the return codes from bash 
will be wrapped into exception classes within Calligraphy, but for the time being you 
can access the return code of the last run Bash command via ``$?``. For example:

.. code-block::

   echo "this is a test" | false

   if $? != 0:
      print('The previous command failed!')

will produce

.. code-block:: console

   The previous command failed!

Sourcing Other Scripts
----------------------

When linking multiple Calligraphy scripts in order to produce a larger program, you'll
use the ``source`` command. It can be used in two ways:

.. code-block::

   source /path/to/foo.script
   source /path/to/bar.script as baz

This has the same effect as if you had imported the transpiled output of ``foo.script`` 
under the module name ``foo`` or had imported the transpiled output of ``bar.script`` 
under the module name ``baz``.

Shell Options
-------------

Normally in Bash scripts you can control shell options with the set_ command.
This functionality has been moved to the ``shellopts`` variable in Calligraphy. To use
it, include ``shellopts.<FLAG>`` in your Calligraphy script with the following list of
flags being supported:

- ``a``
- ``b``
- ``e`` (on by default)
- ``f``
- ``h`` (on by default)
- ``k``
- ``m``
- ``p``
- ``t``
- ``u``
- ``v``
- ``x``
- ``B`` (on by default)
- ``C``
- ``E``
- ``H`` (on by default)
- ``P``
- ``T``
- ``history``
- ``ignoreeof``
- ``pipefail`` (on by default)
- ``posix``

See the set_ documentation for information on each of the flags

Bash Command Formatting
-----------------------

To make working with Bash commands easier in Calligraphy, you are able to include 
variable values directly into Bash lines via f-string syntax. For example, the following
code

.. code-block::

   foobar = "hello world"
   echo "{foobar}"

will produce

.. code-block::

   hello world

while 

.. code-block::

   foobar = "hello world"
   echo "{{foobar}}"

will produce

.. code-block::

   {foobar}

Recommended IDE Settings
------------------------

When working in an IDE with Calligraphy, it is recommended that you configure the 
``.script`` extension to be subject to Python syntax highlighting. In addition, add
``# type: ignore`` to the top of your file so that built-in linters don't complain about
the Bash present in the file.

.. _set: https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html
