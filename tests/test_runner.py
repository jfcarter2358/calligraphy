from calligraphy_scripting.cli import __version__
from calligraphy_scripting import runner
import os
import pytest
import io
import sys
import re

class MockIO():
    def __init__(self, stdin=''):
        self._stdout = io.StringIO()
        self._stderr = io.StringIO()
        self._stdin = io.StringIO(stdin)

    def __enter__(self):
        sys.stdout = self._stdout
        sys.stderr = self._stderr
        sys.stdin = self._stdin
        return self

    def __exit__(self, _, __, ___):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        sys.stdin = sys.__stdin__

    @property
    def stdout(self):
        self._stdout.seek(0)
        return self._stdout.read()

    @property
    def stderr(self):
        self._stderr.seek(0)
        return self._stderr.read()

here = os.path.dirname(os.path.abspath(__file__))

def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

def test_execute(capfd):
    file_path = os.path.join(here, 'data', 'data.txt')

    with open(os.path.join(here, 'data', 'runner.execute.out')) as out_file:
        execute_out = out_file.read()
    execute_out = execute_out.replace('<FILE_PATH>', file_path)

    with open(os.path.join(here, 'data', 'test7.script')) as script_file:
        script = script_file.read()

    runner.execute(script)
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == execute_out
