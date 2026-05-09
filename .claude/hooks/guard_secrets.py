"""
PreToolUse hook: block any Bash command that would accidentally stage or commit .env.
Receives tool info as JSON on stdin. Exit 2 blocks the tool call entirely.
"""
import json
import re
import sys


DANGEROUS_PATTERNS = [
    r"git\s+add\s+\.env\b",
    r"git\s+add\s+-A\b",
    r"git\s+add\s+\.\b",
    r"git\s+commit\s+.*--all\b",
]

WARN_PATTERNS = [
    r"git\s+commit",
]


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")

    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            print(
                "[hook] BLOCKED: This command could commit .env (contains API keys).\n"
                "Use specific file staging: git add <file> — never 'git add .' or '-A'.\n"
                ".env is listed in .gitignore and must never be committed."
            )
            sys.exit(2)

    for pattern in WARN_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            import subprocess
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True, text=True
            )
            if ".env" in result.stdout.splitlines():
                print(
                    "[hook] BLOCKED: .env is staged for commit. Run 'git reset HEAD .env' first.\n"
                    ".env contains API keys and must never be committed."
                )
                sys.exit(2)


if __name__ == "__main__":
    main()
