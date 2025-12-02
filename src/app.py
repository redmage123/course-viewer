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
    ''')
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

COURSES = {
    "ai-plain-english": {
        "id": "ai-plain-english",
        "name": "AI in Plain English",
        "description": "Demystify AI and make informed decisions for your business - ITAG Skillnet AI Advantage",
        "icon": "💡",
        "duration": "90 minutes",
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
    "mastering-llms": {
        "id": "mastering-llms",
        "name": "Mastering LLMs",
        "description": "Complete course on Large Language Models from fundamentals to advanced topics",
        "icon": "🤖",
        "sections": {
            "part1": {
                "title": "Part 1: ML Foundations & LLM Introduction",
                "items": [
                    {"id": "slides-part1", "name": "Slides", "file": "out/mastering-llms-part1-slides.html", "type": "slides"},
                    {"id": "demo-day1", "name": "Day 1: Python & ML Demo", "file": "out/demo-day1-python-ml.html", "type": "demo"},
                    {"id": "demo-day2", "name": "Day 2: Neural Networks Demo", "file": "out/demo-day2-neural-networks.html", "type": "demo"},
                    {"id": "demo-day3", "name": "Day 3: NLP & LLMs Demo", "file": "out/demo-day3-nlp-llms.html", "type": "demo"},
                    {"id": "notes-part1", "name": "Student Notes", "file": "out/student-notes-part1.html", "type": "notes"},
                ]
            },
            "part1-labs": {
                "title": "Part 1: Hands-on Labs",
                "items": [
                    {"id": "lab-01-python", "name": "Lab 1: Python Data Science", "file": "out/lab-01-python-data-science.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-01-python-solution", "name": "Lab 1: Python Data Science (Solution)", "file": "out/lab-01-python-data-science-solution.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-02-ml", "name": "Lab 2: ML Basics", "file": "out/lab-02-ml-basics.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-02-ml-solution", "name": "Lab 2: ML Basics (Solution)", "file": "out/lab-02-ml-basics-solution.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-03-nn", "name": "Lab 3: Neural Networks", "file": "out/lab-03-neural-networks.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-03-nn-solution", "name": "Lab 3: Neural Networks (Solution)", "file": "out/lab-03-neural-networks-solution.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-04-pytorch", "name": "Lab 4: PyTorch Fundamentals", "file": "out/lab-04-pytorch-fundamentals.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-04-pytorch-solution", "name": "Lab 4: PyTorch Fundamentals (Solution)", "file": "out/lab-04-pytorch-fundamentals-solution.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-05-nlp", "name": "Lab 5: NLP Basics", "file": "out/lab-05-nlp-basics.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-05-nlp-solution", "name": "Lab 5: NLP Basics (Solution)", "file": "out/lab-05-nlp-basics-solution.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-06-llm", "name": "Lab 6: LLM APIs", "file": "out/lab-06-llm-apis.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-06-llm-solution", "name": "Lab 6: LLM APIs (Solution)", "file": "out/lab-06-llm-apis-solution.ipynb", "type": "lab", "runnable": True},
                ]
            },
            "part2": {
                "title": "Part 2: Advanced LLM Topics",
                "items": [
                    {"id": "slides-main", "name": "Main Slides", "file": "out/mastering-llms-slides.html", "type": "slides"},
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
        "sections": {
            "materials": {
                "title": "Course Materials",
                "items": [
                    {"id": "py-slides", "name": "Python Fundamentals Slides", "file": "python-fundamentals/python-fundamentals-slides.html", "type": "slides"},
                    {"id": "py-demo", "name": "Interactive Python Demo", "file": "python-fundamentals/demo-python-basics.html", "type": "demo"},
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
    """Return list of all available courses"""
    course_list = []
    for course_id, course in COURSES.items():
        course_list.append({
            "id": course["id"],
            "name": course["name"],
            "description": course["description"],
            "icon": course["icon"]
        })
    return jsonify(course_list)

@app.route('/api/course/<course_id>')
def get_course(course_id):
    """Return details for a specific course"""
    if course_id in COURSES:
        return jsonify(COURSES[course_id])
    return jsonify({"error": "Course not found"}), 404

@app.route('/api/course/<course_id>/materials')
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
# Content Serving (Sandboxed)
# ============================================================================

@app.route('/api/materials')
def get_materials():
    """Return list of all course materials (legacy)"""
    return jsonify(COURSES["mastering-llms"]["sections"])

@app.route('/content/<path:filename>')
def serve_content(filename):
    """Serve course HTML files (sandboxed to materials directory)"""
    try:
        # Validate and resolve path within materials directory
        safe_path = get_safe_path_in_materials(filename)

        # Only serve allowed file types
        allowed_extensions = {'.html', '.css', '.js', '.png', '.jpg', '.jpeg',
                             '.gif', '.svg', '.ico', '.pdf', '.ipynb', '.json'}
        _, ext = os.path.splitext(safe_path)
        if ext.lower() not in allowed_extensions:
            return jsonify({'error': 'File type not allowed'}), 403

        if not os.path.isfile(safe_path):
            return jsonify({'error': 'File not found'}), 404

        # Get the relative path from materials dir
        rel_path = os.path.relpath(safe_path, MATERIALS_DIR)
        return send_from_directory(MATERIALS_DIR, rel_path)

    except SandboxError as e:
        return jsonify({'error': f'Access denied: {str(e)}'}), 403

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve React frontend"""
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

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
# Main
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("  Course Material Viewer - Multi-tenant Platform")
    print("  Running on http://localhost:4050")
    print("=" * 60)
    app.run(host='0.0.0.0', port=4050, debug=True)
