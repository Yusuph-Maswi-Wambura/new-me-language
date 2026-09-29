"""Run a NovaLang source file from the command line."""
import argparse
from pathlib import Path

from novalang import NovaError, run_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a NovaLang source file")
    parser.add_argument("source", type=Path, help="Path to a .nova source file")
    arguments = parser.parse_args()
    try:
        for line in run_file(arguments.source):
            print(line)
    except (OSError, NovaError) as error:
        parser.exit(1, f"NovaLang error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
