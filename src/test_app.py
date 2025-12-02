"""
Automated tests for Course Viewer API
Run with: pytest test_app.py -v
"""
import pytest
import json
import os
import tempfile
import shutil
import sqlite3
import app as app_module
from app import (
    app, COURSES,
    SandboxError, sanitize_path_component, get_safe_user_workspace,
    get_safe_path_in_workspace, get_safe_path_in_materials, validate_lab_id
)

# Store original DATABASE path
ORIGINAL_DATABASE = app_module.DATABASE

@pytest.fixture(autouse=True)
def isolate_database():
    """Use an isolated database for each test"""
    # Create a temporary database file
    fd, temp_db = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    # Patch the DATABASE path in the app module
    app_module.DATABASE = temp_db

    # Initialize the fresh database
    db = sqlite3.connect(temp_db)
    db.row_factory = sqlite3.Row
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

    yield

    # Cleanup - restore original and remove temp db
    app_module.DATABASE = ORIGINAL_DATABASE
    if os.path.exists(temp_db):
        os.unlink(temp_db)

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    app.config['SESSION_COOKIE_SECURE'] = False

    with app.test_client() as client:
        yield client

@pytest.fixture
def authenticated_client():
    """Create a test client with an authenticated user session"""
    app.config['TESTING'] = True
    app.config['SESSION_COOKIE_SECURE'] = False

    with app.test_client() as client:
        # Register a test user (this also logs them in)
        client.post('/api/auth/register',
            json={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'testpass123',
                'full_name': 'Test User'
            })

        # Ensure session is set
        with client.session_transaction() as sess:
            if 'user_id' not in sess:
                sess['user_id'] = 1
                sess['username'] = 'testuser'
                sess['role'] = 'student'

        yield client


class TestCourseEndpoints:
    """Tests for course-related endpoints"""

    def test_get_courses(self, client):
        """Test GET /api/courses returns all courses"""
        response = client.get('/api/courses')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 3

        # Check course IDs
        course_ids = [c['id'] for c in data]
        assert 'ai-plain-english' in course_ids
        assert 'mastering-llms' in course_ids
        assert 'python-fundamentals' in course_ids

    def test_get_course_detail(self, client):
        """Test GET /api/course/<id> returns course details"""
        response = client.get('/api/course/mastering-llms')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['id'] == 'mastering-llms'
        assert data['name'] == 'Mastering LLMs'
        assert 'sections' in data
        assert 'part1' in data['sections']
        assert 'part2' in data['sections']

    def test_get_course_not_found(self, client):
        """Test GET /api/course/<id> returns 404 for invalid course"""
        response = client.get('/api/course/nonexistent-course')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert 'error' in data

    def test_get_course_materials(self, client):
        """Test GET /api/course/<id>/materials returns sections"""
        response = client.get('/api/course/mastering-llms/materials')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'part1' in data
        assert 'part1-labs' in data
        assert 'part2' in data

        # Check part1 has items
        assert 'items' in data['part1']
        assert len(data['part1']['items']) > 0


class TestAuthEndpoints:
    """Tests for authentication endpoints"""

    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post('/api/auth/register',
            json={
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'password123',
                'full_name': 'New User'
            })
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['message'] == 'Registration successful'
        assert data['user']['username'] == 'newuser'
        assert data['user']['email'] == 'new@example.com'
        assert data['user']['role'] == 'student'

    def test_register_missing_fields(self, client):
        """Test registration with missing required fields"""
        response = client.post('/api/auth/register',
            json={
                'username': 'incomplete'
            })
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'error' in data

    def test_register_short_password(self, client):
        """Test registration with password too short"""
        response = client.post('/api/auth/register',
            json={
                'username': 'shortpw',
                'email': 'short@example.com',
                'password': '12345'
            })
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'password' in data['error'].lower()

    def test_register_duplicate_username(self, client):
        """Test registration with duplicate username"""
        # Register first user
        client.post('/api/auth/register',
            json={
                'username': 'duplicate',
                'email': 'first@example.com',
                'password': 'password123'
            })

        # Try to register with same username
        response = client.post('/api/auth/register',
            json={
                'username': 'duplicate',
                'email': 'second@example.com',
                'password': 'password123'
            })
        assert response.status_code == 409

    def test_login_success(self, client):
        """Test successful login"""
        # Register first
        client.post('/api/auth/register',
            json={
                'username': 'logintest',
                'email': 'login@example.com',
                'password': 'password123'
            })

        # Login
        response = client.post('/api/auth/login',
            json={
                'username': 'logintest',
                'password': 'password123'
            })
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['message'] == 'Login successful'
        assert data['user']['username'] == 'logintest'

    def test_login_with_email(self, client):
        """Test login using email instead of username"""
        # Register first
        client.post('/api/auth/register',
            json={
                'username': 'emaillogin',
                'email': 'emaillogin@example.com',
                'password': 'password123'
            })

        # Login with email
        response = client.post('/api/auth/login',
            json={
                'username': 'emaillogin@example.com',
                'password': 'password123'
            })
        assert response.status_code == 200

    def test_login_invalid_credentials(self, client):
        """Test login with wrong password"""
        # Register first
        client.post('/api/auth/register',
            json={
                'username': 'wrongpw',
                'email': 'wrongpw@example.com',
                'password': 'password123'
            })

        # Login with wrong password
        response = client.post('/api/auth/login',
            json={
                'username': 'wrongpw',
                'password': 'wrongpassword'
            })
        assert response.status_code == 401

    def test_get_current_user_not_logged_in(self, client):
        """Test /api/auth/me when not logged in"""
        response = client.get('/api/auth/me')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['user'] is None

    def test_get_current_user_logged_in(self, authenticated_client):
        """Test /api/auth/me when logged in"""
        response = authenticated_client.get('/api/auth/me')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['user'] is not None
        assert data['user']['username'] == 'testuser'

    def test_logout(self, authenticated_client):
        """Test logout clears session"""
        # Verify logged in
        response = authenticated_client.get('/api/auth/me')
        data = json.loads(response.data)
        assert data['user'] is not None

        # Logout
        response = authenticated_client.post('/api/auth/logout')
        assert response.status_code == 200

        # Verify logged out
        response = authenticated_client.get('/api/auth/me')
        data = json.loads(response.data)
        assert data['user'] is None


class TestEnrollmentEndpoints:
    """Tests for course enrollment endpoints"""

    def test_enroll_requires_auth(self, client):
        """Test enrollment requires authentication"""
        response = client.post('/api/course/mastering-llms/enroll')
        assert response.status_code == 401

    def test_enroll_success(self, authenticated_client):
        """Test successful course enrollment"""
        response = authenticated_client.post('/api/course/mastering-llms/enroll')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'message' in data

    def test_enroll_invalid_course(self, authenticated_client):
        """Test enrollment in non-existent course"""
        response = authenticated_client.post('/api/course/fake-course/enroll')
        assert response.status_code == 404

    def test_enroll_duplicate(self, authenticated_client):
        """Test enrolling in same course twice"""
        # First enrollment
        authenticated_client.post('/api/course/ai-plain-english/enroll')

        # Second enrollment should still succeed (idempotent)
        response = authenticated_client.post('/api/course/ai-plain-english/enroll')
        assert response.status_code == 200

    def test_get_enrollments_requires_auth(self, client):
        """Test getting enrollments requires authentication"""
        response = client.get('/api/my/enrollments')
        assert response.status_code == 401

    def test_get_enrollments(self, authenticated_client):
        """Test getting user's enrollments"""
        # Enroll in a course
        authenticated_client.post('/api/course/mastering-llms/enroll')

        # Get enrollments
        response = authenticated_client.get('/api/my/enrollments')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1

        # Check enrollment structure
        enrollment = data[0]
        assert 'course' in enrollment
        assert 'enrolled_at' in enrollment
        assert enrollment['course']['id'] == 'mastering-llms'


class TestLabEndpoints:
    """Tests for lab-related endpoints"""

    def test_start_lab_requires_auth(self, client):
        """Test starting a lab requires authentication"""
        response = client.post('/api/lab/lab-01-python/start')
        assert response.status_code == 401

    def test_start_lab_success(self, authenticated_client):
        """Test starting a lab session"""
        response = authenticated_client.post('/api/lab/lab-01-python/start')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'session_id' in data
        assert data['lab_id'] == 'lab-01-python'

    def test_start_invalid_lab(self, authenticated_client):
        """Test starting a non-existent lab"""
        response = authenticated_client.post('/api/lab/fake-lab/start')
        assert response.status_code == 404

    def test_get_lab_notebook_requires_auth(self, client):
        """Test getting notebook requires authentication"""
        response = client.get('/api/lab/lab-01-python/notebook')
        assert response.status_code == 401

    def test_lab_progress_requires_auth(self, client):
        """Test lab progress requires authentication"""
        response = client.get('/api/lab/lab-01-python/progress')
        assert response.status_code == 401

    def test_save_lab_progress(self, authenticated_client):
        """Test saving lab progress"""
        response = authenticated_client.post('/api/lab/lab-01-python/progress',
            json={
                'cell_index': 0,
                'output': 'Test output'
            })
        assert response.status_code == 200

    def test_get_lab_progress(self, authenticated_client):
        """Test getting lab progress"""
        # Save some progress
        authenticated_client.post('/api/lab/lab-01-python/progress',
            json={'cell_index': 0, 'output': 'Cell 0 output'})
        authenticated_client.post('/api/lab/lab-01-python/progress',
            json={'cell_index': 1, 'output': 'Cell 1 output'})

        # Get progress
        response = authenticated_client.get('/api/lab/lab-01-python/progress')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 2


class TestAdminEndpoints:
    """Tests for admin endpoints"""

    def test_admin_users_requires_auth(self, client):
        """Test admin users endpoint requires authentication"""
        response = client.get('/api/admin/users')
        assert response.status_code == 401

    def test_admin_users_requires_instructor(self, authenticated_client):
        """Test admin users endpoint requires instructor role"""
        response = authenticated_client.get('/api/admin/users')
        assert response.status_code == 403

    def test_admin_user_progress_requires_auth(self, client):
        """Test admin user progress requires authentication"""
        response = client.get('/api/admin/user/1/progress')
        assert response.status_code == 401


class TestContentServing:
    """Tests for content serving"""

    def test_serve_react_frontend(self, client):
        """Test serving React frontend"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data

    def test_serve_spa_routes(self, client):
        """Test SPA routes serve index.html"""
        response = client.get('/course/mastering-llms')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data


class TestMaterialsLegacy:
    """Tests for legacy materials endpoint"""

    def test_get_materials(self, client):
        """Test GET /api/materials returns mastering-llms sections"""
        response = client.get('/api/materials')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'part1' in data
        assert 'part2' in data


class TestSandboxSecurity:
    """Tests for sandbox security and path traversal prevention"""

    def test_sanitize_path_component_valid(self):
        """Test sanitize_path_component with valid inputs"""
        assert sanitize_path_component("file.txt") == "file.txt"
        assert sanitize_path_component("my-file_01.ipynb") == "my-file_01.ipynb"
        assert sanitize_path_component("test123") == "test123"

    def test_sanitize_path_component_rejects_traversal(self):
        """Test sanitize_path_component rejects path traversal"""
        with pytest.raises(SandboxError):
            sanitize_path_component("..")
        with pytest.raises(SandboxError):
            sanitize_path_component(".")
        with pytest.raises(SandboxError):
            sanitize_path_component("")

    def test_sanitize_path_component_removes_separators(self):
        """Test sanitize_path_component removes path separators"""
        # Path separators are removed - "a/b" becomes "ab" which is valid
        result = sanitize_path_component("a/b")
        assert result == "ab"
        # But ".." still fails
        with pytest.raises(SandboxError):
            sanitize_path_component("..")

    def test_validate_lab_id_valid(self):
        """Test validate_lab_id with valid inputs"""
        assert validate_lab_id("lab-01-python") == "lab-01-python"
        assert validate_lab_id("my_lab_123") == "my_lab_123"
        assert validate_lab_id("TestLab") == "TestLab"

    def test_validate_lab_id_rejects_traversal(self):
        """Test validate_lab_id rejects path traversal attempts"""
        with pytest.raises(SandboxError):
            validate_lab_id("../../../etc/passwd")
        with pytest.raises(SandboxError):
            validate_lab_id("lab/../secret")
        with pytest.raises(SandboxError):
            validate_lab_id("")

    def test_validate_lab_id_rejects_special_chars(self):
        """Test validate_lab_id rejects special characters"""
        with pytest.raises(SandboxError):
            validate_lab_id("lab;rm -rf /")
        with pytest.raises(SandboxError):
            validate_lab_id("lab|cat /etc/passwd")
        with pytest.raises(SandboxError):
            validate_lab_id("lab\x00null")

    def test_validate_lab_id_rejects_long_ids(self):
        """Test validate_lab_id rejects excessively long IDs"""
        with pytest.raises(SandboxError):
            validate_lab_id("a" * 101)

    def test_get_safe_user_workspace_valid(self):
        """Test get_safe_user_workspace with valid user_id"""
        workspace = get_safe_user_workspace(1)
        assert os.path.isabs(workspace)
        assert str(1) in workspace

    def test_get_safe_user_workspace_invalid_user_id(self):
        """Test get_safe_user_workspace rejects invalid user IDs"""
        with pytest.raises(SandboxError):
            get_safe_user_workspace(0)
        with pytest.raises(SandboxError):
            get_safe_user_workspace(-1)
        with pytest.raises(SandboxError):
            get_safe_user_workspace("not_an_int")

    def test_get_safe_path_in_workspace_valid(self):
        """Test get_safe_path_in_workspace with valid paths"""
        workspace = get_safe_user_workspace(1)
        safe_path = get_safe_path_in_workspace(workspace, "notebook.ipynb")
        assert os.path.isabs(safe_path)
        assert safe_path.startswith(workspace)

    def test_get_safe_path_in_workspace_rejects_traversal(self):
        """Test get_safe_path_in_workspace rejects path traversal"""
        workspace = get_safe_user_workspace(1)
        with pytest.raises(SandboxError):
            get_safe_path_in_workspace(workspace, "../../../etc/passwd")
        with pytest.raises(SandboxError):
            get_safe_path_in_workspace(workspace, "subdir/../../etc/passwd")

    def test_get_safe_path_in_workspace_rejects_absolute(self):
        """Test get_safe_path_in_workspace rejects absolute paths"""
        workspace = get_safe_user_workspace(1)
        with pytest.raises(SandboxError):
            get_safe_path_in_workspace(workspace, "/etc/passwd")

    def test_get_safe_path_in_materials_valid(self):
        """Test get_safe_path_in_materials with valid paths"""
        # Use a path that might exist in the materials directory
        safe_path = get_safe_path_in_materials("ai-plain-english/slides.html")
        assert os.path.isabs(safe_path)

    def test_get_safe_path_in_materials_rejects_traversal(self):
        """Test get_safe_path_in_materials rejects path traversal"""
        with pytest.raises(SandboxError):
            get_safe_path_in_materials("../../../etc/passwd")
        with pytest.raises(SandboxError):
            get_safe_path_in_materials("course/../../etc/passwd")

    def test_api_lab_start_rejects_special_chars(self, authenticated_client):
        """Test /api/lab/<lab_id>/start rejects special characters in lab_id"""
        # Lab ID with semicolon (command injection attempt)
        response = authenticated_client.post('/api/lab/lab;echo/start')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid lab ID' in data.get('error', '')

    def test_api_lab_start_rejects_dots(self, authenticated_client):
        """Test /api/lab/<lab_id>/start rejects dots in lab_id"""
        # Lab ID with dots (path traversal attempt)
        response = authenticated_client.post('/api/lab/lab..test/start')
        assert response.status_code == 400

    def test_api_lab_notebook_rejects_special_chars(self, authenticated_client):
        """Test /api/lab/<lab_id>/notebook rejects special characters"""
        response = authenticated_client.get('/api/lab/lab|cat/notebook')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid lab ID' in data.get('error', '')

    def test_api_lab_save_rejects_special_chars(self, authenticated_client):
        """Test /api/lab/<lab_id>/save rejects special characters"""
        response = authenticated_client.post('/api/lab/lab$HOME/save',
            json={'cells': []})
        assert response.status_code == 400

    def test_api_content_rejects_traversal(self, client):
        """Test /content/<path> rejects path traversal"""
        response = client.get('/content/../../../etc/passwd')
        assert response.status_code in (403, 404)

    def test_api_content_rejects_disallowed_extensions(self, client):
        """Test /content/<path> rejects disallowed file extensions"""
        response = client.get('/content/test.exe')
        assert response.status_code in (403, 404)
        response = client.get('/content/test.sh')
        assert response.status_code in (403, 404)

    def test_api_download_valid_course(self, client):
        """Test /api/course/<id>/download works for valid courses"""
        response = client.get('/api/course/mastering-llms/download')
        assert response.status_code == 200
        assert response.content_type == 'application/zip'

    def test_api_download_invalid_course(self, client):
        """Test /api/course/<id>/download rejects invalid course IDs"""
        response = client.get('/api/course/nonexistent-course/download')
        assert response.status_code == 404

    def test_api_lab_progress_rejects_special_chars(self, authenticated_client):
        """Test /api/lab/<lab_id>/progress rejects special characters"""
        response = authenticated_client.get('/api/lab/lab;id/progress')
        assert response.status_code == 400

    def test_api_lab_progress_rejects_invalid_cell_index(self, authenticated_client):
        """Test /api/lab/<lab_id>/progress rejects invalid cell index"""
        response = authenticated_client.post('/api/lab/lab-01-python/progress',
            json={'cell_index': -1, 'output': 'test'})
        assert response.status_code == 400

        response = authenticated_client.post('/api/lab/lab-01-python/progress',
            json={'cell_index': 'not_a_number', 'output': 'test'})
        assert response.status_code == 400

    def test_api_lab_progress_rejects_large_output(self, authenticated_client):
        """Test /api/lab/<lab_id>/progress rejects oversized output"""
        # Create output larger than 1MB limit
        large_output = "x" * (1024 * 1024 + 100)
        response = authenticated_client.post('/api/lab/lab-01-python/progress',
            json={'cell_index': 0, 'output': large_output})
        assert response.status_code == 413

    def test_user_isolation(self, client):
        """Test that users cannot access each other's workspaces"""
        # Register two users
        client.post('/api/auth/register',
            json={'username': 'user1', 'email': 'user1@test.com', 'password': 'password123'})

        # Get workspace for user 1
        workspace1 = get_safe_user_workspace(1)

        # Create a second user
        client.post('/api/auth/logout', method='POST')
        client.post('/api/auth/register',
            json={'username': 'user2', 'email': 'user2@test.com', 'password': 'password123'})

        # Get workspace for user 2
        workspace2 = get_safe_user_workspace(2)

        # Verify workspaces are different
        assert workspace1 != workspace2

        # Verify neither workspace is a prefix of the other
        assert not workspace1.startswith(workspace2)
        assert not workspace2.startswith(workspace1)


class TestNotebookViewerFeatures:
    """Tests for notebook viewer frontend features"""

    def test_kernel_restart_functions_exist(self, client):
        """Test that kernel restart functions are in the frontend"""
        response = client.get('/')
        html = response.data.decode('utf-8')

        # Check kernel management functions exist
        assert 'loadKernel' in html, "loadKernel function missing"
        assert 'restartKernel' in html, "restartKernel function missing"
        assert 'restartAndRunAll' in html, "restartAndRunAll function missing"

    def test_kernel_restart_buttons_exist(self, client):
        """Test that kernel restart UI buttons are in the frontend"""
        response = client.get('/')
        html = response.data.decode('utf-8')

        # Check restart buttons exist in toolbar
        assert 'Restart' in html, "Restart button missing"
        assert 'Restart & Run All' in html or 'Restart &amp; Run All' in html, "Restart & Run All button missing"

    def test_kernel_info_state_exists(self, client):
        """Test that kernel info state management exists"""
        response = client.get('/')
        html = response.data.decode('utf-8')

        # Check kernel info state
        assert 'kernelInfo' in html, "kernelInfo state missing"
        assert 'setKernelInfo' in html, "setKernelInfo setter missing"
        assert "Python (Pyodide)" in html, "Kernel name display missing"

    def test_ctrl_enter_runs_cell(self, client):
        """Test that Ctrl+Enter/Cmd+Enter handler exists for running cells"""
        response = client.get('/')
        html = response.data.decode('utf-8')

        # Check Ctrl+Enter handling works with both Ctrl and Cmd (for Mac)
        assert 'e.ctrlKey || e.metaKey' in html, "Ctrl/Cmd key handling missing"
        # Check it's associated with running cells
        assert 'runCell(selectedCell)' in html, "runCell call missing"

    def test_shift_enter_runs_and_advances(self, client):
        """Test that Shift+Enter handler exists for run and advance"""
        response = client.get('/')
        html = response.data.decode('utf-8')

        # Check Shift+Enter handling
        assert 'e.shiftKey' in html, "Shift key handling missing"
        assert 'runCellAndAdvance' in html, "runCellAndAdvance function missing"

    def test_arrow_key_navigation_at_boundaries(self, client):
        """Test that arrow key navigation at cell boundaries exists"""
        response = client.get('/')
        html = response.data.decode('utf-8')

        # Check boundary detection for arrow navigation
        assert 'isAtStart' in html, "isAtStart check missing"
        assert 'isAtEnd' in html, "isAtEnd check missing"
        assert 'selectionStart' in html, "selectionStart check missing"
        assert 'selectionEnd' in html, "selectionEnd check missing"

    def test_arrow_keys_move_between_cells(self, client):
        """Test that ArrowUp/ArrowDown handlers exist"""
        response = client.get('/')
        html = response.data.decode('utf-8')

        # Check arrow key cases in keyboard handler
        assert 'ArrowUp' in html, "ArrowUp handler missing"
        assert 'ArrowDown' in html, "ArrowDown handler missing"

    def test_save_functionality_exists(self, client):
        """Test that save and save-as functionality exists"""
        response = client.get('/')
        html = response.data.decode('utf-8')

        # Check save functions
        assert 'saveNotebook' in html, "saveNotebook function missing"
        assert 'saveNotebookAs' in html, "saveNotebookAs function missing"
        assert 'Save As' in html or 'Save As...' in html, "Save As button missing"

    def test_run_all_cells_exists(self, client):
        """Test that run all cells functionality exists"""
        response = client.get('/')
        html = response.data.decode('utf-8')

        # Check run all function
        assert 'runAllCells' in html, "runAllCells function missing"
        assert 'Run All' in html, "Run All button missing"

    def test_cell_management_functions_exist(self, client):
        """Test that cell management functions exist"""
        response = client.get('/')
        html = response.data.decode('utf-8')

        # Check cell operations
        assert 'addCell' in html, "addCell function missing"
        assert 'deleteCell' in html, "deleteCell function missing"
        assert 'copyCell' in html, "copyCell function missing"
        assert 'cutCell' in html, "cutCell function missing"
        assert 'pasteCell' in html, "pasteCell function missing"
        assert 'moveCellUp' in html, "moveCellUp function missing"
        assert 'moveCellDown' in html, "moveCellDown function missing"

    def test_keyboard_shortcuts_documented(self, client):
        """Test that keyboard shortcuts are shown in the UI"""
        response = client.get('/')
        html = response.data.decode('utf-8')

        # Check keyboard shortcut hints are displayed
        assert 'Ctrl+Enter' in html or 'Ctrl+S' in html, "Keyboard shortcut hints missing"
        assert 'Shift+Enter' in html, "Shift+Enter hint missing"
        assert 'Esc' in html or 'Escape' in html, "Escape hint missing"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
