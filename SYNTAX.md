# NovaLang Syntax Reference

NovaLang 0.1 is a small interpreted language. Every statement ends with `;`, and blocks use `{` and `}`.

## Running a program

From the project folder:

```powershell
python server.py
```

Open `http://localhost:8000`, paste code into the editor, and select **Run program**.

You can also open `web/index.html` directly. In that mode the browser uses a local compatibility runner, and output or errors still appear in the output panel. The Python server remains the complete reference implementation.

To run NovaLang directly from Python:

```powershell
python -c "from novalang import run; print(run('print(2 + 3);'))"
```

The result is a Python list containing each line printed by the program.

## Comments

Comments begin with `//` and continue to the end of the line.

```nova
// This line is ignored by the interpreter.
print("Hello, NovaLang");
```

## Values

NovaLang has five value categories:

```nova
let count = 42;              // number
let ratio = 0.5;             // number
let title = "NovaLang";      // string
let enabled = true;          // boolean
let missing = nil;           // empty value
let scores = [10, 20, 30];   // array
let user = {name: "Ada"};    // map
```

Strings use double quotes. Escape sequences such as `\n`, `\t`, and `\"` are supported.

## Variables

Declare a variable with `let`. Reassign an existing variable with `=`.

```nova
let score = 10;
score = score + 5;
print(score); // 15
```

Assignment must target an existing variable. NovaLang reports an error instead of silently creating a misspelled variable.

## Operators

| Precedence | Operators | Meaning |
|---|---|---|
| 7 | `!`, unary `-` | not, numeric negation |
| 6 | `*`, `/`, `%` | multiply, divide, remainder |
| 5 | `+`, `-` | add, subtract, string concatenation |
| 4 | `<`, `<=`, `>`, `>=` | comparison |
| 3 | `==`, `!=` | equality |
| 2 | `&&` | logical and, short-circuiting |
| 1 | `||` | logical or, short-circuiting |
| 0 | `=` | assignment |

Parentheses can make grouping explicit:

```nova
let result = (2 + 3) * 4;
print(result); // 20
```

`false`, `nil`, `0`, and an empty string are false-like. Other values are true-like.

## Functions

Define functions with `fn`. Functions can accept parameters, return values, and call themselves recursively.

```nova
fn greet(name) {
    return "Hello, " + name;
}

print(greet("Ada"));
```

A function without `return` produces `nil`.

```nova
fn announce(message) {
    print(message);
}
announce("ready");
```

## Conditions

Use `if`, `else if`, and `else` for branching.

```nova
let temperature = 18;
if (temperature >= 25) {
    print("hot");
} else if (temperature >= 15) {
    print("comfortable");
} else {
    print("cold");
}
```

## Loops

Use `while` or C-style `for` loops for repetition. Use `break` to leave the nearest loop.

```nova
let index = 0;
while (index < 5) {
    print(index);
    index = index + 1;
}

while (true) {
    print("runs once");
    break;
}

for (let index = 0; index < 3; index = index + 1) {
    print(index);
}
```

A loop is capped at 100,000 iterations to protect the playground from accidental infinite loops.

## Arrays, maps, and indexing

Arrays are zero-indexed and can contain expressions.

```nova
let names = ["Ada", "Linus", "Grace"];
print(names[0]);
print(length(names));
```

Maps use string or identifier keys. Arrays and maps both support indexed assignment.

```nova
let scores = [10, 20, 30];
scores[1] = 25;
let person = {name: "Ada", score: scores[1]};
person["score"] = 30;
print(person["name"], person["score"]);
```

An invalid index produces a NovaLang error.

## Built-in functions

| Function | Example | Result |
|---|---|---|
| `print(...)` | `print("total", 12);` | Writes one output line |
| `length(value)` | `length([1, 2, 3]);` | Returns `3` |
| `range(end)` | `range(3);` | Returns `[0, 1, 2]` |
| `keys(map)` | `keys({name: "Ada"});` | Returns the map keys |
| `has(map, key)` | `has({name: "Ada"}, "name");` | Returns a boolean |

`print` accepts any number of arguments. `length` accepts strings and arrays. `range` uses an inclusive start of `0` and an exclusive end.

## Complete example

```nova
// Calculate the first even values below a limit.
fn is_even(value) {
    return value % 2 == 0;
}

let value = 0;
let found = 0;
while (value < 20 && found < 5) {
    if (is_even(value)) {
        print(value);
        found = found + 1;
    }
    value = value + 1;
}
```

## Current limits

The reference runtime intentionally keeps its grammar small. It does not yet include imports, user-defined classes, or static type checking. These are planned extensions; examples should use only the syntax described in this document.
