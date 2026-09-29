const starter = `// Try changing a value and run again.\nfn square(value) {\n    return value * value;\n}\n\nlet numbers = [1, 2, 3, 4, 5];\nlet index = 0;\nwhile (index < length(numbers)) {\n    print(numbers[index], "squared =", square(numbers[index]));\n    index = index + 1;\n}`;
const lessons = {
  values: `// Lesson 01: values and output\nlet name = "Ada";\nlet year = 1843;\nprint("My name is", name);\nprint("A number can be calculated:", year + 1);`,
  control: `// Lesson 02: decisions and loops\nfor (let number = 1; number <= 5; number = number + 1) {\n    if (number % 2 == 0) {\n        print(number, "is even");\n    } else {\n        print(number, "is odd");\n    }\n}`,
  functions: `// Lesson 03: functions and maps\nfn introduce(person) {\n    return person["name"] + " is learning NovaLang";\n}\n\nlet student = {name: "Ada", topic: "programming"};\nprint(introduce(student));\nprint("Topics:", keys(student));`
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
  const translated = code
    .replace(/\bfn\s+([A-Za-z_]\w*)\s*\(/g, 'function $1(')
    .replace(/\bnil\b/g, 'null');
  const keys = (value) => Object.keys(value);
  const has = (value, key) => Object.prototype.hasOwnProperty.call(value, key);
  Function('print', 'length', 'range', 'keys', 'has', `"use strict";\n${translated}`)(print, length, range, keys, has);
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
