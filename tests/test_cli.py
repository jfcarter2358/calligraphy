from calligraphy_scripting.cli import __version__
from calligraphy_scripting import cli
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

def test_version(capfd):
    cli.version()
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == f"Calligraphy: {__version__}\n"

def test_explain(capfd):
    file_path = os.path.join(here, 'data', 'data.txt')

    with open(os.path.join(here, 'data', 'cli.explain.out')) as out_file:
        explain_out = out_file.read()

    with open(os.path.join(here, 'data', 'cli.explain.stdin.out')) as out_file:
        explain_stdin_out = out_file.read()

    with open(os.path.join(here, 'data', 'test1.script')) as script_file:
        script = script_file.read()

    # Test with file
    cli.explain(os.path.join(here, 'data', 'test1.script'))
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == explain_out

    # Test with stdin
    with MockIO(stdin=script) as mock:
        cli.explain('-')
        out = mock.stdout

    assert escape_ansi(out) == explain_stdin_out

def test_intermediate(capfd):
    file_path = os.path.join(here, 'data', 'data.txt')

    with open(os.path.join(here, 'data', 'cli.intermediate.out')) as out_file:
        intermediate_out = out_file.read()
    intermediate_out = intermediate_out.replace('<FILE_PATH>', file_path)

    with open(os.path.join(here, 'data', 'cli.intermediate.stdin.out')) as out_file:
        intermediate_stdin_out = out_file.read()
    intermediate_stdin_out = intermediate_stdin_out.replace('<FILE_PATH>', file_path)

    with open(os.path.join(here, 'data', 'test1.script')) as script_file:
        script = script_file.read()

    # Test with file
    cli.intermediate(os.path.join(here, 'data', 'test1.script'), [file_path, 'Plagueis'])
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == intermediate_out

    # Test with stdin
    with MockIO(stdin=script) as mock:
        cli.intermediate('-', [file_path, 'Plagueis'])
        out = mock.stdout

    assert escape_ansi(out) == intermediate_stdin_out
    

def test_execute(capfd):
    file_path = os.path.join(here, 'data', 'data.txt')

    with open(os.path.join(here, 'data', 'cli.execute.out')) as out_file:
        execute_out = out_file.read()
    execute_out = execute_out.replace('<FILE_PATH>', file_path)

    with open(os.path.join(here, 'data', 'test1.script')) as script_file:
        script = script_file.read()

    # Test with file
    cli.execute(os.path.join(here, 'data', 'test1.script'), [file_path, 'Plagueis'])
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == execute_out

    # Test with stdin
    with MockIO(stdin=script) as mock:
        cli.execute('-', [file_path, 'Plagueis'])
        out = mock.stdout

    assert escape_ansi(out) == execute_out

def test_calligraphy_cli(capfd):
    file_path = os.path.join(here, 'data', 'data.txt')

    with open(os.path.join(here, 'data', 'cli.version.out')) as out_file:
        version_out = out_file.read()

    with open(os.path.join(here, 'data', 'cli.explain.out')) as out_file:
        explain_out = out_file.read()

    with open(os.path.join(here, 'data', 'cli.explain.stdin.out')) as out_file:
        explain_stdin_out = out_file.read()

    with open(os.path.join(here, 'data', 'cli.intermediate.out')) as out_file:
        intermediate_out = out_file.read()
    intermediate_out = intermediate_out.replace('<FILE_PATH>', file_path)
    
    with open(os.path.join(here, 'data', 'cli.execute.out')) as out_file:
        execute_out = out_file.read()
    execute_out = execute_out.replace('<FILE_PATH>', file_path)

    with open(os.path.join(here, 'data', 'cli.cli.help.out')) as out_file:
        help_out = out_file.read()

    with open(os.path.join(here, 'data', 'cli.cli.flag_conflict.out')) as out_file:
        conflict_out = out_file.read()

    with open(os.path.join(here, 'data', 'cli.cli.no_program.out')) as out_file:
        no_program_out = out_file.read()

    with open(os.path.join(here, 'data', 'test1.script')) as script_file:
        script = script_file.read()

    # test no args
    sys.argv = ['foobar']
    with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.cli()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == help_out

    # Test help flag
    sys.argv = ['foobar', '-h']
    with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.cli()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == help_out

    # Test long help flag
    sys.argv = ['foobar', '--help']
    with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.cli()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == help_out

    # Test version flag
    sys.argv = ['foobar', '-v']
    with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.cli()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == version_out

    # Test long version flag
    sys.argv = ['foobar', '--version']
    with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.cli()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == version_out

    # Test intermediate flag
    sys.argv = ['foobar', '-i', os.path.join(here, 'data', 'test1.script'), file_path, 'Plagueis']
    with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.cli()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == intermediate_out

    # Test long intermediate flag
    sys.argv = ['foobar', '--intermediate', os.path.join(here, 'data', 'test1.script'), file_path, 'Plagueis']
    with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.cli()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
    out, _ = capfd.readouterr()

    

    assert escape_ansi(out) == intermediate_out

    # Test intermediate flag conflict
    sys.argv = ['foobar', '--intermediate', '-e', os.path.join(here, 'data', 'test1.script'), file_path, 'Plagueis']
    with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.cli()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == conflict_out

    # Test explain flag
    sys.argv = ['foobar', '-e', os.path.join(here, 'data', 'test1.script')]
    with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.cli()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == explain_out

    # Test long explain flag
    sys.argv = ['foobar', '--explain', os.path.join(here, 'data', 'test1.script')]
    with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.cli()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == explain_out

    # Test explain flag conflict
    sys.argv = ['foobar', '-e', '-i', os.path.join(here, 'data', 'test1.script')]
    with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.cli()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == conflict_out

    # Test not passing a path
    sys.argv = ['foobar', '-e']
    with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.cli()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == no_program_out

    # Test running a script
    sys.argv = ['foobar', os.path.join(here, 'data', 'test1.script'), file_path, 'Plagueis']
    cli.cli()
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == execute_out

def test_help_flag(capfd):
    with open(os.path.join(here, 'data', 'cli.help_flag.out')) as out_file:
        help_flag_out = out_file.read()
    
    with open(os.path.join(here, 'data', 'cli.explain2.out')) as out_file:
        explain_out = out_file.read()

    # Test help flag passing
    sys.argv = ['foobar', os.path.join(here, 'data', 'test2.script'), '-h']
    cli.cli()
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == help_flag_out

    # Test explain output with source
    sys.argv = ['foobar', '-e', os.path.join(here, 'data', 'test2.script')]
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.cli()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == explain_out

def test_shellopts(capfd):
    with open(os.path.join(here, 'data', 'cli.shellopts.out')) as out_file:
        shellopts_out = out_file.read()
    with open(os.path.join(here, 'data', 'cli.shellopts.err')) as err_file:
        shellopts_err = err_file.read()

    # Test help flag passing
    sys.argv = ['foobar', os.path.join(here, 'data', 'test4.script')]
    cli.cli()
    out, err = capfd.readouterr()

    assert escape_ansi(out) == shellopts_out
    assert escape_ansi(err) == shellopts_err

def test_formatting(capfd):
    with open(os.path.join(here, 'data', 'cli.formatting.out')) as out_file:
        formatting_out = out_file.read()

    # Test help flag passing
    sys.argv = ['foobar', os.path.join(here, 'data', 'test5.script')]
    cli.cli()
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == formatting_out

def test_exception(capfd):
    file_path = os.path.join(here, 'data', 'test6.script')

    with open(os.path.join(here, 'data', 'cli.exception.out')) as out_file:
        formatting_out = out_file.read()
    formatting_out = formatting_out.replace('<FILE_PATH>', file_path)

    # Test help flag passing
    sys.argv = ['foobar', os.path.join(here, 'data', 'test6.script')]
    cli.cli()
    out, _ = capfd.readouterr()

    assert escape_ansi(out) == formatting_out
