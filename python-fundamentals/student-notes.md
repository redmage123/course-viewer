# Python Fundamentals - Complete Student Notes

## Table of Contents
1. [Getting Started](#1-getting-started)
2. [Variables and Data Types](#2-variables-and-data-types)
3. [User Input and Type Casting](#3-user-input-and-type-casting)
4. [Operators](#4-operators)
5. [Strings](#5-strings)
6. [Lists](#6-lists)
7. [Dictionaries](#7-dictionaries)
8. [Tuples and Sets](#8-tuples-and-sets)
9. [None Type](#9-none-type)
10. [Conditionals](#10-conditionals)
11. [Boolean Logic](#11-boolean-logic)
12. [Loops](#12-loops)
13. [Loop Control](#13-loop-control)
14. [Functions](#14-functions)
15. [Error Handling](#15-error-handling)
16. [File I/O](#16-file-io)
17. [Modules and Imports](#17-modules-and-imports)
18. [List Comprehensions](#18-list-comprehensions)
19. [Working with JSON](#19-working-with-json)
20. [Variable Scope](#20-variable-scope)
21. [Comments and Documentation](#21-comments-and-documentation)
22. [PEP 8 Style Guide](#22-pep-8-style-guide)
23. [Debugging](#23-debugging)

---

## 1. Getting Started

### Why Python?
- **Easy to Learn**: Clean, readable syntax that reads like English
- **Most Popular**: #1 programming language, used by Google, Netflix, Instagram, NASA
- **High Demand**: Top-paying skill in tech
- **Versatile**: Web development, data science, AI/ML, automation, game development

### Your First Program
```python
print("Hello, World!")
```
That's it! One line of code. In other languages, this could be 5-10 lines.

---

## 2. Variables and Data Types

### Creating Variables
Variables are like labeled boxes that store data:
```python
name = "Alice"          # String
age = 25                # Integer
height = 5.6            # Float
is_student = True       # Boolean
```

### Key Points
- No need to declare types (Python figures it out)
- Use descriptive names
- Use `snake_case` (words separated by underscores)
- Variables are case sensitive (`Name` != `name`)

### Python Data Types

| Type | Description | Example |
|------|-------------|---------|
| `str` | Text data in quotes | `"Hello"`, `'World'` |
| `int` | Whole numbers | `42`, `-17`, `0` |
| `float` | Decimal numbers | `3.14`, `-0.5` |
| `bool` | True or False | `True`, `False` |
| `list` | Ordered, changeable collection | `[1, 2, 3]` |
| `dict` | Key-value pairs | `{"name": "Alice"}` |
| `tuple` | Ordered, unchangeable | `(1, 2, 3)` |
| `set` | Unordered, unique values | `{1, 2, 3}` |
| `None` | Absence of value | `None` |

### Checking Types
```python
x = 42
print(type(x))  # <class 'int'>

name = "Alice"
print(type(name))  # <class 'str'>
```

---

## 3. User Input and Type Casting

### Getting Input from Users
```python
name = input("What is your name? ")
print(f"Hello, {name}!")
```

> **IMPORTANT**: The `input()` function **ALWAYS** returns a string, even if the user types a number!

```python
age = input("Enter your age: ")
print(type(age))  # <class 'str'> - It's a string!

# This will NOT work:
next_year = age + 1  # ERROR! Can't add str + int
```

### Type Casting (Converting Types)
```python
# String to Integer
age_str = input("Enter your age: ")
age = int(age_str)          # Convert to integer
print(age + 1)              # Now math works!

# String to Float
price_str = input("Enter price: ")
price = float(price_str)    # Convert to decimal

# One-liner (common pattern)
age = int(input("Enter age: "))
price = float(input("Enter price: "))
```

### Casting Functions

| Function | Converts to | Example |
|----------|-------------|---------|
| `int()` | Integer | `int("42")` → `42` |
| `float()` | Decimal | `float("3.14")` → `3.14` |
| `str()` | String | `str(100)` → `"100"` |
| `bool()` | Boolean | `bool(1)` → `True` |

> **Warning**: If user enters "abc" and you try `int("abc")`, Python crashes! Use try/except to handle this.

---

## 4. Operators

### Arithmetic Operators
```python
a = 10
b = 3

print(a + b)   # 13  (addition)
print(a - b)   # 7   (subtraction)
print(a * b)   # 30  (multiplication)
print(a / b)   # 3.33 (division - always returns float)
print(a // b)  # 3   (floor division - rounds down)
print(a % b)   # 1   (modulo - remainder)
print(a ** b)  # 1000 (power/exponent)
```

### Comparison Operators
```python
x = 5
y = 10

print(x == y)  # False (equal?)
print(x != y)  # True  (not equal?)
print(x < y)   # True  (less than?)
print(x > y)   # False (greater?)
print(x <= y)  # True  (less or equal?)
print(x >= y)  # False (greater or equal?)
```

### Assignment Operators
```python
x = 10
x += 5   # Same as: x = x + 5  → 15
x -= 3   # Same as: x = x - 3  → 12
x *= 2   # Same as: x = x * 2  → 24
x /= 4   # Same as: x = x / 4  → 6.0
```

---

## 5. Strings

### Creating Strings
```python
single = 'Hello'
double = "World"
multiline = """This is a
multi-line string"""
```

### String Operations
```python
name = "Python"

# Length
len(name)      # 6

# Indexing (starts at 0!)
name[0]        # 'P'
name[-1]       # 'n' (last character)
name[-2]       # 'o' (second to last)

# Slicing [start:end] (end not included)
name[0:3]      # 'Pyt'
name[2:]       # 'thon' (from index 2 to end)
name[:3]       # 'Pyt' (from start to index 3)
name[::2]      # 'Pto' (every 2nd character)
```

### String Methods
```python
text = "  Hello World  "

# Case methods
text.upper()           # "  HELLO WORLD  "
text.lower()           # "  hello world  "
text.title()           # "  Hello World  "
text.capitalize()      # "  hello world  "

# Whitespace
text.strip()           # "Hello World"
text.lstrip()          # "Hello World  "
text.rstrip()          # "  Hello World"

# Finding
text.find('World')     # 8 (index where found)
text.find('xyz')       # -1 (not found)

# Replacing
text.replace('World', 'Python')  # "  Hello Python  "

# Checking
"123".isdigit()        # True
"abc".isalpha()        # True
"abc123".isalnum()     # True
text.startswith('  He')  # True
text.endswith('  ')      # True

# Splitting and Joining
csv = "John,Doe,30"
fields = csv.split(',')    # ['John', 'Doe', '30']

words = ['Hello', 'World']
result = ' '.join(words)   # "Hello World"
```

### F-Strings (String Formatting)
```python
name = "Alice"
age = 30
price = 49.99

# Basic formatting
msg = f"Hi {name}, you are {age}"

# Math in f-strings
print(f"Next year: {age + 1}")

# Number formatting
print(f"Price: ${price:.2f}")  # Price: $49.99
print(f"Percent: {0.854:.1%}") # Percent: 85.4%
```

---

## 6. Lists

### Creating Lists
```python
fruits = ["apple", "banana", "cherry"]
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", True, 3.14]
empty = []
```

### Accessing Items
```python
fruits = ["apple", "banana", "cherry"]

print(fruits[0])   # 'apple'
print(fruits[-1])  # 'cherry'
print(fruits[0:2]) # ['apple', 'banana']
```

### Modifying Lists
```python
fruits = ["apple", "banana", "cherry"]

# Change an item
fruits[1] = "blueberry"

# Add items
fruits.append("orange")      # Add to end
fruits.insert(1, "mango")    # Insert at position

# Remove items
fruits.remove("apple")       # Remove by value
popped = fruits.pop()        # Remove and return last
popped = fruits.pop(0)       # Remove and return at index
del fruits[0]                # Delete by index

# Other operations
len(fruits)                  # Number of items
fruits.sort()                # Sort in place
fruits.reverse()             # Reverse in place
fruits.clear()               # Remove all items
```

### Common List Methods

| Method | Description |
|--------|-------------|
| `append(x)` | Add item to end |
| `insert(i, x)` | Insert at position |
| `remove(x)` | Remove first match |
| `pop()` | Remove and return last |
| `pop(i)` | Remove and return at index |
| `sort()` | Sort the list |
| `reverse()` | Reverse order |
| `index(x)` | Find index of item |
| `count(x)` | Count occurrences |
| `copy()` | Return a shallow copy |

---

## 7. Dictionaries

### Creating Dictionaries
```python
person = {
    "name": "Alice",
    "age": 30,
    "city": "New York",
    "is_student": False
}

empty = {}
```

### Accessing Values
```python
# By key
print(person["name"])      # 'Alice'

# Safe access with .get() (no error if missing)
print(person.get("age"))           # 30
print(person.get("email"))         # None
print(person.get("email", "N/A"))  # "N/A" (default)
```

### Modifying Dictionaries
```python
# Add or update
person["email"] = "alice@example.com"
person["age"] = 31

# Remove
del person["is_student"]
removed_value = person.pop("city")

# Clear all
person.clear()
```

### Dictionary Methods
```python
person = {"name": "Alice", "age": 30}

# Get all keys, values, or items
person.keys()    # dict_keys(['name', 'age'])
person.values()  # dict_values(['Alice', 30])
person.items()   # dict_items([('name', 'Alice'), ('age', 30)])

# Check if key exists
if "name" in person:
    print("Name exists!")

# Iterate
for key in person:
    print(f"{key}: {person[key]}")

for key, value in person.items():
    print(f"{key}: {value}")
```

---

## 8. Tuples and Sets

### Tuples (Immutable Lists)
```python
# Creating tuples
coordinates = (10, 20)
rgb_color = (255, 128, 0)
single_item = (42,)  # Note the comma!

# Accessing (like lists)
print(coordinates[0])  # 10
print(rgb_color[-1])   # 0

# Tuple unpacking
x, y = coordinates
name, age, city = ("Alice", 30, "NYC")

# Tuples are immutable!
coordinates[0] = 15  # ERROR! Can't modify
```

**When to use tuples**: Function return values, coordinates, RGB colors, database records - anything that shouldn't change.

### Sets (Unique Collections)
```python
# Creating sets
fruits = {"apple", "banana", "cherry"}
numbers = {1, 2, 3, 4, 5}

# Duplicates are automatically removed
duplicates = {1, 2, 2, 3, 3, 3}
print(duplicates)  # {1, 2, 3}

# Adding and removing
fruits.add("orange")
fruits.add("apple")      # No effect (already exists)
fruits.remove("banana")  # Error if not found
fruits.discard("grape")  # No error if not found

# Membership testing (very fast!)
if "apple" in fruits:
    print("Found!")
```

### Set Operations
```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

# Union (combine all)
print(a | b)  # {1, 2, 3, 4, 5, 6}

# Intersection (common elements)
print(a & b)  # {3, 4}

# Difference (in a but not in b)
print(a - b)  # {1, 2}

# Symmetric difference (in one but not both)
print(a ^ b)  # {1, 2, 5, 6}
```

> **Note**: Sets are unordered - you can't use indexing like `fruits[0]`!

---

## 9. None Type

`None` is Python's way of representing "nothing" or "no value".

```python
# None as default parameter
def greet(name=None):
    if name is None:
        return "Hello, stranger!"
    return f"Hello, {name}!"

# Functions return None by default
def do_something():
    print("Doing...")
    # No return statement

result = do_something()
print(result)  # None

# Always use 'is', not '=='
if value is None:     # Correct!
    print("No value")
```

**Common use cases**:
- Optional function parameters
- Variables not yet assigned
- Functions with no meaningful return value
- Database null values

---

## 10. Conditionals

### If/Elif/Else
```python
age = 18

if age < 13:
    print("Child")
elif age < 20:
    print("Teenager")
else:
    print("Adult")
```

### Multiple Conditions
```python
temperature = 75
is_sunny = True

# AND - both must be True
if temperature > 70 and is_sunny:
    print("Perfect beach day!")

# OR - at least one must be True
if temperature < 32 or temperature > 100:
    print("Extreme weather!")

# NOT - inverts the value
if not is_sunny:
    print("It's cloudy")
```

### Ternary Operator
```python
age = 20
status = "adult" if age >= 18 else "minor"
```

> **Important**: Indentation matters! Python uses 4 spaces to define code blocks.

---

## 11. Boolean Logic

### Truth Tables

| A | B | A and B | A or B | not A |
|---|---|---------|--------|-------|
| True | True | True | True | False |
| True | False | False | True | False |
| False | True | False | True | True |
| False | False | False | False | True |

### Truthy and Falsy Values

These values are considered **False** (falsy):
```python
bool(False)     # False
bool(0)         # False
bool(0.0)       # False
bool("")        # False (empty string)
bool([])        # False (empty list)
bool({})        # False (empty dict)
bool(None)      # False
```

Everything else is **True** (truthy)!

### Short-Circuit Evaluation
```python
# 'and' stops at first False
# 'or' stops at first True

# This prevents errors:
user = None
if user and user.name == "Alice":
    print("Hi Alice!")  # Won't crash!

# Default values pattern:
name = user_input or "Anonymous"
```

---

## 12. Loops

### For Loops
```python
# Loop through a list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(f"I love {fruit}!")

# Loop with range
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

for i in range(2, 6):
    print(i)  # 2, 3, 4, 5

for i in range(0, 10, 2):
    print(i)  # 0, 2, 4, 6, 8

# Loop with index using enumerate
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")

# Loop through dictionary
person = {"name": "Alice", "age": 30}
for key, value in person.items():
    print(f"{key}: {value}")
```

### While Loops
```python
count = 0
while count < 5:
    print(count)
    count += 1

# Infinite loop with break
while True:
    user_input = input("Enter 'quit' to exit: ")
    if user_input == 'quit':
        break
```

> **Tip**: Use `for` when you know how many iterations. Use `while` when you don't!

---

## 13. Loop Control

### break - Exit Loop Early
```python
for num in [1, 2, 3, 4, 5]:
    if num == 3:
        break
    print(num)  # Prints: 1, 2
```

### continue - Skip Iteration
```python
for num in range(10):
    if num % 2 == 0:
        continue
    print(num)  # 1, 3, 5, 7, 9
```

### pass - Do Nothing (Placeholder)
```python
def future_feature():
    pass  # Will implement later

if condition:
    pass  # TODO: handle later
```

### Loop else Clause
```python
# 'else' runs if NO break occurred
for num in [1, 3, 5, 7]:
    if num % 2 == 0:
        print("Found even!")
        break
else:
    print("No evens found")  # This runs!
```

### enumerate() and zip()
```python
# enumerate - get index with value
fruits = ['apple', 'banana', 'cherry']
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")

for i, fruit in enumerate(fruits, start=1):
    print(f"{i}. {fruit}")

# zip - combine multiple lists
names = ['Alice', 'Bob']
ages = [25, 30]

for name, age in zip(names, ages):
    print(f"{name} is {age}")

# Create dictionary from two lists
person_dict = dict(zip(names, ages))
```

---

## 14. Functions

### Defining Functions
```python
def greet(name):
    return f"Hello, {name}!"

print(greet("Alice"))  # Hello, Alice!
```

### Parameters and Arguments
```python
# Default parameters
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Bob"))           # Hello, Bob!
print(greet("Bob", "Hi"))     # Hi, Bob!

# Keyword arguments
print(greet(greeting="Hey", name="Carol"))
```

### Multiple Return Values
```python
def get_stats(numbers):
    return min(numbers), max(numbers), sum(numbers)/len(numbers)

minimum, maximum, average = get_stats([1, 5, 3, 9, 2])
```

### *args and **kwargs
```python
# *args - variable number of positional arguments
def add_all(*numbers):
    return sum(numbers)

print(add_all(1, 2, 3, 4))  # 10

# **kwargs - variable number of keyword arguments
def print_info(**info):
    for key, value in info.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=30, city="NYC")
```

### Why Use Functions?
- **DRY**: Don't Repeat Yourself
- **Organize**: Break code into logical pieces
- **Reuse**: Write once, use many times
- **Test**: Easier to test small functions

---

## 15. Error Handling

### Try/Except
```python
try:
    number = int(input("Enter a number: "))
    result = 10 / number
    print(f"Result: {result}")
except ValueError:
    print("That's not a valid number!")
except ZeroDivisionError:
    print("Can't divide by zero!")
except Exception as e:
    print(f"Something went wrong: {e}")
finally:
    print("This always runs!")
```

### Common Exceptions

| Exception | When it happens |
|-----------|-----------------|
| `ValueError` | Wrong type of value |
| `TypeError` | Wrong type operation |
| `KeyError` | Dict key not found |
| `IndexError` | List index out of range |
| `FileNotFoundError` | File doesn't exist |
| `ZeroDivisionError` | Division by zero |
| `NameError` | Variable not defined |

### Raising Exceptions
```python
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero!")
    return a / b
```

---

## 16. File I/O

### Reading Files
```python
# Read entire file
with open("data.txt", "r") as file:
    content = file.read()
    print(content)

# Read line by line
with open("data.txt", "r") as file:
    for line in file:
        print(line.strip())

# Read all lines into list
with open("data.txt", "r") as file:
    lines = file.readlines()
```

### Writing Files
```python
# Write (overwrites existing content)
with open("output.txt", "w") as file:
    file.write("Hello, File!\n")
    file.write("Second line")

# Append (adds to existing content)
with open("log.txt", "a") as file:
    file.write("New log entry\n")
```

> **Important**: Always use the `with` statement! It automatically closes the file when done, even if an error occurs.

### File Modes

| Mode | Description |
|------|-------------|
| `'r'` | Read (default) |
| `'w'` | Write (overwrites) |
| `'a'` | Append |
| `'x'` | Create (fails if exists) |
| `'b'` | Binary mode |

---

## 17. Modules and Imports

### Importing Modules
```python
# Import entire module
import math
print(math.sqrt(16))  # 4.0
print(math.pi)        # 3.14159...

# Import specific functions
from random import randint, choice
print(randint(1, 100))
print(choice(["a", "b", "c"]))

# Import with alias
import datetime as dt
today = dt.date.today()

# Import everything (not recommended)
from math import *
```

### Popular Built-in Modules

| Module | Purpose |
|--------|---------|
| `math` | Mathematical functions |
| `random` | Random numbers |
| `datetime` | Date and time |
| `os` | Operating system interface |
| `sys` | System-specific parameters |
| `json` | JSON parsing |
| `re` | Regular expressions |
| `collections` | Specialized containers |

---

## 18. List Comprehensions

### Basic Syntax
```python
# [expression for item in iterable]
squares = [x ** 2 for x in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

### With Condition
```python
# [expression for item in iterable if condition]
evens = [x for x in range(20) if x % 2 == 0]
# [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
```

### Transforming Data
```python
names = ["alice", "bob", "charlie"]
upper_names = [name.upper() for name in names]
# ['ALICE', 'BOB', 'CHARLIE']

# With condition
long_names = [name for name in names if len(name) > 4]
# ['alice', 'charlie']
```

### Dictionary Comprehension
```python
# {key: value for item in iterable}
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
```

---

## 19. Working with JSON

### JSON to Python Mapping

| JSON | Python |
|------|--------|
| object | dict |
| array | list |
| string | str |
| number | int/float |
| true/false | True/False |
| null | None |

### Converting
```python
import json

data = {"name": "Alice", "age": 30}

# Python to JSON string
json_str = json.dumps(data)
print(json_str)  # '{"name": "Alice", "age": 30}'

# JSON string to Python
data = json.loads(json_str)

# Pretty print
print(json.dumps(data, indent=4))
```

### File Operations
```python
import json

# Write to file
data = {"users": [{"id": 1, "name": "Alice"}]}
with open("data.json", "w") as f:
    json.dump(data, f, indent=4)

# Read from file
with open("data.json", "r") as f:
    data = json.load(f)
```

---

## 20. Variable Scope

### LEGB Rule
Python looks for variables in this order:
1. **L**ocal: Inside current function
2. **E**nclosing: In parent functions
3. **G**lobal: Module level
4. **B**uilt-in: Python's built-ins

```python
x = "global"  # Global scope

def outer():
    x = "enclosing"  # Enclosing

    def inner():
        x = "local"  # Local
        print(x)     # "local"

    inner()
    print(x)  # "enclosing"

outer()
print(x)  # "global"
```

### Global Keyword
```python
count = 0

def increment():
    global count  # Required to modify global
    count += 1
```

> **Best Practice**: Avoid global variables! Pass values as parameters and use return values instead.

---

## 21. Comments and Documentation

### Comments
```python
# Single-line comment
x = 5  # Comment after code

# Explain WHY, not WHAT
# Bad: increment x by 1
x += 1

# Good: Account for 1-based indexing
x += 1
```

### Docstrings
```python
def calculate_area(radius):
    """
    Calculate the area of a circle.

    Args:
        radius (float): The radius of the circle

    Returns:
        float: The area of the circle

    Example:
        >>> calculate_area(5)
        78.54
    """
    return 3.14159 * radius ** 2

# Access docstring
print(calculate_area.__doc__)
```

---

## 22. PEP 8 Style Guide

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables | snake_case | `user_name` |
| Functions | snake_case | `calculate_total()` |
| Classes | PascalCase | `UserAccount` |
| Constants | UPPER_CASE | `MAX_SIZE` |

### Key Rules
- Use 4 spaces for indentation (not tabs)
- Maximum line length: 79-120 characters
- Two blank lines before classes/functions
- Imports at the top of the file

### Import Order
```python
# Standard library
import os
import sys

# Third-party
import numpy as np

# Local
from myapp import utils
```

---

## 23. Debugging

### Reading Error Messages
```python
Traceback (most recent call last):
  File "script.py", line 10
    result = divide(10, 0)
  File "script.py", line 5
    return a / b
ZeroDivisionError: division by zero

# Read bottom to top:
# 1. Error type: ZeroDivisionError
# 2. Message: division by zero
# 3. Where: line 5 in divide()
# 4. Called from: line 10
```

### Common Errors

| Error | Cause |
|-------|-------|
| `IndentationError` | Wrong indentation |
| `NameError` | Variable not defined |
| `TypeError` | Wrong type operation |
| `SyntaxError` | Invalid Python syntax |
| `KeyError` | Dict key not found |
| `IndexError` | List index out of range |

### Print Debugging
```python
def calc(price, discount):
    print(f"DEBUG: {price=}, {discount=}")
    result = price * (1 - discount)
    print(f"DEBUG: {result=}")
    return result
```

---

## Quick Reference

### Essential Built-in Functions
```python
len(x)          # Length of x
type(x)         # Type of x
print(x)        # Print x
input(prompt)   # Get user input
range(n)        # Numbers 0 to n-1
int(x)          # Convert to integer
float(x)        # Convert to float
str(x)          # Convert to string
list(x)         # Convert to list
dict(x)         # Convert to dictionary
sorted(x)       # Return sorted list
sum(x)          # Sum of numbers
min(x)          # Minimum value
max(x)          # Maximum value
abs(x)          # Absolute value
round(x, n)     # Round to n decimals
enumerate(x)    # Get index and value
zip(a, b)       # Combine iterables
```

---

*Happy Coding! Remember: Practice makes perfect!*
