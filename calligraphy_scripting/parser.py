# pylint: disable=C0301, R1702, R0912, R0914, R0915
"""Module to parse Calligraphy scripts into token representation"""

from __future__ import annotations
import re


def get_imports(contents: str) -> list[str]:
    """Get all Python imports defined in the text

    Args:
        contents (str): Text to process

    Returns:
        list[str]: List of import names/aliases discovered
    """

    # Define the pattern to look for and search for it
    import_pattern = r"import\s*(\S*)(?:\s*as\s*(\S*))?"
    matches = re.findall(import_pattern, contents)
    output = []

    # Check if each match has an alias or not, record the name/alias
    for match in matches:
        if match[1]:
            output.append(match[1])
        else:
            output.append(match[0])

    return output


def get_functions(contents: str) -> list[str]:
    """Get all Python functions defined in the text

    Args:
        contents (str): Text to process

    Returns:
        list[str]: List of function names discovered
    """

    # Define the pattern to look for and search for it
    function_pattern = r"def\s*([a-zA-Z0-9_]*)\("
    output = re.findall(function_pattern, contents)
    return output


def determine_language(
    code: str,
) -> tuple[list[str], list[str], list[tuple[int, int, int]]]:
    """Determine the language of each line of Calligraphy code

    Args:
        code (str): Contents of the Calligraphy script with newlines replaced

    Returns:
        tuple[list[str], list[str], list[tuple[int, int, int]]]: list of lines, detected
            languages, and indices for inline Bash as detected in the Calligraphy script
    """

    keywords = [
        "and",
        "as",
        "assert",
        "break",
        "class",
        "continue",
        "def",
        "del",
        "elif",
        "else",
        "except",
        "finally",
        "for",
        "from",
        "global",
        "if",
        "import",
        "in",
        "is",
        "lambda",
        "nonlocal",
        "not",
        "or",
        "pass",
        "raise",
        "return",
        "try",
        "while",
        "with",
        "yield",
        "str",
        "int",
        "float",
        "complex",
        "list",
        "tuple",
        "dict",
        "set",
        "bool",
        "bytes",
        "bytearray",
        "range",
        "abs",
        "all",
        "any",
        "ascii",
        "bin",
        "bool",
        "bytearray",
        "bytes",
        "callable",
        "chr",
        "classmethod",
        "compile",
        "complex",
        "delattr",
        "dict",
        "dir",
        "divmod",
        "enumerate",
        "eval",
        "exec",
        "filter",
        "float",
        "format",
        "frozenset",
        "getattr",
        "globals",
        "hasattr",
        "hash",
        "help",
        "hex",
        "id",
        "input",
        "int",
        "isinstance",
        "insubclass",
        "iter",
        "len",
        "list",
        "locals",
        "map",
        "max",
        "memoryview",
        "min",
        "next",
        "object",
        "oct",
        "open",
        "ord",
        "pow",
        "print",
        "property",
        "range",
        "repr",
        "reversed",
        "round",
        "set",
        "setattr",
        "slice",
        "sorted",
        "staticmethod",
        "str",
        "sum",
        "super",
        "tuple",
        "type",
        "vars",
        "zip",
    ]
    inline_bash_pattern = (
        r'[\$?]\((.*)\)(?=([^"\\]*(\\.|"([^"\\]*\\.)*[^"\\]*"))*[^"]*$)'
    )
    assignment_pattern = r"^[ \t]*\(?((?:[a-zA-Z0-9_]+\s*,?\s*)+)\)?[ \t]$"

    lines = [line for line in code.split("\n") if len(line.strip()) > 0]
    variables = ["env."]
    langs = []
    inline_indices = []
    imports = get_imports(code)
    functions = get_functions(code)

    for idx, line in enumerate(lines):
        is_python = False
        stripped = line.lstrip()
        if stripped.startswith("#") or stripped.startswith('"""'):
            langs.append("COMMENT")
            continue
        for keyword in keywords:
            if stripped.startswith(keyword):
                is_python = True
                break
        for var in variables:
            if stripped.startswith(var):
                is_python = True
                break
        for imp in imports:
            if stripped.startswith(imp):
                is_python = True
                break
        for func in functions:
            if stripped.startswith(func):
                is_python = True
                break
        if not is_python:
            inline_removed = re.sub(inline_bash_pattern, "<INLINE_BASH>", line)
            parts = inline_removed.split("=")
            if len(parts) > 1:
                match = re.search(assignment_pattern, parts[0])
                if match:
                    variables += [var.strip() for var in match.group(1).split(",")]
                    inline_match = re.search(inline_bash_pattern, line)
                    if inline_match:
                        span = inline_match.span()
                        inline_indices.append((idx, span[0], span[1]))
                        langs.append("MIX")
                        continue
                    langs.append("PYTHON")
                    continue
        else:
            inline_match = re.search(inline_bash_pattern, line)
            if inline_match:
                span = inline_match.span()
                inline_indices.append((idx, span[0], span[1]))
                langs.append("MIX")
                continue
            langs.append("PYTHON")
            continue
        langs.append("BASH")

    return lines, langs, inline_indices


def handle_line_breaks(code: str) -> str:
    """Go through Calligraphy script and replace linebreaks for ease of regex parsing

    Args:
        code (str): Contents of the Calligraphy script

    Returns:
        str: Calligraphy script with newlines replace with <CALLIGRAPHY_NEWLINE>
    """

    depths = {"PAREN": 0, "BRACE": 0, "BRACKET": 0}

    flags = {"SINGLE_QUOTE": False, "DOUBLE_QUOTE": False}

    output = ""

    for idx, token in enumerate(code):
        look_behind = None
        if idx > 0:
            look_behind = code[idx - 1]

        if token == "'" and look_behind != "\\" and not flags["DOUBLE_QUOTE"]:
            flags["SINGLE_QUOTE"] = not flags["SINGLE_QUOTE"]

        if token == '"' and look_behind != "\\" and not flags["SINGLE_QUOTE"]:
            flags["DOUBLE_QUOTE"] = not flags["DOUBLE_QUOTE"]

        if (
            token == "("
            and look_behind != "\\"
            and not (flags["SINGLE_QUOTE"] or flags["DOUBLE_QUOTE"])
        ):
            depths["PAREN"] += 1

        if (
            token == ")"
            and look_behind != "\\"
            and not (flags["SINGLE_QUOTE"] or flags["DOUBLE_QUOTE"])
        ):
            depths["PAREN"] -= 1

        if (
            token == "{"
            and look_behind != "\\"
            and not (flags["SINGLE_QUOTE"] or flags["DOUBLE_QUOTE"])
        ):
            depths["BRACE"] += 1

        if (
            token == "}"
            and look_behind != "\\"
            and not (flags["SINGLE_QUOTE"] or flags["DOUBLE_QUOTE"])
        ):
            depths["BRACE"] -= 1

        if (
            token == "["
            and look_behind != "\\"
            and not (flags["SINGLE_QUOTE"] or flags["DOUBLE_QUOTE"])
        ):
            depths["BRACKET"] += 1

        if (
            token == "]"
            and look_behind != "\\"
            and not (flags["SINGLE_QUOTE"] or flags["DOUBLE_QUOTE"])
        ):
            depths["BRACKET"] -= 1

        if token == "\n":
            if look_behind != "\\":
                if (
                    depths["PAREN"] > 0
                    or depths["BRACKET"] > 0
                    or depths["BRACE"] > 0
                    or flags["DOUBLE_QUOTE"]
                ):
                    output += "<CALLIGRAPHY_NEWLINE>"
                    continue
            else:
                output += "<CALLIGRAPHY_NEWLINE>"
                continue

        output += token
    return output
