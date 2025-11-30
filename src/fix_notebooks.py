#!/usr/bin/env python3
"""
Script to fix lab notebooks:
1. Student labs: Remove code cells, keep only markdown instructions
2. Solution labs: Add walkthrough markdown before each code cell
"""
import json
import os
import re

OUT_DIR = '/home/bbrelin/course-viewer/out'

# Labs to process (base names without -solution suffix)
LABS = [
    'lab-01-python-data-science',
    'lab-02-ml-basics',
    'lab-03-neural-networks',
    'lab-04-pytorch-fundamentals',
    'lab-05-nlp-basics',
    'lab-06-llm-apis',
]


def extract_function_info(code):
    """Extract function name and docstring from code."""
    # Find function definition
    func_match = re.search(r'def\s+(\w+)\s*\([^)]*\):', code)
    if func_match:
        func_name = func_match.group(1)
        # Find docstring
        doc_match = re.search(r'"""([^"]*)"""', code)
        docstring = doc_match.group(1).strip() if doc_match else None
        return func_name, docstring
    return None, None


def generate_walkthrough(code, cell_index):
    """Generate a markdown walkthrough for a code cell."""
    lines = code.strip().split('\n')

    # Detect what the code does
    has_imports = any(line.strip().startswith(('import ', 'from ')) for line in lines)
    has_function = 'def ' in code
    has_class = 'class ' in code
    has_print = 'print(' in code
    has_plot = any(x in code for x in ['plt.', 'plot(', '.show()'])
    has_return = 'return ' in code

    func_name, docstring = extract_function_info(code)

    # Build walkthrough
    walkthrough = []
    walkthrough.append(f"### Code Walkthrough - Cell {cell_index + 1}\n")

    if has_imports:
        imports = [l.strip() for l in lines if l.strip().startswith(('import ', 'from '))]
        walkthrough.append("**Imports:**")
        for imp in imports[:5]:  # Limit to 5 imports
            walkthrough.append(f"- `{imp}`")
        walkthrough.append("")

    if has_function:
        walkthrough.append(f"**Function: `{func_name}()`**")
        if docstring:
            walkthrough.append(f"> {docstring}")
        walkthrough.append("")

    if has_class:
        class_match = re.search(r'class\s+(\w+)', code)
        if class_match:
            walkthrough.append(f"**Class: `{class_match.group(1)}`**")
            walkthrough.append("")

    # Add general description based on content
    walkthrough.append("**What this code does:**")

    descriptions = []
    if has_imports:
        descriptions.append("Sets up required libraries and dependencies")
    if has_function:
        descriptions.append(f"Defines the `{func_name}` function" + (f" which {docstring.lower()}" if docstring else ""))
    if has_plot:
        descriptions.append("Creates a visualization using matplotlib")
    if has_print:
        descriptions.append("Outputs results to the console")
    if has_return:
        descriptions.append("Returns computed values for further use")

    if not descriptions:
        descriptions.append("Executes the main logic for this exercise")

    for desc in descriptions:
        walkthrough.append(f"- {desc}")

    walkthrough.append("")
    walkthrough.append("**Run this cell** to see the output below.")
    walkthrough.append("")

    return '\n'.join(walkthrough)


def fix_student_lab(filepath):
    """Remove code cells from student lab, keep only markdown."""
    with open(filepath, 'r') as f:
        nb = json.load(f)

    # Keep only markdown cells
    new_cells = []
    for cell in nb['cells']:
        if cell['cell_type'] == 'markdown':
            new_cells.append(cell)
        elif cell['cell_type'] == 'code':
            # Convert code cell to a placeholder markdown cell
            source = cell.get('source', [])
            code_content = ''.join(source) if isinstance(source, list) else source

            # Check if it's a TODO/exercise cell
            if 'TODO' in code_content or '# Your code here' in code_content.lower():
                # Add a placeholder for the exercise
                placeholder = [
                    "**Your Code Here:**\n",
                    "\n",
                    "```python\n",
                    "# Write your solution in the interactive lab environment\n",
                    "```\n"
                ]
                new_cells.append({
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': placeholder
                })

    nb['cells'] = new_cells

    with open(filepath, 'w') as f:
        json.dump(nb, f, indent=2)

    print(f"Fixed student lab: {filepath}")
    print(f"  - Removed code cells, kept {len(new_cells)} markdown cells")


def fix_solution_lab(filepath):
    """Add walkthrough markdown before each code cell in solution lab."""
    with open(filepath, 'r') as f:
        nb = json.load(f)

    new_cells = []
    code_cell_count = 0

    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = cell.get('source', [])
            code_content = ''.join(source) if isinstance(source, list) else source

            # Generate walkthrough markdown
            walkthrough = generate_walkthrough(code_content, code_cell_count)

            # Add walkthrough cell before code cell
            new_cells.append({
                'cell_type': 'markdown',
                'metadata': {},
                'source': [walkthrough]
            })

            new_cells.append(cell)
            code_cell_count += 1
        else:
            new_cells.append(cell)

    nb['cells'] = new_cells

    with open(filepath, 'w') as f:
        json.dump(nb, f, indent=2)

    print(f"Fixed solution lab: {filepath}")
    print(f"  - Added {code_cell_count} walkthrough cells")


def main():
    print("Fixing lab notebooks...\n")

    for lab_name in LABS:
        student_path = os.path.join(OUT_DIR, f'{lab_name}.ipynb')
        solution_path = os.path.join(OUT_DIR, f'{lab_name}-solution.ipynb')

        if os.path.exists(student_path):
            fix_student_lab(student_path)
        else:
            print(f"Warning: Student lab not found: {student_path}")

        if os.path.exists(solution_path):
            fix_solution_lab(solution_path)
        else:
            print(f"Warning: Solution lab not found: {solution_path}")

        print()

    print("Done!")


if __name__ == '__main__':
    main()
