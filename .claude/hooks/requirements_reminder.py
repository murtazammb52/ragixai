"""
PostToolUse hook: remind to reinstall dependencies when requirements.txt is modified.
"""
import json
import sys


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path.endswith("requirements.txt"):
        sys.exit(0)

    print(
        "[hook] requirements.txt changed — remember to reinstall:\n"
        "  pip install -r requirements.txt"
    )


if __name__ == "__main__":
    main()
