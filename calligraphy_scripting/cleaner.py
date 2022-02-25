# pylint: disable=C0301, R1702, R0912, R0914
"""Module to clean up token lists to make parsing more straight-forward"""

from __future__ import annotations
from calligraphy_scripting import tokenizer


def clean_tokens(tokens: list[tokenizer.Token]) -> list[tokenizer.Token]:
    """Detect and collapse line-continuations in Calligraphy source

    Args:
        tokens (list[tokenizer.Token]): Token objects to be cleaned

    Returns:
        list[tokenizer.Token]: Token objects with unneeded newlines removed
    """

    # Initialize variables with defaults
    paren_count = 0
    brace_count = 0
    bracket_count = 0
    should_skip = False
    cleaned = []

    # Loop through tokens
    for tok in tokens:
        if should_skip:
            should_skip = False
            continue
        # Update parenthesis depth
        if tok.t_type == "LPAREN":
            paren_count += 1
        elif tok.t_type == "RPAREN":
            paren_count -= 1
        # Update brace depth
        elif tok.t_type == "LBRACE":
            brace_count += 1
        elif tok.t_type == "RBRACE":
            brace_count -= 1
        # Update bracket depth
        elif tok.t_type == "LBRACKET":
            bracket_count += 1
        elif tok.t_type == "RBRACKET":
            bracket_count -= 1
        # Cleanup newlines if continuation is due to parens, braces, or brackets
        elif tok.t_type == "INDENT":
            if paren_count > 0 or brace_count > 0 or bracket_count > 0:
                continue
        # Skip over backslash line continuation
        elif tok.t_type == "CONTINUE":
            should_skip = True
            continue
        cleaned.append(tok)

    return cleaned
