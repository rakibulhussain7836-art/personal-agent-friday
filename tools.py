"""
tools.py
Defines the actual functions the AI can call.
"""
import os
import sympy
from ddgs import DDGS
import subprocess
import webbrowser


def calculate(expression: str) -> str:
    """Evaluate a mathematical expression using sympy. Handles arithmetic, algebra, equations.

    Args:
        expression: The math expression to evaluate, e.g. '12*7+5' or 'solve(x**2 - 4, x)'
    """
    try:
        result = sympy.sympify(expression)
        return str(result.evalf() if result.is_number else result)
    except Exception as e:
        return f"Error calculating '{expression}': {e}"


def read_file(path: str) -> str:
    """Read the contents of a text file from disk.

    Args:
        path: File path to read
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


def write_file(path: str, content: str, confirm: bool = False) -> str:
    """Write text content to a file on disk.
    SAFETY: If the file already exists, this is a two-step tool. First call with
    confirm=False — it will NOT write yet, it just warns you the file exists.
    After the user explicitly confirms overwriting it, call again with confirm=True.
    New files (that don't exist yet) are written immediately, no confirmation needed.

    Args:
        path: File path to write to
        content: Content to write
        confirm: Set to True only after the user has explicitly approved overwriting an existing file
    """
    try:
        if os.path.exists(path) and not confirm:
            return f"File '{path}' already exists. Ask the user to confirm overwriting it. If they say yes, call write_file again with confirm=True."

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {e}"

def web_search(query: str) -> str:
    """Search the web for current information, news, or facts you don't know.

    Args:
        query: The search query, e.g. 'latest news on AI regulation'
    """
    try:
        results = DDGS().text(query, max_results=5)
        if not results:
            return "No results found."

        formatted = []
        for r in results:
            formatted.append(f"Title: {r['title']}\nSnippet: {r['body']}\nURL: {r['href']}")
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Error searching: {e}"
DANGEROUS_PATTERNS = ["rm -rf", "del /f", "del /s", "format ", "shutdown", "diskpart", "> /dev/", "mkfs"]


def run_command(command: str, confirm: bool = False) -> str:
    """Execute a shell/terminal command on the user's computer.
    SAFETY: This is a two-step tool. First call it with confirm=False (default) to
    preview the command. It will NOT run yet — it just describes what it will do.
    After the user explicitly confirms in chat, call it again with confirm=True to
    actually execute it.

    Args:
        command: The shell command to run, e.g. 'dir' or 'python --version'
        confirm: Set to True only after the user has explicitly approved running this exact command
    """
    lowered = command.lower()
    for pattern in DANGEROUS_PATTERNS:
        if pattern in lowered:
            return f"BLOCKED: This command matches a dangerous pattern ('{pattern}') and will never be run, even with confirmation."

    if not confirm:
        return f"This will run the command: '{command}'. Ask the user to confirm. If they say yes, call run_command again with confirm=True."

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=15
        )
        output = result.stdout if result.stdout else result.stderr
        return output.strip() if output.strip() else "Command ran with no output."
    except Exception as e:
        return f"Error running command: {e}"


def open_website(url: str) -> str:
    """Open a website in the user's default browser.

    Args:
        url: The URL to open, e.g. 'https://youtube.com'
    """
    try:
        webbrowser.open(url)
        return f"Opened {url}"
    except Exception as e:
        return f"Error opening website: {e}"