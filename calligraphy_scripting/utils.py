"""Module to handle repeated operations throughout Calligraphy"""

import os


def load_header():
    """Load the header file for use in transpiling Calligraphy scripts

    Returns:
        str: The contents of the header file
    """
    here = os.path.dirname(os.path.abspath(__file__))
    header = ""
    with open(os.path.join(here, "data", "header.py"), encoding="utf-8") as header_file:
        header = header_file.read()
    return header
