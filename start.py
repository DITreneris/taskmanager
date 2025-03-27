import os
import sys
import subprocess
import time
import webbrowser
import signal
import platform

# Configuration
BACKEND_PORT = 8000
FRONTEND_PORT = 8080

processes = []

def cleanup():
    print("\nShutting down servers...")
    for proc in processes:
        if proc and proc.poll() is None:  # If process is still running
            if platform.system() == "Windows":
                # Windows requires different command to terminate
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(proc.pid)])
            else:
                proc.terminate()
                proc.wait()
    print("All servers stopped")

def start_servers():
    # Register cleanup handler for graceful shutdown
    signal.signal(signal.SIGINT, lambda s, f: (cleanup(), sys.exit(0)))
    
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(current_dir, 'backend')
    frontend_dir = os.path.join(current_dir, 'frontend')
    
    # Start the backend server
    print(f"Starting backend server on port {BACKEND_PORT}...")
    try:
        if platform.system() == "Windows":
            backend_proc = subprocess.Popen(
                ['python', 'server.py'], 
                cwd=backend_dir
            )
        else:
            backend_proc = subprocess.Popen(
                ['python3', 'server.py'],
                cwd=backend_dir
            )
        processes.append(backend_proc)
    except Exception as e:
        print(f"Error starting backend server: {e}")
        cleanup()
        sys.exit(1)
    
    # Give the backend server some time to start
    time.sleep(2)
    
    # Test if backend is running
    try:
        import urllib.request
        urllib.request.urlopen(f"http://localhost:{BACKEND_PORT}/api/hello", timeout=3)
        print(f"Backend server is running at http://localhost:{BACKEND_PORT}")
    except:
        print("Warning: Backend server might not be running correctly")
    
    # Start the frontend server
    print(f"Starting frontend server on port {FRONTEND_PORT}...")
    try:
        if platform.system() == "Windows":
            frontend_proc = subprocess.Popen(
                ['python', '-m', 'http.server', str(FRONTEND_PORT)],
                cwd=frontend_dir
            )
        else:
            frontend_proc = subprocess.Popen(
                ['python3', '-m', 'http.server', str(FRONTEND_PORT)],
                cwd=frontend_dir
            )
        processes.append(frontend_proc)
    except Exception as e:
        print(f"Error starting frontend server: {e}")
        cleanup()
        sys.exit(1)
    
    # Give the frontend server some time to start
    time.sleep(1)
    
    print(f"Frontend server is running at http://localhost:{FRONTEND_PORT}")
    
    # Open the application in the browser
    try:
        print("Opening application in your browser...")
        # Pre-warm the API to avoid connection issues
        try:
            urllib.request.urlopen(f"http://localhost:{BACKEND_PORT}/api/tasks", timeout=3)
        except:
            pass
        webbrowser.open(f"http://localhost:{FRONTEND_PORT}")
    except Exception as e:
        print(f"Could not open browser automatically: {e}")
    
    print("\nServers are running! Press Ctrl+C to stop them.")
    
    # Keep the script running until interrupted
    try:
        while True:
            time.sleep(1)
            # Check if processes are still running
            if backend_proc.poll() is not None:
                print("Backend server stopped unexpectedly")
                cleanup()
                sys.exit(1)
            if frontend_proc.poll() is not None:
                print("Frontend server stopped unexpectedly")
                cleanup()
                sys.exit(1)
    except KeyboardInterrupt:
        cleanup()
        sys.exit(0)

if __name__ == "__main__":
    start_servers() 