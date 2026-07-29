import os
import sys
import time
import socket
import subprocess
import webbrowser
import threading

def kill_process_on_port(port: int):
    """Find and terminate any process listening on target port (Windows/Linux)."""
    try:
        if sys.platform == "win32":
            output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True, text=True)
            for line in output.strip().split("\n"):
                if "LISTENING" in line:
                    parts = line.strip().split()
                    pid = parts[-1]
                    print(f"Terminating stale process on port {port} (PID: {pid})...")
                    subprocess.call(f"taskkill /F /PID {pid}", shell=True)
    except Exception:
        pass

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def start_backend():
    """Start FastAPI uvicorn backend server on port 8000."""
    if is_port_in_use(8000):
        kill_process_on_port(8000)
        time.sleep(1.0)

    print("Starting FastAPI OCR Backend on http://127.0.0.1:8000...")
    cmd = [
        sys.executable, "-m", "uvicorn", "src.ocr_pipeline.api:app",
        "--host", "127.0.0.1", "--port", "8000"
    ]
    return subprocess.Popen(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))

def start_frontend():
    """Start Vite React frontend dev server on port 3000."""
    if is_port_in_use(3000):
        kill_process_on_port(3000)
        time.sleep(1.0)

    print("Starting Vite Frontend Web App on http://localhost:3000...")
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
    cmd = ["npx.cmd" if sys.platform == "win32" else "npx", "vite", "--port", "3000"]
    return subprocess.Popen(cmd, cwd=frontend_dir)

def open_browser():
    """Open default web browser after short delay."""
    time.sleep(2.5)
    print("Opening web interface in browser: http://localhost:3000")
    webbrowser.open("http://localhost:3000")

def main():
    print("=" * 60)
    print("      LAUNCHING END-TO-END OCR PIPELINE WEB APPLICATION     ")
    print("=" * 60)

    backend_process = start_backend()
    frontend_process = start_frontend()

    # Open browser thread
    threading.Thread(target=open_browser, daemon=True).start()

    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down backend and frontend servers...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("Application stopped cleanly.")

if __name__ == "__main__":
    main()
