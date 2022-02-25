# pylint: disable=C0301, R1702, R0912, R0914
"""Module to convert bash code inside of Calligraphy scripts to Python"""

from __future__ import annotations
import re
from calligraphy_scripting import tokenizer

NO_LEFT_PAD = ["COLON", "RPAREN", "RBRACE", "RBRACKET", "COMMA"]
NO_RIGHT_PAD = ["LPAREN", "LBRACE", "LBRACKET", "SHELL"]


def dump(tokens: list[tokenizer.Token]) -> str:
    """Get text represented by a list of tokens

    Args:
        tokens (list[tokenizer.Token]): Token objects that make up the text

    Returns:
        str: Text that was represented by the tokens
    """

    # Set defaults for variables
    output = ""
    no_right_pad = True

    # Go through all the tokens
    for tok in tokens:

        text = ""
        if tok.t_type == "INDENT":
            # Indents equate to a new line
            output += "\n" + (" " * tok.t_value)
            no_right_pad = True
            continue
        if tok.t_type == "STRING":
            # Add quotes around strings
            string = tok.t_value.replace('"', '\\"')
            text = f'"{string}"'
        else:
            text += f"{tok.t_value}"

        # Check if we should add a space to the left
        if not (tok.t_type in NO_LEFT_PAD or no_right_pad):
            text = f" {text}"

        output += text
        no_right_pad = False

        # Check if we should have no space to the right
        if tok.t_type in NO_RIGHT_PAD:
            no_right_pad = True

    return output


def get_line_types(
    lines: list[list[tokenizer.Token]], imports: list[str], functions: list[str]
) -> list[str]:
    """Get the language type for each line of the passed in source

    Args:
        lines (list[list[tokenizer.Token]]): List of token lists representing the script
        imports (list[str]): List of string names of imported modules
        functions (list[str]): List of string names of defined functions

    Returns:
        list[str]: Either "PYTHON" or "BASH" describing that line's language
    """

    # Setup types list
    types = []

    # Loop through the lines
    for line in lines:
        # If we start with a Python keyword then it's a Python line
        if line[1].t_type == "KEYWORD":
            types.append("PYTHON")
        else:
            # If we start with a defined function name, then it's Python
            # since we're calling that function
            for func in functions:
                str_line = dump(line[1:])
                if str_line.startswith(func):
                    types.append("PYTHON")
                    continue
            # Check for more complicated conditions
            is_python = False
            is_function = False
            for tok in line:
                # If we are assigning a variable then it's Python since Calligraphy
                # disallows assigning variables in a bash-like way
                if tok.t_type == "ASSIGN":
                    is_python = True
                    break
                # If we find a built-in Python function name then we need to record
                # that there might be a function here
                if tok.t_type == "FUNCTION":
                    is_function = True
                    continue
                # If we find a name token then we need to check a bit deeper
                if tok.t_type == "NAME":
                    # Check to see if the name corresponds to accessing something from
                    # one of the imported modules
                    for imp in imports:
                        if tok.t_value.startswith(f"{imp}."):
                            is_function = True
                            break
                    if is_function:
                        continue
                # If we just found a function and now find a parenthesis then we're in a
                # Python line
                if tok.t_type == "LPAREN":
                    if is_function:
                        is_python = True
                        break
                is_function = False
            # Assign the type according to what we discovered
            if is_python:
                types.append("PYTHON")
            else:
                types.append("BASH")
    return types


def preprocess_tokens(
    tokens: list[tokenizer.Token], imports: list[str], functions: list[str]
) -> tuple[list[list[tokenizer.Token]], list]:
    """Process token list into an array with language annotations

    Args:
        tokens (list[tokenizer.Token]): List of tokens that make up the script file
        imports (list[str]): List of string names of imported modules
        functions (list[str]): List of string names of defined functions_

    Returns:
        tuple[list[list[tokenizer.Token]], list[str]]: tokens organized into lines, their corresponding languages
    """
    # Setup defaults for variables
    lines = []
    current = []

    # Split the tokens into their lines based on where the indents are located
    for tok in tokens:
        if tok.t_type == "INDENT":
            lines.append(current)
            current = []
        current.append(tok)
    lines.append(current)

    # Remove empty lines
    lines = lines[1:]
    lines = [l for l in lines if len(l) > 1]

    # Get the type annotations for lines
    types = get_line_types(lines, imports, functions)

    return lines, types


def explain(
    tokens: list[tokenizer.Token], imports: list[str], functions: list[str]
) -> str:
    """Get the language annotations for a script

    Args:
        tokens (list[tokenizer.Token]): List of tokens that make up the script file
        imports (list[str]): List of string names of imported modules
        functions (list[str]): List of string names of defined functions

    Returns:
        str: Text of annotated script
    """
    output = ""

    # Process list of tokens
    lines, types = preprocess_tokens(tokens, imports, functions)

    # Generate language annotations
    for idx, line in enumerate(lines):
        indent = " " * int(line[0].t_value)
        if types[idx] == "BASH":
            # Format Bash line
            cmd = dump(line[1:])
            output += f"[blue]BASH[/blue]   | [blue]{indent}{cmd}[/blue]\n"
        else:
            is_shell = False
            shell_idx = -1
            rc_idx = -1
            r_paren_idx = -1
            paren_depth = 0
            for jdx, tok in enumerate(line):
                # Record shell calls we find
                if tok.t_type == "SHELL":
                    shell_idx = jdx
                    is_shell = True
                    continue
                if is_shell:
                    # If we find a '?' after a shell call then we're referencing the
                    # last RC of a bash command and need to record that
                    if tok.t_type == "QUESTION":
                        if shell_idx == jdx - 1:
                            rc_idx = jdx
                            continue
                    # If we find a '(' after a shell call then we want to know that
                    # wer're inside parenthesis
                    if tok.t_type == "LPAREN":
                        paren_depth += 1
                        continue
                    # If we find a ')' after a shell call then we want to know that
                    # wer're exiting parenthesis and record the position
                    if tok.t_type == "RPAREN":
                        paren_depth -= 1
                        if paren_depth == 0:
                            r_paren_idx = jdx
                        continue
            if is_shell:
                if rc_idx != -1:
                    # Format mixed line when checking bash RC
                    output += f"[cyan]MIX[/cyan]    | [green]{indent}{dump(line[1:shell_idx])}[/green] [blue]$?[/blue] [green]{dump(line[rc_idx + 1:])}[/green]\n"
                else:
                    # Format mixed line when making shell call
                    output += f"[cyan]MIX[/cyan]    | [green]{indent}{dump(line[1:shell_idx])}[/green] [blue]{dump(line[shell_idx:r_paren_idx+1])}[/blue] [green]{dump(line[r_paren_idx + 1:])}[/green]\n"
            else:
                # Format Python line
                output += (
                    f"[green]PYTHON[/green] | [green]{indent}{dump(line[1:])}[/green]\n"
                )

    return output


def convert(
    tokens: list[tokenizer.Token], imports: list[str], functions: list[str]
) -> list[tokenizer.Token]:
    """Convert Calligraphy tokens into purely Python tokens

    Args:
        tokens (list[tokenizer.Token]): List of tokens that make up the script file
        imports (list[str]): List of string names of imported modules
        functions (list[str]): List of string names of defined functions

    Returns:
        list[tokenizer.Token]: List of tokens that make up the intermediate Python code
    """

    # Setup defaults for variables
    output = []

    # Process list of tokens
    lines, types = preprocess_tokens(tokens, imports, functions)

    for idx, line in enumerate(lines):
        if types[idx] == "BASH":
            # Wrap bash line in sh function call
            cmd = dump(line[1:])
            cmd = re.sub(r"env\.((?:[a-zA-Z0-9]|_)*)", r"${\g<1>}", cmd)
            lines[idx] = [line[0]] + [
                tokenizer.Token("NAME", "shell"),
                tokenizer.Token("LPAREN", "("),
                tokenizer.Token("STRING", cmd),
                tokenizer.Token("RPAREN", ")"),
            ]
        else:
            is_shell = False
            is_if = False
            shell_idx = -1
            rc_idx = -1
            l_paren_idx = -1
            r_paren_idx = -1
            paren_depth = 0
            for jdx, tok in enumerate(line):
                # Record if the shell call is inside an if statement or not
                if tok.t_value == "if" and not is_shell:
                    is_if = True
                    continue
                # Record shell calls we find
                if tok.t_type == "SHELL":
                    shell_idx = jdx
                    is_shell = True
                    continue
                if is_shell:
                    # If we find a '?' after a shell call then we're referencing the
                    # last RC of a bash command and need to record that
                    if tok.t_type == "QUESTION":
                        if shell_idx == jdx - 1:
                            rc_idx = jdx
                            continue
                    # If we find a '(' after a shell call then we want to know that
                    # wer're inside parenthesis and record the position
                    if tok.t_type == "LPAREN":
                        if paren_depth == 0:
                            l_paren_idx = jdx
                        paren_depth += 1
                        continue
                    # If we find a ')' after a shell call then we want to know that
                    # wer're exiting parenthesis and record the position
                    if tok.t_type == "RPAREN":
                        paren_depth -= 1
                        if paren_depth == 0:
                            r_paren_idx = jdx
                        continue
            if is_shell:
                if rc_idx != -1:
                    lines[idx] = (
                        line[:shell_idx]
                        + [tokenizer.Token("NAME", "RC")]
                        + line[rc_idx + 1 :]
                    )
                else:
                    line[shell_idx] = tokenizer.Token("NAME", "shell")
                    cmd = dump(line[l_paren_idx + 1 : r_paren_idx])
                    cmd = re.sub(r"env\.((?:[a-zA-Z0-9]|_)*)", r"${\g<1>}", cmd)
                    if is_if:
                        # Wrap shell call in function with get_rc argument True
                        lines[idx] = (
                            line[: l_paren_idx + 1]
                            + [
                                tokenizer.Token("STRING", cmd),
                                tokenizer.Token("COMMA", ","),
                                tokenizer.Token("NAME", "get_rc"),
                                tokenizer.Token("ASSIGN", "="),
                                tokenizer.Token("BOOL", "True"),
                            ]
                            + line[r_paren_idx:]
                        )
                    else:
                        # Wrap shell call in function with get_stdout argument True
                        lines[idx] = (
                            line[: l_paren_idx + 1]
                            + [
                                tokenizer.Token("STRING", cmd),
                                tokenizer.Token("COMMA", ","),
                                tokenizer.Token("NAME", "get_stdout"),
                                tokenizer.Token("ASSIGN", "="),
                                tokenizer.Token("BOOL", "True"),
                            ]
                            + line[r_paren_idx:]
                        )

    # Collapse array into a 1D list
    for line in lines:
        output += line

    return output
