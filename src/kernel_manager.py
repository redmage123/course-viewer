"""
Jupyter Kernel Manager for Course Viewer

Manages Python kernels for executing notebook cells server-side.
Supports PyTorch, scikit-learn, and other libraries not available in Pyodide.
"""

import os
import sys
import uuid
import time
import queue
import threading
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from jupyter_client import KernelManager
from jupyter_client.kernelspec import NoSuchKernel
import base64


@dataclass
class KernelSession:
    """Represents a user's kernel session"""
    kernel_id: str
    user_id: int
    lab_id: str
    manager: KernelManager
    client: Any
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    execution_count: int = 0


class KernelPool:
    """
    Manages a pool of Jupyter kernels for multiple users.
    Each user gets their own isolated kernel per lab.
    """

    def __init__(self, max_kernels: int = 20, idle_timeout: int = 1800):
        """
        Initialize the kernel pool.

        Args:
            max_kernels: Maximum number of concurrent kernels
            idle_timeout: Seconds before idle kernels are shut down (default 30 min)
        """
        self.max_kernels = max_kernels
        self.idle_timeout = idle_timeout
        self.kernels: Dict[str, KernelSession] = {}
        self._lock = threading.Lock()

        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()

    def _make_kernel_key(self, user_id: int, lab_id: str) -> str:
        """Create a unique key for a user's lab kernel"""
        return f"{user_id}:{lab_id}"

    def get_or_create_kernel(self, user_id: int, lab_id: str) -> Dict[str, Any]:
        """
        Get an existing kernel or create a new one for the user/lab.

        Returns:
            Dict with kernel_id, status, and message
        """
        key = self._make_kernel_key(user_id, lab_id)

        with self._lock:
            # Check if kernel already exists
            if key in self.kernels:
                session = self.kernels[key]
                session.last_activity = time.time()

                # Check if kernel is still alive
                if session.manager.is_alive():
                    return {
                        "kernel_id": session.kernel_id,
                        "status": "existing",
                        "message": "Using existing kernel"
                    }
                else:
                    # Kernel died, clean it up
                    self._shutdown_kernel(key)

            # Check if we're at capacity
            if len(self.kernels) >= self.max_kernels:
                # Try to free up an old kernel
                self._evict_oldest_kernel()

                if len(self.kernels) >= self.max_kernels:
                    return {
                        "kernel_id": None,
                        "status": "error",
                        "message": "Server at capacity. Please try again later."
                    }

            # Create new kernel
            try:
                kernel_id = str(uuid.uuid4())
                km = KernelManager(kernel_name='python3')
                km.start_kernel()
                client = km.client()
                client.start_channels()

                # Wait for kernel to be ready
                client.wait_for_ready(timeout=30)

                session = KernelSession(
                    kernel_id=kernel_id,
                    user_id=user_id,
                    lab_id=lab_id,
                    manager=km,
                    client=client
                )

                self.kernels[key] = session

                # Run startup code
                self._run_startup_code(client)

                return {
                    "kernel_id": kernel_id,
                    "status": "created",
                    "message": "New kernel started"
                }

            except NoSuchKernel:
                return {
                    "kernel_id": None,
                    "status": "error",
                    "message": "Python kernel not found. Please install ipykernel."
                }
            except Exception as e:
                return {
                    "kernel_id": None,
                    "status": "error",
                    "message": f"Failed to start kernel: {str(e)}"
                }

    def _run_startup_code(self, client):
        """Run initialization code in the kernel"""
        startup = """
import warnings
warnings.filterwarnings('ignore')

# Configure matplotlib for non-interactive backend
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Helper to capture figures
def _capture_figure():
    import io
    import base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

print("Kernel ready!")
"""
        # Execute silently
        client.execute(startup, silent=True)
        # Wait for completion
        while True:
            try:
                msg = client.get_iopub_msg(timeout=5)
                if msg['msg_type'] == 'status' and msg['content']['execution_state'] == 'idle':
                    break
            except queue.Empty:
                break

    def execute_code(self, user_id: int, lab_id: str, code: str) -> Dict[str, Any]:
        """
        Execute code in the user's kernel.

        Returns:
            Dict with outputs, status, and execution_count
        """
        key = self._make_kernel_key(user_id, lab_id)

        with self._lock:
            if key not in self.kernels:
                return {
                    "status": "error",
                    "error": "No kernel found. Please start a kernel first.",
                    "outputs": []
                }

            session = self.kernels[key]
            session.last_activity = time.time()

            if not session.manager.is_alive():
                del self.kernels[key]
                return {
                    "status": "error",
                    "error": "Kernel died. Please restart.",
                    "outputs": []
                }

        client = session.client

        # Wrap code to capture matplotlib figures
        wrapped_code = f"""
{code}

# Auto-capture any open figures
import matplotlib.pyplot as plt
if plt.get_fignums():
    _fig_data = _capture_figure()
    plt.close('all')
    from IPython.display import display, Image
    import base64
    display({{'image/png': _fig_data}}, raw=True)
"""

        try:
            # Execute the code
            msg_id = client.execute(wrapped_code)
            session.execution_count += 1

            outputs = []
            error = None

            # Collect outputs
            while True:
                try:
                    msg = client.get_iopub_msg(timeout=60)
                    msg_type = msg['msg_type']
                    content = msg['content']

                    if msg_type == 'status':
                        if content['execution_state'] == 'idle':
                            break

                    elif msg_type == 'stream':
                        outputs.append({
                            "type": "stream",
                            "name": content.get('name', 'stdout'),
                            "text": content.get('text', '')
                        })

                    elif msg_type == 'execute_result':
                        data = content.get('data', {})
                        if 'text/plain' in data:
                            outputs.append({
                                "type": "execute_result",
                                "text": data['text/plain']
                            })
                        if 'image/png' in data:
                            outputs.append({
                                "type": "image",
                                "data": data['image/png']
                            })

                    elif msg_type == 'display_data':
                        data = content.get('data', {})
                        if 'image/png' in data:
                            outputs.append({
                                "type": "image",
                                "data": data['image/png']
                            })
                        elif 'text/plain' in data:
                            outputs.append({
                                "type": "display",
                                "text": data['text/plain']
                            })

                    elif msg_type == 'error':
                        error = {
                            "ename": content.get('ename', 'Error'),
                            "evalue": content.get('evalue', ''),
                            "traceback": content.get('traceback', [])
                        }
                        outputs.append({
                            "type": "error",
                            "ename": error['ename'],
                            "evalue": error['evalue'],
                            "traceback": '\n'.join(error['traceback'])
                        })

                except queue.Empty:
                    # Timeout waiting for output
                    break

            return {
                "status": "ok" if error is None else "error",
                "execution_count": session.execution_count,
                "outputs": outputs,
                "error": error
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "outputs": []
            }

    def interrupt_kernel(self, user_id: int, lab_id: str) -> Dict[str, Any]:
        """Interrupt a running kernel"""
        key = self._make_kernel_key(user_id, lab_id)

        with self._lock:
            if key not in self.kernels:
                return {"status": "error", "message": "No kernel found"}

            session = self.kernels[key]
            try:
                session.manager.interrupt_kernel()
                return {"status": "ok", "message": "Kernel interrupted"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

    def restart_kernel(self, user_id: int, lab_id: str) -> Dict[str, Any]:
        """Restart a kernel"""
        key = self._make_kernel_key(user_id, lab_id)

        with self._lock:
            if key not in self.kernels:
                return {"status": "error", "message": "No kernel found"}

            session = self.kernels[key]
            try:
                session.manager.restart_kernel()
                session.client.start_channels()
                session.client.wait_for_ready(timeout=30)
                session.execution_count = 0
                self._run_startup_code(session.client)
                return {"status": "ok", "message": "Kernel restarted"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

    def shutdown_kernel(self, user_id: int, lab_id: str) -> Dict[str, Any]:
        """Shutdown a specific kernel"""
        key = self._make_kernel_key(user_id, lab_id)

        with self._lock:
            if key not in self.kernels:
                return {"status": "ok", "message": "No kernel to shut down"}

            self._shutdown_kernel(key)
            return {"status": "ok", "message": "Kernel shut down"}

    def _shutdown_kernel(self, key: str):
        """Internal method to shutdown a kernel (must hold lock)"""
        if key in self.kernels:
            session = self.kernels[key]
            try:
                session.client.stop_channels()
                session.manager.shutdown_kernel(now=True)
            except:
                pass
            del self.kernels[key]

    def _evict_oldest_kernel(self):
        """Evict the oldest idle kernel (must hold lock)"""
        if not self.kernels:
            return

        oldest_key = min(self.kernels.keys(),
                        key=lambda k: self.kernels[k].last_activity)
        self._shutdown_kernel(oldest_key)

    def _cleanup_loop(self):
        """Background thread to clean up idle kernels"""
        while True:
            time.sleep(60)  # Check every minute

            with self._lock:
                now = time.time()
                to_remove = []

                for key, session in self.kernels.items():
                    # Check if kernel is idle too long
                    if now - session.last_activity > self.idle_timeout:
                        to_remove.append(key)
                    # Check if kernel died
                    elif not session.manager.is_alive():
                        to_remove.append(key)

                for key in to_remove:
                    self._shutdown_kernel(key)

    def get_kernel_info(self, user_id: int, lab_id: str) -> Dict[str, Any]:
        """Get info about a user's kernel"""
        key = self._make_kernel_key(user_id, lab_id)

        with self._lock:
            if key not in self.kernels:
                return {"status": "none", "message": "No kernel running"}

            session = self.kernels[key]
            return {
                "status": "running" if session.manager.is_alive() else "dead",
                "kernel_id": session.kernel_id,
                "execution_count": session.execution_count,
                "created_at": session.created_at,
                "last_activity": session.last_activity
            }

    def shutdown_all(self):
        """Shutdown all kernels (for clean server shutdown)"""
        with self._lock:
            for key in list(self.kernels.keys()):
                self._shutdown_kernel(key)


# Global kernel pool instance
kernel_pool = KernelPool()
