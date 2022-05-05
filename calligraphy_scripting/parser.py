# pylint: disable=C0301, R1702, R0912, R0914, R0915, W1401
"""Module to parse Calligraphy scripts into token representation"""

from __future__ import annotations
import re
import os
from calligraphy_scripting import transpiler
from calligraphy_scripting import utils


def handle_sourcing(contents: str) -> str:
    """Handle replacing Calligraphy source statements and recursively transpiling other files

    Args:
        contents (str): Contents of a Calligraphy script

    Returns:
        str: Contents of the Calligraphy script with the source statements replaced
    """

    def compile_sourced(matches):
        for match in matches:
            with open(
                os.path.join(match[0], f"{match[1]}.{match[2]}"), encoding="utf-8"
            ) as code_file:
                code_contents = code_file.read()
            code_contents, inline_indices = handle_line_breaks(code_contents)
            lines, langs = determine_language(code_contents)
            transpiled = transpiler.transpile(lines, langs, inline_indices)

            # Add the header to enable functionality
            header = utils.load_header()
            header = header.replace('sys.argv = "PROGRAM_ARGS"', "")
            code = f"{header}\n\n{transpiled}"
            with open(
                os.path.join(match[0], f".{match[1]}.py"), "w", encoding="utf-8"
            ) as output_file:
                output_file.write(code)

    source_pattern = r"^[ \t]*source[ \t]+(?:([a-zA-Z0-9_/]*)\/)*([a-zA-Z0-9_]*)\.([a-zA-Z0-9]*)[ \t]*$"
    source_pattern_rename = r"^[ \t]*source[ \t]+(?:([a-zA-Z0-9_/]*)\/)*([a-zA-Z0-9_]*)\.([a-zA-Z0-9]*)[ \t]as[ \t]([a-zA-Z0-9_]*)[ \t]*"

    sourced = re.findall(source_pattern, contents, re.MULTILINE)
    sourced_rename = re.findall(source_pattern_rename, contents, re.MULTILINE)

    compile_sourced(sourced)
    compile_sourced(sourced_rename)

    contents = re.sub(
        source_pattern,
        '\g<2> = source_import(os.path.join("\g<1>", "\g<2>"+"."+"\g<3>"), "\g<2>")',
        contents,
        flags=re.MULTILINE,
    )
    contents = re.sub(
        source_pattern_rename,
        '\g<4> = source_import(os.path.join("\g<1>", "\g<2>"+"."+"\g<3>"), "\g<4>")',
        contents,
        flags=re.MULTILINE,
    )

    return contents


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
    variables = ["env.", "shellopts."]
    langs = []
    imports = get_imports(code)
    functions = get_functions(code)

    for line in lines:
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
                        langs.append("MIX")
                        continue
                    langs.append("PYTHON")
                    continue
        else:
            inline_match = re.search(inline_bash_pattern, line)
            if inline_match:
                langs.append("MIX")
                continue
            langs.append("PYTHON")
            continue
        if line.strip().startswith("source "):
            langs.append("CALLIGRAPHY")
            continue
        langs.append("BASH")

    return lines, langs


def handle_line_breaks(code: str) -> str:
    """Go through Calligraphy script and replace linebreaks for ease of regex parsing

    Args:
        code (str): Contents of the Calligraphy script

    Returns:
        str: Calligraphy script with newlines replace with <CALLIGRAPHY_NEWLINE>
    """

    depths = {"PAREN": 0, "BRACE": 0, "BRACKET": 0}
    flags = {"SINGLE_QUOTE": False, "DOUBLE_QUOTE": False}
    inline_indices = []
    output = ""
    line_idx = 0
    char_idx = 0
    in_inline = False
    inline_paren_depth = 0

    for idx, token in enumerate(code):
        look_ahead = None
        look_behind = None
        if idx > 0:
            look_behind = code[idx - 1]
        if idx < len(code) - 1:
            look_ahead = code[idx + 1]

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
            if in_inline:
                if depths["PAREN"] == inline_paren_depth:
                    inline_indices[-1][2] = char_idx + 1
                    in_inline = False
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
                    char_idx += 1
                    continue
                if char_idx != 0:
                    line_idx += 1
                char_idx = -1
            else:
                output += "<CALLIGRAPHY_NEWLINE>"
                char_idx += 1
                continue
        if token in ("$", "?", "!"):
            if look_ahead == "(":
                inline_paren_depth = depths["PAREN"]
                in_inline = True
                inline_indices.append([line_idx, char_idx, None])

        output += token
        char_idx += 1
    return output, inline_indices
