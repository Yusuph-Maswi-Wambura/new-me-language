const starter = `// Try changing a value and run again.\nfn square(value) {\n    return value * value;\n}\n\nlet numbers = [1, 2, 3, 4, 5];\nlet index = 0;\nwhile (index < length(numbers)) {\n    print(numbers[index], "squared =", square(numbers[index]));\n    index = index + 1;\n}`;
const lessons = {
  values: `// Lesson 01: values and output\nlet name = "Ada";\nlet year = 1843;\nprint("My name is", name);\nprint("A number can be calculated:", year + 1);`,
  control: `// Lesson 02: decisions and loops\nfor (let number = 1; number <= 5; number = number + 1) {\n    if (number % 2 == 0) {\n        print(number, "is even");\n    } else {\n        print(number, "is odd");\n    }\n}`,
  functions: `// Lesson 03: functions and maps\nfn introduce(person) {\n    return person["name"] + " is learning NovaLang";\n}\n\nlet student = {name: "Ada", topic: "programming"};\nprint(introduce(student));\nprint("Topics:", keys(student));`
  ,objects: `// Lesson 04: objects and inheritance\nclass Animal {\n    fn init(name) { this.name = name; }\n    fn speak() { return this.name; }\n}\n\nclass Dog < Animal {\n    fn speak() { return super.speak() + " says woof"; }\n}\n\nlet dog = Dog("Milo");\nprint(dog.speak());`,
  advanced: `// Lesson 05: functional programming and errors\nlet values = [1, 2, 3, 4];\nlet even = filter(lambda(value) { return value % 2 == 0; }, values);\nlet total = reduce(lambda(left, right) { return left + right; }, even, 0);\ntry {\n    if (total > 0) { throw "Total is ready"; }\n} catch (message) {\n    print(message, "=", total);\n} finally {\n    print("cleanup complete");\n}`
};

const source = document.querySelector('#source');
const output = document.querySelector('#output');
const lineCount = document.querySelector('#line-count');
const runButton = document.querySelector('#run');
source.value = starter;

function updateLineCount() {
  const count = source.value.split('\n').length;
  lineCount.textContent = `${count} line${count === 1 ? '' : 's'}`;
}

function translateClasses(code) {
  const classNames = [];
  const header = /class\s+([A-Za-z_]\w*)(?:\s*<\s*([A-Za-z_]\w*))?\s*\{/g;
  let result = '';
  let cursor = 0;
  let match;
  while ((match = header.exec(code))) {
    let depth = 1;
    let end = match.index + match[0].length;
    while (depth && end < code.length) {
      if (code[end] === '{') depth += 1;
      if (code[end] === '}') depth -= 1;
      end += 1;
    }
    const bodyStart = match.index + match[0].length;
    let body = code.slice(bodyStart, end - 1)
      .replace(/\bfn\s+([A-Za-z_]\w*)\s*\(/g, '$1(')
      .replace(/\binit\s*\(/, 'constructor(');
    const parent = match[2] ? ` extends ${match[2]}` : '';
    result += code.slice(cursor, match.index) + `class ${match[1]}${parent} {${body}}`;
    classNames.push(match[1]);
    cursor = end;
    header.lastIndex = end;
  }
  result += code.slice(cursor);
  for (const className of classNames) {
    result = result.replace(new RegExp(`(\\blet\\s+[A-Za-z_]\\w*\\s*=\\s*)${className}\\(`, 'g'), `$1new ${className}(`);
  }
  return result;
}

function runLocalProgram(code) {
  const lines = [];
  const print = (...values) => lines.push(values.map((value) => {
    if (value === null) return 'nil';
    if (value === true) return 'true';
    if (value === false) return 'false';
    return Array.isArray(value) ? `[${value.join(', ')}]` : String(value);
  }).join(' '));
  const length = (value) => value.length;
  const range = (end) => Array.from({ length: Number(end) }, (_, index) => index);
  const set = (values) => [...new Set(values)];
  const contains = (value, item) => value.includes(item);
  const map = (functionValue, values) => values.map((value) => functionValue(value));
  const filter = (functionValue, values) => values.filter((value) => functionValue(value));
  const reduce = (functionValue, values, initial) => values.reduce((total, value) => functionValue(total, value), initial);
  const translated = translateClasses(code)
    .replace(/\bfn\s+([A-Za-z_]\w*)\s*\(/g, 'function $1(')
    .replace(/\blambda\s*\(/g, 'function(')
    .replace(/\bnil\b/g, 'null');
  const keys = (value) => Object.keys(value);
  const has = (value, key) => Object.prototype.hasOwnProperty.call(value, key);
  Function('print', 'length', 'range', 'keys', 'has', 'set', 'contains', 'map', 'filter', 'reduce', `"use strict";\n${translated}`)(print, length, range, keys, has, set, contains, map, filter, reduce);
  return lines;
}

function showResult(lines, isError = false) {
  output.textContent = lines.join('\n') || 'Program finished without output.';
  output.classList.toggle('error', isError);
}

async function runProgram() {
  runButton.disabled = true;
  runButton.querySelector('span').textContent = 'Running...';
  try {
    if (window.location.protocol === 'file:' || window.location.hostname.endsWith('github.io')) {
      showResult(runLocalProgram(source.value));
      return;
    }
    const response = await fetch('/api/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ source: source.value }) });
    const result = await response.json();
    showResult(result.ok ? result.output : [`Error: ${result.error}`], !result.ok);
  } catch (error) {
    try {
      showResult(runLocalProgram(source.value));
    } catch (localError) {
      showResult([`Error: ${localError.message}`], true);
    }
  } finally {
    runButton.disabled = false;
    runButton.querySelector('span').textContent = 'Run program';
  }
}

document.querySelector('#reset').addEventListener('click', () => { source.value = starter; updateLineCount(); });
document.querySelectorAll('.lesson-button').forEach((button) => {
  button.addEventListener('click', () => {
    source.value = lessons[button.dataset.lesson];
    updateLineCount();
    source.scrollIntoView({ behavior: 'smooth', block: 'center' });
    source.focus();
  });
});
source.addEventListener('input', updateLineCount);
runButton.addEventListener('click', runProgram);
source.addEventListener('keydown', (event) => { if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') runProgram(); });
updateLineCount();
