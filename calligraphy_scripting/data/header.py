# pylint: disable=W0603

"""
A header module that contains the code required to make transpiled calligraphy
scripts run
"""

import subprocess
import os
import sys
import base64
from typing import Union
import importlib.util

sys.argv = "PROGRAM_ARGS"


class Environment:
    """A class to act as a convenient method to access environment variables"""

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


class Options:
    """A class to make setting of bash shell options more convenient"""

    def __init__(self) -> None:
        """Initialize the Options object and set all shell options to default values"""

        # ignores:
        # * -n
        # * -o noexec
        # * -o emacs
        # * -o vi
        self.a = False
        self.b = False
        self.e = True  # non-default
        self.f = False
        self.h = True
        self.k = False
        self.m = False
        self.p = False
        self.t = False
        self.u = False
        self.v = False
        self.x = False
        self.B = True
        self.C = False
        self.E = False
        self.H = True
        self.P = False
        self.T = False
        self.history = True
        self.ignoreeof = False
        self.pipefail = True  # non-default
        self.posix = False

        self.keys = [
            "a",
            "b",
            "e",
            "f",
            "h",
            "k",
            "m",
            "p",
            "t",
            "u",
            "v",
            "x",
            "B",
            "C",
            "E",
            "H",
            "P",
            "T",
            "history",
            "ignoreeof",
            "pipefail",
            "posix",
        ]

    def bash_string(self) -> None:
        """Construct the set command for all the options and their values"""

        true_single_opts = [
            key for key in self.keys if getattr(self, key) == True and len(key) == 1
        ]
        false_single_opts = [
            key for key in self.keys if getattr(self, key) == False and len(key) == 1
        ]
        true_multiple_opts = [
            key for key in self.keys if getattr(self, key) == True and len(key) > 1
        ]
        false_multiple_opts = [
            key for key in self.keys if getattr(self, key) == False and len(key) > 1
        ]

        string = "set "
        if len(true_single_opts) > 0:
            string += "-"
            for opt in true_single_opts:
                string += opt
            string += " "
        if len(false_single_opts) > 0:
            string += "+"
            for opt in false_single_opts:
                string += opt
            string += " "
        for opt in true_multiple_opts:
            string += f"-o {opt} "
        for opt in false_multiple_opts:
            string += f"+o {opt} "

        return string


def source_import(calligraphy_path, module_name):
    if not calligraphy_path.endswith(".script"):
        raise ImportError(
            "Calligraphy only support sourcing other scripts that end with the '.script' extension"
        )
    if not os.path.exists(calligraphy_path):
        raise FileNotFoundError(
            f"Sourced script of '{calligraphy_path}' does not exist"
        )

    directory, script = os.path.split(calligraphy_path)
    python_path = os.path.join(directory, f".{script[:-7]}.py")

    spec = importlib.util.spec_from_file_location(module_name, python_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


RC = 0
env = Environment()
shellopts = Options()


def shell(
    cmd: str,
    get_rc: bool = False,
    get_stdout: bool = False,
    silent: bool = False,
    format_dict: dict = {},
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
        format_dict (dict): Dictionary of values to use in command formatting

    Raises:
        RuntimeError: The shell command exited with a non-zero return code when not in
            an if statement where the RC is being explicitly checked

    Returns:
        Union[None, str, int]: Default None, stdout contents if get_stdout is True and
            return code if get_rc is True
    """

    global RC
    global env

    cmd_bytes = cmd.encode("utf-8")
    decoded_bytes = base64.b64decode(cmd_bytes)

    decoded = decoded_bytes.decode("utf-8")
    decoded = decoded.format(**format_dict)

    decoded = f"{shellopts.bash_string()} && {decoded} && echo '\n' && echo ~~~~START_ENVIRONMENT_HERE~~~~ && printenv && echo ~~~~START_CWD_HERE~~~~ && pwd"

    decoded_bytes = decoded.encode("utf-8")
    cmd_bytes = base64.b64encode(decoded_bytes)
    cmd = cmd_bytes.decode("utf-8")

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

    # change our directory to where the shell command took us
    os.chdir(cwd_path)

    # update environment with what was modified by the shell command
    for line in envout:
        line = line.strip().split("=")
        if len(line) > 1:
            os.environ[line[0]] = line[1]

    # we don't want to raise exceptions if a user is checking for the return code
    # explicitly
    if not get_rc and shellopts.e and RC != 0:
        raise RuntimeError(f"The shell command failed with return code {RC}")

    if get_stdout:
        return "\n".join(stdout)
    if get_rc:
        return RC
    return None
