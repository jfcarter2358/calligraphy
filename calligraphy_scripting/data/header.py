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
