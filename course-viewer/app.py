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
                    {"id": "slides-part1", "name": "Slides", "file": "mastering-llms-part1-slides.html", "type": "slides"},
                    {"id": "demo-day1", "name": "Day 1: Python & ML Demo", "file": "demo-day1-python-ml.html", "type": "demo"},
                    {"id": "demo-day2", "name": "Day 2: Neural Networks Demo", "file": "demo-day2-neural-networks.html", "type": "demo"},
                    {"id": "demo-day3", "name": "Day 3: NLP & LLMs Demo", "file": "demo-day3-nlp-llms.html", "type": "demo"},
                    {"id": "notes-part1", "name": "Student Notes", "file": "student-notes-part1.html", "type": "notes"},
                ]
            },
            "part1-labs": {
                "title": "Part 1: Hands-on Labs",
                "items": [
                    {"id": "lab-01-python", "name": "Lab 1: Python Data Science", "file": "lab-01-python-data-science.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-02-ml", "name": "Lab 2: ML Basics", "file": "lab-02-ml-basics.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-03-nn", "name": "Lab 3: Neural Networks", "file": "lab-03-neural-networks.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-04-pytorch", "name": "Lab 4: PyTorch Fundamentals", "file": "lab-04-pytorch-fundamentals.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-05-nlp", "name": "Lab 5: NLP Basics", "file": "lab-05-nlp-basics.ipynb", "type": "lab", "runnable": True},
                    {"id": "lab-06-llm", "name": "Lab 6: LLM APIs", "file": "lab-06-llm-apis.ipynb", "type": "lab", "runnable": True},
                ]
            },
            "part2": {
                "title": "Part 2: Advanced LLM Topics",
                "items": [
                    {"id": "slides-main", "name": "Main Slides", "file": "mastering-llms-slides.html", "type": "slides"},
                    {"id": "demo-attention", "name": "Attention Visualization", "file": "demo-attention-visualization.html", "type": "demo"},
                    {"id": "demo-rag", "name": "RAG Pipeline", "file": "demo-rag-pipeline.html", "type": "demo"},
                    {"id": "demo-agent", "name": "Agent Builder", "file": "demo-agent-builder.html", "type": "demo"},
                    {"id": "notes-main", "name": "Student Notes", "file": "student-notes.html", "type": "notes"},
                ]
            },
        }
    },
    "python-fundamentals": {
        "id": "python-fundamentals",
        "name": "Python Fundamentals",
        "description": "Introduction to Python programming for beginners",
        "icon": "🐍",
        "sections": {
            "basics": {
                "title": "Python Basics",
                "items": [
                    {"id": "py-intro", "name": "Introduction to Python", "file": "python-intro.html", "type": "slides"},
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
    """Download all course materials as a zip file"""
    if course_id not in COURSES:
        return jsonify({"error": "Course not found"}), 404

    course = COURSES[course_id]

    # Create zip file in memory
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        files_added = set()

        for section_id, section in course['sections'].items():
            for item in section['items']:
                file_path = item['file']
                full_path = os.path.join(MATERIALS_DIR, file_path)

                # Skip if already added or file doesn't exist
                if file_path in files_added:
                    continue

                if os.path.isfile(full_path):
                    # Add individual file
                    zip_file.write(full_path, file_path)
                    files_added.add(file_path)
                elif os.path.isdir(os.path.dirname(full_path)):
                    # If it's in a subdirectory, try to add the whole directory
                    dir_path = os.path.dirname(full_path)
                    if os.path.exists(dir_path):
                        for root, dirs, files in os.walk(dir_path):
                            for file in files:
                                abs_path = os.path.join(root, file)
                                rel_path = os.path.relpath(abs_path, MATERIALS_DIR)
                                if rel_path not in files_added:
                                    zip_file.write(abs_path, rel_path)
                                    files_added.add(rel_path)

    zip_buffer.seek(0)

    # Create safe filename
    safe_name = course_id.replace(' ', '-').lower()
    filename = f"{safe_name}-materials.zip"

    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=filename
    )

# ============================================================================
# Lab Routes - Jupyter Integration
# ============================================================================

@app.route('/api/lab/<lab_id>/start', methods=['POST'])
@login_required
def start_lab(lab_id):
    """Start a lab session for the current user"""
    # Find the lab in courses
    lab_info = None
    for course in COURSES.values():
        for section in course['sections'].values():
            for item in section['items']:
                if item['id'] == lab_id and item.get('runnable'):
                    lab_info = item
                    break

    if not lab_info:
        return jsonify({'error': 'Lab not found or not runnable'}), 404

    user_id = session['user_id']
    user_workspace = os.path.join(WORKSPACES_DIR, str(user_id))
    os.makedirs(user_workspace, exist_ok=True)

    # Copy notebook to user workspace if not exists
    source_notebook = os.path.join(MATERIALS_DIR, lab_info['file'])
    user_notebook = os.path.join(user_workspace, lab_info['file'])

    if not os.path.exists(user_notebook) and os.path.exists(source_notebook):
        shutil.copy2(source_notebook, user_notebook)

    # Record lab session
    db = get_db()
    db.execute(
        'INSERT INTO lab_sessions (user_id, lab_id, notebook_path, last_activity) VALUES (?, ?, ?, ?)',
        (user_id, lab_id, user_notebook, datetime.now())
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

@app.route('/api/lab/<lab_id>/notebook')
@login_required
def get_lab_notebook(lab_id):
    """Get the notebook content for a lab"""
    user_id = session['user_id']
    user_workspace = os.path.join(WORKSPACES_DIR, str(user_id))

    # Find lab file
    lab_file = None
    for course in COURSES.values():
        for section in course['sections'].values():
            for item in section['items']:
                if item['id'] == lab_id:
                    lab_file = item['file']
                    break

    if not lab_file:
        return jsonify({'error': 'Lab not found'}), 404

    # Try user workspace first, then materials dir
    notebook_path = os.path.join(user_workspace, lab_file)
    if not os.path.exists(notebook_path):
        notebook_path = os.path.join(MATERIALS_DIR, lab_file)

    if not os.path.exists(notebook_path):
        return jsonify({'error': 'Notebook file not found'}), 404

    with open(notebook_path, 'r') as f:
        notebook = json.load(f)

    return jsonify(notebook)

@app.route('/api/lab/<lab_id>/save', methods=['POST'])
@login_required
def save_lab_notebook(lab_id):
    """Save the notebook content for a lab"""
    user_id = session['user_id']
    user_workspace = os.path.join(WORKSPACES_DIR, str(user_id))
    os.makedirs(user_workspace, exist_ok=True)

    # Find lab file
    lab_file = None
    for course in COURSES.values():
        for section in course['sections'].values():
            for item in section['items']:
                if item['id'] == lab_id:
                    lab_file = item['file']
                    break

    if not lab_file:
        return jsonify({'error': 'Lab not found'}), 404

    notebook_path = os.path.join(user_workspace, lab_file)
    notebook_data = request.get_json()

    with open(notebook_path, 'w') as f:
        json.dump(notebook_data, f, indent=2)

    return jsonify({'message': 'Notebook saved successfully'})

@app.route('/api/lab/<lab_id>/progress', methods=['GET', 'POST'])
@login_required
def lab_progress(lab_id):
    """Get or save progress for a lab"""
    if request.method == 'POST':
        data = request.get_json()
        cell_index = data.get('cell_index')
        output = data.get('output', '')

        db = get_db()
        db.execute(
            'INSERT INTO lab_progress (user_id, lab_id, cell_index, output) VALUES (?, ?, ?, ?)',
            (session['user_id'], lab_id, cell_index, json.dumps(output))
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
# Content Serving
# ============================================================================

@app.route('/api/materials')
def get_materials():
    """Return list of all course materials (legacy)"""
    return jsonify(COURSES["mastering-llms"]["sections"])

@app.route('/content/<path:filename>')
def serve_content(filename):
    """Serve course HTML files"""
    return send_from_directory(MATERIALS_DIR, filename)

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
