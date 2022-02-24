import subprocess
import os
import sys

sys.argv = "PROGRAM_ARGS"


class Environment:
    def __init__(self):
        pass

    def __getattribute__(self, name):
        return os.getenv(name)

    def __setattr__(self, name, value):
        os.environ[name] = value


RC = 0
env = Environment()


def sh(cmd, get_rc=False, get_stdout=False):
    env_marker = "~~~~START_ENVIRONMENT_HERE~~~~"
    global RC
    cmd = cmd + f" && echo {env_marker} && printenv"
    stdout = []
    env = []

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, env=os.environ.copy())
    # output = p.communicate()[0].decode('utf-8').splitlines()
    # grab and return the exit code
    is_stdout = True
    for line in iter(p.stdout.readline, b""):
        str_line = line.decode("utf-8")[:-1]
        if str_line == env_marker:
            is_stdout = False
        elif is_stdout:
            print(str_line)
            stdout.append(str_line)
        else:
            env.append(str_line)
    p.stdout.close()
    p.wait()
    RC = p.poll()

    for line in env:
        line = line.strip().split("=")
        if len(line) > 1:
            os.environ[line[0]] = line[1]
    if get_stdout:
        return "\n".join(stdout)
    if get_rc:
        return RC
