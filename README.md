# NovaLang

NovaLang is a small, readable programming language designed as a learning laboratory for core programming principles. It currently has a hand-written lexer, recursive-descent parser, AST evaluator, lexical environments, first-class functions, and a zero-dependency browser playground.

## Features

- Numbers, strings, booleans, `nil`, arrays, and maps
- Variables with `let`
- Functions and recursion with `fn`
- `if` / `else if` / `else`, `while`, `for`, `break`, `return`
- Arithmetic, comparison, boolean operators, indexing, and indexed assignment
- Built-ins: `print`, `length`, `range`, `keys`, and `has`
- Clear runtime errors and a 100,000-iteration loop guard
- Python runtime, Java reference lexer, HTML/CSS/JavaScript playground

## Run the playground

```powershell
python server.py
```

Open <http://localhost:8000>. No package installation is required.

Opening `web/index.html` directly also works: the browser runs a compatible local fallback and shows output or errors in the page. The server URL uses the full Python reference runtime and is recommended for exact language behavior.

## Run tests

```powershell
python -m unittest discover -s tests -v
```

## Run a `.nova` file

```powershell
python run_nova.py examples/basics.nova
```

The command prints the program's output and returns a non-zero exit code for a syntax or runtime error.

## Language syntax

Read the complete reference in [SYNTAX.md](SYNTAX.md). It lists every supported value, operator, statement, built-in function, runnable example, and current limitation.

## Use the Java lexer

```powershell
javac java/NovaLang.java
java -cp java NovaLang examples/basics.nova
```

The Java program is intentionally a companion implementation: it makes the tokenization stage inspectable while Python remains the executable reference runtime. The next natural evolution is a shared AST contract and a bytecode backend.

## Publish the learning app

The repository includes a GitHub Pages workflow at `.github/workflows/pages.yml`. After pushing the project to a GitHub repository's `main` branch, enable **Settings → Pages → GitHub Actions**. GitHub will publish the `web` folder, including the browser fallback runtime and learning lessons.

GitHub Pages hosts the browser experience. The complete Python server and Java lexer still run locally from the project folder.

## Example

```nova
fn greet(name) {
    return "Hello, " + name;
}

let names = ["Ada", "Linus", "Grace"];
let index = 0;
while (index < length(names)) {
    print(greet(names[index]));
    index = index + 1;
}
```
