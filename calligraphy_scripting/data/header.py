# pylint: disable=W0603

"""
A header module that contains the code required to make transpiled calligraphy
scripts run
"""

import subprocess
import os
import sys
from typing import Union

sys.argv = "PROGRAM_ARGS"


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


RC = 0
env = Environment()


def shell(
    cmd: str, get_rc: bool = False, get_stdout: bool = False
) -> Union[None, str, int]:
    """Perform a shell call and update the environment with any env variable changes

    Args:
        cmd (str): The command to run
        get_rc (bool, optional): Should the return code of the call be returned.
            Defaults to False.
        get_stdout (bool, optional): Should the contents of stdout of the call be
            returned. Defaults to False.

    Returns:
        Union[None, str, int]: Default None, stdout contents if get_stdout is True and
            return code if get_rc is True
    """

    env_marker = "~~~~START_ENVIRONMENT_HERE~~~~"
    global RC
    cmd = cmd + f" && echo {env_marker} && printenv"
    stdout = []
    envout = []

    with subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, env=os.environ.copy()
    ) as proc:
        # grab and return the exit code
        is_stdout = True
        for line in iter(proc.stdout.readline, b""):
            str_line = line.decode("utf-8")[:-1]
            if str_line == env_marker:
                is_stdout = False
            elif is_stdout:
                print(str_line)
                stdout.append(str_line)
            else:
                envout.append(str_line)
        proc.stdout.close()
        proc.wait()
        RC = proc.poll()

    for line in envout:
        line = line.strip().split("=")
        if len(line) > 1:
            os.environ[line[0]] = line[1]
    if get_stdout:
        return "\n".join(stdout)
    if get_rc:
        return RC
    return None
