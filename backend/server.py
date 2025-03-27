from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import datetime
import time
import sys
import traceback
from urllib.parse import parse_qs, urlparse, unquote

# File storage
DATA_FILE = 'tasks.json'

def load_tasks():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        else:
            return [
                {"id": 1, "title": "Complete project", "status": "pending", "priority": "medium", "due_date": "2025-04-15", "created_at": "2025-03-26"},
                {"id": 2, "title": "Read documentation", "status": "completed", "priority": "low", "due_date": "2025-03-30", "created_at": "2025-03-26"}
            ]
    except Exception as e:
        print(f"Error loading tasks: {e}")
        traceback.print_exc()
        return []

def save_tasks():
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(tasks, f, indent=2)
    except Exception as e:
        print(f"Error saving tasks: {e}")
        traceback.print_exc()

# Initialize tasks
tasks = load_tasks()

class SimpleHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json"):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        # Enhanced CORS handling
        self.send_header('Access-Control-Allow-Origin', '*')  # For CORS
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')  # 24 hours
        self.end_headers()
    
    def _handle_error(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        # Enhanced CORS handling for errors
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        self.wfile.write(json.dumps({'detail': message}).encode())
    
    def do_OPTIONS(self):
        # Fully handle preflight requests to support browsers
        self._set_headers()
        self.wfile.write(json.dumps({}).encode())
    
    def do_GET(self):
        # Print the path being requested for debugging
        print(f"Received GET request for path: {self.path}")
        
        try:
            # Parse URL and query parameters
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            # Handle various endpoints
            if path == '/':
                self._set_headers()
                response = {'message': 'Welcome to Tempo Task API', 'tagline': 'Master Tasks with AI'}
                self.wfile.write(json.dumps(response).encode())
            elif path == '/api/hello':
                self._set_headers()
                response = {'message': 'Hello from Tempo Task!'}
                self.wfile.write(json.dumps(response).encode())
            elif path == '/api/tasks':
                self._set_headers()
                filtered_tasks = list(tasks)  # Make a copy to avoid modifying original
                
                # Filter by status
                if 'status' in query_params:
                    status = query_params['status'][0]
                    filtered_tasks = [t for t in filtered_tasks if t.get('status') == status]
                
                # Filter by priority
                if 'priority' in query_params:
                    priority = query_params['priority'][0]
                    filtered_tasks = [t for t in filtered_tasks if t.get('priority') == priority]
                
                # Filter by search term
                if 'search' in query_params:
                    search_term = query_params['search'][0].lower()
                    filtered_tasks = [t for t in filtered_tasks if search_term in t.get('title', '').lower()]
                
                # Sort by parameter
                if 'sort' in query_params:
                    sort_by = query_params['sort'][0]
                    reverse = False
                    if sort_by.startswith('-'):
                        sort_by = sort_by[1:]
                        reverse = True
                    
                    if sort_by in ['title', 'status', 'priority', 'due_date', 'created_at']:
                        # Default to empty string if key not found to avoid errors
                        filtered_tasks = sorted(filtered_tasks, key=lambda t: t.get(sort_by, ''), reverse=reverse)
                    elif sort_by == 'id':
                        filtered_tasks = sorted(filtered_tasks, key=lambda t: t.get('id', 0), reverse=reverse)
                
                # Ensure we return an empty array rather than null if no tasks match
                if filtered_tasks is None:
                    filtered_tasks = []
                    
                self.wfile.write(json.dumps(filtered_tasks).encode())
            elif path.startswith('/api/tasks/'):
                try:
                    task_id = int(path.split('/')[-1])
                    task = next((t for t in tasks if t.get("id") == task_id), None)
                    if task:
                        self._set_headers()
                        self.wfile.write(json.dumps(task).encode())
                    else:
                        self._handle_error(404, 'Task not found')
                except ValueError:
                    self._handle_error(400, 'Invalid task ID')
            elif path == '/favicon.ico':
                # Handle favicon requests gracefully
                self._handle_error(404, 'Favicon not found')
            else:
                self._handle_error(404, 'Not Found')
        except Exception as e:
            print(f"Error handling GET request: {e}")
            self._handle_error(500, f'Internal Server Error: {str(e)}')
    
    def do_POST(self):
        print(f"Received POST request for path: {self.path}")
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            if self.path == '/api/tasks':
                task_data = json.loads(post_data)
                
                # Validate required fields
                if not task_data.get("title"):
                    self._handle_error(400, 'Title is required')
                    return
                
                # Generate a new ID
                next_id = max([t.get("id", 0) for t in tasks]) + 1 if tasks else 1
                
                # Get current date for created_at
                today = datetime.datetime.now().strftime('%Y-%m-%d')
                
                task = {
                    "id": next_id,
                    "title": task_data.get("title", ""),
                    "status": task_data.get("status", "pending"),
                    "priority": task_data.get("priority", "medium"),
                    "due_date": task_data.get("due_date", ""),
                    "created_at": today
                }
                tasks.append(task)
                save_tasks()  # Save to file
                
                self._set_headers()
                self.wfile.write(json.dumps(task).encode())
            else:
                self._handle_error(404, 'Not Found')
        except json.JSONDecodeError:
            self._handle_error(400, 'Invalid JSON')
        except Exception as e:
            print(f"Error handling POST request: {e}")
            self._handle_error(500, f'Internal Server Error: {str(e)}')
    
    def do_PUT(self):
        print(f"Received PUT request for path: {self.path}")
        
        try:
            if self.path.startswith('/api/tasks/'):
                try:
                    task_id = int(self.path.split('/')[-1])
                    content_length = int(self.headers.get('Content-Length', 0))
                    put_data = self.rfile.read(content_length)
                    task_data = json.loads(put_data)
                    
                    task_index = next((i for i, t in enumerate(tasks) if t.get("id") == task_id), None)
                    if task_index is not None:
                        tasks[task_index].update({
                            "title": task_data.get("title", tasks[task_index].get("title", "")),
                            "status": task_data.get("status", tasks[task_index].get("status", "pending")),
                            "priority": task_data.get("priority", tasks[task_index].get("priority", "medium")),
                            "due_date": task_data.get("due_date", tasks[task_index].get("due_date", ""))
                        })
                        
                        save_tasks()  # Save to file
                        
                        self._set_headers()
                        self.wfile.write(json.dumps(tasks[task_index]).encode())
                    else:
                        self._handle_error(404, 'Task not found')
                except ValueError:
                    self._handle_error(400, 'Invalid task ID')
            else:
                self._handle_error(404, 'Not Found')
        except json.JSONDecodeError:
            self._handle_error(400, 'Invalid JSON')
        except Exception as e:
            print(f"Error handling PUT request: {e}")
            self._handle_error(500, f'Internal Server Error: {str(e)}')
    
    def do_DELETE(self):
        print(f"Received DELETE request for path: {self.path}")
        
        try:
            if self.path.startswith('/api/tasks/'):
                try:
                    task_id = int(self.path.split('/')[-1])
                    task_index = next((i for i, t in enumerate(tasks) if t.get("id") == task_id), None)
                    
                    if task_index is not None:
                        deleted_task = tasks.pop(task_index)
                        
                        save_tasks()  # Save to file
                        
                        self._set_headers()
                        self.wfile.write(json.dumps({'message': 'Task deleted successfully'}).encode())
                    else:
                        self._handle_error(404, 'Task not found')
                except ValueError:
                    self._handle_error(400, 'Invalid task ID')
            else:
                self._handle_error(404, 'Not Found')
        except Exception as e:
            print(f"Error handling DELETE request: {e}")
            self._handle_error(500, f'Internal Server Error: {str(e)}')

def run(server_class=HTTPServer, handler_class=SimpleHandler, port=8000):
    server_address = ('', port)
    
    # Improved error handling for server startup
    try:
        httpd = server_class(server_address, handler_class)
        print(f'Starting server on port {port}...')
        print(f'API endpoints:')
        print(f'  GET    /api/hello     - Hello World message')
        print(f'  GET    /api/tasks     - List all tasks')
        print(f'  GET    /api/tasks?status=pending&priority=high&sort=due_date - Filtered and sorted tasks')
        print(f'  GET    /api/tasks/:id - Get task by ID')
        print(f'  POST   /api/tasks     - Create a new task')
        print(f'  PUT    /api/tasks/:id - Update a task')
        print(f'  DELETE /api/tasks/:id - Delete a task')
        print(f'Data will be saved to {os.path.abspath(DATA_FILE)}')
        
        # Brief delay to ensure server is fully initialized
        time.sleep(1)
        print(f'Server is ready! Access the API at http://localhost:{port}')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nServer shutdown requested...')
            httpd.server_close()
            print('Server has been shut down')
    except Exception as e:
        print(f'Failed to start server: {e}')
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    run() 