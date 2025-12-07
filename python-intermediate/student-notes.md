# Intermediate Python Programming - Complete Student Notes

## Table of Contents
1. [Object-Oriented Programming (OOP)](#1-object-oriented-programming-oop)
2. [Classes and Objects](#2-classes-and-objects)
3. [Inheritance](#3-inheritance)
4. [Polymorphism](#4-polymorphism)
5. [Encapsulation](#5-encapsulation)
6. [ABC, Protocol, and Mixins](#6-abc-protocol-and-mixins)
7. [Operator Overloading](#7-operator-overloading)
8. [Functional Programming](#8-functional-programming)
9. [Decorators](#9-decorators)
10. [Generators](#10-generators)
11. [Generator Pipelines and Coroutines](#11-generator-pipelines-and-coroutines)
12. [itertools Module](#12-itertools-module)
13. [Collections Module](#13-collections-module)
14. [Data Handling](#14-data-handling)
15. [Regular Expressions](#15-regular-expressions)
16. [The os and sys Modules](#16-the-os-and-sys-modules)
17. [Testing with unittest and pytest](#17-testing-with-unittest-and-pytest)
18. [Python Packaging](#18-python-packaging)

---

## 1. Object-Oriented Programming (OOP)

### The Four Pillars of OOP
1. **Encapsulation**: Bundling data and methods together
2. **Abstraction**: Hiding complex implementation details
3. **Inheritance**: Creating new classes from existing ones
4. **Polymorphism**: Using a unified interface for different types

### Why OOP?
- **Organization**: Group related data and behavior
- **Reusability**: Inherit and extend existing code
- **Maintainability**: Easier to modify and debug
- **Real-world modeling**: Objects represent real entities

---

## 2. Classes and Objects

### Defining a Class
```python
class Dog:
    # Class attribute (shared by all instances)
    species = "Canis familiaris"

    # Constructor (initializer)
    def __init__(self, name, age):
        # Instance attributes (unique to each object)
        self.name = name
        self.age = age

    # Instance method
    def bark(self):
        return f"{self.name} says Woof!"

    # Another instance method
    def describe(self):
        return f"{self.name} is {self.age} years old"

# Create objects (instances)
dog1 = Dog("Buddy", 3)
dog2 = Dog("Max", 5)

print(dog1.bark())       # Buddy says Woof!
print(dog2.describe())   # Max is 5 years old
print(Dog.species)       # Canis familiaris
```

### Understanding `__init__` and `self`
- `__init__`: The constructor method - called automatically when creating an object
- `self`: Reference to the current instance - must be the first parameter of instance methods

### Class vs Instance Attributes
```python
class Car:
    # Class attribute - same for all cars
    wheels = 4

    def __init__(self, brand, color):
        # Instance attributes - unique per car
        self.brand = brand
        self.color = color

car1 = Car("Toyota", "Red")
car2 = Car("Honda", "Blue")

print(car1.wheels)  # 4 (from class)
print(car1.brand)   # Toyota (from instance)
```

### Special Methods (Dunder Methods)
```python
class Book:
    def __init__(self, title, pages):
        self.title = title
        self.pages = pages

    def __str__(self):
        """Human-readable string representation"""
        return f"'{self.title}'"

    def __repr__(self):
        """Developer string representation"""
        return f"Book(title='{self.title}', pages={self.pages})"

    def __len__(self):
        """Allow len() to work on Book objects"""
        return self.pages

book = Book("Python Guide", 350)
print(book)          # 'Python Guide'
print(repr(book))    # Book(title='Python Guide', pages=350)
print(len(book))     # 350
```

---

## 3. Inheritance

### Basic Inheritance
```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "Some sound"

class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"

class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow!"

dog = Dog("Buddy")
cat = Cat("Whiskers")

print(dog.speak())  # Buddy says Woof!
print(cat.speak())  # Whiskers says Meow!
```

### Using super()
```python
class Animal:
    def __init__(self, name, age):
        self.name = name
        self.age = age

class Dog(Animal):
    def __init__(self, name, age, breed):
        super().__init__(name, age)  # Call parent's __init__
        self.breed = breed

dog = Dog("Buddy", 3, "Labrador")
print(f"{dog.name} is a {dog.breed}")
```

### Multiple Inheritance
```python
class Flyable:
    def fly(self):
        return "Flying high!"

class Swimmable:
    def swim(self):
        return "Swimming fast!"

class Duck(Flyable, Swimmable):
    def quack(self):
        return "Quack!"

duck = Duck()
print(duck.fly())   # Flying high!
print(duck.swim())  # Swimming fast!
print(duck.quack()) # Quack!
```

### Method Resolution Order (MRO)
```python
# Check the order Python searches for methods
print(Duck.__mro__)
# (<class 'Duck'>, <class 'Flyable'>, <class 'Swimmable'>, <class 'object'>)
```

---

## 4. Polymorphism

### Duck Typing
"If it walks like a duck and quacks like a duck, it's a duck."

```python
class Dog:
    def speak(self):
        return "Woof!"

class Cat:
    def speak(self):
        return "Meow!"

class Robot:
    def speak(self):
        return "Beep boop!"

# Same function works with any object that has speak()
def make_speak(creature):
    print(creature.speak())

make_speak(Dog())    # Woof!
make_speak(Cat())    # Meow!
make_speak(Robot())  # Beep boop!
```

### Polymorphism with Inheritance
```python
class Shape:
    def area(self):
        raise NotImplementedError("Subclasses must implement area()")

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14159 * self.radius ** 2

# Works with any Shape
shapes = [Rectangle(4, 5), Circle(3)]
for shape in shapes:
    print(f"Area: {shape.area()}")
```

---

## 5. Encapsulation

### Access Modifiers (Convention)
```python
class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner          # Public
        self._balance = balance     # Protected (convention)
        self.__pin = "1234"         # Private (name mangling)

    def get_balance(self):
        return self._balance

    def deposit(self, amount):
        if amount > 0:
            self._balance += amount

    def withdraw(self, amount):
        if 0 < amount <= self._balance:
            self._balance -= amount
            return amount
        return 0

account = BankAccount("Alice", 1000)
print(account.owner)           # Alice (public - OK)
print(account._balance)        # 1000 (protected - works but not recommended)
# print(account.__pin)         # Error! (private)
print(account._BankAccount__pin)  # 1234 (name mangling - avoid this)
```

### Properties (Getters/Setters)
```python
class Temperature:
    def __init__(self, celsius=0):
        self._celsius = celsius

    @property
    def celsius(self):
        """Getter for celsius"""
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        """Setter for celsius with validation"""
        if value < -273.15:
            raise ValueError("Temperature below absolute zero!")
        self._celsius = value

    @property
    def fahrenheit(self):
        """Computed property"""
        return self._celsius * 9/5 + 32

temp = Temperature(25)
print(temp.celsius)     # 25
print(temp.fahrenheit)  # 77.0
temp.celsius = 30       # Uses setter
# temp.celsius = -300   # Raises ValueError
```

---

## 6. ABC, Protocol, and Mixins

### Abstract Base Classes (ABC)
Formal interfaces with runtime enforcement.

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    """Abstract base class - cannot be instantiated directly"""

    @abstractmethod
    def area(self) -> float:
        """Must be implemented by subclasses"""
        pass

    @abstractmethod
    def perimeter(self) -> float:
        pass

    def describe(self) -> str:
        """Concrete method - shared implementation"""
        return f"{self.__class__.__name__}: area={self.area():.2f}"

class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return 3.14159 * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * 3.14159 * self.radius

# shape = Shape()  # TypeError: Can't instantiate abstract class
circle = Circle(5)
print(circle.describe())  # Circle: area=78.54
```

### Protocol Classes (Structural Subtyping)
Duck typing with type checker support - no inheritance required!

```python
from typing import Protocol

class Drawable(Protocol):
    """Any class with draw() and get_color() is Drawable"""

    def draw(self) -> str:
        ...

    def get_color(self) -> str:
        ...

class Button:
    """Implements Drawable - no inheritance needed!"""
    def draw(self) -> str:
        return f"Drawing {self.get_color()} button"

    def get_color(self) -> str:
        return "blue"

def render(item: Drawable) -> None:
    """Works with ANY object that has the right methods"""
    print(item.draw())

button = Button()
render(button)  # Works! Button matches the Protocol structure
```

### ABC vs Protocol

| Aspect | ABC | Protocol |
|--------|-----|----------|
| Subtyping | Nominal (explicit inheritance) | Structural (duck typing) |
| Enforcement | Runtime error on instantiation | Type checker only |
| Shared Code | Can have concrete methods | Signatures only |
| Best For | Internal APIs, frameworks | External code, flexibility |

### Mixins
Small, focused classes for composable functionality.

```python
class TimestampMixin:
    """Adds timestamp tracking to any class"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from datetime import datetime
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def touch(self):
        from datetime import datetime
        self.updated_at = datetime.now()

class SerializableMixin:
    """Adds JSON serialization to any class"""
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()
                if not k.startswith('_')}

    def to_json(self):
        import json
        return json.dumps(self.to_dict(), default=str)

class User(TimestampMixin, SerializableMixin):
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
        super().__init__()

user = User("Alice", "alice@example.com")
print(user.to_json())
# {"name": "Alice", "email": "alice@example.com", "created_at": "..."}
```

> **Convention**: Name mixins with `Mixin` suffix and keep them focused and small.

---

## 7. Operator Overloading

### Arithmetic Operators
```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        """v1 + v2"""
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """v1 - v2"""
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        """v * 3"""
        return Vector(self.x * scalar, self.y * scalar)

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

v1 = Vector(2, 3)
v2 = Vector(1, 4)
print(v1 + v2)  # Vector(3, 7)
print(v1 * 3)   # Vector(6, 9)
```

### Comparison Operators
```python
from functools import total_ordering

@total_ordering  # Generates other comparisons from __eq__ and __lt__
class Student:
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade

    def __eq__(self, other):
        return self.grade == other.grade

    def __lt__(self, other):
        return self.grade < other.grade

    def __repr__(self):
        return f"{self.name}: {self.grade}"

students = [Student("Alice", 85), Student("Bob", 92), Student("Charlie", 78)]
print(sorted(students))  # [Charlie: 78, Alice: 85, Bob: 92]
```

### Container Operations
```python
class Inventory:
    def __init__(self):
        self._items = {}

    def __getitem__(self, key):
        """inventory["sword"]"""
        return self._items[key]

    def __setitem__(self, key, value):
        """inventory["sword"] = 5"""
        self._items[key] = value

    def __contains__(self, key):
        """'sword' in inventory"""
        return key in self._items

    def __len__(self):
        """len(inventory)"""
        return len(self._items)

inv = Inventory()
inv["sword"] = 3
print("sword" in inv)  # True
print(len(inv))        # 1
```

### Callable Objects
```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor

    def __call__(self, value):
        """Make instance callable like a function"""
        return value * self.factor

double = Multiplier(2)
triple = Multiplier(3)

print(double(5))  # 10
print(triple(5))  # 15

# Use with map
prices = [10, 20, 30]
print(list(map(double, prices)))  # [20, 40, 60]
```

### Common Magic Methods

| Method | Operator/Usage |
|--------|----------------|
| `__add__` | `+` |
| `__sub__` | `-` |
| `__mul__` | `*` |
| `__truediv__` | `/` |
| `__floordiv__` | `//` |
| `__mod__` | `%` |
| `__pow__` | `**` |
| `__eq__` | `==` |
| `__lt__` | `<` |
| `__le__` | `<=` |
| `__gt__` | `>` |
| `__ge__` | `>=` |
| `__len__` | `len()` |
| `__getitem__` | `obj[key]` |
| `__setitem__` | `obj[key] = value` |
| `__contains__` | `in` |
| `__call__` | `obj()` |

---

## 8. Functional Programming

### Key Concepts
- **Pure Functions**: Same input → Same output, no side effects
- **Immutability**: Data doesn't change after creation
- **First-class Functions**: Functions as values (assign, pass, return)
- **Higher-order Functions**: Functions that take/return functions

### Lambda Functions
```python
# Anonymous single-expression functions
square = lambda x: x ** 2
add = lambda x, y: x + y

print(square(5))    # 25
print(add(3, 4))    # 7

# Often used with map/filter
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))
```

### map() - Transform Each Element
```python
numbers = [1, 2, 3, 4, 5]

# Apply function to each element
squared = list(map(lambda x: x**2, numbers))
# [1, 4, 9, 16, 25]

# Multiple iterables
a = [1, 2, 3]
b = [10, 20, 30]
sums = list(map(lambda x, y: x + y, a, b))
# [11, 22, 33]
```

### filter() - Select Elements
```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Keep only elements where function returns True
evens = list(filter(lambda x: x % 2 == 0, numbers))
# [2, 4, 6, 8, 10]

# Filter with None keeps truthy values
mixed = [0, 1, "", "hello", None, [], [1, 2]]
truthy = list(filter(None, mixed))
# [1, "hello", [1, 2]]
```

### reduce() - Aggregate to Single Value
```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]

# Reduce to single value
total = reduce(lambda acc, x: acc + x, numbers)  # 15
product = reduce(lambda acc, x: acc * x, numbers)  # 120

# With initial value
total = reduce(lambda acc, x: acc + x, numbers, 100)  # 115
```

### Combining map, filter, reduce
```python
from functools import reduce

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Sum of squares of even numbers
result = reduce(
    lambda acc, x: acc + x,  # Sum
    map(
        lambda x: x ** 2,     # Square
        filter(
            lambda x: x % 2 == 0,  # Even only
            numbers
        )
    )
)
print(result)  # 220 (4 + 16 + 36 + 64 + 100)
```

---

## 9. Decorators

### What are Decorators?
Functions that modify the behavior of other functions.

```python
def uppercase_decorator(func):
    def wrapper():
        result = func()
        return result.upper()
    return wrapper

@uppercase_decorator
def greet():
    return "hello world"

print(greet())  # "HELLO WORLD"

# @ syntax is equivalent to:
# greet = uppercase_decorator(greet)
```

### Decorator with Arguments
```python
from functools import wraps

def timer(func):
    @wraps(func)  # Preserves function metadata
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@timer
def slow_function(n):
    import time
    time.sleep(n)
    return "Done!"

slow_function(1)  # slow_function took 1.0012 seconds
```

### Decorator with Parameters
```python
def repeat(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def say_hello(name):
    print(f"Hello, {name}!")

say_hello("Alice")
# Hello, Alice!
# Hello, Alice!
# Hello, Alice!
```

### Common Built-in Decorators
```python
class MyClass:
    @staticmethod
    def static_method():
        """No self parameter - doesn't access instance"""
        return "I'm static!"

    @classmethod
    def class_method(cls):
        """First param is class, not instance"""
        return f"I'm a method of {cls.__name__}"

    @property
    def computed_value(self):
        """Access like attribute, not method"""
        return 42

# functools decorators
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

fibonacci(100)  # Instant with caching!
```

---

## 10. Generators

### What are Generators?
Functions that yield values one at a time, maintaining state between calls.

```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

# Generator object (doesn't execute yet)
gen = countdown(5)

# Iterate to get values
for num in gen:
    print(num)  # 5, 4, 3, 2, 1

# Or use next()
gen = countdown(3)
print(next(gen))  # 3
print(next(gen))  # 2
print(next(gen))  # 1
# print(next(gen))  # StopIteration!
```

### Generator Expressions
```python
# List comprehension - creates entire list in memory
squares = [x**2 for x in range(1000000)]  # ~8MB

# Generator expression - lazy evaluation
squares_gen = (x**2 for x in range(1000000))  # ~200 bytes!

import sys
print(sys.getsizeof([x**2 for x in range(1000)]))   # 8856 bytes
print(sys.getsizeof((x**2 for x in range(1000))))   # 200 bytes
```

### When to Use Generators
- **Large/infinite sequences**: Don't fit in memory
- **Single iteration**: Only need to process once
- **Lazy evaluation**: Compute values only when needed
- **Chaining operations**: Pipeline processing

### Practical Example
```python
def read_large_file(file_path):
    """Memory-efficient file reading"""
    with open(file_path) as f:
        for line in f:
            yield line.strip()

def grep(pattern, lines):
    """Filter lines containing pattern"""
    for line in lines:
        if pattern in line:
            yield line

# Process huge file with constant memory
log_lines = read_large_file("huge.log")
errors = grep("ERROR", log_lines)

for error in errors:
    print(error)
```

---

## 11. Generator Pipelines and Coroutines

### Generator Pipelines
Chain generators for efficient data processing.

```python
def read_lines(filename):
    """Stage 1: Read lines from file"""
    with open(filename) as f:
        for line in f:
            yield line.strip()

def filter_comments(lines):
    """Stage 2: Remove comment lines"""
    for line in lines:
        if not line.startswith('#'):
            yield line

def parse_csv(lines):
    """Stage 3: Parse CSV fields"""
    for line in lines:
        yield line.split(',')

def extract_field(records, index):
    """Stage 4: Extract specific field"""
    for record in records:
        if len(record) > index:
            yield record[index]

# Build the pipeline - no data processed yet!
pipeline = extract_field(
    parse_csv(
        filter_comments(
            read_lines('data.csv')
        )
    ),
    index=2
)

# Process lazily - one line at a time
for value in pipeline:
    print(value)
```

### Why Generator Pipelines?
- **Memory efficient**: Only one item in memory at a time
- **Composable**: Mix and match pipeline stages
- **Reusable**: Same stages work with different data

### Coroutines with send()
Push-based data flow: send values INTO generators.

```python
def averager():
    """Coroutine that computes running average"""
    total = 0.0
    count = 0
    average = None
    while True:
        value = yield average  # Receive value, send back average
        total += value
        count += 1
        average = total / count

# Create and prime the coroutine
avg = averager()
next(avg)  # Prime: advance to first yield

# Send values in and get running average back
print(avg.send(10))  # 10.0
print(avg.send(20))  # 15.0
print(avg.send(30))  # 20.0
```

### Priming Decorator
```python
def coroutine(func):
    """Auto-prime coroutines"""
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)  # Prime it
        return gen
    return wrapper

@coroutine
def grep(pattern):
    """Filter lines by pattern"""
    while True:
        line = yield
        if pattern in line:
            print(f"Found: {line}")

searcher = grep("ERROR")
searcher.send("INFO: All good")
searcher.send("ERROR: Disk full")  # Found: ERROR: Disk full
```

---

## 12. itertools Module

### Python's Stream Processing (Java Streams Equivalent)

| Java Stream | Python itertools | Description |
|-------------|------------------|-------------|
| `.filter()` | `filter()`, `filterfalse()` | Select elements |
| `.map()` | `map()`, `starmap()` | Transform elements |
| `.flatMap()` | `chain.from_iterable()` | Flatten nested |
| `.limit()` | `islice()` | Take first N |
| `.skip()` | `islice(iter, n, None)` | Skip first N |
| `.sorted()` | `sorted()` | Sort elements |
| `.reduce()` | `functools.reduce()` | Aggregate |
| `.collect()` | `list()`, `set()`, `dict()` | Terminal operation |
| `.groupingBy()` | `groupby()` | Group by key |

### Infinite Iterators
```python
from itertools import count, cycle, repeat

# count - infinite counter
for i in count(10, 2):
    if i > 20:
        break
    print(i)  # 10, 12, 14, 16, 18, 20

# cycle - repeat sequence forever
counter = 0
for item in cycle(['A', 'B', 'C']):
    print(item)
    counter += 1
    if counter >= 7:
        break
# A, B, C, A, B, C, A

# repeat - repeat value
list(repeat(5, 3))  # [5, 5, 5]
```

### Combining Iterables
```python
from itertools import chain, zip_longest

# chain - combine iterables
combined = list(chain([1, 2, 3], [4, 5, 6]))
# [1, 2, 3, 4, 5, 6]

# zip_longest - zip with fill value
a = [1, 2, 3]
b = ['a', 'b']
result = list(zip_longest(a, b, fillvalue='-'))
# [(1, 'a'), (2, 'b'), (3, '-')]
```

### Filtering and Slicing
```python
from itertools import islice, takewhile, dropwhile, filterfalse

# islice - slice an iterator
from itertools import count
first_5 = list(islice(count(), 5))  # [0, 1, 2, 3, 4]

# takewhile - take while condition is True
data = [1, 3, 5, 2, 4, 6]
list(takewhile(lambda x: x < 4, data))  # [1, 3]

# dropwhile - skip while condition is True
list(dropwhile(lambda x: x < 4, data))  # [5, 2, 4, 6]

# filterfalse - opposite of filter
list(filterfalse(lambda x: x % 2, range(10)))  # [0, 2, 4, 6, 8]
```

### Combinatorics
```python
from itertools import combinations, permutations, product

items = ['A', 'B', 'C']

# combinations - order doesn't matter
list(combinations(items, 2))
# [('A', 'B'), ('A', 'C'), ('B', 'C')]

# permutations - order matters
list(permutations(items, 2))
# [('A', 'B'), ('A', 'C'), ('B', 'A'), ('B', 'C'), ('C', 'A'), ('C', 'B')]

# product - Cartesian product
colors = ['red', 'blue']
sizes = ['S', 'M', 'L']
list(product(colors, sizes))
# [('red', 'S'), ('red', 'M'), ('red', 'L'),
#  ('blue', 'S'), ('blue', 'M'), ('blue', 'L')]
```

### Grouping and Accumulating
```python
from itertools import groupby, accumulate

# groupby - group consecutive elements (must be sorted!)
data = [('fruit', 'apple'), ('fruit', 'banana'),
        ('veg', 'carrot'), ('veg', 'lettuce')]

for key, group in groupby(data, key=lambda x: x[0]):
    print(f"{key}: {list(group)}")
# fruit: [('fruit', 'apple'), ('fruit', 'banana')]
# veg: [('veg', 'carrot'), ('veg', 'lettuce')]

# accumulate - running totals
numbers = [1, 2, 3, 4, 5]
list(accumulate(numbers))  # [1, 3, 6, 10, 15]

# With custom function
from operator import mul
list(accumulate(numbers, mul))  # [1, 2, 6, 24, 120]
```

---

## 13. Collections Module

### Counter - Count Hashable Objects
```python
from collections import Counter

# Count elements
colors = ['red', 'blue', 'red', 'green', 'blue', 'blue']
color_count = Counter(colors)
print(color_count)  # Counter({'blue': 3, 'red': 2, 'green': 1})

# Most common
print(color_count.most_common(2))  # [('blue', 3), ('red', 2)]

# Arithmetic
c1 = Counter(apples=5, oranges=3)
c2 = Counter(apples=2, bananas=4)
print(c1 + c2)  # Counter({'apples': 7, 'bananas': 4, 'oranges': 3})
```

### defaultdict - Dict with Default Values
```python
from collections import defaultdict

# No more KeyError!
dd = defaultdict(list)
dd['colors'].append('red')
dd['colors'].append('blue')
print(dd)  # defaultdict(<class 'list'>, {'colors': ['red', 'blue']})

# Group items
products = [('fruit', 'apple'), ('veg', 'carrot'), ('fruit', 'banana')]
grouped = defaultdict(list)
for category, item in products:
    grouped[category].append(item)
# {'fruit': ['apple', 'banana'], 'veg': ['carrot']}

# Count with int
word_count = defaultdict(int)
for word in "the quick brown fox".split():
    word_count[word] += 1
```

### deque - Double-Ended Queue
```python
from collections import deque

d = deque(['a', 'b', 'c'])

# O(1) operations on both ends
d.append('d')       # Right: ['a', 'b', 'c', 'd']
d.appendleft('z')   # Left: ['z', 'a', 'b', 'c', 'd']
d.pop()             # Remove right
d.popleft()         # Remove left

# Rotate
d = deque([1, 2, 3, 4, 5])
d.rotate(2)   # [4, 5, 1, 2, 3]
d.rotate(-2)  # [1, 2, 3, 4, 5]

# Fixed-size buffer (drops oldest)
buffer = deque(maxlen=3)
buffer.append(1)  # [1]
buffer.append(2)  # [1, 2]
buffer.append(3)  # [1, 2, 3]
buffer.append(4)  # [2, 3, 4] - 1 removed!
```

### namedtuple - Tuple with Named Fields
```python
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
p = Point(3, 4)

print(p.x, p.y)   # 3 4
print(p[0])       # 3
print(p._asdict())  # {'x': 3, 'y': 4}

# Modern alternative: dataclasses
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
```

### ChainMap - Combine Multiple Dicts
```python
from collections import ChainMap

defaults = {'color': 'red', 'size': 'medium'}
user_prefs = {'color': 'blue'}

config = ChainMap(user_prefs, defaults)
print(config['color'])  # 'blue' (from user_prefs)
print(config['size'])   # 'medium' (from defaults)
```

---

## 14. Data Handling

### Working with JSON
```python
import json

data = {"name": "Alice", "age": 30, "skills": ["Python", "SQL"]}

# Serialize (Python → JSON)
json_str = json.dumps(data, indent=4)

# Deserialize (JSON → Python)
data = json.loads(json_str)

# File operations
with open("data.json", "w") as f:
    json.dump(data, f, indent=4)

with open("data.json", "r") as f:
    data = json.load(f)
```

### Working with CSV
```python
import csv

# Reading
with open('data.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # Skip header
    for row in reader:
        print(row)

# Reading as dictionaries
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row['name'], row['age'])

# Writing
with open('output.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['name', 'age'])
    writer.writerow(['Alice', 30])
```

### Working with Datetime
```python
from datetime import datetime, date, timedelta

# Current date/time
now = datetime.now()
today = date.today()

# Create specific date
birthday = datetime(1990, 5, 15, 10, 30)

# Formatting
print(now.strftime("%Y-%m-%d %H:%M"))  # 2024-01-15 14:30

# Parsing
dt = datetime.strptime("2024-01-15", "%Y-%m-%d")

# Arithmetic
tomorrow = today + timedelta(days=1)
next_week = today + timedelta(weeks=1)
```

---

## 15. Regular Expressions

### Basic Patterns
```python
import re

text = "Email: alice@example.com, bob@test.org"

# Find all emails
emails = re.findall(r'\b[\w.-]+@[\w.-]+\.\w+\b', text)
# ['alice@example.com', 'bob@test.org']

# Search (first match)
match = re.search(r'\d+', "Order 12345")
if match:
    print(match.group())  # 12345

# Match (from start)
if re.match(r'Hello', "Hello World"):
    print("Starts with Hello")

# Replace
result = re.sub(r'\d+', 'X', "Call 555-1234")
# "Call X-X"
```

### Common Patterns

| Pattern | Matches |
|---------|---------|
| `\d` | Digit [0-9] |
| `\w` | Word char [a-zA-Z0-9_] |
| `\s` | Whitespace |
| `.` | Any char (except newline) |
| `^` | Start of string |
| `$` | End of string |
| `*` | 0 or more |
| `+` | 1 or more |
| `?` | 0 or 1 |
| `{n}` | Exactly n |
| `{n,m}` | Between n and m |
| `[abc]` | Character class |
| `(...)` | Capture group |

---

## 16. The os and sys Modules

### os - File System Operations
```python
import os

# Current working directory
print(os.getcwd())
os.chdir('/tmp')

# List directory
files = os.listdir('.')

# Create/remove directories
os.mkdir('new_folder')
os.makedirs('a/b/c')  # Nested
os.rmdir('new_folder')

# File operations
os.rename('old.txt', 'new.txt')
os.remove('file.txt')

# Check paths
os.path.exists('/tmp')
os.path.isfile('file.txt')
os.path.isdir('/tmp')
```

### os.path - Path Manipulation
```python
import os
from pathlib import Path  # Modern alternative

path = '/home/user/documents/report.pdf'

os.path.basename(path)   # 'report.pdf'
os.path.dirname(path)    # '/home/user/documents'
os.path.splitext(path)   # ('/home/.../report', '.pdf')
os.path.join('home', 'user', 'file.txt')  # 'home/user/file.txt'

# Modern pathlib
path = Path('/home/user/documents/report.pdf')
print(path.name)    # 'report.pdf'
print(path.stem)    # 'report'
print(path.suffix)  # '.pdf'
print(path.parent)  # Path('/home/user/documents')

# Glob patterns
for f in Path('.').glob('*.py'):
    print(f)
```

### Environment Variables
```python
import os

# Get environment variable
home = os.environ.get('HOME')
api_key = os.environ.get('API_KEY', 'default')

# Set environment variable
os.environ['MY_VAR'] = 'my_value'

# Walk directory tree
for root, dirs, files in os.walk('/project'):
    for file in files:
        if file.endswith('.py'):
            print(os.path.join(root, file))
```

### sys - Python Runtime
```python
import sys

# Command line arguments
print(sys.argv)       # ['script.py', 'arg1', 'arg2']
print(sys.argv[1:])   # Arguments only

# Python version
print(sys.version)
print(sys.version_info.major)  # 3

# Module search path
print(sys.path)
sys.path.append('/my/modules')

# Platform
print(sys.platform)  # 'linux', 'darwin', 'win32'

# Exit program
sys.exit(0)  # Success
sys.exit(1)  # Error

# Memory info
print(sys.getsizeof([1, 2, 3]))
```

---

## 17. Testing with unittest and pytest

### unittest
```python
import unittest

def add(a, b):
    return a + b

class TestMath(unittest.TestCase):
    def test_add_positive(self):
        self.assertEqual(add(2, 3), 5)

    def test_add_negative(self):
        self.assertEqual(add(-1, -1), -2)

    def test_add_zero(self):
        self.assertEqual(add(0, 0), 0)

if __name__ == '__main__':
    unittest.main()
```

### pytest (Recommended)
```python
# test_math.py
def add(a, b):
    return a + b

def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, -1) == -2

def test_add_zero():
    assert add(0, 0) == 0

# Run with: pytest test_math.py -v
```

### pytest Fixtures
```python
import pytest

@pytest.fixture
def sample_data():
    return [1, 2, 3, 4, 5]

def test_sum(sample_data):
    assert sum(sample_data) == 15

def test_length(sample_data):
    assert len(sample_data) == 5
```

### Parametrized Tests
```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input, expected):
    assert input ** 2 == expected
```

---

## 18. Python Packaging

### Virtual Environments
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install packages
pip install requests pandas

# Save dependencies
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt

# Deactivate
deactivate
```

### Project Structure
```
myproject/
├── myproject/           # Package directory
│   ├── __init__.py      # Makes it a package
│   ├── main.py          # Main module
│   └── utils.py         # Utility functions
├── tests/               # Test directory
│   ├── __init__.py
│   └── test_main.py
├── venv/                # Virtual environment
├── .gitignore
├── requirements.txt     # Dependencies
├── pyproject.toml       # Package metadata
└── README.md
```

### pyproject.toml
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "myproject"
version = "0.1.0"
description = "My awesome project"
authors = [{name = "Your Name", email = "you@example.com"}]
dependencies = [
    "requests>=2.28.0",
    "pandas>=1.5.0",
]

[project.optional-dependencies]
dev = ["pytest", "black", "mypy"]
```

---

## Quick Reference

### Common Design Patterns

**Singleton**
```python
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**Factory**
```python
class AnimalFactory:
    @staticmethod
    def create(animal_type):
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()
```

**Observer**
```python
class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def notify(self, message):
        for observer in self._observers:
            observer.update(message)
```

### Type Hints
```python
from typing import List, Dict, Optional, Union, Callable

def greet(name: str) -> str:
    return f"Hello, {name}"

def process(items: List[int]) -> Dict[str, int]:
    return {"sum": sum(items), "count": len(items)}

def find_user(id: int) -> Optional[str]:
    # Returns str or None
    pass

def handler(callback: Callable[[int], str]) -> None:
    pass
```

---

*Keep practicing and building projects! The best way to learn is by doing.*
