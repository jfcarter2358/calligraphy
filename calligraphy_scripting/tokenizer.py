# pylint: disable=C0301, R1702, R0912, R0914
"""Objects and data related to Calligraphy tokenization"""

from __future__ import annotations
import re

TOKEN_TYPES = {
    "LPAREN": r"\(",
    "RPAREN": r"\)",
    "LBRACE": r"\{",
    "RBRACE": r"\}",
    "LBRACKET": r"\[",
    "RBRACKET": r"\]",
    "OP": r"(?:==|<=|>=|\+|-|\*|^|/|<|>)",
    "ASSIGN": r"=",
    "QUOTE": r"(?:\"|\')",
    "FLOAT": r"(?:\d|\.)*",
    "INT": r"\d*",
    "BOOL": r"(?:True|False|None)",
    "INDENT": r"(?:\d*:INDENT)",
    "CONTINUE": r"\\",
    "COMMA": r",",
    "COLON": r":",
    "SHELL": r"\$",
    "QUESTION": r"\?",
    "FLAG": r"-(?:[a-zA-Z0-9]|_)*",
    "FLOW": r"(?:\||&|\|\||&&)",
    "TYPE": r"(?:str|int|float|complex|list|tuple|dict|set|bool|bytes|bytearray|range)",
    "KEYWORD": r"(?:and|as|assert|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yeild)",
    "FUNCTION": r"(?:abs|all|any|ascii|bin|bool|bytearray|bytes|callable|chr|classmethod|compile|complex|delattr|dict|dir|divmod|enumerate|eval|exec|filter|float|format|frozenset|getattr|globals|hasattr|hash|help|hex|id|input|int|isinstance|insubclass|iter|len|list|locals|map|max|memoryview|min|next|object|oct|open|ord|pow|print|property|range|repr|reversed|round|set|setattr|slice|sorted|staticmethod|str|sum|super|tuple|type|vars|zip)",
    "IF": r"if",
    "ELSE": r"else",
    "ELIF": r"elif",
    "COMMENT": r"#*",
    "NAME": r"(?:[a-zA-Z0-9]|_|\.)*",
    "STRING": r".*",
    "NEWLINE": r"\n",
}

TOKEN_FORMATTERS = [
    "(",
    ")",
    "{",
    "}",
    "[",
    "]",
    "+",
    "-",
    "*",
    "^",
    "/",
    ":",
    "=",
    "<",
    ">",
    "|",
    ",",
    "$",
    "?",
]

NUMERIC_TOKEN_FORMATTERS = ["-", "*", "+", "^", "/", "<", ">"]

MULTI_LETTER_TOKEN_FORMATTERS = [
    "==",
    "<=",
    ">=",
]

TOKEN_NAMES = [TOKEN_TYPES]


def detect_type(word: str) -> Token:
    """Detect the token that corresponds to an input string

    Args:
        word (str): Input text to be turned into a token

    Returns:
        Token: Token corresponding to the input text
    """

    for name, pattern in TOKEN_TYPES.items():
        if re.fullmatch(pattern, word):
            return Token(name, word)
    return None  # pragma: no cover


class Token:
    """Parser token representing source code"""

    def __init__(self, t_type: str, t_value: str) -> None:
        """Initialize a Token object

        Args:
            t_type (str): The Token's type
            t_value (str): The Token's value
        """
        self.t_type = t_type
        if self.t_type == "INDENT":
            self.t_value = int(t_value[:-7])
        else:
            self.t_value = t_value

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        """Get string representation of Token

        Returns:
            str: String representation of Token
        """

        return f"<{self.t_type}:{self.t_value}>"
