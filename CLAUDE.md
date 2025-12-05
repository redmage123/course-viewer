# Course Viewer Project

## Overview
Educational course platform with HTML slides and Jupyter notebook labs for Python and AI/ML training.

## Project Structure
```
course-viewer/
├── python-fundamentals/     # Basic Python course
│   ├── python-fundamentals-slides.html  (32 slides)
│   ├── lab-python-basics.ipynb
│   └── lab-python-basics-solution.ipynb
├── python-intermediate/     # Intermediate Python course
│   ├── python-intermediate-slides.html
│   ├── lab-python-intermediate.ipynb
│   └── lab-python-intermediate-solutions.ipynb
├── ai-plain-english/        # AI concepts course
├── out/                     # Generated outputs, ML/LLM courses
└── src/                     # Source code and workspaces
```

## Python Fundamentals Course (32 slides)
Covers: Variables, data types, strings, lists, dictionaries, control flow, functions, error handling, files, modules, tuples, sets, None, boolean logic, loop control (break/continue/pass), enumerate/zip, sorting, nested data, JSON, string methods, variable scope, comments/docstrings, PEP 8, debugging.

## Python Intermediate Course
Covers: OOP (classes, inheritance, polymorphism), properties, descriptors, pattern matching (match), functional programming (lambda, map, filter, reduce), closures, decorators, generators, partial functions, currying, lazy vs eager evaluation, monads, data handling (CSV, JSON), testing (unittest, pytest), packaging.

## Slide HTML Format
- Uses reveal.js-style structure with `<div class="slide" id="slideX">`
- CSS classes: `.two-column`, `.three-column`, `.card`, `.code-block`, `.tip-box`, `.warning-box`, `.highlight`, `.comparison-table`
- Navigation script at bottom with `totalSlides` variable

## Lab Notebook Format
- Jupyter notebooks with markdown instruction cells and code cells
- Code cells use `# YOUR CODE HERE` placeholders
- Solutions in separate `-solution.ipynb` files

## Commands
- Virtual env: `.venv/bin/python`
- Tests: `.venv/bin/pytest`

## Git
- Branch: master
- Remote: github.com:redmage123/course-viewer.git
