Usage
=====

.. _install:

Installation
------------

To use Calligraphy, first install it using pip:

.. code-block:: console

   (.venv) $ pip install calligraphy

Writing Scripts
---------------

See the :doc:`writing` section to get started writing scripts in Calligraphy.

Running Scripts
---------------

To run a script file, you can use the following command:

.. code-block:: console
    
    (.venv) $ calligraphy /path/to/file/to/run arg1 arg2 ...

In addition, you can pass the script source into calligraphy via stdin by using ``-`` as your path parameter as follows:

.. code-block:: console

    (.venv) $ cat << EOF | calligraphy -
    env.MESSAGE = 'Hello world!'
    echo "env.MESSAGE"
    EOF

Explaining Scripts
------------------

Calligraphy has the ability to output an annotated version of the source it was provided 
in order to show which part of the script it understands to be Python and which part
is Bash. You can view this output by adding the ``-e`` or ``--explain`` flag to your 
command. For example,

.. code-block:: console

    (.venv) # cat << EOF | calligraphy -e -
    env.MESSAGE = 'Hello world!'
    echo "env.MESSAGE"
    EOF

Will output

.. code-block:: console

    PYTHON      | env.MESSAGE = 'Hello world!'
    BASH        | echo "env.MESSAGE"

Intermediate Output
-------------------

Calligraphy works by transpiling any detected Bash sections of the script into wrapped
Python calls. If you want to view the code that _actually_ is being run after the
transpiling, you can add the ``-i`` or ``--intermediate`` flag to your calligraphy 
command. For example,

.. code-block:: console

    cat << EOF | calligraphy -i -
    env.MESSAGE = 'Hello world!'
    echo "env.MESSAGE"
    EOF

Will output

.. code-block:: python

    # pylint: disable=W0603

    """
    A header module that contains the code required to make transpiled calligraphy
    scripts run
    """

    import subprocess
    import os
    import sys
    from typing import Union
    import importlib.util

    sys.argv = ['calligraphy']


    class Environment:
        """A class to act as a convient method to access environment variables"""

        def __init__(self) -> None:
            """Initialize the Environment object"""

        def __getattribute__(self, name: str) -> str:
            """Retrieve an environment variable by name

            Args:
                name (str): Name of the environment variable to get

            Returns:
                str: Value of the environment variable accessed
            """

            return os.getenv(name)

        def __setattr__(self, name: str, value: str) -> None:
            """Set and environment variable to the given value

            Args:
                name (str): Name of the environment variable to set
                value (str): Value to set the environment variable to
            """

            os.environ[name] = value

    def source_import(calligraphy_path, module_name):
        if not calligraphy_path.endswith('.script'):
            raise ImportError("Calligraphy only support sourcing other scripts that end with the '.script' extension")
        if not os.path.exists(calligraphy_path):
            raise FileNotFoundError(f"Sourced script of '{calligraphy_path}' does not exist")
        
        directory, script = os.path.split(calligraphy_path)
        python_path = os.path.join(directory, f'.{script[:-7]}.py')

        spec = importlib.util.spec_from_file_location(module_name, python_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    RC = 0
    env = Environment()


    def shell(
        cmd: str, get_rc: bool = False, get_stdout: bool = False, silent: bool = False
    ) -> Union[None, str, int]:
        """Perform a shell call and update the environment with any env variable changes

        Args:
            cmd (str): The command to run
            get_rc (bool, optional): Should the return code of the call be returned.
                Defaults to False.
            get_stdout (bool, optional): Should the contents of stdout of the call be
                returned. Defaults to False.
            silent (bool, optional): Should the output to stdout be suppressed when printing
                to the terminal. Defaults to False.

        Returns:
            Union[None, str, int]: Default None, stdout contents if get_stdout is True and
                return code if get_rc is True
        """

        global RC
        global env
        cmd = f"echo '{cmd}' | base64 -d | bash"
        stdout = []
        envout = []
        cwd_path = os.getcwd()

        with subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, env=os.environ.copy()
        ) as proc:
            # grab and return the exit code
            is_stdout = True
            is_env = False
            for line in iter(proc.stdout.readline, b""):
                str_line = line.decode("utf-8")[:-1]
                if str_line == "~~~~START_ENVIRONMENT_HERE~~~~":
                    if len(stdout) > 1:
                        if stdout[-2]:
                            print(stdout[-2])
                        stdout = stdout[:-1]
                    is_stdout = False
                    is_env = True
                elif str_line == "~~~~START_CWD_HERE~~~~":
                    is_env = False
                elif is_stdout:
                    if not silent and len(stdout) > 1:
                        print(stdout[-2])
                    stdout.append(str_line)
                elif is_env:
                    envout.append(str_line)
                else:
                    cwd_path = str_line
            proc.stdout.close()
            proc.wait()
            RC = proc.poll()

        env.CALLIGRAPHY_RC = str(RC)
        os.chdir(cwd_path)

        for line in envout:
            line = line.strip().split("=")
            if len(line) > 1:
                os.environ[line[0]] = line[1]
        if get_stdout:
            return "\n".join(stdout)
        if get_rc:
            return RC
        return None


    env.MESSAGE = 'Hello world!'
    shell("ZWNobyAiJHtNRVNTQUdFfSIgJiYgZWNobyAnCicgJiYgZWNobyB+fn5+U1RBUlRfRU5WSVJPTk1FTlRfSEVSRX5+fn4gJiYgcHJpbnRlbnYgJiYgZWNobyB+fn5+U1RBUlRfQ1dEX0hFUkV+fn5+ICYmIHB3ZA==")

Reference
---------

See the :doc:`reference` section for an in-depth reference to the parts of the Calligraphy
language
