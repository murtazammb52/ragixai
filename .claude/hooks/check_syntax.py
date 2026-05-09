"""
PostToolUse hook: syntax-check any Python file that was just edited or written.
Receives tool info as JSON on stdin. Exits non-zero to surface errors to Claude.
"""
import json
import subprocess
import sys


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path.endswith(".py"):
        sys.exit(0)

    result = subprocess.run(
        [sys.executable, "-m", "py_compile", file_path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[hook] SYNTAX ERROR in {file_path}")
        print(result.stderr.strip())
        sys.exit(1)

    print(f"[hook] Syntax OK — {file_path}")


if __name__ == "__main__":
    main()
