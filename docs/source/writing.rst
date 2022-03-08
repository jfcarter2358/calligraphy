Writing
=======

Basics
------

Under the hood Calligraphy parses script source and tries to detect the language of any 
given line. In addition, it looks for code wrapped in ``$(...)`` to inform it of a mixed
language line (with anything inside being Bash). After determining and annotating the 
language for the script, Calligraphy then transpiles the script to pure Python and runs 
it. This approach means that the rules for the language are fairly straightforward.

Rules
-----

For the most part Calligraphy allows you to freely mix Bash and Python code, however 
there are a few rules that must be followed:

1. The base syntax is that of Python

   Whenever you write Calligraphy code you'll primarily be writing be writing Python code. 
   For example, let's say you want to create a program which searches for some text in a 
   file. To do this, you'll want a ``search`` function which takes in two arguments and
   prints out if the text is found or not.

   .. code-block: Python

      import sys

      def search(search_path, search_pattern):

         if $(cat env.search_path | grep -q env.search_pattern):
            print('The pattern exists in the file')
         else:
            print('The pattern does not exist in the file')

      env.search_path = sys.argv[1]
      env.search_pattern = sys.argv[2]
      search(search_path, search_pattern)

   You'll notice that other than a few parts this is stock Python
   code. All the base rules and syntax of Python apply except for the exceptions called out
   in the following rules.

2. Using ``__name__ == '__main__'`` is disallowed

   At this point in the development of Calligraphy, the ``__name__`` property of the
   transpiled code isn't yet overridden, so calling ``__name__`` in your main Calligraphy
   script won't give you ``'__main__'``. Changes to this behavior are currently on the
   roadmap, but until then this pattern is disallowed in the language.

3. ``env``, ``shell``, ``shellopts``, ``Options``, and ``Environment`` are reserved

   All the normal Python keywords apply in Calligraphy, however three new ones have been
   added. ``env`` is an object of the ``Environment`` class used to get/set environment 
   variables so both of those are no longer available. In addition, ``shell`` is the name 
   of the function used to execute shell commands in the transpiled code, so that is also
   protected. Finally, you cannot use ``shellopts`` and ``Options`` as those are the 
   variable/class used for setting shell options.

4. Any lines written entirely in Bash will be executed in Bash

   Calligraphy works by detecting the language for each line. If it finds that a line is 
   written in Python, it will then check for inline bash. Otherwise, it registers the line
   as being Bash code and will execute it as such. For example, if we took the following
   code snippet:

   .. code-block::

      cat test.txt | grep "foobar" > matches.txt
      with open('matches.txt') as f:
         matches = f.read().split('\n')

   We can see that the first line would be executed as a shell command and the following
   lines would be executed as Python code. You can use the ``--explain`` flag of the
   Calligraphy interpreter to show how Calligraphy has parsed your script/interpreted the
   languages.

5. ``$(...)`` and ``?(...)`` denote inline Bash

   A decent chunk of the time it isn't super useful to pipe output to files and read them
   in so that you can access them from the Python side of things. To help with this issue
   you can wrap Bash code that's on a Python line with ``$(...)`` to tell Calligraphy that 
   it's a shell command. Calligraphy will return the contents of stdout when calls are 
   wrapped in such a manner except for when it's contained within an if statement. In that 
   scenario Calligraphy will return the return code of the shell call performed. In 
   addition, wrapping the Bash code with ``?(...)`` will act in the same manner as 
   ``$(...)`` except it won't print to stdout.

6. ``$?`` will give you the return code of the last shell command to be run

   If you need to check the RC of the previous shell command for whatever reason, you can
   reference it with ``$?``

7. Use ``env.NAME`` to get/set environment variables

   the ``env`` keyword acts as a convenient alias to your local environment variables. You 
   can access env variables with ``env.NAME`` and you can set variables with 
   ``env.NAME = 'value'``. If an env variable doesn't exist then it will return ``None``

8. Setting environment variables from Bash lines is disallowed

   While it's not explicitly checked/disallowed, it will lead to improper language
   determination. Therefore, the Bash pattern of ``NAME="value"`` is not permitted in the 
   Calligraphy language. If you need to set and environment variable to the output of a
   shell command you can use ``env.NAME = $(...)``

9. Other Calligraphy scripts can be imported via ``source path/to/other/module.script`` 

   For example, if you used ``source path/to/foo.script`` you when then be able to use
   ``foo.bar`` to access the variable ``bar`` within the ``foo`` module. You can also 
   use ``source path/to/foo.script as baz`` to rename the import, meaning you would
   instead use ``baz.bar`` instead of ``foo.bar``

10. You can set shell options using the ``shellopts`` variable

   In order to control shell options for your bash commands, you can use the ``shellopts``
   built-in variable. To do this, you'll want to use something of the following form:

   .. code-block::

      shellopts.x = True
      shellopts.pipefail = True
