"""Interactive NovaLang read-eval-print loop."""
from novalang import Interpreter, NovaError, Parser, lex


def main() -> int:
    interpreter = Interpreter()
    print("New Me REPL | NovaLang 0.2 | :help for commands")
    while True:
        try:
            source = input("nova> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if source.strip() in {":quit", ":q"}:
            return 0
        if source.strip() == ":help":
            print(":help  Show commands")
            print(":quit  Exit the REPL")
            continue
        if not source.strip():
            continue
        try:
            interpreter.run(Parser(lex(source)).parse())
            for line in interpreter.output:
                print(line)
            interpreter.output.clear()
        except NovaError as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    raise SystemExit(main())
