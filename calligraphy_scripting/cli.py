# pylint: disable=C0301, R1702, R0912, R0914, W0122, W1401
"""Main entrypoint into Calligraphy that handles CLI parsing"""

from __future__ import annotations
import sys
import os
from rich.console import Console
from calligraphy_scripting import parser
from calligraphy_scripting import transpiler
from calligraphy_scripting import cleaner
from calligraphy_scripting import __version__

# Setup global helper variables
console = Console()
here = os.path.dirname(os.path.abspath(__file__))


def version() -> None:
    """Print out the currently installed version of Calligraphy"""

    # Output the detected version
    console.print(f"[bold green]Calligraphy[/bold green]: {__version__}")


def explain(path: str) -> None:
    """Print out the source code with language annotations

    Args:
        path (str): Path to the Calligraphy script file
    """

    if path == "-":
        # Grab the code from stdin
        contents = "\n".join(sys.stdin.readlines())
    else:
        # Open the file to parse
        with open(path, encoding="utf-8") as code_file:
            contents = code_file.read()

    # Process the contents
    imports = parser.get_imports(contents)
    functions = parser.get_functions(contents)
    lines = [line for line in contents.split("\n") if len(line) > 0]
    tokens = parser.parse_lines(lines)
    cleaned = cleaner.clean_tokens(tokens)
    explanation = transpiler.explain(cleaned, imports, functions)
    console.print(explanation)


def intermediate(path: str, args: list) -> None:
    """Print out the intermediate Python code that will be run

    Args:
        path (str): Path to the Calligraphy script file
        args (list): Command line arguments to pass to the program
    """

    if path == "-":
        # Grab the code from stdin
        contents = "\n".join(sys.stdin.readlines())
    else:
        # Open the file to parse
        with open(path, encoding="utf-8") as code_file:
            contents = code_file.read()

    # Process the contents
    imports = parser.get_imports(contents)
    functions = parser.get_functions(contents)
    lines = [line for line in contents.split("\n") if len(line) > 0]
    tokens = parser.parse_lines(lines)
    cleaned = cleaner.clean_tokens(tokens)
    converted = transpiler.convert(cleaned, imports, functions)
    code = transpiler.dump(converted)

    # Add the header to enable functionality
    with open(os.path.join(here, "data", "header.py"), encoding="utf-8") as header_file:
        header = header_file.read()
    header = header.replace('"PROGRAM_ARGS"', str(["calligraphy"] + args))
    code = f"{header}\n\n{code}"

    console.print(code)


def execute(path: str, args: list) -> None:
    """Run a Calligraphy script

    Args:
        path (str): Path to the Calligraphy script file
        args (list): Command line arguments to pass to the program
    """

    if path == "-":
        # Grab the code from stdin
        contents = "\n".join(sys.stdin.readlines())
    else:
        # Open the file to parse
        with open(path, encoding="utf-8") as code_file:
            contents = code_file.read()

    # Process the contents
    imports = parser.get_imports(contents)
    functions = parser.get_functions(contents)
    lines = [line for line in contents.split("\n") if len(line) > 0]
    tokens = parser.parse_lines(lines)
    cleaned = cleaner.clean_tokens(tokens)
    converted = transpiler.convert(cleaned, imports, functions)
    code = transpiler.dump(converted)

    # Add the header to enable functionality
    with open(os.path.join(here, "data", "header.py"), encoding="utf-8") as header_file:
        header = header_file.read()
    header = header.replace('"PROGRAM_ARGS"', str(["calligraphy"] + args))
    code = f"{header}\n\n{code}"

    # Run the code
    exec(code, globals())


def cli() -> None:
    """Handle command line parsing"""

    # Help text to be displayed if need be
    help_text = """[green]usage[/green]: calpgraphy \[option] \[file | -] \[arg]
    [bold blue]options:[/bold blue]
        -h, --help            Show this help message and exit
        -e, --explain         Parse input and show the language breakdown of the source
        -v, --version         Print out the version of Calligraphy and exit
        -i, --intermediate    Print out the compiled Python code and exit
    [bold blue]arguments:[/bold blue]
        file                  Program read from script file
        -                     Program read from stdin
        arg ...               Arguments passed to the program"""
    args = sys.argv[1:]

    # Check if any arguments have been passed
    if len(args) == 0:
        console.print(help_text)
        sys.exit(1)

    # Setup variable defaults
    flag_intermediate = False
    flag_explain = False
    program_path = ""
    program_args = []

    # Parse arguments
    for arg in args:
        if arg in ("-h", "--help"):
            console.print(help_text)
            sys.exit(0)
        if arg in ("-v", "--version"):
            version()
            sys.exit(0)
        if arg in ("-i", "--intermediate"):
            flag_intermediate = True
            if flag_explain:
                console.print(
                    "[bold red][ERROR][/bold red] :: Both the `intermediate` and `explain` options cannot be set at the same time."
                )
                sys.exit(1)
            continue  # pragma: no cover
        if arg in ("-e", "--explain"):
            flag_explain = True
            if flag_intermediate:
                console.print(
                    "[bold red][ERROR][/bold red] :: Both the `intermediate` and `explain` options cannot be set at the same time."
                )
                sys.exit(1)
            continue  # pragma: no cover
        if not program_path:
            program_path = arg
            continue
        program_args.append(arg)

    # Make sure a program path was supplied
    if not program_path:
        console.print(
            "[bold red][ERROR][/bold red] :: Program input is required, either supply a file path or use `-` for stdin"
        )
        sys.exit(1)

    # Handle any set flags
    if flag_explain:
        explain(program_path)
        sys.exit(0)
    if flag_intermediate:
        intermediate(program_path, program_args)
        sys.exit(0)

    # If we did nothing else then run the program
    execute(program_path, program_args)


if __name__ == "__main__":
    cli()  # pragma: no cover
