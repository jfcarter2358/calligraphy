from calligraphy_scripting import parser
from calligraphy_scripting import transpiler
import os
import traceback

here = os.path.dirname(os.path.abspath(__file__))

def execute(contents: str) -> None:
    """Run Calligraphy code from another program

    Args:
        code (str): The Calligraphy code to run
    """


    # Process the contents
    contents, inline_indices = parser.handle_line_breaks(contents)
    contents = parser.handle_sourcing(contents)
    lines, langs = parser.determine_language(contents)
    transpiled = transpiler.transpile(lines, langs, inline_indices)

    # Add the header to enable functionality
    with open(os.path.join(here, "data", "header.py"), encoding="utf-8") as header_file:
        header = header_file.read()
    header = header.replace('"PROGRAM_ARGS"', str([]))
    code = f"{header}\n\n{transpiled}"

    # Run the code
    try:
        exec(code, globals())
    except Exception:
        trace = traceback.format_exc()
        parts = trace.split("\n")
        idx = 1
        exception_out = [parts[0]]
        while not parts[idx].startswith('  File "<string>"') and idx < len(parts):
            idx += 1
        while idx < len(parts):
            exception_out.append(parts[idx])
            idx += 1
        print("\n".join(exception_out))
