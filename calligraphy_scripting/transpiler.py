# pylint: disable=C0301, R1702, R0912, R0914, W1401
"""Module to convert bash code inside of Calligraphy scripts to Python"""

from __future__ import annotations
import re
import base64

ANSI_GREEN = "\033[32m"
ANSI_BLUE = "\033[34m"
ANSI_CYAN = "\033[36m"
ANSI_MAGENTA = "\033[35m"
ANSI_GREY = "\033[90m"
ANSI_RESET = "\033[0m"


def explain(lines: list[str], langs: list[str], inline_indices: list[str]) -> str:
    """Get the language annotations for a script

    Args:
        lines (list[str]): Lines that make up the script
        langs (list[str]): Detected languages for the lines
        inline_indices (list[str]): Indices of inline bash elements of the script

    Returns:
        str: Text of annotated script
    """

    output = ""

    # Generate language annotations
    for idx, line in enumerate(lines):
        if langs[idx] == "COMMENT":
            output += (
                f"{ANSI_GREY}COMMENT{ANSI_RESET}     | {ANSI_GREY}{line}{ANSI_RESET}\n"
            )
        elif langs[idx] == "BASH":
            output += (
                f"{ANSI_BLUE}BASH{ANSI_RESET}        | {ANSI_BLUE}{line}{ANSI_RESET}\n"
            )
        elif langs[idx] == "PYTHON":
            output += f"{ANSI_GREEN}PYTHON{ANSI_RESET}      | {ANSI_GREEN}{line}{ANSI_RESET}\n"
        elif langs[idx] == "CALLIGRAPHY":
            output += f"{ANSI_MAGENTA}CALLIGRAPHY{ANSI_RESET} | {ANSI_MAGENTA}{line}{ANSI_RESET}\n"
        else:
            inline_idx = [i for i in inline_indices if i[0] == idx][0]
            output += f"{ANSI_CYAN}MIX{ANSI_RESET}         | {ANSI_GREEN}{line[:inline_idx[1]]}{ANSI_RESET}{ANSI_BLUE}{line[inline_idx[1]:inline_idx[2]+1]}{ANSI_RESET}{ANSI_GREEN}{line[inline_idx[2] + 1:]}{ANSI_RESET}\n"

    output = output.replace("<CALLIGRAPHY_NEWLINE>", "\n")
    return output


def transpile(lines: list[str], langs: list[str], inline_indices: list[str]) -> str:
    """Convert Calligraphy script into a purely Python script

    Args:
        lines (list[str]): Lines that make up the script
        langs (list[str]): Detected languages for the lines
        inline_indices (list[str]): Indices of inline bash elements of the script

    Returns:
        str: Transpiled Python script
    """

    bash_rc_pattern = r"\$\?(?=([^'\\]*(\\.|'([^'\\]*\\.)*[^'\\]*'))*[^']*$)"
    rc_pattern = r'\$\?(?=([^"\\]*(\\.|"([^"\\]*\\.)*[^"\\]*"))*[^"]*$)'
    arg_pattern = r'\$([0-9]+)(?=([^"\\]*(\\.|"([^"\\]*\\.)*[^"\\]*"))*[^"]*$)'
    env_pattern = r"env\.((?:[a-zA-Z0-9]|_)*)"

    output = ""

    # Generate language annotations
    for idx, line in enumerate(lines):
        if langs[idx] == "COMMENT":
            output += f"{line}\n"
        elif langs[idx] == "BASH":
            indent = " " * (len(line) - len(line.lstrip()))
            cmd = line.lstrip()
            cmd = re.sub(env_pattern, r"${{\g<1>}}", cmd)
            cmd = re.sub(bash_rc_pattern, "$CALLIGRAPHY_RC", cmd)
            cmd_bytes = cmd.encode("utf-8")
            base64_cmd_bytes = base64.b64encode(cmd_bytes)
            base64_cmd = base64_cmd_bytes.decode("utf8")
            output += f'{indent}shell("{base64_cmd}", format_dict={{**globals(), **locals()}})\n'
        elif langs[idx] == "PYTHON":
            line = re.sub(rc_pattern, "RC", line)
            line = re.sub(arg_pattern, r"sys.argv[\g<1>]", line)
            output += f"{line}\n"
        else:
            inline_idx = [i for i in inline_indices if i[0] == idx][0]
            raw = line[inline_idx[1] : inline_idx[2]]
            cmd = raw[2:-1]
            cmd = re.sub(env_pattern, r"${{\g<1>}}", cmd)
            cmd = re.sub(bash_rc_pattern, "$CALLIGRAPHY_RC", cmd)
            cmd_bytes = cmd.encode("utf-8")
            base64_cmd_bytes = base64.b64encode(cmd_bytes)
            base64_cmd = base64_cmd_bytes.decode("utf8")
            if "if" in line[: inline_idx[1]].split(" "):
                output += f'{line[:inline_idx[1]]}shell("{base64_cmd}", get_rc=True, silent={raw[0]=="?"}, format_dict={{**globals(), **locals()}}){line[inline_idx[2]:]}\n'
            else:
                output += f'{line[:inline_idx[1]]}shell("{base64_cmd}", get_stdout=True, silent={raw[0]=="?"}, format_dict={{**globals(), **locals()}}){line[inline_idx[2]:]}\n'

    output = output.replace("<CALLIGRAPHY_NEWLINE>", "\n")
    return output
