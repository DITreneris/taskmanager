from locust import HttpUser, task, between
import random
import string
import datetime
import time

def random_task_title():
    prefixes = ["Review", "Complete", "Update", "Prepare", "Analyze", "Draft", "Schedule", "Research"]
    subjects = ["report", "document", "presentation", "meeting", "project", "code", "data", "analysis"]
    return f"{random.choice(prefixes)} {random.choice(subjects)} {random.randint(1, 100)}"

def random_due_date():
    """Generate a random future date within next 30 days"""
    days_ahead = random.randint(1, 30)
    future_date = datetime.datetime.now() + datetime.timedelta(days=days_ahead)
    return future_date.strftime("%Y-%m-%d")

class TempoUser(HttpUser):
    wait_time = between(0.1, 0.5)  # 100–500ms delay
    
    def on_start(self):
        # Initialize task tracking
        self.created_tasks = []
    
    @task
    def task_flow(self):
        # Step 1: Create task with retry logic
        task_id = self.create_task_with_retry()
        if not task_id:
            return
            
        # Track created task ID for potential cleanup
        self.created_tasks.append(task_id)
        
        # Step 2: Update status to in-progress with error handling
        if not self.update_task(task_id, {"status": "in-progress"}):
            return
            
        # Step 3: Update status to completed with error handling
        if not self.update_task(task_id, {"status": "completed"}):
            return
        
        # Step 4: Get all tasks with different filters (with error handling)
        self.get_tasks_with_retry("/api/tasks")
        self.get_tasks_with_retry("/api/tasks?sort=due_date")
        self.get_tasks_with_retry("/api/tasks?status=completed")
        self.get_tasks_with_retry("/api/tasks?priority=high")
        
        # Step 5: Delete the task with retry
        self.delete_task_with_retry(task_id)
        if task_id in self.created_tasks:
            self.created_tasks.remove(task_id)
        
    def create_task_with_retry(self, max_retries=3):
        """Create a task with retry logic"""
        title = random_task_title()
        task_data = {
            "title": title,
            "status": "pending",
            "priority": random.choice(["low", "medium", "high"]),
            "due_date": random_due_date()
        }
        
        for attempt in range(max_retries):
            with self.client.post("/api/tasks", 
                                json=task_data, 
                                catch_response=True) as response:
                if response.status_code == 200:
                    try:
                        task_id = response.json().get("id")
                        return task_id
                    except Exception as e:
                        if attempt == max_retries - 1:
                            response.failure(f"Failed to parse response: {e}")
                            return None
                else:
                    if attempt == max_retries - 1:
                        response.failure(f"Failed to create task: {response.text}")
                        return None
            # Wait before retry
            time.sleep(0.5)
    
    def update_task(self, task_id, data, max_retries=3):
        """Update a task with retry logic"""
        for attempt in range(max_retries):
            with self.client.put(f"/api/tasks/{task_id}", 
                                json=data, 
                                catch_response=True) as response:
                if response.status_code == 200:
                    return True
                else:
                    if attempt == max_retries - 1:
                        response.failure(f"Failed to update task {task_id}: {response.text}")
                        return False
            # Wait before retry
            time.sleep(0.5)
    
    def get_tasks_with_retry(self, endpoint, max_retries=3):
        """Get tasks with retry logic"""
        for attempt in range(max_retries):
            with self.client.get(endpoint, catch_response=True) as response:
                if response.status_code == 200:
                    return True
                else:
                    if attempt == max_retries - 1:
                        response.failure(f"Failed to get tasks from {endpoint}: {response.text}")
                        return False
            # Wait before retry
            time.sleep(0.5)
    
    def delete_task_with_retry(self, task_id, max_retries=3):
        """Delete a task with retry logic"""
        for attempt in range(max_retries):
            with self.client.delete(f"/api/tasks/{task_id}", 
                                catch_response=True) as response:
                if response.status_code == 200:
                    return True
                else:
                    if attempt == max_retries - 1:
                        response.failure(f"Failed to delete task {task_id}: {response.text}")
                        return False
            # Wait before retry
            time.sleep(0.5)
    
    def on_stop(self):
        """Clean up any remaining tasks when test stops"""
        for task_id in self.created_tasks:
            try:
                self.client.delete(f"/api/tasks/{task_id}")
            except:
                pass 