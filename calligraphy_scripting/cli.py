# pylint: disable=C0301, R1702, R0912, R0914, W0122, W1401, W0703
"""Main entrypoint into Calligraphy that handles CLI parsing"""

from __future__ import annotations
import sys
import os
from calligraphy_scripting import parser
from calligraphy_scripting import runner
from calligraphy_scripting import transpiler
from calligraphy_scripting import __version__

# Setup global helper variables
here = os.path.dirname(os.path.abspath(__file__))
if "-n" in sys.argv or "--no-ansi" in sys.argv:  # pragma: no cover
    ANSI_BOLD = ""
    ANSI_RED = ""
    ANSI_GREEN = ""
    ANSI_BLUE = ""
    ANSI_RESET = ""
    transpiler.ANSI_GREEN = ""
    transpiler.ANSI_CYAN = ""
    transpiler.ANSI_BLUE = ""
    transpiler.ANSI_RESET = ""
else:
    ANSI_BOLD = "\033[1m"
    ANSI_RED = "\033[31m"
    ANSI_GREEN = "\033[32m"
    ANSI_BLUE = "\033[34m"
    ANSI_RESET = "\033[0m"


def version() -> None:
    """Print out the currently installed version of Calligraphy"""

    # Output the detected version
    print(
        f"{ANSI_GREEN}{ANSI_BOLD}Calligraphy{ANSI_RESET}: {ANSI_BLUE}{__version__}{ANSI_RESET}"
    )


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
    contents, inline_indices = parser.handle_line_breaks(contents)
    lines, langs = parser.determine_language(contents)
    explanation = transpiler.explain(lines, langs, inline_indices)

    print(explanation)


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
    contents, inline_indices = parser.handle_line_breaks(contents)
    contents = parser.handle_sourcing(contents)
    lines, langs = parser.determine_language(contents)
    transpiled = transpiler.transpile(lines, langs, inline_indices)

    # Add the header to enable functionality
    with open(os.path.join(here, "data", "header.py"), encoding="utf-8") as header_file:
        header = header_file.read()
    header = header.replace('"PROGRAM_ARGS"', str(["calligraphy"] + args))
    code = f"{header}\n\n{transpiled}"

    print(code)


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

    # Run the code
    try:
        runner.execute(contents, args=[sys.argv[1]] + args)
    except Exception:
        help_prefix = f'Use `calligraphy -i {path} {" ".join(args)}'.strip()
        print(f"{help_prefix}` to see the intermediate Python for debugging")


def cli() -> None:
    """Handle command line parsing"""

    # Help text to be displayed if need be
    help_text = f"""{ANSI_GREEN}usage{ANSI_RESET}: calligraphy [option] [file | -] [arg]
    {ANSI_BOLD}{ANSI_BLUE}options:{ANSI_RESET}
        -h, --help            Show this help message and exit
        -e, --explain         Parse input and show the language breakdown of the source
        -v, --version         Print out the version of Calligraphy and exit
        -i, --intermediate    Print out the compiled Python code and exit
        -n, --no-ansi         Print without ANSI terminal colors
    {ANSI_BOLD}{ANSI_BLUE}arguments:{ANSI_RESET}
        file                  Program read from script file
        -                     Program read from stdin
        arg ...               Arguments passed to the program"""
    args = sys.argv[1:]

    # Check if any arguments have been passed
    if len(args) == 0:
        print(help_text)
        sys.exit(1)

    # Setup variable defaults
    flag_intermediate = False
    flag_explain = False
    program_path = ""
    program_args = []

    # Parse arguments
    for arg in args:
        if program_path:
            program_args.append(arg)
            continue
        if arg in ("-n", "--no-ansi"):
            continue  # pragma: no cover
        if arg in ("-h", "--help"):
            print(help_text)
            sys.exit(0)
        if arg in ("-v", "--version"):
            version()
            sys.exit(0)
        if arg in ("-i", "--intermediate"):
            flag_intermediate = True
            if flag_explain:
                print(
                    f"{ANSI_RED}{ANSI_BOLD}[ERROR]{ANSI_RESET} :: Both the `intermediate` and `explain` options cannot be set at the same time."
                )
                sys.exit(1)
            continue  # pragma: no cover
        if arg in ("-e", "--explain"):
            flag_explain = True
            if flag_intermediate:
                print(
                    f"{ANSI_RED}{ANSI_BOLD}[ERROR]{ANSI_RESET} :: Both the `intermediate` and `explain` options cannot be set at the same time."
                )
                sys.exit(1)
            continue  # pragma: no cover
        program_path = arg

    # Make sure a program path was supplied
    if not program_path:
        print(
            f"{ANSI_RED}{ANSI_BOLD}[ERROR]{ANSI_RESET} :: Program input is required, either supply a file path or use `-` for stdin"
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
