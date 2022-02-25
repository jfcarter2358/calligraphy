# pylint: disable=C0301, R1702, R0912, R0914
"""Module to parse Calligraphy scripts into token representation"""

from __future__ import annotations
import re
from calligraphy_scripting import tokenizer


def space_special(contents: str) -> str:
    """Put spaces around special characters within a block of text for parsing

    Args:
        contents (str): Text to process

    Returns:
        str: Text with extra spacing added
    """

    # Initialize variables to default values
    in_single_quotes = False
    in_double_quotes = False
    indices = []

    # Loop through the text
    for idx, ltr in enumerate(contents):
        # Did we find a double qupte
        if ltr == '"':
            if not in_single_quotes:
                # If it's not escaped/in another string then record it
                if idx > 0:
                    if contents[idx - 1] != "\\":
                        in_double_quotes = not in_double_quotes
                        indices.append(idx)
        # Did we find a single quote
        elif ltr == "'":
            if not in_double_quotes:
                # If it's not escaped/in another string then record it
                if idx > 0:
                    if contents[idx - 1] != "\\":
                        in_single_quotes = not in_single_quotes
                        indices.append(idx)
        # Did we find a character taht needs formatting
        elif ltr in tokenizer.TOKEN_FORMATTERS:
            # Check if it's in a string
            if not in_double_quotes and not in_single_quotes:
                # Check if it's actually a multi-letter token
                if (
                    not contents[idx - 1 : idx + 1]
                    in tokenizer.MULTI_LETTER_TOKEN_FORMATTERS
                ):
                    # Check if we should only format if before a number
                    if ltr in tokenizer.NUMERIC_TOKEN_FORMATTERS:
                        if not contents[idx + 1].isalpha():
                            indices.append(idx)
                    else:
                        indices.append(idx)

    indices.reverse()
    # Add beginning/end spaces to make checking easier
    contents = f" {contents} "
    for idx, index in enumerate(indices):
        indices[idx] = index + 1

    # loop through indices to add spaces
    for idx in indices:
        r_offset = 1
        # If it's multi-letter, than we want to add spaces a bit further apart
        if contents[idx : idx + 2] in tokenizer.MULTI_LETTER_TOKEN_FORMATTERS:
            r_offset = 2
        # Don't double up on spaces that already exist and add them to either side of the token
        if contents[idx + r_offset] != " ":
            contents = f"{contents[:idx+r_offset]} {contents[idx+r_offset:]}"
        if contents[idx - 1] != " ":
            contents = f"{contents[:idx]} {contents[idx:]}"

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
    function_pattern = r"def\s*(\S*)\("
    output = re.findall(function_pattern, contents)
    return output


def parse_lines(lines: list[str]) -> list[tokenizer.Token]:
    """Break lines of text into list of tokens

    Args:
        lines (list[str]): Lines of text from the script

    Returns:
        list[tokenizer.Token]: List of Tokens representing the script
    """

    # Setup default variables
    tokens = []
    string_tokens = []
    in_string = False
    string_buffer = ""
    quote_char = ""

    # Loop through the lines
    for line in lines:
        # Grab the indent depth for the lien
        indent = len(line) - len(line.lstrip())
        # Space out special characters
        line = space_special(line)
        # Add strings to a list to process
        string_tokens.append([f"{indent}:INDENT"] + line.split())

    # Go through all the line's string tokens
    for string in string_tokens:
        for word in string:
            # Get the token for the word we're looking at
            tok = tokenizer.detect_type(word)
            if in_string:
                # If we're in a string then just add the value to the string's value
                # instead of creating a new line
                if tok.t_type == "QUOTE" and tok.t_value == quote_char:
                    tok2 = tokenizer.Token("STRING", string_buffer[:-1])
                    in_string = False
                    string_buffer = ""
                    tokens.append(tok2)
                    continue
                string_buffer += word + " "
                continue
            # Ignore comments
            if tok.t_type == "COMMENT":
                break
            # If we're in a string then record that
            if tok.t_type == "QUOTE":
                quote_char = tok.t_value
                in_string = True
                continue
            tokens.append(tok)

    return tokens
