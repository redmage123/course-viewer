"""
Flask backend for Course Material Viewer
Multi-tenant course platform with Jupyter notebook integration
"""
from flask import Flask, send_from_directory, jsonify, request, session, redirect, url_for, send_file
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import json
import shutil
import zipfile
import io
from datetime import datetime, timedelta
from functools import wraps
import secrets
from dotenv import load_dotenv
from kernel_manager import kernel_pool

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

app = Flask(__name__, static_folder='static')
app.secret_key = secrets.token_hex(32)
CORS(app, supports_credentials=True)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATERIALS_DIR = os.path.dirname(BASE_DIR)
DATABASE = os.path.join(BASE_DIR, 'course_viewer.db')
WORKSPACES_DIR = os.path.join(BASE_DIR, 'workspaces')

# Ensure directories exist
os.makedirs(WORKSPACES_DIR, exist_ok=True)

# ============================================================================
# Sandbox Security Utilities
# ============================================================================

class SandboxError(Exception):
    """Raised when a sandbox violation is detected"""
    pass

def sanitize_path_component(component):
    """
    Sanitize a single path component to prevent directory traversal.
    Removes any dangerous characters and path separators.
    """
    if not component:
        raise SandboxError("Empty path component")

    # Remove any path separators
    component = component.replace('/', '').replace('\\', '')

    # Remove null bytes
    component = component.replace('\x00', '')

    # Reject path traversal attempts
    if component in ('.', '..'):
        raise SandboxError(f"Invalid path component: {component}")

    # Only allow alphanumeric, dash, underscore, and dot
    import re
    if not re.match(r'^[\w\-\.]+$', component):
        raise SandboxError(f"Invalid characters in path component: {component}")

    return component

def get_safe_user_workspace(user_id):
    """
    Get a user's workspace directory with strict validation.
    Creates the workspace if it doesn't exist.
    Returns the absolute, resolved path.
    """
    if not isinstance(user_id, int) or user_id <= 0:
        raise SandboxError(f"Invalid user_id: {user_id}")

    # Create workspace path using only the numeric user_id
    workspace = os.path.join(WORKSPACES_DIR, str(user_id))

    # Resolve to absolute path
    workspace = os.path.realpath(workspace)

    # Verify it's under WORKSPACES_DIR
    workspaces_real = os.path.realpath(WORKSPACES_DIR)
    if not workspace.startswith(workspaces_real + os.sep):
        raise SandboxError("Workspace path escape detected")

    # Create if doesn't exist
    os.makedirs(workspace, exist_ok=True)

    return workspace

def get_safe_path_in_workspace(workspace, relative_path):
    """
    Safely resolve a relative path within a workspace.
    Prevents directory traversal and symlink attacks.
    Returns the absolute, resolved path.
    """
    if not relative_path:
        raise SandboxError("Empty relative path")

    # Normalize the path (handles .. and .)
    normalized = os.path.normpath(relative_path)

    # Reject absolute paths
    if os.path.isabs(normalized):
        raise SandboxError("Absolute paths not allowed")

    # Reject paths that try to escape
    if normalized.startswith('..'):
        raise SandboxError("Path traversal detected")

    # Join with workspace
    full_path = os.path.join(workspace, normalized)

    # Resolve to real path (follows symlinks)
    real_path = os.path.realpath(full_path)

    # Verify the resolved path is still within workspace
    workspace_real = os.path.realpath(workspace)
    if not real_path.startswith(workspace_real + os.sep) and real_path != workspace_real:
        raise SandboxError(f"Path escape detected: {relative_path}")

    return real_path

def get_safe_path_in_materials(relative_path):
    """
    Safely resolve a relative path within the materials directory.
    Prevents directory traversal and symlink attacks.
    Returns the absolute, resolved path.
    """
    if not relative_path:
        raise SandboxError("Empty relative path")

    # Normalize the path
    normalized = os.path.normpath(relative_path)

    # Reject absolute paths
    if os.path.isabs(normalized):
        raise SandboxError("Absolute paths not allowed")

    # Reject paths that try to escape
    if normalized.startswith('..'):
        raise SandboxError("Path traversal detected")

    # Join with materials dir
    full_path = os.path.join(MATERIALS_DIR, normalized)

    # Resolve to real path
    real_path = os.path.realpath(full_path)

    # Verify the resolved path is still within materials
    materials_real = os.path.realpath(MATERIALS_DIR)
    if not real_path.startswith(materials_real + os.sep) and real_path != materials_real:
        raise SandboxError(f"Path escape detected: {relative_path}")

    return real_path

def validate_lab_id(lab_id):
    """
    Validate a lab ID to ensure it's safe.
    Lab IDs should only contain alphanumeric characters, dashes, and underscores.
    """
    if not lab_id:
        raise SandboxError("Empty lab_id")

    import re
    if not re.match(r'^[\w\-]+$', lab_id):
        raise SandboxError(f"Invalid lab_id format: {lab_id}")

    if len(lab_id) > 100:
        raise SandboxError("Lab ID too long")

    return lab_id

def safe_copy_file(src, dst, max_size_mb=50):
    """
    Safely copy a file with size limits.
    Prevents copying excessively large files.
    """
    # Check source exists and is a regular file
    if not os.path.isfile(src):
        raise SandboxError(f"Source is not a file: {src}")

    # Check file size
    file_size = os.path.getsize(src)
    max_size = max_size_mb * 1024 * 1024
    if file_size > max_size:
        raise SandboxError(f"File too large: {file_size} bytes (max {max_size} bytes)")

    # Ensure destination directory exists
    dst_dir = os.path.dirname(dst)
    if dst_dir:
        os.makedirs(dst_dir, exist_ok=True)

    # Copy the file
    shutil.copy2(src, dst)

# ============================================================================
# Database Setup
# ============================================================================

def get_db():
    """Get database connection"""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Initialize the database"""
    db = get_db()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id TEXT NOT NULL,
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            progress JSON DEFAULT '{}',
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, course_id)
        );

        CREATE TABLE IF NOT EXISTS lab_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lab_id TEXT NOT NULL,
            notebook_path TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS lab_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lab_id TEXT NOT NULL,
            cell_index INTEGER,
            output TEXT,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS poll_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            poll_id TEXT NOT NULL,
            technical_level TEXT,
            use_cases TEXT,
            ai_tools_used TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Migration: Add use_cases column if it doesn't exist
    try:
        db.execute('SELECT use_cases FROM poll_responses LIMIT 1')
    except:
        db.execute('ALTER TABLE poll_responses ADD COLUMN use_cases TEXT')

    # Create default admin user if not exists
    existing = db.execute('SELECT id FROM users WHERE username = ?', ('bbrelin',)).fetchone()
    if not existing:
        db.execute(
            'INSERT INTO users (username, email, password_hash, full_name, role) VALUES (?, ?, ?, ?, ?)',
            ('bbrelin', 'bbrelin@ai-elevate.ai', generate_password_hash('f00bar123!'), 'Braun Brelin', 'instructor')
        )

    db.commit()
    db.close()

# Initialize database on startup
init_db()

# ============================================================================
# Authentication Decorators
# ============================================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def instructor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        if session.get('role') not in ['instructor', 'admin']:
            return jsonify({'error': 'Instructor access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# Course Configuration
# ============================================================================

# Course categories for organized navigation
COURSE_CATEGORIES = {
    "python": {
        "id": "python",
        "name": "Python Programming",
        "icon": "🐍",
        "description": "Learn Python from basics to advanced concepts",
        "order": 1
    },
    "ai-technical": {
        "id": "ai-technical",
        "name": "AI/ML Technical",
        "icon": "🧠",
        "description": "Deep-dive technical AI and machine learning courses",
        "order": 2
    },
    "ai-business": {
        "id": "ai-business",
        "name": "AI for Business",
        "icon": "💼",
        "description": "AI strategy, adoption, and applications for business professionals",
        "order": 3
    },
    "azure": {
        "id": "azure",
        "name": "Azure Certifications",
        "icon": "☁️",
        "description": "Microsoft Azure certification preparation courses",
        "order": 4
    },
    "itag-skillnet": {
        "id": "itag-skillnet",
        "name": "ITAG Skillnet AI Advantage",
        "icon": "🎯",
        "description": "AI awareness and prompting seminars for ITAG Skillnet",
        "order": 5
    }
}

COURSES = {
    "ai-plain-english": {
        "id": "ai-plain-english",
        "name": "AI in Plain English",
        "description": "Demystify AI and make informed decisions for your business",
        "icon": "💡",
        "duration": "90 minutes",
        "category": "itag-skillnet",
        "syllabus": ["What AI Actually Is", "Machine Learning vs Deep Learning", "How ChatGPT & LLMs Work", "AI Use Cases for Business", "Risks & Limitations", "Getting Started with AI Tools"],
        "goals": ["Understand core AI concepts without technical jargon", "Identify practical AI applications for your role", "Evaluate AI tools and vendors with confidence", "Recognise common AI myths and misconceptions"],
        "audience": "Business professionals and decision-makers with no technical background",
        "prerequisites": None,
        "topic_descriptions": {
            "What AI Actually Is": "Demystifies artificial intelligence by cutting through the hype and explaining what AI systems actually do under the hood. Covers the difference between narrow AI and general AI, how modern AI is essentially sophisticated pattern recognition, and why understanding these fundamentals matters for every professional.",
            "Machine Learning vs Deep Learning": "Breaks down the relationship between AI, machine learning, and deep learning in plain terms. Explains how machines learn from data through examples and feedback, and when deep learning's neural network approach offers advantages over traditional machine learning techniques.",
            "How ChatGPT & LLMs Work": "Explains the technology behind large language models like ChatGPT, including how they are trained on text data and generate responses. Covers key concepts like tokens, context windows, and probabilistic text generation without requiring any technical background.",
            "AI Use Cases for Business": "Surveys the most impactful ways businesses are applying AI today, from customer service automation to data-driven decision making. Provides concrete examples across industries so participants can identify opportunities relevant to their own organizations.",
            "Risks & Limitations": "Addresses the real limitations of current AI systems, including hallucinations, bias, data privacy concerns, and overreliance on AI outputs. Equips participants with a practical understanding of what AI cannot do and how to mitigate common risks when adopting AI tools.",
            "Getting Started with AI Tools": "Provides a practical roadmap for beginning to use AI tools effectively in day-to-day work. Covers popular AI assistants and platforms, best practices for prompting and interaction, and how to evaluate which tools are appropriate for specific tasks.",
        },
        "sections": {
            "workshop": {
                "title": "Workshop Materials",
                "items": [
                    {"id": "aipe-slides", "name": "Presentation Slides", "file": "ai-plain-english/ai-plain-english-slides.html", "type": "slides"},
                    {"id": "aipe-demo", "name": "Interactive AI Demo", "file": "ai-plain-english/demo/index.html", "type": "demo", "external": True},
                    {"id": "aipe-lab", "name": "Take-Home Lab (PDF)", "file": "ai-plain-english/lab/ai-plain-english-lab.html", "type": "lab", "printable": True},
                ]
            }
        }
    },
    "mastering-ai": {
        "id": "mastering-ai",
        "name": "Mastering AI",
        "description": "Complete course on AI and Large Language Models from fundamentals to advanced topics",
        "icon": "🤖",
        "category": "ai-technical",
        "syllabus": ["ML Foundations & Statistics", "Neural Networks & Deep Learning", "Natural Language Processing", "Transformer Architecture", "Large Language Models", "Retrieval-Augmented Generation (RAG)", "AI Agents & Orchestration", "Attention Mechanisms"],
        "goals": ["Build ML models from scratch using Python and PyTorch", "Understand transformer architecture and attention mechanisms", "Implement RAG pipelines for knowledge-grounded AI", "Design and deploy AI agent systems"],
        "audience": "Developers and ML engineers seeking comprehensive AI mastery",
        "prerequisites": "Intermediate Python programming and basic statistics",
        "topic_descriptions": {
            "ML Foundations & Statistics": "Establishes the mathematical and statistical bedrock required for understanding machine learning algorithms. Covers probability distributions, hypothesis testing, regression, and classification fundamentals that underpin all modern ML systems.",
            "Neural Networks & Deep Learning": "Explores the architecture and training of neural networks from single perceptrons to deep multi-layer networks. Students learn about activation functions, backpropagation, gradient descent, and how to build and train networks for real-world tasks.",
            "Natural Language Processing": "Covers the core techniques for processing and understanding human language computationally. Topics include tokenization, embeddings, sequence modeling, and the evolution from bag-of-words approaches to modern contextual language understanding.",
            "Transformer Architecture": "Provides a detailed examination of the Transformer architecture that revolutionized NLP and beyond. Students dissect encoder-decoder structures, positional encoding, multi-head attention, and understand why this architecture enables massive parallelization and superior performance.",
            "Large Language Models": "Explores how large language models like GPT and LLaMA are built, trained, and fine-tuned at scale. Covers pre-training objectives, scaling laws, emergent capabilities, instruction tuning, and reinforcement learning from human feedback (RLHF).",
            "Retrieval-Augmented Generation (RAG)": "Teaches how to ground LLM outputs in factual, up-to-date information by combining retrieval systems with generative models. Students learn about vector databases, embedding-based search, chunking strategies, and how to build end-to-end RAG pipelines.",
            "AI Agents & Orchestration": "Examines autonomous AI agents that can plan, reason, and execute multi-step tasks using tools and external APIs. Covers agent architectures, tool use, memory systems, multi-agent orchestration patterns, and frameworks for building reliable agentic systems.",
            "Attention Mechanisms": "Provides a deep dive into the attention mechanism that is the core innovation behind modern AI breakthroughs. Students work through self-attention, cross-attention, and scaled dot-product attention mathematically and intuitively, understanding how attention allows models to dynamically focus on relevant information.",
        },
        "sections": {
            "part1": {
                "title": "Part 1: ML Foundations & AI Introduction",
                "items": [
                    {"id": "slides-part1", "name": "Slides", "file": "out/mastering-ai-part1-slides.html", "type": "slides"},
                    {"id": "demo-day1", "name": "Day 1: Python & ML Demo", "file": "out/demo-day1-python-ml.html", "type": "demo"},
                    {"id": "demo-day2", "name": "Day 2: Neural Networks Demo", "file": "out/demo-day2-neural-networks.html", "type": "demo"},
                    {"id": "demo-day3", "name": "Day 3: NLP & LLMs Demo", "file": "out/demo-day3-nlp-llms.html", "type": "demo"},
                    {"id": "notes-part1", "name": "Student Notes", "file": "out/student-notes-part1.html", "type": "notes"},
                ]
            },
            "part1-labs": {
                "title": "Part 1: Hands-on Labs",
                "items": [
                    {"id": "lab-01-python", "name": "Lab 1: Python for Data Science", "file": "out/lab-01-python-data-science.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-01-python-solution", "name": "Lab 1: Python for Data Science (Solutions)", "file": "out/lab-01-python-data-science-solutions.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-02-ml", "name": "Lab 2: Machine Learning with PyTorch", "file": "out/lab-02-ml-pytorch.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-02-ml-solution", "name": "Lab 2: Machine Learning (Solutions)", "file": "out/lab-02-ml-pytorch-solutions.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-nlp", "name": "Lab: NLP Fundamentals", "file": "out/lab-03-nlp.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-03-genai", "name": "Lab 3: Generative AI with Ollama", "file": "out/lab-03-generative-ai.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-03-genai-solution", "name": "Lab 3: Generative AI (Solutions)", "file": "out/lab-03-generative-ai-solutions.ipynb", "type": "lab", "runnable": True},
                ]
            },
            "part2": {
                "title": "Part 2: Advanced AI Topics",
                "items": [
                    {"id": "slides-main", "name": "Main Slides", "file": "out/mastering-ai-slides.html", "type": "slides"},
                    {"id": "demo-attention", "name": "Attention Visualization", "file": "out/demo-attention-visualization.html", "type": "demo"},
                    {"id": "demo-rag", "name": "RAG Pipeline", "file": "out/demo-rag-pipeline.html", "type": "demo"},
                    {"id": "demo-agent", "name": "Agent Builder", "file": "out/demo-agent-builder.html", "type": "demo"},
                    {"id": "notes-main", "name": "Student Notes", "file": "out/student-notes.html", "type": "notes"},
                ]
            },
        }
    },
    "python-fundamentals": {
        "id": "python-fundamentals",
        "name": "Python Fundamentals",
        "description": "Introduction to Python programming for beginners",
        "icon": "🐍",
        "duration": "4 hours",
        "category": "python",
        "syllabus": ["Variables & Data Types", "Strings & String Methods", "Lists & Dictionaries", "Control Flow (if/else)", "Loops & Iteration", "Functions", "Error Handling", "File I/O", "Modules & Imports", "Tuples & Sets", "Boolean Logic", "Sorting & Nested Data", "JSON Processing", "PEP 8 Style Guide"],
        "goals": ["Write and run Python scripts confidently", "Work with core data structures: lists, dicts, tuples, and sets", "Control program flow with conditionals and loops", "Define reusable functions and handle errors gracefully"],
        "audience": "Complete beginners with no prior programming experience",
        "prerequisites": None,
        "topic_descriptions": {
            "Variables & Data Types": "Introduces how Python stores and manages data through variables, covering integers, floats, strings, and booleans. Students learn about dynamic typing, type conversion, and best practices for naming variables in Python programs.",
            "Strings & String Methods": "Covers Python's powerful string handling capabilities, including slicing, concatenation, formatting with f-strings, and essential built-in methods. Students practice manipulating text data using methods like split, join, strip, replace, and format.",
            "Lists & Dictionaries": "Explores Python's two most essential data structures for storing collections of data. Students learn to create, access, modify, and iterate over lists and dictionaries, and understand when to use each structure for different programming tasks.",
            "Control Flow (if/else)": "Teaches how to make programs respond to different conditions using if, elif, and else statements. Covers comparison operators, logical operators, nested conditionals, and how to structure decision-making logic clearly and effectively.",
            "Loops & Iteration": "Covers for loops and while loops for repeating operations over sequences and until conditions are met. Students learn to iterate over lists, dictionaries, and ranges while understanding loop mechanics and common iteration patterns.",
            "Functions": "Introduces how to organize code into reusable, modular functions using def statements. Covers parameters, return values, default arguments, scope, and docstrings, establishing the foundation for writing clean and maintainable Python code.",
            "Error Handling": "Teaches how to anticipate and gracefully handle runtime errors using try, except, else, and finally blocks. Students learn about common exception types, how to raise custom exceptions, and defensive programming practices that make code robust.",
            "File I/O": "Covers reading from and writing to files using Python's built-in file handling capabilities. Students learn to work with text files using open, read, write, and the context manager pattern, as well as handling file paths and common file operations.",
            "Modules & Imports": "Explains how to leverage Python's module system to organize code and use external libraries. Covers import statements, the standard library, creating custom modules, and understanding packages and namespaces.",
            "Tuples & Sets": "Introduces tuples as immutable sequences and sets as unordered collections of unique elements. Students learn when to choose tuples over lists for data integrity, and how to use sets for membership testing, deduplication, and set operations like union and intersection.",
            "Boolean Logic": "Provides a thorough understanding of boolean values, logical operators (and, or, not), and truthiness in Python. Covers short-circuit evaluation, truthy and falsy values, and how to write clear boolean expressions for program logic.",
            "Sorting & Nested Data": "Teaches how to sort lists and other iterables using sorted() and the sort method with custom key functions. Covers working with nested data structures like lists of dictionaries, accessing deeply nested values, and organizing complex data.",
            "JSON Processing": "Covers how to work with JSON, the most common data interchange format in modern applications. Students learn to parse JSON strings, read and write JSON files, convert between Python dictionaries and JSON, and handle real-world API response data.",
            "PEP 8 Style Guide": "Introduces Python's official style guide and the importance of writing clean, readable, and consistent code. Covers naming conventions, indentation rules, line length, import ordering, and how to use linting tools to enforce style standards automatically.",
        },
        "sections": {
            "materials": {
                "title": "Course Materials",
                "items": [
                    {"id": "py-slides", "name": "Python Fundamentals Slides", "file": "python-fundamentals/python-fundamentals-slides.html", "type": "slides"},
                    {"id": "py-demo", "name": "Interactive Python Demo", "file": "python-fundamentals/demo-python-basics.html", "type": "demo"},
                    {"id": "py-notes", "name": "Student Notes", "file": "python-fundamentals/student-notes.md", "type": "notes"},
                ]
            },
            "labs": {
                "title": "Hands-on Labs",
                "items": [
                    {"id": "py-lab", "name": "Python Basics Lab", "file": "python-fundamentals/lab-python-basics.ipynb", "type": "lab", "runnable": True},
                    {"id": "py-lab-solution", "name": "Python Basics Lab (Solution)", "file": "python-fundamentals/lab-python-basics-solution.ipynb", "type": "lab", "runnable": True},
                ]
            }
        }
    },
    "python-intermediate": {
        "id": "python-intermediate",
        "name": "Python Intermediate",
        "description": "Advanced Python concepts including OOP, functional programming, decorators, and testing",
        "icon": "🐍",
        "duration": "8 hours",
        "category": "python",
        "syllabus": ["Object-Oriented Programming", "Classes & Inheritance", "Polymorphism & Properties", "Pattern Matching", "Functional Programming", "Lambda, Map, Filter, Reduce", "Closures & Decorators", "Generators & Iterators", "Partial Functions & Currying", "Lazy Evaluation", "Unit Testing with unittest", "Testing with pytest"],
        "goals": ["Design classes using OOP principles: inheritance, encapsulation, polymorphism", "Apply functional programming patterns with higher-order functions", "Write decorators and generators for clean, reusable code", "Build and run test suites with unittest and pytest"],
        "audience": "Developers with basic Python knowledge ready to level up",
        "prerequisites": "Python Fundamentals or equivalent experience with variables, loops, and functions",
        "topic_descriptions": {
            "Object-Oriented Programming": "Introduces the principles and philosophy of object-oriented programming, including encapsulation, abstraction, and code organization around objects. Students learn why OOP is a dominant paradigm in software development and how it promotes reusable, maintainable code.",
            "Classes & Inheritance": "Covers how to define classes with attributes and methods, and how to build class hierarchies using inheritance. Students learn about constructors, instance vs class variables, method overriding, and the super() function for extending parent class behavior.",
            "Polymorphism & Properties": "Explores how different classes can share a common interface through polymorphism, enabling flexible and extensible code. Also covers Python's property decorator for creating managed attributes with getters, setters, and deleters that maintain clean APIs.",
            "Pattern Matching": "Teaches Python's structural pattern matching syntax introduced in Python 3.10 using match/case statements. Students learn to match against literal values, sequences, mappings, and class instances, replacing complex if/elif chains with more readable and powerful constructs.",
            "Functional Programming": "Introduces the functional programming paradigm in Python, emphasizing pure functions, immutability, and function composition. Students learn how functional approaches can complement OOP to produce cleaner, more testable, and more concise code.",
            "Lambda, Map, Filter, Reduce": "Covers anonymous functions with lambda and the key higher-order functions for transforming data. Students practice using map for element-wise transformations, filter for selecting elements by condition, and reduce for aggregating sequences into single values.",
            "Closures & Decorators": "Explains how closures capture variables from enclosing scopes and how decorators use this mechanism to modify function behavior. Students learn to write and apply decorators for cross-cutting concerns like logging, timing, authentication, and caching.",
            "Generators & Iterators": "Teaches how to create memory-efficient iterables using generator functions with yield and generator expressions. Students learn about the iterator protocol, lazy evaluation benefits, and how to process large datasets that cannot fit entirely in memory.",
            "Partial Functions & Currying": "Covers techniques for creating specialized functions from more general ones using functools.partial and currying patterns. Students learn how to reduce function arity, create reusable function factories, and apply these techniques to simplify callback-heavy code.",
            "Lazy Evaluation": "Explores the concept of deferring computation until results are actually needed, improving performance and memory efficiency. Students learn how Python implements lazy evaluation through generators, itertools, and other deferred execution patterns for processing large or infinite data streams.",
            "Unit Testing with unittest": "Introduces Python's built-in unittest framework for writing and organizing automated tests. Covers TestCase classes, assertion methods, setUp and tearDown fixtures, test discovery, and best practices for structuring a test suite.",
            "Testing with pytest": "Covers the pytest framework as a more modern and Pythonic alternative for testing Python code. Students learn about simple assert-based tests, fixtures, parameterized testing, markers, and plugins that make testing more expressive and productive.",
        },
        "sections": {
            "materials": {
                "title": "Course Materials",
                "items": [
                    {"id": "pyi-slides", "name": "Python Intermediate Slides", "file": "python-intermediate/python-intermediate-slides.html", "type": "slides"},
                    {"id": "pyi-notes", "name": "Student Notes", "file": "python-intermediate/student-notes.md", "type": "notes"},
                ]
            },
            "labs": {
                "title": "Hands-on Labs",
                "items": [
                    {"id": "pyi-lab", "name": "Python Intermediate Lab", "file": "python-intermediate/lab-python-intermediate.ipynb", "type": "lab", "runnable": True},
                    {"id": "pyi-lab-solution", "name": "Python Intermediate Lab (Solutions)", "file": "python-intermediate/lab-python-intermediate-solutions.ipynb", "type": "lab", "runnable": True},
                ]
            }
        }
    },
    "enterprise-ai-adoption": {
        "id": "enterprise-ai-adoption",
        "name": "Enterprise AI Adoption",
        "description": "5-day intensive course on adopting AI in enterprise environments - governance, workflows, and implementation",
        "icon": "🏢",
        "duration": "5 days",
        "category": "ai-business",
        "syllabus": ["AI Strategy Development", "AI Readiness Assessment", "Governance Frameworks", "Workflow Mapping & Automation", "Change Management", "Risk Assessment & Mitigation", "Stakeholder Analysis", "30-60-90 Day Implementation Plans", "AI for Managers", "Technical Deep-Dive Module"],
        "goals": ["Develop an actionable AI adoption strategy for your organisation", "Build governance and risk frameworks for responsible AI use", "Map existing workflows and identify automation opportunities", "Lead change management for AI transformation initiatives"],
        "audience": "Senior leaders, managers, and transformation leads driving AI adoption",
        "prerequisites": "No technical background required; management or leadership experience recommended",
        "topic_descriptions": {
            "AI Strategy Development": "Guides participants through creating a comprehensive AI strategy aligned with business objectives and organizational capabilities. Covers vision setting, opportunity identification, prioritization frameworks, and building a strategic roadmap that connects AI initiatives to measurable business outcomes.",
            "AI Readiness Assessment": "Provides frameworks for evaluating an organization's current readiness to adopt and scale AI across data maturity, technical infrastructure, talent, and culture. Students learn to conduct gap analyses and build actionable plans to address readiness shortfalls before committing to AI investments.",
            "Governance Frameworks": "Covers the essential structures, policies, and oversight mechanisms needed to govern AI responsibly within an enterprise. Topics include model validation processes, data governance, ethical review boards, accountability structures, and regulatory compliance considerations.",
            "Workflow Mapping & Automation": "Teaches how to identify, document, and analyze existing business workflows to find high-impact automation opportunities. Students learn process mapping techniques, criteria for selecting workflows suitable for AI augmentation, and how to design human-AI collaborative processes.",
            "Change Management": "Addresses the people side of AI adoption, covering strategies for managing resistance, building buy-in, and driving cultural transformation. Students learn proven change management frameworks adapted specifically for AI initiatives, including communication strategies and training program design.",
            "Risk Assessment & Mitigation": "Provides a structured approach to identifying, evaluating, and mitigating the risks associated with enterprise AI deployments. Covers technical risks like model drift and data quality, organizational risks like skill gaps, and external risks including regulatory changes and reputational concerns.",
            "Stakeholder Analysis": "Teaches how to identify, categorize, and engage the key stakeholders who will influence or be affected by AI initiatives. Students learn stakeholder mapping techniques, influence-interest matrices, and strategies for tailoring communication and engagement plans to different stakeholder groups.",
            "30-60-90 Day Implementation Plans": "Guides participants through creating phased implementation plans with clear milestones, deliverables, and success metrics for the first 90 days. Covers quick-win identification for the first 30 days, scaling strategies for days 31-60, and optimization and measurement approaches for days 61-90.",
            "AI for Managers": "Equips managers with the practical knowledge they need to lead AI-enabled teams and make informed decisions about AI adoption. Covers how to evaluate AI vendor claims, set realistic expectations, manage AI projects, and foster a data-driven culture within their departments.",
            "Technical Deep-Dive Module": "Provides a more technical exploration of AI technologies for participants who want deeper understanding of the underlying systems. Covers machine learning pipelines, model training and evaluation basics, API integration patterns, and infrastructure considerations for deploying AI in production environments.",
        },
        "sections": {
            "slides": {
                "title": "Course Slides",
                "items": [
                    {"id": "eai-slides", "name": "Enterprise AI Adoption Slides", "file": "enterprise-ai-adoption/enterprise-ai-adoption-slides.html", "type": "slides"},
                ]
            },
            "materials": {
                "title": "Course Materials",
                "items": [
                    {"id": "eai-notes", "name": "Student Notes", "file": "enterprise-ai-adoption/student-notes.md", "type": "notes"},
                    {"id": "eai-case-studies", "name": "Case Studies", "file": "enterprise-ai-adoption/case-studies.md", "type": "notes"},
                    {"id": "eai-facilitator", "name": "Facilitator Guide", "file": "enterprise-ai-adoption/facilitator-guide.md", "type": "notes"},
                    {"id": "eai-resources", "name": "Follow-up Resources", "file": "enterprise-ai-adoption/resources.md", "type": "notes"},
                ]
            },
            "labs": {
                "title": "Labs & Exercises",
                "items": [
                    {"id": "eai-labs", "name": "Lab Exercises", "file": "enterprise-ai-adoption/labs/lab-exercises.md", "type": "lab"},
                    {"id": "eai-assessments", "name": "Assessments & Quizzes", "file": "enterprise-ai-adoption/assessments.md", "type": "lab"},
                ]
            },
            "templates": {
                "title": "Downloadable Templates",
                "items": [
                    {"id": "eai-readiness", "name": "AI Readiness Canvas (CSV)", "file": "enterprise-ai-adoption/templates/ai-readiness-canvas.csv", "type": "notes"},
                    {"id": "eai-governance", "name": "Governance Canvas (CSV)", "file": "enterprise-ai-adoption/templates/governance-canvas.csv", "type": "notes"},
                    {"id": "eai-workflow", "name": "Workflow Mapping Template", "file": "enterprise-ai-adoption/templates/workflow-mapping-template.md", "type": "notes"},
                    {"id": "eai-rollout", "name": "30-60-90 Day Plan (CSV)", "file": "enterprise-ai-adoption/templates/30-60-90-day-plan.csv", "type": "notes"},
                    {"id": "eai-playbook", "name": "AI Playbook Template", "file": "enterprise-ai-adoption/templates/ai-playbook-template.md", "type": "notes"},
                    {"id": "eai-stakeholder", "name": "Stakeholder Analysis (CSV)", "file": "enterprise-ai-adoption/templates/stakeholder-analysis.csv", "type": "notes"},
                ]
            },
            "advanced": {
                "title": "Advanced Modules",
                "items": [
                    {"id": "eai-managers", "name": "AI for Managers Module", "file": "enterprise-ai-adoption/advanced-modules/ai-for-managers.md", "type": "notes"},
                    {"id": "eai-technical", "name": "Technical Deep-Dive Module", "file": "enterprise-ai-adoption/advanced-modules/technical-deep-dive.md", "type": "notes"},
                    {"id": "eai-change", "name": "Change Management Module", "file": "enterprise-ai-adoption/advanced-modules/change-management.md", "type": "notes"},
                ]
            }
        }
    },
    "mastering-ai-agents": {
        "id": "mastering-ai-agents",
        "name": "Mastering AI Agents",
        "description": "3-day intensive course on AI agents, agentic swarms, and Google's A2A protocol",
        "icon": "🤖",
        "duration": "3 days",
        "category": "ai-technical",
        "syllabus": ["Reactive vs Deliberative Agents", "Agent Architectures & Patterns", "Tool Use & Function Calling", "Multi-Agent Systems", "Swarm Intelligence", "Google A2A Protocol", "Agent Orchestration Frameworks", "Building Production Agents"],
        "goals": ["Understand the spectrum of AI agent architectures", "Build reactive and deliberative agents from scratch", "Implement multi-agent swarms for complex problem-solving", "Integrate agents using Google's Agent-to-Agent (A2A) protocol"],
        "audience": "Developers and ML engineers building autonomous AI systems",
        "prerequisites": "Intermediate Python and basic understanding of LLMs and prompt engineering",
        "topic_descriptions": {
            "Reactive vs Deliberative Agents": "Explore the two fundamental paradigms of AI agent design: reactive agents that respond directly to environmental stimuli, and deliberative agents that maintain internal models and plan ahead. You will learn when each approach is appropriate and how modern systems often combine both strategies for robust behavior.",
            "Agent Architectures & Patterns": "Study the core architectural patterns used to build AI agents, including BDI (Belief-Desire-Intention), subsumption architectures, and layered hybrid designs. You will examine how these patterns address challenges like scalability, modularity, and real-time decision-making in complex environments.",
            "Tool Use & Function Calling": "Learn how AI agents extend their capabilities by invoking external tools, APIs, and functions during reasoning and execution. You will implement function-calling patterns that allow large language models to interact with databases, code interpreters, web services, and other external systems reliably.",
            "Multi-Agent Systems": "Understand how multiple AI agents collaborate, negotiate, and coordinate to solve problems that exceed the capability of any single agent. You will explore communication protocols, shared memory architectures, and conflict resolution strategies used in distributed agent systems.",
            "Swarm Intelligence": "Discover how decentralized, self-organizing agent collectives can produce emergent intelligent behavior inspired by biological systems like ant colonies and bird flocks. You will implement swarm algorithms and learn how simple local rules give rise to sophisticated global problem-solving without centralized control.",
            "Google A2A Protocol": "Examine Google's Agent-to-Agent (A2A) protocol, an open standard for enabling interoperability and communication between AI agents built on different platforms. You will learn the protocol's message format, discovery mechanisms, and task lifecycle management for building cross-platform agent ecosystems.",
            "Agent Orchestration Frameworks": "Survey the leading frameworks for orchestrating AI agents, including LangGraph, CrewAI, AutoGen, and others. You will compare their approaches to workflow definition, state management, error handling, and human-in-the-loop patterns to select the right tool for your use case.",
            "Building Production Agents": "Apply everything you have learned to design, build, and deploy production-grade AI agents with proper error handling, observability, and guardrails. You will address real-world concerns including latency management, cost optimization, safety constraints, and techniques for testing and monitoring agents in live environments.",
        },
        "sections": {
            "slides": {
                "title": "Course Slides",
                "items": [
                    {"id": "maa-slides", "name": "AI Agents Slides", "file": "mastering-ai-agents/mastering-ai-agents-slides.html", "type": "slides"},
                    {"id": "maa-pdf", "name": "Slides (PDF Download)", "file": "mastering-ai-agents/mastering-ai-agents-slides.pdf", "type": "notes", "printable": True},
                ]
            },
            "materials": {
                "title": "Course Materials",
                "items": [
                    {"id": "maa-notes", "name": "Student Notes", "file": "mastering-ai-agents/student-notes.md", "type": "notes"},
                ]
            },
            "labs": {
                "title": "Hands-on Labs",
                "items": [
                    {"id": "maa-lab1", "name": "Lab 1: Reactive Agents", "file": "mastering-ai-agents/labs/lab-01-reactive-agents.ipynb", "type": "lab", "runnable": True},
                    {"id": "maa-lab2", "name": "Lab 2: Swarm Intelligence", "file": "mastering-ai-agents/labs/lab-02-swarm-intelligence.ipynb", "type": "lab", "runnable": True},
                ]
            },
            "demos": {
                "title": "Interactive Demos",
                "items": [
                    {"id": "maa-demo1", "name": "Demo: Agent Types Comparison", "file": "mastering-ai-agents/demos/demo-01-agent-types.ipynb", "type": "lab", "runnable": True},
                ]
            }
        }
    },
    "use-case-prompting": {
        "id": "use-case-prompting",
        "name": "Use Case Lab & Prompting Foundations",
        "description": "90-minute seminar on identifying AI use cases and mastering prompt engineering",
        "icon": "💬",
        "duration": "90 minutes",
        "category": "itag-skillnet",
        "syllabus": ["CRAFT Prompt Framework", "Context Engineering", "AI Use Case Identification", "Prompt Engineering Techniques", "Iterative Prompt Refinement", "Hands-on CRAFT Builder"],
        "goals": ["Master the CRAFT framework for writing effective prompts", "Identify high-value AI use cases in your daily work", "Write prompts that produce consistent, reliable outputs", "Apply context engineering to improve AI responses"],
        "audience": "Business professionals exploring AI for productivity and decision-making",
        "prerequisites": None,
        "topic_descriptions": {
            "CRAFT Prompt Framework": "Learn the CRAFT framework \u2014 Context, Role, Action, Format, Target \u2014 a structured methodology for composing effective prompts that consistently produce high-quality AI outputs. You will practice applying each element of the framework to transform vague requests into precise, actionable instructions.",
            "Context Engineering": "Understand how to design and supply the right context to an AI model so it can generate accurate, relevant responses. You will explore techniques for selecting background information, setting constraints, and framing problems in ways that dramatically improve output quality.",
            "AI Use Case Identification": "Develop a systematic approach to identifying high-value AI use cases within your organization or domain. You will learn evaluation criteria for assessing feasibility, impact, and effort so you can prioritize opportunities where AI delivers the greatest return.",
            "Prompt Engineering Techniques": "Master a toolkit of proven prompt engineering techniques including few-shot examples, chain-of-thought reasoning, role assignment, and output formatting directives. You will learn how each technique influences model behavior and when to apply them for optimal results.",
            "Iterative Prompt Refinement": "Practice the disciplined process of testing, evaluating, and improving prompts through successive iterations. You will learn how to diagnose common failure modes in AI outputs and apply targeted adjustments to progressively achieve the quality and consistency you need.",
            "Hands-on CRAFT Builder": "Put your skills into practice in a guided, interactive session where you build complete CRAFT prompts for real-world scenarios. You will work through multiple exercises, receive feedback, and leave with a personal library of refined prompts you can use immediately.",
        },
        "sections": {
            "workshop": {
                "title": "Workshop Materials",
                "items": [
                    {"id": "ucp-slides", "name": "Presentation Slides", "file": "use-case-prompting-seminar/use-case-prompting-slides.html", "type": "slides"},
                    {"id": "ucp-pdf", "name": "Slides (PDF Download)", "file": "use-case-prompting-seminar/use-case-prompting-slides.pdf", "type": "notes", "printable": True},
                ]
            },
            "demo": {
                "title": "Interactive Demo",
                "items": [
                    {"id": "ucp-demo-app", "name": "CRAFT Prompt Builder (Interactive)", "file": "use-case-prompting-seminar/demo/index.html", "type": "demo", "external": True},
                    {"id": "ucp-poll", "name": "Audience Poll (AI Experience)", "file": "use-case-prompting-seminar/demo/poll.html", "type": "demo", "external": True},
                    {"id": "ucp-demo", "name": "ChatGPT Demo Guide (Instructor)", "file": "use-case-prompting-seminar/interactive-demo-guide.html", "type": "notes"},
                ]
            },
            "exercise": {
                "title": "Take-Home Exercise",
                "items": [
                    {"id": "ucp-exercise", "name": "Take-Home Practice Exercise (PDF)", "file": "use-case-prompting-seminar/take-home-exercise.pdf", "type": "notes", "printable": True},
                ]
            }
        }
    },
    "ai-copilot-seminar": {
        "id": "ai-copilot-seminar",
        "name": "Build Your Own AI Copilot",
        "description": "90-minute seminar on turning your content into an AI-powered assistant using RAG and knowledge bases",
        "icon": "🤖",
        "duration": "90 minutes",
        "category": "itag-skillnet",
        "syllabus": ["What is RAG?", "Knowledge Bases & Vector Stores", "Document Chunking Strategies", "Building a Custom Copilot", "Grounding AI with Your Data", "RAG Simulator Demo"],
        "goals": ["Understand how Retrieval-Augmented Generation (RAG) works", "Learn to turn your documents into an AI knowledge base", "Evaluate tools for building custom AI copilots", "See a live RAG pipeline in action"],
        "audience": "Business professionals and team leads interested in custom AI assistants",
        "prerequisites": None,
        "topic_descriptions": {
            "What is RAG?": "Learn the fundamentals of Retrieval-Augmented Generation, a technique that enhances AI responses by grounding them in relevant external documents retrieved at query time. You will understand how RAG addresses the limitations of static training data and reduces hallucinations by anchoring outputs in verified sources.",
            "Knowledge Bases & Vector Stores": "Explore how knowledge bases and vector databases store and retrieve information using semantic embeddings rather than traditional keyword matching. You will learn how documents are converted into vector representations and how similarity search enables AI systems to find the most relevant information for any query.",
            "Document Chunking Strategies": "Understand why and how documents must be split into appropriately sized chunks before being embedded and stored for retrieval. You will compare chunking strategies \u2014 fixed-size, semantic, recursive, and hierarchical \u2014 and learn how chunk size and overlap affect retrieval accuracy and response quality.",
            "Building a Custom Copilot": "Walk through the end-to-end process of building a custom AI copilot tailored to your organization's specific knowledge and workflows. You will learn how to connect a language model to your own data sources, configure retrieval pipelines, and design conversational interfaces that provide domain-specific assistance.",
            "Grounding AI with Your Data": "Learn techniques for ensuring AI-generated responses are grounded in your organization's actual documents, policies, and data rather than generic training knowledge. You will explore methods for source attribution, confidence scoring, and contextual filtering that build trust and accuracy in enterprise AI applications.",
            "RAG Simulator Demo": "Experience an interactive demonstration of a working RAG system that lets you experiment with different configurations and see their effects in real time. You will observe how changes to retrieval parameters, chunk sizes, and prompt templates influence the quality and relevance of AI-generated answers.",
        },
        "sections": {
            "workshop": {
                "title": "Workshop Materials",
                "items": [
                    {"id": "aic-slides", "name": "Presentation Slides", "file": "ai-copilot-seminar/ai-copilot-slides.html", "type": "slides"},
                    {"id": "aic-pdf", "name": "Slides (PDF Download)", "file": "ai-copilot-seminar/ai-copilot-slides.pdf", "type": "notes", "printable": True},
                ]
            },
            "demo": {
                "title": "Interactive Demo",
                "items": [
                    {"id": "aic-rag-demo", "name": "RAG Simulator (Interactive)", "file": "ai-copilot-seminar/demo/index.html", "type": "demo", "external": True},
                    {"id": "aic-poll", "name": "Audience Poll (AI Experience)", "file": "use-case-prompting-seminar/demo/poll.html", "type": "demo", "external": True},
                ]
            },
            "materials": {
                "title": "Course Materials",
                "items": [
                    {"id": "aic-notes", "name": "Student Notes", "file": "ai-copilot-seminar/student-notes.html", "type": "notes"},
                    {"id": "aic-demo-guide", "name": "Instructor Demo Guide", "file": "ai-copilot-seminar/interactive-demo-guide.html", "type": "notes"},
                    {"id": "aic-exercise", "name": "Take-Home Exercise (PDF)", "file": "ai-copilot-seminar/take-home-exercise.pdf", "type": "notes", "printable": True},
                ]
            }
        }
    },
    "proposal-report-accelerator": {
        "id": "proposal-report-accelerator",
        "name": "Proposal & Report Accelerator",
        "description": "90-minute seminar on using AI to write proposals and reports faster while maintaining quality, compliance, and consistency",
        "icon": "📝",
        "duration": "90 minutes",
        "category": "itag-skillnet",
        "syllabus": ["WRITE Framework for AI Documents", "Proposal Structure & Templates", "Report Generation Workflow", "Quality & Compliance Checks", "Tone & Style Consistency", "Live AI Writing Demo"],
        "goals": ["Use the WRITE framework to draft proposals and reports with AI", "Maintain quality, compliance, and brand consistency", "Speed up document creation while keeping human oversight", "Apply AI-assisted editing and revision techniques"],
        "audience": "Professionals who write proposals, reports, or business documents regularly",
        "prerequisites": None,
        "topic_descriptions": {
            "WRITE Framework for AI Documents": "Learn the WRITE framework \u2014 a structured methodology for producing professional documents with AI assistance that maintains quality, consistency, and compliance standards. You will understand how each step in the framework guides the AI through drafting, reviewing, and refining documents to meet professional expectations.",
            "Proposal Structure & Templates": "Study the essential components of winning proposals, including executive summaries, scope definitions, methodology sections, and pricing structures. You will learn how to create reusable templates that AI can populate intelligently while maintaining your organization's voice and formatting standards.",
            "Report Generation Workflow": "Master a systematic workflow for using AI to generate reports from raw data, research findings, or project updates. You will learn how to structure inputs, guide the AI through logical analysis, and produce polished reports that communicate insights clearly and persuasively to your target audience.",
            "Quality & Compliance Checks": "Discover techniques for using AI to verify that generated documents meet quality benchmarks and regulatory or organizational compliance requirements. You will build checklists and automated review prompts that catch errors, inconsistencies, and compliance gaps before documents reach stakeholders.",
            "Tone & Style Consistency": "Learn how to maintain a consistent professional tone, voice, and style across AI-generated documents, even when multiple authors or sessions are involved. You will practice crafting style guides and reference examples that anchor the AI's output to your brand standards and audience expectations.",
            "Live AI Writing Demo": "Participate in a live demonstration where a complete professional document is drafted, refined, and finalized using AI in real time. You will see the full workflow in action, from initial brief through iterative improvement, and learn practical tips for achieving publication-ready results efficiently.",
        },
        "sections": {
            "workshop": {
                "title": "Workshop Materials",
                "items": [
                    {"id": "pra-slides", "name": "Presentation Slides", "file": "proposal-report-accelerator/proposal-report-accelerator-slides.html", "type": "slides"},
                    {"id": "pra-pdf", "name": "Slides (PDF Download)", "file": "proposal-report-accelerator/proposal-report-accelerator-slides.pdf", "type": "notes", "printable": True},
                ]
            },
            "demo": {
                "title": "Interactive Demo",
                "items": [
                    {"id": "pra-prompt-builder", "name": "WRITE Framework Prompt Builder (Interactive)", "file": "proposal-report-accelerator/demo/index.html", "type": "demo", "external": True},
                    {"id": "pra-poll", "name": "Audience Poll (AI Experience)", "file": "use-case-prompting-seminar/demo/poll.html", "type": "demo", "external": True},
                ]
            },
            "materials": {
                "title": "Course Materials",
                "items": [
                    {"id": "pra-notes", "name": "Student Notes", "file": "proposal-report-accelerator/student-notes.html", "type": "notes"},
                ]
            }
        }
    },
    "handling-hallucinations": {
        "id": "handling-hallucinations",
        "name": "Handling Hallucinations: Fact-Checking AI",
        "description": "90-minute seminar on identifying, preventing, and verifying AI-generated content using the VERIFY framework",
        "icon": "🔍",
        "duration": "90 minutes",
        "category": "itag-skillnet",
        "syllabus": ["Why AI Hallucinates", "Types of AI Hallucinations", "The VERIFY Framework", "Fact-Checking Techniques", "Prompt Strategies to Reduce Errors", "Hallucination Detector Demo"],
        "goals": ["Recognise the different types of AI hallucinations", "Apply the VERIFY framework to fact-check AI outputs", "Write prompts that minimise hallucination risk", "Build a personal verification workflow for AI content"],
        "audience": "Professionals using AI-generated content who need accuracy and reliability",
        "prerequisites": None,
        "topic_descriptions": {
            "Why AI Hallucinates": "Understand the technical and architectural reasons why large language models generate plausible-sounding but factually incorrect information. You will explore how training data gaps, probabilistic token generation, and lack of true world knowledge contribute to hallucinations.",
            "Types of AI Hallucinations": "Learn to identify and categorize the different forms of AI hallucination, including factual fabrication, source invention, logical inconsistency, and context drift. You will study real-world examples of each type so you can quickly recognize when an AI output requires additional scrutiny or correction.",
            "The VERIFY Framework": "Master the VERIFY framework, a systematic approach for evaluating AI-generated content for accuracy and reliability before it is used or shared. You will learn each step of the framework and practice applying it to real outputs, building a repeatable process that dramatically reduces the risk of acting on false information.",
            "Fact-Checking Techniques": "Develop practical skills for efficiently fact-checking AI-generated claims using authoritative sources, cross-referencing strategies, and triangulation methods. You will learn how to prioritize which claims to verify, where to find reliable sources, and how to build verification workflows that balance thoroughness with speed.",
            "Prompt Strategies to Reduce Errors": "Explore prompt engineering techniques specifically designed to minimize hallucinations, including grounding instructions, citation requirements, confidence qualifiers, and chain-of-verification prompting. You will learn how to structure prompts that encourage the model to acknowledge uncertainty rather than fabricate answers.",
            "Hallucination Detector Demo": "Experience a hands-on demonstration of tools and techniques for automatically detecting potential hallucinations in AI-generated text. You will see how detection systems flag suspicious claims, compare outputs against source material, and provide confidence scores that help you decide which content to trust.",
        },
        "sections": {
            "workshop": {
                "title": "Workshop Materials",
                "items": [
                    {"id": "hh-slides", "name": "Presentation Slides", "file": "handling-hallucinations-seminar/handling-hallucinations-slides.html", "type": "slides"},
                    {"id": "hh-pdf", "name": "Slides (PDF Download)", "file": "handling-hallucinations-seminar/handling-hallucinations-slides.pdf", "type": "notes", "printable": True},
                ]
            },
            "demo": {
                "title": "Interactive Demo",
                "items": [
                    {"id": "hh-fact-checker", "name": "Hallucination Detector (Interactive)", "file": "handling-hallucinations-seminar/demo/index.html", "type": "demo", "external": True},
                    {"id": "hh-poll", "name": "Audience Poll (AI Experience)", "file": "use-case-prompting-seminar/demo/poll.html", "type": "demo", "external": True},
                ]
            },
            "materials": {
                "title": "Course Materials",
                "items": [
                    {"id": "hh-notes", "name": "Student Notes", "file": "handling-hallucinations-seminar/student-notes.html", "type": "notes"},
                ]
            }
        }
    },
    "data-safety-ethics": {
        "id": "data-safety-ethics",
        "name": "Data Safety & Ethics: Use AI Responsibly",
        "description": "90-minute seminar on data protection, privacy, and ethical AI use with the SHIELD framework",
        "icon": "🛡️",
        "duration": "90 minutes",
        "category": "itag-skillnet",
        "syllabus": ["The SHIELD Framework", "Data Protection & GDPR", "Privacy in AI Systems", "Bias & Fairness", "Ethical AI Decision-Making", "Data Safety Assessment Tool"],
        "goals": ["Apply the SHIELD framework for responsible AI use", "Understand GDPR and data protection implications of AI", "Identify and mitigate bias in AI-driven decisions", "Conduct a data safety assessment for your AI tools"],
        "audience": "Professionals handling sensitive data or making decisions with AI assistance",
        "prerequisites": None,
        "topic_descriptions": {
            "The SHIELD Framework": "Learn a structured approach to data safety using the SHIELD framework, which covers Security, Handling, Integrity, Ethics, Legal compliance, and Documentation. This practical model provides a repeatable methodology for assessing and managing data risks across any organisation.",
            "Data Protection & GDPR": "Understand the core principles of data protection legislation, with a focus on the General Data Protection Regulation and its impact on how organisations collect, store, and process personal data. You will learn about lawful bases for processing, data subject rights, and the responsibilities of data controllers and processors.",
            "Privacy in AI Systems": "Explore the unique privacy challenges that arise when AI systems process large volumes of personal and sensitive data. Topics include data minimisation, anonymisation and pseudonymisation techniques, and strategies for building privacy-preserving machine learning pipelines.",
            "Bias & Fairness": "Examine how bias can enter AI systems at every stage of the development lifecycle, from data collection and labelling to model training and deployment. You will learn practical techniques for detecting, measuring, and mitigating bias to promote fair and equitable outcomes.",
            "Ethical AI Decision-Making": "Develop a working understanding of ethical frameworks and principles that guide responsible AI development and deployment. This topic covers transparency, accountability, human oversight, and how to navigate the complex trade-offs that arise when AI systems make or inform consequential decisions.",
            "Data Safety Assessment Tool": "Apply your learning by using a hands-on data safety assessment tool to evaluate real-world scenarios and organisational practices. You will learn how to conduct structured assessments, identify risk areas, and produce actionable recommendations for improving data safety posture.",
        },
        "sections": {
            "slides": {
                "title": "Workshop Materials",
                "items": [
                    {"id": "dse-slides", "name": "Presentation Slides", "file": "data-safety-ethics-seminar/data-safety-ethics-slides.html", "type": "slides"},
                    {"id": "dse-pdf", "name": "Slides (PDF Download)", "file": "data-safety-ethics-seminar/data-safety-ethics-slides.pdf", "type": "notes", "printable": True},
                ]
            },
            "demo": {
                "title": "Interactive Demo",
                "items": [
                    {"id": "dse-assessment", "name": "Data Safety Assessment Tool (Interactive)", "file": "data-safety-ethics-seminar/demo/index.html", "type": "demo", "external": True},
                    {"id": "dse-poll", "name": "Audience Poll (AI Experience)", "file": "use-case-prompting-seminar/demo/poll.html", "type": "demo", "external": True},
                ]
            },
            "materials": {
                "title": "Course Materials",
                "items": [
                    {"id": "dse-notes", "name": "Student Notes", "file": "data-safety-ethics-seminar/student-notes.html", "type": "notes"},
                ]
            }
        }
    },
    "budget-friendly-ai-toolkit": {
        "id": "budget-friendly-ai-toolkit",
        "name": "Budget-Friendly AI Toolkit: Practical Tools Under €50/Month",
        "description": "90-minute seminar on building a powerful AI toolkit without breaking the bank using the VALUE framework",
        "icon": "💰",
        "duration": "90 minutes",
        "category": "itag-skillnet",
        "syllabus": ["The VALUE Framework", "Free & Open-Source AI Tools", "Budget AI Tool Comparison", "Building Your AI Stack", "Cost Optimisation Strategies", "AI Toolkit Budget Calculator"],
        "goals": ["Build a powerful AI toolkit for under €50/month", "Evaluate free and open-source AI alternatives", "Apply the VALUE framework to tool selection decisions", "Create a personalised AI budget plan"],
        "audience": "Budget-conscious professionals and small teams looking to adopt AI affordably",
        "prerequisites": None,
        "topic_descriptions": {
            "The VALUE Framework": "Learn the VALUE framework for evaluating AI tools based on Viability, Accessibility, Longevity, Usability, and Effectiveness. This structured approach ensures you make informed decisions when selecting AI tools that deliver genuine return on investment without unnecessary spend.",
            "Free & Open-Source AI Tools": "Survey the landscape of free and open-source AI tools available for common business tasks including text generation, image creation, data analysis, and automation. You will gain hands-on familiarity with tools that can deliver professional-grade results at zero licensing cost.",
            "Budget AI Tool Comparison": "Learn how to systematically compare AI tools across dimensions such as capability, cost, ease of integration, and scalability. This topic provides evaluation templates and criteria that help you objectively assess which tools best meet your specific needs and budget constraints.",
            "Building Your AI Stack": "Discover how to assemble a cohesive set of AI tools that work together to support your workflows and business objectives. You will learn strategies for integrating free and low-cost tools into a unified stack that maximises productivity while minimising redundancy.",
            "Cost Optimisation Strategies": "Explore proven strategies for reducing AI-related costs, including leveraging free tiers, optimising API usage, batching requests, and choosing the right model size for each task. You will learn how to monitor spending and identify opportunities to maintain capability while cutting expenses.",
            "AI Toolkit Budget Calculator": "Put your knowledge into practice using an interactive budget calculator that helps you plan and forecast AI tool expenditure. You will learn to model different scenarios, compare build-versus-buy decisions, and create a realistic budget plan for your AI toolkit.",
        },
        "sections": {
            "slides": {
                "title": "Workshop Materials",
                "items": [
                    {"id": "bfat-slides", "name": "Presentation Slides", "file": "budget-friendly-ai-toolkit/budget-friendly-ai-toolkit-slides.html", "type": "slides"},
                    {"id": "bfat-pdf", "name": "Slides (PDF Download)", "file": "budget-friendly-ai-toolkit/budget-friendly-ai-toolkit-slides.pdf", "type": "notes", "printable": True},
                ]
            },
            "demo": {
                "title": "Interactive Demos",
                "items": [
                    {"id": "bfat-calculator", "name": "AI Toolkit Budget Calculator", "file": "budget-friendly-ai-toolkit/demo/index.html", "type": "demo", "external": True},
                    {"id": "bfat-opensource", "name": "Free & Open Source AI Toolkit", "file": "budget-friendly-ai-toolkit/demo/opensource.html", "type": "demo", "external": True},
                    {"id": "bfat-poll", "name": "Audience Poll (AI Experience)", "file": "use-case-prompting-seminar/demo/poll.html", "type": "demo", "external": True},
                ]
            },
            "materials": {
                "title": "Course Materials",
                "items": [
                    {"id": "bfat-notes", "name": "Student Notes", "file": "budget-friendly-ai-toolkit/student-notes.html", "type": "notes"},
                ]
            }
        }
    },
    "ai-impact-work": {
        "id": "ai-impact-work",
        "name": "AI's Impact on Work & Rolling Out AI Successfully",
        "description": "90-minute seminar on understanding how AI transforms the workplace and building a practical rollout strategy using the LAUNCH framework",
        "icon": "🚀",
        "duration": "90 minutes",
        "category": "itag-skillnet",
        "syllabus": ["The LAUNCH Framework", "AI's Impact on Jobs & Roles", "Workforce Readiness Assessment", "Change Management for AI", "Building Your AI Rollout Plan", "Measuring AI Success & ROI"],
        "goals": ["Understand how AI is transforming jobs, roles, and workflows", "Apply the LAUNCH framework to plan a successful AI rollout", "Assess your organisation's AI readiness across 5 key dimensions", "Build a 90-day AI rollout plan with measurable KPIs"],
        "audience": "Business leaders, managers, and professionals responsible for AI adoption and digital transformation",
        "prerequisites": None,
        "topic_descriptions": {
            "The LAUNCH Framework": "Learn the LAUNCH framework — Landscape, Alignment, Upskilling, Navigate, Champion, Harvest — a structured six-step methodology for planning and executing successful AI rollouts in any organisation. You will understand how each phase builds on the previous one to create a sustainable, people-centred approach to AI adoption.",
            "AI's Impact on Jobs & Roles": "Explore how AI is reshaping the workplace through augmentation, automation, and the creation of entirely new roles. You will examine real-world data on which tasks and industries are most affected, and learn to distinguish between jobs that will be transformed versus those that will emerge in the AI era.",
            "Workforce Readiness Assessment": "Conduct a structured assessment of your organisation's readiness for AI adoption across five critical dimensions: leadership and vision, data and infrastructure, people and skills, process and governance, and culture and change readiness. You will use a practical scoring tool to identify strengths and gaps.",
            "Change Management for AI": "Master the people side of AI adoption by learning proven change management strategies tailored specifically to technology transformation. You will explore techniques for building AI champions, managing resistance, crafting effective communication plans, and creating psychological safety during periods of change.",
            "Building Your AI Rollout Plan": "Design a practical 90-day AI rollout plan that takes your organisation from pilot selection through implementation to evaluation and scaling. You will learn criteria for choosing high-impact, low-risk pilot projects and create a structured timeline with clear milestones and accountability.",
            "Measuring AI Success & ROI": "Develop a comprehensive measurement framework for tracking AI impact across efficiency, quality, revenue, and employee satisfaction dimensions. You will learn how to define meaningful KPIs, establish baselines, set realistic targets, and build an AI dashboard that demonstrates clear return on investment to stakeholders.",
        },
        "sections": {
            "workshop": {
                "title": "Workshop Materials",
                "items": [
                    {"id": "aiw-slides", "name": "Presentation Slides", "file": "ai-impact-work-seminar/ai-impact-work-slides.html", "type": "slides"},
                    {"id": "aiw-pdf", "name": "Slides (PDF Download)", "file": "ai-impact-work-seminar/ai-impact-work-slides.pdf", "type": "notes", "printable": True},
                ]
            },
            "demo": {
                "title": "Interactive Demo",
                "items": [
                    {"id": "aiw-readiness", "name": "AI Readiness Assessment Tool (Interactive)", "file": "ai-impact-work-seminar/demo/index.html", "type": "demo", "external": True},
                    {"id": "aiw-poll", "name": "Audience Poll (AI Experience)", "file": "use-case-prompting-seminar/demo/poll.html", "type": "demo", "external": True},
                ]
            },
            "materials": {
                "title": "Course Materials",
                "items": [
                    {"id": "aiw-notes", "name": "Student Notes", "file": "ai-impact-work-seminar/student-notes.html", "type": "notes"},
                    {"id": "aiw-demo-guide", "name": "Instructor Demo Guide", "file": "ai-impact-work-seminar/interactive-demo-guide.html", "type": "notes"},
                    {"id": "aiw-exercise", "name": "Take-Home Exercise (PDF)", "file": "ai-impact-work-seminar/take-home-exercise.pdf", "type": "notes", "printable": True},
                ]
            }
        }
    },
    "ai-sales-marketing": {
        "id": "ai-sales-marketing",
        "name": "AI for Sales and Marketing",
        "description": "2-day practical course on AI applications for sales and marketing professionals - customer engagement, content generation, lead scoring, and campaign analytics",
        "icon": "📈",
        "duration": "2 days",
        "category": "ai-business",
        "syllabus": ["AI-Powered Content Generation", "The CRAFT Prompt Framework", "Lead Scoring with AI", "Campaign Analytics & Optimisation", "Customer Engagement & Personalisation", "A/B Testing with AI", "Prompt Library Templates", "Implementation Strategy"],
        "goals": ["Generate marketing content using AI tools and the CRAFT framework", "Build AI-driven lead scoring and customer segmentation models", "Analyse campaign performance with AI-powered analytics", "Create a practical AI implementation roadmap for your team"],
        "audience": "Sales and marketing professionals looking to leverage AI in their workflows",
        "prerequisites": "No technical background required; familiarity with marketing concepts helpful",
        "topic_descriptions": {
            "AI-Powered Content Generation": "Learn how to leverage AI tools to create compelling marketing content including blog posts, social media copy, email campaigns, and product descriptions. You will explore techniques for maintaining brand voice and quality while dramatically increasing content production speed.",
            "The CRAFT Prompt Framework": "Master the CRAFT prompt engineering framework, which stands for Context, Role, Action, Format, and Target. This structured approach to writing prompts ensures you consistently get high-quality, relevant outputs from any generative AI tool you use in your sales and marketing work.",
            "Lead Scoring with AI": "Discover how AI can transform lead scoring by analysing behavioural signals, demographic data, and engagement patterns to predict conversion likelihood. You will learn to build and refine AI-driven scoring models that help sales teams prioritise their efforts on the highest-value prospects.",
            "Campaign Analytics & Optimisation": "Explore how AI enhances campaign analytics by uncovering patterns, predicting performance, and recommending optimisations in real time. You will learn to use AI tools to analyse campaign data, identify underperforming segments, and make data-driven adjustments that improve ROI.",
            "Customer Engagement & Personalisation": "Understand how AI enables hyper-personalised customer experiences across channels by analysing preferences, behaviour, and context. You will learn strategies for implementing personalised recommendations, dynamic content, and tailored messaging that increase engagement and loyalty.",
            "A/B Testing with AI": "Learn how AI accelerates and improves A/B testing by automating hypothesis generation, optimising test design, and analysing results with greater statistical rigor. You will explore multi-armed bandit approaches and AI-driven experimentation platforms that reduce testing cycles and improve outcomes.",
            "Prompt Library Templates": "Build a reusable library of proven prompt templates tailored to common sales and marketing tasks such as outreach emails, ad copy, customer responses, and competitive analysis. You will learn how to organise, version, and continuously improve your prompt library for team-wide use.",
            "Implementation Strategy": "Develop a practical roadmap for integrating AI into your sales and marketing operations, covering tool selection, team training, workflow redesign, and success metrics. You will learn change management techniques and how to build a phased implementation plan that delivers quick wins while building toward long-term transformation.",
        },
        "sections": {
            "slides": {
                "title": "Course Slides",
                "items": [
                    {"id": "asm-slides", "name": "Presentation Slides", "file": "ai-sales-marketing/ai-sales-marketing-slides.html", "type": "slides"},
                    {"id": "asm-pdf", "name": "Slides (PDF Download)", "file": "ai-sales-marketing/ai-sales-marketing-slides.pdf", "type": "notes", "printable": True},
                ]
            },
            "materials": {
                "title": "Course Materials",
                "items": [
                    {"id": "asm-notes", "name": "Student Notes", "file": "ai-sales-marketing/student-notes.md", "type": "notes"},
                ]
            },
            "labs": {
                "title": "Hands-on Labs",
                "items": [
                    {"id": "asm-labs", "name": "Lab Exercises", "file": "ai-sales-marketing/labs/lab-exercises.md", "type": "lab"},
                ]
            },
            "templates": {
                "title": "Templates & Resources",
                "items": [
                    {"id": "asm-prompts", "name": "AI Prompt Library Template", "file": "ai-sales-marketing/templates/prompt-library-template.md", "type": "notes"},
                ]
            }
        }
    },
    "ai-ml-data-scientists": {
        "id": "ai-ml-data-scientists",
        "name": "AI/ML for Data Scientists",
        "description": "3-day comprehensive course on modern AI/ML approaches and deployment for data scientists and business analysts",
        "icon": "🧠",
        "duration": "3 days",
        "category": "ai-technical",
        "syllabus": ["ML Foundations & Model Selection", "Data Preprocessing & Feature Engineering", "Evaluation Metrics & Validation", "Deep Learning with CNNs & RNNs", "Transformers & Transfer Learning", "AutoML & Multimodal AI", "MLOps & Model Deployment", "Model Monitoring & Drift Detection", "Responsible AI & Explainability"],
        "goals": ["Apply modern ML techniques from preprocessing to production deployment", "Build deep learning models with PyTorch including CNNs and Transformers", "Implement MLOps best practices for model lifecycle management", "Evaluate models with appropriate metrics and ensure responsible AI practices"],
        "audience": "Data scientists and business analysts deepening their AI/ML expertise",
        "prerequisites": "Python programming experience and basic statistics/linear algebra",
        "topic_descriptions": {
            "ML Foundations & Model Selection": "Build a solid understanding of core machine learning paradigms including supervised, unsupervised, and reinforcement learning, along with the key algorithms in each category. You will learn systematic approaches to model selection, understanding when to apply linear models, tree-based methods, SVMs, or ensemble techniques based on your data and problem characteristics.",
            "Data Preprocessing & Feature Engineering": "Master the essential techniques for preparing raw data for machine learning, including handling missing values, encoding categorical variables, scaling, and normalisation. You will also learn feature engineering strategies such as polynomial features, interaction terms, and domain-driven transformations that can significantly boost model performance.",
            "Evaluation Metrics & Validation": "Learn how to rigorously evaluate model performance using appropriate metrics for classification, regression, and ranking tasks, including accuracy, precision, recall, F1, AUC-ROC, and RMSE. You will also master validation strategies such as k-fold cross-validation, stratified sampling, and proper train-validation-test splits to ensure your models generalise well.",
            "Deep Learning with CNNs & RNNs": "Explore the architectures and training procedures for convolutional neural networks and recurrent neural networks, understanding when and why each is suited to different data types. You will gain hands-on experience building CNNs for image tasks and RNNs for sequential data, learning about key concepts such as pooling, dropout, LSTM cells, and gradient flow.",
            "Transformers & Transfer Learning": "Dive into the transformer architecture that underpins modern AI breakthroughs, understanding self-attention mechanisms, positional encoding, and encoder-decoder structures. You will learn how to leverage transfer learning and pre-trained models to achieve strong performance on downstream tasks with limited data and compute.",
            "AutoML & Multimodal AI": "Discover how AutoML platforms automate the machine learning pipeline from feature engineering through hyperparameter tuning and model selection. You will also explore multimodal AI systems that can process and reason across text, images, audio, and structured data simultaneously.",
            "MLOps & Model Deployment": "Learn the principles and practices of MLOps for taking models from experimentation to production reliably and repeatably. Topics include containerisation, model serving APIs, CI/CD for ML, model registries, and infrastructure considerations for deploying models at scale.",
            "Model Monitoring & Drift Detection": "Understand how to monitor deployed models for performance degradation, data drift, and concept drift over time. You will learn to implement automated monitoring pipelines, set up alerting thresholds, and design retraining strategies that keep your models accurate and reliable in production.",
            "Responsible AI & Explainability": "Explore the principles and techniques for building AI systems that are transparent, fair, and accountable. You will learn to apply explainability methods such as SHAP, LIME, and feature importance analysis, and understand how to conduct fairness audits and document model behaviour for stakeholders.",
        },
        "sections": {
            "slides": {
                "title": "Course Slides",
                "items": [
                    {"id": "aiml-slides", "name": "Presentation Slides", "file": "ai-ml-data-scientists/ai-ml-data-scientists-slides.html", "type": "slides"},
                    {"id": "aiml-pdf", "name": "Slides (PDF Download)", "file": "ai-ml-data-scientists/ai-ml-data-scientists-slides.pdf", "type": "notes", "printable": True},
                ]
            },
            "materials": {
                "title": "Course Materials",
                "items": [
                    {"id": "aiml-notes", "name": "Student Notes", "file": "ai-ml-data-scientists/student-notes.md", "type": "notes"},
                ]
            },
            "labs": {
                "title": "Hands-on Labs",
                "items": [
                    {"id": "aiml-lab1", "name": "Lab 1: Data Preprocessing & Feature Engineering", "file": "ai-ml-data-scientists/labs/lab-01-data-preprocessing.ipynb", "type": "lab", "runnable": True},
                    {"id": "aiml-lab2", "name": "Lab 2: Deep Learning with PyTorch", "file": "ai-ml-data-scientists/labs/lab-02-deep-learning.ipynb", "type": "lab", "runnable": True},
                ]
            }
        }
    },
    "intro-data-science-engineering": {
        "id": "intro-data-science-engineering",
        "name": "Introduction to Data Science & Engineering",
        "description": "3-day course for IT professionals and developers transitioning into data roles, covering data science foundations, data engineering fundamentals, and end-to-end machine learning",
        "icon": "\ud83d\udcca",
        "duration": "3 days",
        "category": "ai-technical",
        "syllabus": ["Data Science Foundations", "Data Exploration & Visualisation", "Data Engineering Fundamentals", "Building Data Pipelines", "ETL Processes", "End-to-End ML Projects", "Model Training & Evaluation", "Data Wrangling with Pandas"],
        "goals": ["Explore and visualise datasets using Python data science libraries", "Build robust data pipelines for production data workflows", "Train and evaluate machine learning models end-to-end", "Transition confidently from IT/development into data roles"],
        "audience": "IT professionals and developers transitioning into data science or engineering roles",
        "prerequisites": "Basic Python programming and familiarity with SQL concepts",
        "topic_descriptions": {
            "Data Science Foundations": "Establish a solid understanding of the data science lifecycle, from problem formulation and data collection through analysis, modelling, and communication of results. You will learn the core statistical concepts, analytical thinking patterns, and tooling ecosystem that underpin effective data science practice.",
            "Data Exploration & Visualisation": "Learn systematic techniques for exploring datasets to uncover patterns, distributions, outliers, and relationships before building models. You will master visualisation libraries and best practices for creating clear, informative charts and dashboards that communicate insights effectively to both technical and non-technical audiences.",
            "Data Engineering Fundamentals": "Understand the role of data engineering in the modern data stack, including data storage architectures, databases, data warehouses, and data lakes. You will learn how data engineers ensure data is reliable, accessible, and properly structured to support analytics and machine learning workloads.",
            "Building Data Pipelines": "Learn how to design and implement robust data pipelines that move data from source systems through transformation stages to analytical destinations. You will explore pipeline orchestration tools, scheduling, error handling, and best practices for building pipelines that are maintainable and scalable.",
            "ETL Processes": "Master Extract, Transform, and Load processes that form the backbone of data integration in any organisation. You will learn practical techniques for extracting data from diverse sources, applying cleaning and transformation logic, and loading results into target systems while maintaining data quality and consistency.",
            "End-to-End ML Projects": "Walk through the complete lifecycle of a machine learning project, from business problem definition and data gathering through model development, evaluation, and deployment. You will learn project management techniques specific to ML, including experiment tracking, reproducibility practices, and stakeholder communication.",
            "Model Training & Evaluation": "Gain hands-on experience training machine learning models using popular frameworks, and learn how to evaluate their performance using appropriate metrics and validation strategies. You will understand overfitting, underfitting, hyperparameter tuning, and how to select the best model for your specific use case.",
            "Data Wrangling with Pandas": "Develop proficiency with the Pandas library for cleaning, reshaping, merging, and analysing structured data in Python. You will learn to handle real-world messy data using techniques such as filtering, grouping, pivoting, handling missing values, and working with time series data efficiently.",
        },
        "sections": {
            "slides": {
                "title": "Course Slides",
                "items": [
                    {"id": "idse-slides", "name": "Presentation Slides", "file": "intro-data-science-engineering/intro-data-science-engineering-slides.html", "type": "slides"},
                ]
            },
            "materials": {
                "title": "Course Materials",
                "items": [
                    {"id": "idse-notes", "name": "Student Notes", "file": "intro-data-science-engineering/student-notes.md", "type": "notes"},
                ]
            },
            "labs": {
                "title": "Hands-on Labs",
                "items": [
                    {"id": "idse-lab1", "name": "Lab 1: Data Exploration & Visualization", "file": "intro-data-science-engineering/labs/lab-01-data-exploration.ipynb", "type": "lab", "runnable": True},
                    {"id": "idse-lab1-sol", "name": "Lab 1: Data Exploration (Solutions)", "file": "intro-data-science-engineering/labs/lab-01-data-exploration-solution.ipynb", "type": "lab", "runnable": True},
                    {"id": "idse-lab2", "name": "Lab 2: Building a Data Pipeline", "file": "intro-data-science-engineering/labs/lab-02-data-pipeline.ipynb", "type": "lab", "runnable": True},
                    {"id": "idse-lab2-sol", "name": "Lab 2: Data Pipeline (Solutions)", "file": "intro-data-science-engineering/labs/lab-02-data-pipeline-solution.ipynb", "type": "lab", "runnable": True},
                    {"id": "idse-lab3", "name": "Lab 3: End-to-End ML Project", "file": "intro-data-science-engineering/labs/lab-03-ml-end-to-end.ipynb", "type": "lab", "runnable": True},
                    {"id": "idse-lab3-sol", "name": "Lab 3: ML Project (Solutions)", "file": "intro-data-science-engineering/labs/lab-03-ml-end-to-end-solution.ipynb", "type": "lab", "runnable": True},
                ]
            }
        }
    },
    "ai-data-discovery": {
        "id": "ai-data-discovery",
        "name": "Data Discovery: Harnessing AI, AGI & Vector Databases",
        "description": "2-day technical workshop on AI-powered data discovery, classification, vector databases, sensitive data detection, and compliance risk scoring",
        "icon": "\ud83d\udd0d",
        "duration": "2 days",
        "category": "ai-technical",
        "syllabus": ["Data Discovery Fundamentals", "AI-Driven Classification", "Vector Databases & Semantic Search", "Unsupervised Clustering", "Sensitive Data Detection", "Hybrid Regex + NER Detection", "Compliance Risk Scoring", "Data Governance & Ethics"],
        "goals": ["Build AI-powered data discovery pipelines using ML classification and vector search", "Detect sensitive data (PII, PHI, financial) with hybrid regex and NER techniques", "Compute automated compliance risk scores and build governance dashboards", "Deploy semantic search catalogues with ChromaDB and sentence transformers"],
        "audience": "Data engineers, data scientists, compliance professionals, and IT architects responsible for data governance",
        "prerequisites": "Basic Python programming and familiarity with pandas and scikit-learn",
        "topic_descriptions": {
            "Data Discovery Fundamentals": "Learn the core principles and methodologies behind data discovery, including how organizations catalog, profile, and understand their data assets. This topic covers the data discovery lifecycle from initial inventory through metadata enrichment, establishing the foundation for automated and AI-assisted approaches.",
            "AI-Driven Classification": "Explore how machine learning models can automatically classify and categorize data assets based on content, structure, and context. Students will learn to build and apply classification pipelines that label datasets by type, sensitivity, and business relevance with far greater speed and consistency than manual tagging.",
            "Vector Databases & Semantic Search": "Understand how vector embeddings represent data semantically and how vector databases such as Pinecone, Weaviate, and ChromaDB enable similarity-based retrieval. This topic covers indexing strategies, approximate nearest neighbor search, and how semantic search surfaces related data assets that keyword-based approaches would miss.",
            "Unsupervised Clustering": "Learn how unsupervised learning techniques such as K-Means, DBSCAN, and hierarchical clustering can reveal hidden groupings and patterns within large data repositories. Students will apply clustering algorithms to organize unstructured and semi-structured data into meaningful categories without the need for pre-labeled training data.",
            "Sensitive Data Detection": "Discover techniques for automatically identifying personally identifiable information (PII), protected health information (PHI), financial data, and other sensitive content across enterprise data stores. This topic covers pattern-based detection, contextual analysis, and strategies for scanning data at scale to reduce exposure risk.",
            "Hybrid Regex + NER Detection": "Master the combination of regular expression patterns and Named Entity Recognition (NER) models to build robust sensitive data detection pipelines. Students will learn how regex provides precision for structured patterns like credit card numbers, while NER models handle contextual entities such as names, addresses, and organizations.",
            "Compliance Risk Scoring": "Learn how to quantify and prioritize data compliance risks by building scoring models that assess sensitivity levels, access patterns, and regulatory exposure. This topic covers frameworks for mapping data assets to regulatory requirements such as GDPR, HIPAA, and PCI-DSS, enabling organizations to focus remediation efforts where risk is greatest.",
            "Data Governance & Ethics": "Examine the principles and frameworks that guide responsible data management, including data stewardship, lineage tracking, access controls, and ethical considerations in AI-driven discovery. Students will learn how to establish governance policies that balance data utility with privacy, fairness, and organizational accountability.",
        },
        "sections": {
            "slides": {
                "title": "Course Slides",
                "items": [
                    {"id": "add-slides", "name": "Presentation Slides", "file": "ai-data-discovery/ai-data-discovery-slides.html", "type": "slides"},
                ]
            },
            "materials": {
                "title": "Course Materials",
                "items": [
                    {"id": "add-notes", "name": "Student Notes", "file": "ai-data-discovery/student-notes.md", "type": "notes"},
                ]
            },
            "labs": {
                "title": "Hands-on Labs",
                "items": [
                    {"id": "add-lab1", "name": "Lab 1: Data Discovery & Classification", "file": "ai-data-discovery/labs/lab-01-data-discovery-classification.ipynb", "type": "lab", "runnable": True},
                    {"id": "add-lab1-sol", "name": "Lab 1: Data Discovery & Classification (Solutions)", "file": "ai-data-discovery/labs/lab-01-data-discovery-classification-solution.ipynb", "type": "lab", "runnable": True},
                    {"id": "add-lab2", "name": "Lab 2: Sensitive Data Detection", "file": "ai-data-discovery/labs/lab-02-sensitive-data-detection.ipynb", "type": "lab", "runnable": True},
                    {"id": "add-lab2-sol", "name": "Lab 2: Sensitive Data Detection (Solutions)", "file": "ai-data-discovery/labs/lab-02-sensitive-data-detection-solution.ipynb", "type": "lab", "runnable": True},
                    {"id": "add-lab3", "name": "Lab 3: Semantic Search & Data Catalogue RAG", "file": "ai-data-discovery/labs/lab-03-semantic-search-rag.ipynb", "type": "lab", "runnable": True},
                    {"id": "add-lab3-sol", "name": "Lab 3: Semantic Search & RAG (Solutions)", "file": "ai-data-discovery/labs/lab-03-semantic-search-rag-solution.ipynb", "type": "lab", "runnable": True},
                    {"id": "add-lab4", "name": "Lab 4: Data Governance & Policy Engine", "file": "ai-data-discovery/labs/lab-04-governance-policy-engine.ipynb", "type": "lab", "runnable": True},
                    {"id": "add-lab4-sol", "name": "Lab 4: Governance & Policy Engine (Solutions)", "file": "ai-data-discovery/labs/lab-04-governance-policy-engine-solution.ipynb", "type": "lab", "runnable": True},
                ]
            }
        }
    },
    "azure-ai-900": {
        "id": "azure-ai-900",
        "name": "Azure AI-900 Certification Prep",
        "description": "3-day certification prep course for Microsoft Azure AI Fundamentals (AI-900) exam",
        "icon": "🤖",
        "duration": "3 days",
        "category": "azure",
        "syllabus": ["AI Workloads & Considerations", "ML Principles on Azure", "Azure AI Services Overview", "Natural Language Processing", "Computer Vision", "Generative AI on Azure", "Responsible AI Principles", "Practice Exam Questions"],
        "goals": ["Understand core AI and ML concepts tested on the AI-900 exam", "Navigate Azure AI services: Cognitive Services, Bot Service, ML Studio", "Apply responsible AI principles in real-world scenarios", "Pass the Microsoft Azure AI Fundamentals (AI-900) certification"],
        "audience": "IT professionals preparing for the Azure AI-900 certification exam",
        "prerequisites": "Basic understanding of cloud computing concepts",
        "topic_descriptions": {
            "AI Workloads & Considerations": "Explore the common categories of AI workloads including prediction, anomaly detection, computer vision, natural language processing, and conversational AI. Students will learn how to identify appropriate AI solutions for different business scenarios and understand the key considerations for selecting and deploying AI workloads on Azure.",
            "ML Principles on Azure": "Learn the foundational concepts of machine learning including supervised, unsupervised, and reinforcement learning, and how these principles apply within the Azure ecosystem. This topic covers the end-to-end ML workflow from data preparation through model training, evaluation, and deployment using Azure Machine Learning.",
            "Azure AI Services Overview": "Survey the breadth of Azure's pre-built AI services including Azure OpenAI Service, Azure AI Search, and the Azure AI Studio platform. Students will understand how these managed services abstract away infrastructure complexity and enable rapid integration of AI capabilities into applications without deep ML expertise.",
            "Natural Language Processing": "Discover how Azure AI Language and related services enable text analytics, sentiment analysis, key phrase extraction, entity recognition, and language understanding. Students will learn to leverage these NLP capabilities to build solutions that extract insights from unstructured text and understand user intent.",
            "Computer Vision": "Learn how Azure AI Vision, Custom Vision, and Face API enable applications to analyze images and video, detect objects, read text via OCR, and identify visual patterns. This topic covers practical use cases from document processing to spatial analysis and the configuration of these services for production scenarios.",
            "Generative AI on Azure": "Understand the principles of generative AI and how Azure OpenAI Service provides access to large language models such as GPT-4 and DALL-E. Students will explore prompt engineering fundamentals, responsible deployment patterns, and how to integrate generative capabilities into applications using Azure's managed infrastructure.",
            "Responsible AI Principles": "Examine Microsoft's six responsible AI principles: fairness, reliability and safety, privacy and security, inclusiveness, transparency, and accountability. This topic covers how these principles translate into practical guidelines, tools, and organizational practices for building AI systems that are trustworthy and ethically sound.",
            "Practice Exam Questions": "Consolidate your learning through a comprehensive set of practice questions modeled on the AI-900 certification exam format. This topic provides targeted review across all exam domains, helping students identify knowledge gaps and build the confidence needed to pass the Azure AI Fundamentals certification.",
        },
        "sections": {
            "slides": {
                "title": "Course Slides",
                "items": [
                    {"id": "ai900-slides", "name": "Presentation Slides", "file": "azure-ai-900/azure-ai-900-slides.html", "type": "slides"},
                    {"id": "ai900-pdf", "name": "Slides (PDF Download)", "file": "azure-ai-900/azure-ai-900-slides.pdf", "type": "notes", "printable": True},
                ]
            },
            "materials": {
                "title": "Study Materials",
                "items": [
                    {"id": "ai900-notes", "name": "Student Notes", "file": "azure-ai-900/student-notes.md", "type": "notes"},
                ]
            },
            "practice": {
                "title": "Practice Tests",
                "items": [
                    {"id": "ai900-practice", "name": "Practice Questions", "file": "azure-ai-900/practice-tests/practice-questions.md", "type": "lab"},
                ]
            }
        }
    },
    "azure-az-900": {
        "id": "azure-az-900",
        "name": "Azure AZ-900 Certification Prep",
        "description": "3-day certification prep course for Microsoft Azure Fundamentals (AZ-900) exam",
        "icon": "☁️",
        "duration": "3 days",
        "category": "azure",
        "syllabus": ["Cloud Concepts & Models", "Azure Architecture & Services", "Compute & Networking", "Storage Solutions", "Identity & Access (Entra ID)", "Governance & Compliance", "Cost Management & SLAs", "Practice Exam Questions"],
        "goals": ["Describe cloud concepts including IaaS, PaaS, and SaaS models", "Navigate Azure architecture, regions, and availability zones", "Understand Azure identity, governance, and compliance tools", "Pass the Microsoft Azure Fundamentals (AZ-900) certification"],
        "audience": "IT professionals preparing for the Azure AZ-900 certification exam",
        "prerequisites": "No prior cloud experience required",
        "topic_descriptions": {
            "Cloud Concepts & Models": "Learn the fundamental concepts of cloud computing including the shared responsibility model, and the differences between IaaS, PaaS, and SaaS service models. This topic also covers public, private, and hybrid cloud deployment models, along with the core economic benefits of cloud adoption such as elasticity, scalability, and capital expenditure reduction.",
            "Azure Architecture & Services": "Explore Azure's global infrastructure including regions, availability zones, and resource groups that underpin service reliability and data residency. Students will learn how Azure organizes resources through subscriptions and management groups, and gain an understanding of the Azure Resource Manager (ARM) deployment model.",
            "Compute & Networking": "Understand Azure's core compute offerings including Virtual Machines, App Service, Azure Functions, and Azure Kubernetes Service, and when to use each. This topic also covers Azure networking fundamentals such as Virtual Networks, VPN Gateway, ExpressRoute, and DNS, providing the foundation for designing connected cloud solutions.",
            "Storage Solutions": "Learn about Azure's storage services including Blob Storage, File Storage, Queue Storage, and Table Storage, along with their respective access tiers and redundancy options. Students will understand how to select the appropriate storage solution based on performance, cost, durability, and data access pattern requirements.",
            "Identity & Access (Entra ID)": "Discover how Microsoft Entra ID (formerly Azure Active Directory) provides identity and access management for cloud resources. This topic covers authentication methods, single sign-on, multi-factor authentication, conditional access policies, and role-based access control (RBAC) for securing Azure environments.",
            "Governance & Compliance": "Learn how Azure Policy, Blueprints, Management Groups, and resource locks enable organizations to enforce standards and maintain regulatory compliance at scale. Students will understand how to implement governance strategies that ensure consistent resource configuration, cost control, and adherence to organizational and industry requirements.",
            "Cost Management & SLAs": "Understand Azure's pricing models, the factors that affect cost, and the tools available for estimating, monitoring, and optimizing cloud spending. This topic also covers Azure Service Level Agreements (SLAs), how composite SLAs are calculated, and strategies for designing solutions that meet availability and budget targets.",
            "Practice Exam Questions": "Reinforce your understanding through practice questions that mirror the AZ-900 certification exam in format and difficulty. This topic provides comprehensive review across all exam domains, enabling students to assess their readiness and focus study efforts on areas that need the most attention before the Azure Fundamentals exam.",
        },
        "sections": {
            "slides": {
                "title": "Course Slides",
                "items": [
                    {"id": "az900-slides", "name": "Presentation Slides", "file": "azure-az-900/azure-az-900-slides.html", "type": "slides"},
                    {"id": "az900-pdf", "name": "Slides (PDF Download)", "file": "azure-az-900/azure-az-900-slides.pdf", "type": "notes", "printable": True},
                ]
            },
            "materials": {
                "title": "Study Materials",
                "items": [
                    {"id": "az900-notes", "name": "Student Notes", "file": "azure-az-900/student-notes.md", "type": "notes"},
                ]
            },
            "practice": {
                "title": "Practice Tests",
                "items": [
                    {"id": "az900-practice", "name": "Practice Questions", "file": "azure-az-900/practice-tests/practice-questions.md", "type": "lab"},
                ]
            }
        }
    },
    "azure-sc-900": {
        "id": "azure-sc-900",
        "name": "Azure SC-900 Certification Prep",
        "description": "3-day certification prep course for Microsoft Security, Compliance, and Identity Fundamentals (SC-900) exam",
        "icon": "🛡️",
        "duration": "3 days",
        "category": "azure",
        "syllabus": ["Security Concepts & Zero Trust", "Microsoft Entra (Azure AD)", "Network & Endpoint Security", "Microsoft Defender XDR", "Microsoft Sentinel (SIEM)", "Microsoft Purview Compliance", "Information Protection & DLP", "Practice Exam Questions"],
        "goals": ["Describe security, compliance, and identity concepts including Zero Trust", "Navigate Microsoft Entra for identity and access management", "Understand Microsoft Defender XDR and Sentinel for threat protection", "Pass the Microsoft SC-900 certification exam"],
        "audience": "IT professionals preparing for the SC-900 security certification exam",
        "prerequisites": "Basic understanding of networking and cloud concepts",
        "topic_descriptions": {
            "Security Concepts & Zero Trust": "Learn the foundational security concepts including defense in depth, the CIA triad (confidentiality, integrity, availability), and the Zero Trust security model. Students will understand how the Zero Trust principles of verify explicitly, least privilege access, and assume breach reshape modern security architectures across cloud and hybrid environments.",
            "Microsoft Entra (Azure AD)": "Explore Microsoft Entra ID's identity services including user and group management, authentication methods, conditional access, and identity governance. This topic covers how Entra ID serves as the central identity provider for Microsoft cloud services and how features like Privileged Identity Management and Identity Protection mitigate identity-based threats.",
            "Network & Endpoint Security": "Understand how to protect network perimeters and endpoints using Azure Firewall, Network Security Groups, Azure DDoS Protection, and Microsoft Defender for Endpoint. Students will learn how these services work together to segment networks, filter traffic, detect intrusions, and secure devices across the organization.",
            "Microsoft Defender XDR": "Learn how Microsoft Defender XDR (Extended Detection and Response) unifies threat detection and response across endpoints, email, identity, and cloud applications. This topic covers how Defender for Office 365, Defender for Identity, and Defender for Cloud Apps correlate signals to provide automated investigation and coordinated incident response.",
            "Microsoft Sentinel (SIEM)": "Discover how Microsoft Sentinel provides cloud-native Security Information and Event Management (SIEM) and Security Orchestration, Automation, and Response (SOAR) capabilities. Students will learn how Sentinel collects data from diverse sources, uses analytics rules and machine learning to detect threats, and automates response through playbooks.",
            "Microsoft Purview Compliance": "Explore how Microsoft Purview provides a unified compliance platform for managing data governance, risk, and regulatory obligations. This topic covers Compliance Manager, compliance score calculation, and how organizations use Purview to assess their compliance posture against standards such as GDPR, ISO 27001, and NIST.",
            "Information Protection & DLP": "Learn how Microsoft Purview Information Protection and Data Loss Prevention (DLP) policies classify, label, and protect sensitive data across Microsoft 365 and beyond. Students will understand how sensitivity labels, encryption, and DLP rules work together to prevent unauthorized sharing and ensure data remains protected throughout its lifecycle.",
            "Practice Exam Questions": "Test your knowledge with practice questions aligned to the SC-900 certification exam objectives and format. This topic provides a structured review across security, compliance, and identity domains, helping students identify weak areas and build confidence for the Microsoft Security, Compliance, and Identity Fundamentals exam.",
        },
        "sections": {
            "slides": {
                "title": "Course Slides",
                "items": [
                    {"id": "sc900-slides", "name": "Presentation Slides", "file": "azure-sc-900/azure-sc-900-slides.html", "type": "slides"},
                    {"id": "sc900-pdf", "name": "Slides (PDF Download)", "file": "azure-sc-900/azure-sc-900-slides.pdf", "type": "notes", "printable": True},
                ]
            },
            "materials": {
                "title": "Study Materials",
                "items": [
                    {"id": "sc900-notes", "name": "Student Notes", "file": "azure-sc-900/student-notes.md", "type": "notes"},
                ]
            },
            "practice": {
                "title": "Practice Tests",
                "items": [
                    {"id": "sc900-practice", "name": "Practice Questions", "file": "azure-sc-900/practice-tests/practice-questions.md", "type": "lab"},
                ]
            }
        }
    },
    "llm-fine-tuning": {
        "id": "llm-fine-tuning",
        "name": "LLM Fine-Tuning",
        "description": "2-day technical workshop on customizing Large Language Models using LoRA, QLoRA, and PEFT methods",
        "icon": "🔧",
        "duration": "2 days",
        "category": "ai-technical",
        "syllabus": ["When to Fine-Tune vs Prompt", "LoRA & QLoRA Methods", "PEFT (Parameter-Efficient Fine-Tuning)", "Data Preparation & Formatting", "Hugging Face Ecosystem", "Hands-on Training with Mistral-7B", "Evaluation Metrics (BLEU, ROUGE)", "Adapter Merging & Deployment", "Cost Optimisation"],
        "goals": ["Decide when fine-tuning is the right approach vs prompting or RAG", "Fine-tune open-source LLMs using QLoRA and the Hugging Face stack", "Evaluate fine-tuned models with BLEU, ROUGE, and custom metrics", "Merge adapters and deploy fine-tuned models to production"],
        "audience": "ML engineers and developers customising LLMs for domain-specific tasks",
        "prerequisites": "Python programming, basic ML concepts, and familiarity with Hugging Face Transformers",
        "topic_descriptions": {
            "When to Fine-Tune vs Prompt": "Understand the decision framework for choosing between prompt engineering, retrieval-augmented generation, and fine-tuning based on your use case, data availability, and performance requirements. Students will learn to evaluate trade-offs in cost, latency, control, and accuracy to determine when fine-tuning provides genuine value over simpler alternatives.",
            "LoRA & QLoRA Methods": "Learn how Low-Rank Adaptation (LoRA) enables efficient fine-tuning by injecting trainable low-rank matrices into frozen model layers, dramatically reducing memory and compute requirements. This topic also covers QLoRA, which combines 4-bit quantization with LoRA to make fine-tuning of large models feasible on consumer-grade GPUs.",
            "PEFT (Parameter-Efficient Fine-Tuning)": "Explore the broader landscape of parameter-efficient fine-tuning methods including prefix tuning, prompt tuning, and adapter layers alongside LoRA. Students will learn how PEFT techniques modify only a small fraction of model parameters while achieving performance comparable to full fine-tuning.",
            "Data Preparation & Formatting": "Master the critical steps of curating, cleaning, and formatting training data for instruction fine-tuning of large language models. This topic covers dataset construction best practices, chat template formats such as Alpaca and ChatML, quality filtering strategies, and how data composition and volume directly impact fine-tuned model behavior.",
            "Hugging Face Ecosystem": "Navigate the Hugging Face ecosystem including the Transformers library, Model Hub, Datasets library, and the TRL training framework. Students will gain practical fluency with the tools and workflows that have become the industry standard for accessing, fine-tuning, and sharing open-source language models.",
            "Hands-on Training with Mistral-7B": "Apply fine-tuning techniques in a guided hands-on lab using the Mistral-7B model as the base for QLoRA instruction tuning. Students will configure training hyperparameters, manage GPU memory, monitor training metrics, and iteratively refine their approach to produce a fine-tuned model tailored to a specific task.",
            "Evaluation Metrics (BLEU, ROUGE)": "Learn how to rigorously evaluate fine-tuned language models using automated metrics including BLEU, ROUGE, perplexity, and task-specific benchmarks. This topic covers the strengths and limitations of each metric, how to design evaluation datasets, and how to combine quantitative scores with qualitative human evaluation for a complete assessment.",
            "Adapter Merging & Deployment": "Understand how to merge trained LoRA adapters back into the base model to create standalone deployable models, and explore serving options. Students will learn merging strategies, model quantization for efficient inference, and deployment approaches using frameworks such as vLLM, text-generation-inference, and Ollama for production use.",
            "Cost Optimisation": "Explore strategies for minimizing the compute, storage, and operational costs of fine-tuning and deploying large language models. This topic covers GPU selection and cloud instance sizing, training efficiency techniques such as gradient checkpointing and mixed precision, and inference optimization methods that reduce serving costs without sacrificing quality.",
        },
        "sections": {
            "slides": {
                "title": "Course Slides",
                "items": [
                    {"id": "ft-slides", "name": "Presentation Slides", "file": "llm-fine-tuning/llm-fine-tuning-slides.html", "type": "slides"},
                    {"id": "ft-pdf", "name": "Slides (PDF Download)", "file": "llm-fine-tuning/llm-fine-tuning-slides.pdf", "type": "notes", "printable": True},
                ]
            },
            "materials": {
                "title": "Course Materials",
                "items": [
                    {"id": "ft-notes", "name": "Student Notes", "file": "llm-fine-tuning/student-notes.md", "type": "notes"},
                ]
            },
            "labs": {
                "title": "Hands-on Labs",
                "items": [
                    {"id": "ft-lab1", "name": "Lab 1: QLoRA Fine-Tuning", "file": "llm-fine-tuning/labs/lab1-qlora-finetuning.ipynb", "type": "lab", "runnable": True},
                    {"id": "ft-lab2", "name": "Lab 2: Evaluation & Deployment", "file": "llm-fine-tuning/labs/lab2-evaluation-deployment.ipynb", "type": "lab", "runnable": True},
                ]
            }
        }
    }
}

# ============================================================================
# Authentication Routes
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()

    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()

    if not all([username, email, password]):
        return jsonify({'error': 'Username, email, and password are required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    db = get_db()
    try:
        # Create user
        db.execute(
            'INSERT INTO users (username, email, password_hash, full_name) VALUES (?, ?, ?, ?)',
            (username, email, generate_password_hash(password), full_name)
        )
        db.commit()

        # Get the new user
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        # Create user workspace
        user_workspace = os.path.join(WORKSPACES_DIR, str(user['id']))
        os.makedirs(user_workspace, exist_ok=True)

        # Set session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']

        return jsonify({
            'message': 'Registration successful',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'role': user['role']
            }
        })
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username or email already exists'}), 409
    finally:
        db.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()

    username = data.get('username', '').strip()
    password = data.get('password', '')

    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE username = ? OR email = ?',
        (username, username)
    ).fetchone()
    db.close()

    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']

        # Update last login
        db = get_db()
        db.execute('UPDATE users SET last_login = ? WHERE id = ?',
                   (datetime.now(), user['id']))
        db.commit()
        db.close()

        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'role': user['role']
            }
        })

    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/auth/me')
def get_current_user():
    """Get current logged in user"""
    if 'user_id' not in session:
        return jsonify({'user': None})

    db = get_db()
    user = db.execute('SELECT id, username, email, full_name, role FROM users WHERE id = ?',
                      (session['user_id'],)).fetchone()
    db.close()

    if user:
        return jsonify({
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'role': user['role']
            }
        })

    session.clear()
    return jsonify({'user': None})

# ============================================================================
# Course Routes
# ============================================================================

@app.route('/api/courses')
def get_courses():
    """Return list of all available courses with category info"""
    course_list = []
    for course_id, course in COURSES.items():
        course_list.append({
            "id": course["id"],
            "name": course["name"],
            "description": course["description"],
            "icon": course["icon"],
            "category": course.get("category", "other"),
            "duration": course.get("duration", "")
        })
    return jsonify(course_list)

@app.route('/api/categories')
def get_categories():
    """Return list of all course categories with their courses"""
    # Sort categories by order
    sorted_categories = sorted(COURSE_CATEGORIES.values(), key=lambda x: x.get("order", 99))

    result = []
    for category in sorted_categories:
        cat_id = category["id"]
        # Get courses in this category
        category_courses = []
        for course_id, course in COURSES.items():
            if course.get("category") == cat_id:
                category_courses.append({
                    "id": course["id"],
                    "name": course["name"],
                    "description": course["description"],
                    "icon": course["icon"],
                    "duration": course.get("duration", "")
                })

        if category_courses:  # Only include categories with courses
            result.append({
                "id": cat_id,
                "name": category["name"],
                "icon": category["icon"],
                "description": category["description"],
                "courses": category_courses
            })

    return jsonify(result)

@app.route('/api/course/<course_id>')
def get_course(course_id):
    """Return details for a specific course"""
    if course_id in COURSES:
        return jsonify(COURSES[course_id])
    return jsonify({"error": "Course not found"}), 404

@app.route('/api/course/<course_id>/materials')
@login_required
def get_course_materials(course_id):
    """Return materials for a specific course"""
    if course_id in COURSES:
        return jsonify(COURSES[course_id]["sections"])
    return jsonify({"error": "Course not found"}), 404

@app.route('/api/course/<course_id>/enroll', methods=['POST'])
@login_required
def enroll_course(course_id):
    """Enroll current user in a course"""
    if course_id not in COURSES:
        return jsonify({"error": "Course not found"}), 404

    db = get_db()
    try:
        db.execute(
            'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
            (session['user_id'], course_id)
        )
        db.commit()
        return jsonify({"message": "Enrolled successfully"})
    except sqlite3.IntegrityError:
        return jsonify({"message": "Already enrolled"})
    finally:
        db.close()

@app.route('/api/my/enrollments')
@login_required
def get_my_enrollments():
    """Get current user's enrollments"""
    db = get_db()
    enrollments = db.execute(
        'SELECT course_id, enrolled_at, progress FROM enrollments WHERE user_id = ?',
        (session['user_id'],)
    ).fetchall()
    db.close()

    result = []
    for e in enrollments:
        if e['course_id'] in COURSES:
            result.append({
                'course': COURSES[e['course_id']],
                'enrolled_at': e['enrolled_at'],
                'progress': json.loads(e['progress']) if e['progress'] else {}
            })

    return jsonify(result)

@app.route('/api/course/<course_id>/download')
@login_required
def download_course_materials(course_id):
    """Download all course materials as a zip file (sandboxed)"""
    # Validate course_id format
    import re
    if not re.match(r'^[\w\-]+$', course_id):
        return jsonify({"error": "Invalid course ID"}), 400

    if course_id not in COURSES:
        return jsonify({"error": "Course not found"}), 404

    course = COURSES[course_id]

    # Create zip file in memory
    zip_buffer = io.BytesIO()

    # Limit zip size (max 100MB)
    max_zip_size = 100 * 1024 * 1024
    total_size = 0

    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            files_added = set()

            for section_id, section in course['sections'].items():
                for item in section['items']:
                    file_path = item['file']
                    item_type = item.get('type', '')

                    # For slides, use PDF version instead of HTML source
                    if item_type == 'slides' and file_path.endswith('.html'):
                        pdf_path = file_path.replace('.html', '.pdf')
                        try:
                            safe_pdf_path = get_safe_path_in_materials(pdf_path)
                            if os.path.isfile(safe_pdf_path):
                                # Use PDF instead of HTML for slides
                                if pdf_path not in files_added:
                                    file_size = os.path.getsize(safe_pdf_path)
                                    total_size += file_size
                                    if total_size > max_zip_size:
                                        return jsonify({"error": "Download too large"}), 413
                                    zip_file.write(safe_pdf_path, pdf_path)
                                    files_added.add(pdf_path)
                                continue  # Skip the HTML source file
                        except SandboxError:
                            pass  # Fall through to try original file

                    # Skip if already added
                    if file_path in files_added:
                        continue

                    try:
                        # Get safe path within materials
                        safe_path = get_safe_path_in_materials(file_path)

                        if os.path.isfile(safe_path):
                            # Check file size
                            file_size = os.path.getsize(safe_path)
                            total_size += file_size
                            if total_size > max_zip_size:
                                return jsonify({"error": "Download too large"}), 413

                            # Add individual file
                            zip_file.write(safe_path, file_path)
                            files_added.add(file_path)

                    except SandboxError:
                        # Skip files that fail validation
                        continue

        zip_buffer.seek(0)

        # Create safe filename
        safe_name = re.sub(r'[^\w\-]', '-', course_id).lower()
        filename = f"{safe_name}-materials.zip"

        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({"error": "Failed to create download"}), 500

# ============================================================================
# Lab Routes - Jupyter Integration
# ============================================================================

@app.route('/api/lab/<lab_id>/start', methods=['POST'])
@login_required
def start_lab(lab_id):
    """Start a lab session for the current user (sandboxed)"""
    try:
        # Validate lab_id to prevent injection
        validate_lab_id(lab_id)
    except SandboxError as e:
        return jsonify({'error': f'Invalid lab ID: {str(e)}'}), 400

    # Find the lab in courses (only allow labs defined in config)
    lab_info = None
    for course in COURSES.values():
        for section in course['sections'].values():
            for item in section['items']:
                if item['id'] == lab_id and item.get('runnable'):
                    lab_info = item
                    break

    if not lab_info:
        return jsonify({'error': 'Lab not found or not runnable'}), 404

    try:
        user_id = session['user_id']

        # Get sandboxed user workspace
        user_workspace = get_safe_user_workspace(user_id)

        # Get safe paths for source and destination
        source_notebook = get_safe_path_in_materials(lab_info['file'])
        user_notebook = get_safe_path_in_workspace(user_workspace, lab_info['file'])

        # Copy notebook to user workspace if not exists
        if not os.path.exists(user_notebook) and os.path.exists(source_notebook):
            # Ensure parent directory exists (for paths like out/lab-01.ipynb)
            notebook_dir = os.path.dirname(user_notebook)
            if notebook_dir:
                os.makedirs(notebook_dir, exist_ok=True)
            safe_copy_file(source_notebook, user_notebook)

        # Record lab session (store relative path, not absolute)
        db = get_db()
        db.execute(
            'INSERT INTO lab_sessions (user_id, lab_id, notebook_path, last_activity) VALUES (?, ?, ?, ?)',
            (user_id, lab_id, lab_info['file'], datetime.now())  # Store relative path
        )
        db.commit()
        session_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        db.close()

        return jsonify({
            'session_id': session_id,
            'lab_id': lab_id,
            'notebook_path': f'/api/lab/{lab_id}/notebook',
            'message': 'Lab session started'
        })

    except SandboxError as e:
        return jsonify({'error': f'Security error: {str(e)}'}), 403

@app.route('/api/lab/<lab_id>/notebook')
@login_required
def get_lab_notebook(lab_id):
    """Get the notebook content for a lab (sandboxed)"""
    try:
        # Validate lab_id
        validate_lab_id(lab_id)
    except SandboxError as e:
        return jsonify({'error': f'Invalid lab ID: {str(e)}'}), 400

    # Find lab file (only allow labs defined in config)
    lab_file = None
    for course in COURSES.values():
        for section in course['sections'].values():
            for item in section['items']:
                if item['id'] == lab_id:
                    lab_file = item['file']
                    break

    if not lab_file:
        return jsonify({'error': 'Lab not found'}), 404

    try:
        user_id = session['user_id']

        # Get sandboxed user workspace
        user_workspace = get_safe_user_workspace(user_id)

        # Try user workspace first (sandboxed path)
        try:
            notebook_path = get_safe_path_in_workspace(user_workspace, lab_file)
            if not os.path.exists(notebook_path):
                raise FileNotFoundError()
        except (SandboxError, FileNotFoundError):
            # Fall back to materials dir (sandboxed path)
            notebook_path = get_safe_path_in_materials(lab_file)

        if not os.path.exists(notebook_path):
            return jsonify({'error': 'Notebook file not found'}), 404

        # Read with size limit (max 10MB)
        file_size = os.path.getsize(notebook_path)
        if file_size > 10 * 1024 * 1024:
            return jsonify({'error': 'Notebook file too large'}), 413

        with open(notebook_path, 'r') as f:
            notebook = json.load(f)

        return jsonify(notebook)

    except SandboxError as e:
        return jsonify({'error': f'Security error: {str(e)}'}), 403

@app.route('/api/lab/<lab_id>/save', methods=['POST'])
@login_required
def save_lab_notebook(lab_id):
    """Save the notebook content for a lab (sandboxed)"""
    try:
        # Validate lab_id
        validate_lab_id(lab_id)
    except SandboxError as e:
        return jsonify({'error': f'Invalid lab ID: {str(e)}'}), 400

    # Find lab file (only allow labs defined in config)
    lab_file = None
    for course in COURSES.values():
        for section in course['sections'].values():
            for item in section['items']:
                if item['id'] == lab_id:
                    lab_file = item['file']
                    break

    if not lab_file:
        return jsonify({'error': 'Lab not found'}), 404

    try:
        user_id = session['user_id']

        # Get sandboxed user workspace
        user_workspace = get_safe_user_workspace(user_id)

        # Get safe path for the notebook (within user's sandbox)
        notebook_path = get_safe_path_in_workspace(user_workspace, lab_file)

        # Ensure parent directory exists
        notebook_dir = os.path.dirname(notebook_path)
        if notebook_dir:
            os.makedirs(notebook_dir, exist_ok=True)

        # Get and validate notebook data
        notebook_data = request.get_json()
        if not notebook_data:
            return jsonify({'error': 'No notebook data provided'}), 400

        # Validate it's a proper notebook structure
        if not isinstance(notebook_data, dict):
            return jsonify({'error': 'Invalid notebook format'}), 400

        # Check size limit (max 10MB when serialized)
        notebook_json = json.dumps(notebook_data, indent=2)
        if len(notebook_json) > 10 * 1024 * 1024:
            return jsonify({'error': 'Notebook too large to save'}), 413

        # Write atomically using temp file
        temp_path = notebook_path + '.tmp'
        with open(temp_path, 'w') as f:
            f.write(notebook_json)

        # Atomic rename
        os.replace(temp_path, notebook_path)

        return jsonify({'message': 'Notebook saved successfully'})

    except SandboxError as e:
        return jsonify({'error': f'Security error: {str(e)}'}), 403

@app.route('/api/lab/<lab_id>/progress', methods=['GET', 'POST'])
@login_required
def lab_progress(lab_id):
    """Get or save progress for a lab (with input validation)"""
    try:
        # Validate lab_id
        validate_lab_id(lab_id)
    except SandboxError as e:
        return jsonify({'error': f'Invalid lab ID: {str(e)}'}), 400

    if request.method == 'POST':
        data = request.get_json()
        cell_index = data.get('cell_index')
        output = data.get('output', '')

        # Validate cell_index
        if not isinstance(cell_index, int) or cell_index < 0 or cell_index > 1000:
            return jsonify({'error': 'Invalid cell index'}), 400

        # Limit output size (max 1MB)
        output_json = json.dumps(output)
        if len(output_json) > 1024 * 1024:
            return jsonify({'error': 'Output too large'}), 413

        db = get_db()
        db.execute(
            'INSERT INTO lab_progress (user_id, lab_id, cell_index, output) VALUES (?, ?, ?, ?)',
            (session['user_id'], lab_id, cell_index, output_json)
        )
        db.commit()
        db.close()

        return jsonify({'message': 'Progress saved'})
    else:
        db = get_db()
        progress = db.execute(
            '''SELECT cell_index, output, completed_at FROM lab_progress
               WHERE user_id = ? AND lab_id = ? ORDER BY cell_index''',
            (session['user_id'], lab_id)
        ).fetchall()
        db.close()

        return jsonify([{
            'cell_index': p['cell_index'],
            'output': json.loads(p['output']) if p['output'] else None,
            'completed_at': p['completed_at']
        } for p in progress])

# ============================================================================
# Server-Side Kernel API (for PyTorch and other libraries not in Pyodide)
# ============================================================================

@app.route('/api/kernel/start', methods=['POST'])
@login_required
def start_kernel():
    """Start or get a kernel for a lab"""
    data = request.get_json() or {}
    lab_id = data.get('lab_id')

    if not lab_id:
        return jsonify({'error': 'lab_id required'}), 400

    try:
        validate_lab_id(lab_id)
    except SandboxError as e:
        return jsonify({'error': f'Invalid lab ID: {str(e)}'}), 400

    result = kernel_pool.get_or_create_kernel(session['user_id'], lab_id)

    if result['status'] == 'error':
        return jsonify({'error': result['message']}), 503

    return jsonify(result)

@app.route('/api/kernel/execute', methods=['POST'])
@login_required
def execute_code():
    """Execute code in the user's kernel"""
    data = request.get_json() or {}
    lab_id = data.get('lab_id')
    code = data.get('code', '')

    if not lab_id:
        return jsonify({'error': 'lab_id required'}), 400

    if not code.strip():
        return jsonify({'status': 'ok', 'outputs': [], 'execution_count': 0})

    try:
        validate_lab_id(lab_id)
    except SandboxError as e:
        return jsonify({'error': f'Invalid lab ID: {str(e)}'}), 400

    # Limit code size (max 100KB)
    if len(code) > 100 * 1024:
        return jsonify({'error': 'Code too large'}), 413

    result = kernel_pool.execute_code(session['user_id'], lab_id, code)
    return jsonify(result)

@app.route('/api/kernel/interrupt', methods=['POST'])
@login_required
def interrupt_kernel():
    """Interrupt a running kernel"""
    data = request.get_json() or {}
    lab_id = data.get('lab_id')

    if not lab_id:
        return jsonify({'error': 'lab_id required'}), 400

    result = kernel_pool.interrupt_kernel(session['user_id'], lab_id)
    return jsonify(result)

@app.route('/api/kernel/restart', methods=['POST'])
@login_required
def restart_kernel():
    """Restart a kernel"""
    data = request.get_json() or {}
    lab_id = data.get('lab_id')

    if not lab_id:
        return jsonify({'error': 'lab_id required'}), 400

    result = kernel_pool.restart_kernel(session['user_id'], lab_id)
    return jsonify(result)

@app.route('/api/kernel/stop', methods=['POST'])
@login_required
def stop_kernel():
    """Stop a kernel"""
    data = request.get_json() or {}
    lab_id = data.get('lab_id')

    if not lab_id:
        return jsonify({'error': 'lab_id required'}), 400

    result = kernel_pool.shutdown_kernel(session['user_id'], lab_id)
    return jsonify(result)

@app.route('/api/kernel/status')
@login_required
def kernel_status():
    """Get kernel status for a lab"""
    lab_id = request.args.get('lab_id')

    if not lab_id:
        return jsonify({'error': 'lab_id required'}), 400

    result = kernel_pool.get_kernel_info(session['user_id'], lab_id)
    return jsonify(result)

# ============================================================================
# OpenAI API Proxy (for demo)
# ============================================================================

@app.route('/api/openai/chat', methods=['POST'])
def openai_proxy():
    """Proxy requests to OpenAI API to avoid browser CORS/network issues"""
    import urllib.request
    import urllib.error

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    api_key = data.get('api_key')
    if not api_key:
        return jsonify({'error': 'No API key provided'}), 400

    # Build the OpenAI request
    openai_payload = {
        'model': data.get('model', 'gpt-4o'),
        'messages': data.get('messages', []),
        'temperature': data.get('temperature', 0.7),
        'max_tokens': data.get('max_tokens', 500)
    }

    try:
        req = urllib.request.Request(
            'https://api.openai.com/v1/chat/completions',
            data=json.dumps(openai_payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        )

        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            return jsonify(result)

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            error_json = json.loads(error_body)
            return jsonify(error_json), e.code
        except:
            return jsonify({'error': {'message': error_body}}), e.code
    except urllib.error.URLError as e:
        return jsonify({'error': {'message': f'Network error: {str(e)}'}}), 500
    except Exception as e:
        return jsonify({'error': {'message': str(e)}}), 500


@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Generate a report/proposal using AI based on the WRITE framework prompt"""
    import urllib.request
    import urllib.error

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    model = data.get('model', 'gpt-5.2')
    doc_type = data.get('doc_type', 'proposal')

    # Check for API key in environment or request
    api_key = os.environ.get('OPENAI_API_KEY') or data.get('api_key')
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY') or data.get('anthropic_key')

    # Determine which API to use based on model selection
    if model.startswith('claude') and anthropic_key:
        # Use Anthropic API
        return _generate_with_anthropic(prompt, model, anthropic_key, doc_type)
    elif api_key:
        # Use OpenAI API
        return _generate_with_openai(prompt, model, api_key, doc_type)
    else:
        return jsonify({'error': 'No API key configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable, or provide api_key in the request.'}), 400


def _generate_with_openai(prompt, model, api_key, doc_type):
    """Generate report using OpenAI API"""
    import urllib.request
    import urllib.error

    selected_model = model if model in ['gpt-5.2', 'gpt-4', 'gpt-3.5-turbo', 'gpt-4o'] else 'gpt-5.2'

    openai_payload = {
        'model': selected_model,
        'messages': [
            {
                'role': 'system',
                'content': f'You are an expert {doc_type} writer. Generate professional, well-structured documents based on the provided requirements.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'temperature': 0.7
    }

    # GPT-5.2 uses max_completion_tokens, older models use max_tokens
    if selected_model == 'gpt-5.2':
        openai_payload['max_completion_tokens'] = 4000
    else:
        openai_payload['max_tokens'] = 4000

    try:
        req = urllib.request.Request(
            'https://api.openai.com/v1/chat/completions',
            data=json.dumps(openai_payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        )

        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            return jsonify({
                'report': content,
                'model': model,
                'doc_type': doc_type
            })

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            error_json = json.loads(error_body)
            return jsonify({'error': error_json.get('error', {}).get('message', 'API error')}), e.code
        except:
            return jsonify({'error': error_body}), e.code
    except urllib.error.URLError as e:
        return jsonify({'error': f'Network error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _generate_with_anthropic(prompt, model, api_key, doc_type):
    """Generate report using Anthropic API"""
    import urllib.request
    import urllib.error

    # Map model names to Anthropic model IDs
    model_map = {
        'claude-3': 'claude-3-sonnet-20240229',
        'claude-2': 'claude-2.1',
        'claude-3-opus': 'claude-3-opus-20240229',
        'claude-3-sonnet': 'claude-3-sonnet-20240229',
        'claude-3-haiku': 'claude-3-haiku-20240307'
    }

    anthropic_model = model_map.get(model, 'claude-3-sonnet-20240229')

    anthropic_payload = {
        'model': anthropic_model,
        'max_tokens': 4000,
        'messages': [
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'system': f'You are an expert {doc_type} writer. Generate professional, well-structured documents based on the provided requirements.'
    }

    try:
        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=json.dumps(anthropic_payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01'
            }
        )

        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result.get('content', [{}])[0].get('text', '')
            return jsonify({
                'report': content,
                'model': model,
                'doc_type': doc_type
            })

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            error_json = json.loads(error_body)
            return jsonify({'error': error_json.get('error', {}).get('message', 'API error')}), e.code
        except:
            return jsonify({'error': error_body}), e.code
    except urllib.error.URLError as e:
        return jsonify({'error': f'Network error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Content Serving (Sandboxed)
# ============================================================================

@app.route('/api/materials')
def get_materials():
    """Return list of all course materials (legacy)"""
    return jsonify(COURSES["mastering-ai"]["sections"])

@app.route('/content/<path:filename>')
@login_required
def serve_content(filename):
    """Serve course HTML files (sandboxed to materials directory)"""
    try:
        # Validate and resolve path within materials directory
        safe_path = get_safe_path_in_materials(filename)

        # If it's a directory, try to serve index.html from it
        if os.path.isdir(safe_path):
            index_path = os.path.join(safe_path, 'index.html')
            if os.path.isfile(index_path):
                safe_path = index_path
            else:
                return jsonify({'error': 'Directory listing not available. Please specify a file.'}), 404

        # Only serve allowed file types
        allowed_extensions = {'.html', '.css', '.js', '.png', '.jpg', '.jpeg',
                             '.gif', '.svg', '.ico', '.pdf', '.ipynb', '.json', '.md', '.csv',
                             '.mp4', '.webm', '.ogg', '.mp3', '.wav'}
        _, ext = os.path.splitext(safe_path)
        if ext.lower() not in allowed_extensions:
            return jsonify({'error': 'File type not allowed'}), 403

        if not os.path.isfile(safe_path):
            return jsonify({'error': 'File not found'}), 404

        # Get the relative path from materials dir
        rel_path = os.path.relpath(safe_path, MATERIALS_DIR)
        response = send_from_directory(MATERIALS_DIR, rel_path)
        # Disable caching for HTML files during development
        if ext.lower() == '.html':
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

    except SandboxError as e:
        return jsonify({'error': f'Access denied: {str(e)}'}), 403

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve React frontend"""
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    response = send_from_directory(app.static_folder, 'index.html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# ============================================================================
# Admin Routes
# ============================================================================

@app.route('/api/admin/users')
@instructor_required
def get_all_users():
    """Get all users (instructor only)"""
    db = get_db()
    users = db.execute(
        'SELECT id, username, email, full_name, role, created_at, last_login FROM users'
    ).fetchall()
    db.close()

    return jsonify([dict(u) for u in users])

@app.route('/api/admin/user/<int:user_id>/progress')
@instructor_required
def get_user_progress(user_id):
    """Get a specific user's progress (instructor only)"""
    db = get_db()

    enrollments = db.execute(
        'SELECT course_id, enrolled_at, progress FROM enrollments WHERE user_id = ?',
        (user_id,)
    ).fetchall()

    lab_progress = db.execute(
        '''SELECT lab_id, COUNT(*) as cells_completed, MAX(completed_at) as last_activity
           FROM lab_progress WHERE user_id = ? GROUP BY lab_id''',
        (user_id,)
    ).fetchall()

    db.close()

    return jsonify({
        'enrollments': [dict(e) for e in enrollments],
        'lab_progress': [dict(p) for p in lab_progress]
    })

# ============================================================================
# Poll Routes
# ============================================================================

@app.route('/api/poll/<poll_id>/submit', methods=['POST'])
def submit_poll_response(poll_id):
    """Submit a poll response (no auth required for anonymous polls)"""
    import re
    if not re.match(r'^[\w\-]+$', poll_id):
        return jsonify({'error': 'Invalid poll ID'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    session_id = data.get('session_id', '')
    technical_level = data.get('technical_level', '')
    use_cases = data.get('use_cases', [])
    ai_tools = data.get('ai_tools', [])

    # Validate technical_level (allow "other" or "other: text")
    valid_levels = ['none', 'beginner', 'intermediate', 'advanced', 'expert']
    if technical_level not in valid_levels and not technical_level.startswith('other'):
        return jsonify({'error': 'Invalid technical level'}), 400
    # Limit length of "other" text
    if len(technical_level) > 200:
        technical_level = technical_level[:200]

    # Validate use_cases (list of strings)
    if not isinstance(use_cases, list):
        return jsonify({'error': 'use_cases must be a list'}), 400
    use_cases_str = ','.join([str(u)[:50] for u in use_cases[:20]])  # Limit

    # Validate ai_tools (list of strings)
    if not isinstance(ai_tools, list):
        return jsonify({'error': 'ai_tools must be a list'}), 400
    ai_tools_str = ','.join([str(t)[:50] for t in ai_tools[:20]])  # Limit

    db = get_db()
    db.execute(
        '''INSERT INTO poll_responses (session_id, poll_id, technical_level, use_cases, ai_tools_used)
           VALUES (?, ?, ?, ?, ?)''',
        (session_id, poll_id, technical_level, use_cases_str, ai_tools_str)
    )
    db.commit()
    db.close()

    return jsonify({'message': 'Response submitted successfully'})

@app.route('/api/poll/<poll_id>/results')
def get_poll_results(poll_id):
    """Get aggregated poll results"""
    import re
    if not re.match(r'^[\w\-]+$', poll_id):
        return jsonify({'error': 'Invalid poll ID'}), 400

    db = get_db()
    responses = db.execute(
        'SELECT * FROM poll_responses WHERE poll_id = ? ORDER BY submitted_at DESC',
        (poll_id,)
    ).fetchall()
    db.close()

    # Aggregate results
    technical_counts = {'none': 0, 'beginner': 0, 'intermediate': 0, 'advanced': 0, 'expert': 0}
    use_case_counts = {}
    tool_counts = {}
    total = len(responses)

    for r in responses:
        level = r['technical_level']
        if level in technical_counts:
            technical_counts[level] += 1

        # Aggregate use cases
        use_cases = r['use_cases'].split(',') if r.get('use_cases') else []
        for use_case in use_cases:
            use_case = use_case.strip()
            if use_case:
                use_case_counts[use_case] = use_case_counts.get(use_case, 0) + 1

        tools = r['ai_tools_used'].split(',') if r['ai_tools_used'] else []
        for tool in tools:
            tool = tool.strip()
            if tool:
                tool_counts[tool] = tool_counts.get(tool, 0) + 1

    return jsonify({
        'total_responses': total,
        'technical_levels': technical_counts,
        'use_cases': use_case_counts,
        'ai_tools': tool_counts,
        'responses': [dict(r) for r in responses]  # Individual responses for review
    })

@app.route('/api/poll/<poll_id>/clear', methods=['POST'])
@instructor_required
def clear_poll_responses(poll_id):
    """Clear all responses for a poll (instructor only)"""
    import re
    if not re.match(r'^[\w\-]+$', poll_id):
        return jsonify({'error': 'Invalid poll ID'}), 400

    db = get_db()
    db.execute('DELETE FROM poll_responses WHERE poll_id = ?', (poll_id,))
    db.commit()
    db.close()

    return jsonify({'message': 'Poll responses cleared'})

# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("  Course Material Viewer - Multi-tenant Platform")
    print("  Running on http://localhost:4050")
    print("=" * 60)
    app.run(host='0.0.0.0', port=4050, debug=True)
