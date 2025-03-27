import requests
import unittest
import datetime
import time
import random
import string

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/tasks"

def generate_random_title():
    """Generate a random task title"""
    return f"Test Task {''.join(random.choices(string.ascii_letters, k=8))}"

def generate_future_date(days_ahead=10):
    """Generate a date in the future"""
    future_date = datetime.datetime.now() + datetime.timedelta(days=days_ahead)
    return future_date.strftime("%Y-%m-%d")

class TempoAPITest(unittest.TestCase):
    """Test suite for Tempo Task Manager API"""
    
    def setUp(self):
        """Setup for each test - create a task to use in tests"""
        self.task_data = {
            "title": generate_random_title(),
            "status": "pending",
            "priority": "medium",
            "due_date": generate_future_date()
        }
        # Create a task to use in tests
        response = requests.post(API_URL, json=self.task_data)
        self.assertEqual(response.status_code, 200, "Failed to create setup task")
        self.task_id = response.json().get("id")
        print(f"\nCreated test task: ID={self.task_id}, Title={self.task_data['title']}")
    
    def tearDown(self):
        """Cleanup after each test - delete the created task"""
        if hasattr(self, 'task_id'):
            requests.delete(f"{API_URL}/{self.task_id}")
            print(f"Deleted test task: ID={self.task_id}")
    
    def test_1_create_task(self):
        """Test creating a new task"""
        task_data = {
            "title": generate_random_title(),
            "status": "pending",
            "priority": "high",
            "due_date": generate_future_date(5)
        }
        response = requests.post(API_URL, json=task_data)
        self.assertEqual(response.status_code, 200, "Failed to create task")
        
        # Verify the task was created with correct data
        data = response.json()
        self.assertIn("id", data, "Response missing task ID")
        task_id = data["id"]
        
        # Cleanup - delete the created task
        requests.delete(f"{API_URL}/{task_id}")
        
    def test_2_get_all_tasks(self):
        """Test getting all tasks"""
        response = requests.get(API_URL)
        self.assertEqual(response.status_code, 200, "Failed to get tasks")
        
        data = response.json()
        self.assertIsInstance(data, list, "Response is not a list")
        
        # Verify our setup task is in the list
        task_ids = [task.get("id") for task in data]
        self.assertIn(self.task_id, task_ids, "Setup task not found in tasks list")
    
    def test_3_get_task_by_id(self):
        """Test getting a specific task by ID"""
        response = requests.get(f"{API_URL}/{self.task_id}")
        self.assertEqual(response.status_code, 200, "Failed to get task by ID")
        
        data = response.json()
        self.assertEqual(data.get("id"), self.task_id, "Returned task ID doesn't match")
        self.assertEqual(data.get("title"), self.task_data["title"], "Task title doesn't match")
        self.assertEqual(data.get("status"), self.task_data["status"], "Task status doesn't match")
    
    def test_4_update_task(self):
        """Test updating a task"""
        update_data = {
            "status": "in-progress",
            "priority": "high"
        }
        response = requests.put(f"{API_URL}/{self.task_id}", json=update_data)
        self.assertEqual(response.status_code, 200, "Failed to update task")
        
        # Verify the task was updated
        response = requests.get(f"{API_URL}/{self.task_id}")
        data = response.json()
        self.assertEqual(data.get("status"), update_data["status"], "Task status not updated")
        self.assertEqual(data.get("priority"), update_data["priority"], "Task priority not updated")
    
    def test_5_delete_task(self):
        """Test deleting a task"""
        # Create a new task to delete
        task_data = {
            "title": generate_random_title(),
            "status": "pending",
            "priority": "low"
        }
        response = requests.post(API_URL, json=task_data)
        self.assertEqual(response.status_code, 200, "Failed to create task for deletion test")
        
        task_id = response.json().get("id")
        
        # Delete the task
        response = requests.delete(f"{API_URL}/{task_id}")
        self.assertEqual(response.status_code, 200, "Failed to delete task")
        
        # Verify the task was deleted
        response = requests.get(f"{API_URL}/{task_id}")
        self.assertEqual(response.status_code, 404, "Task was not deleted")
    
    def test_6_filter_by_status(self):
        """Test filtering tasks by status"""
        # Update our task to completed status
        requests.put(f"{API_URL}/{self.task_id}", json={"status": "completed"})
        
        # Get completed tasks
        response = requests.get(f"{API_URL}?status=completed")
        self.assertEqual(response.status_code, 200, "Failed to filter tasks by status")
        
        # Check if our task is in the filtered results
        data = response.json()
        task_ids = [task.get("id") for task in data]
        self.assertIn(self.task_id, task_ids, "Task not found in status filtered results")
    
    def test_7_filter_by_priority(self):
        """Test filtering tasks by priority"""
        # Update our task to high priority
        requests.put(f"{API_URL}/{self.task_id}", json={"priority": "high"})
        
        # Get high priority tasks
        response = requests.get(f"{API_URL}?priority=high")
        self.assertEqual(response.status_code, 200, "Failed to filter tasks by priority")
        
        # Check if our task is in the filtered results
        data = response.json()
        task_ids = [task.get("id") for task in data]
        self.assertIn(self.task_id, task_ids, "Task not found in priority filtered results")
    
    def test_8_sort_by_due_date(self):
        """Test sorting tasks by due date"""
        response = requests.get(f"{API_URL}?sort=due_date")
        self.assertEqual(response.status_code, 200, "Failed to sort tasks by due date")
        
        # Verify response is a list and has tasks
        data = response.json()
        self.assertIsInstance(data, list, "Response is not a list")
        
        # Check if due dates are in ascending order
        if len(data) > 1:
            dates = []
            for task in data:
                if task.get("due_date"):
                    dates.append(task.get("due_date"))
            
            sorted_dates = sorted(dates)
            self.assertEqual(dates, sorted_dates, "Tasks not sorted by due date correctly")
    
    def test_9_error_handling(self):
        """Test error handling for invalid requests"""
        # Test invalid task ID
        response = requests.get(f"{API_URL}/invalid_id")
        self.assertEqual(response.status_code, 400, "Expected 400 for invalid task ID")
        
        # Test invalid update data
        response = requests.put(f"{API_URL}/{self.task_id}", json={"status": "invalid_status"})
        self.assertNotEqual(response.status_code, 200, "Server accepted invalid status")
        
        # Test missing required field
        response = requests.post(API_URL, json={"status": "pending"})  # Missing title
        self.assertNotEqual(response.status_code, 200, "Server accepted task without title")

if __name__ == "__main__":
    # Run a few tests with server check and delay
    try:
        # Check if server is running
        requests.get(BASE_URL, timeout=2)
        print(f"Successfully connected to server at {BASE_URL}")
        print("Running functional tests for Tempo Task Manager API...")
        unittest.main()
    except requests.ConnectionError:
        print(f"ERROR: Could not connect to server at {BASE_URL}")
        print("Please make sure the backend server is running.")
    except Exception as e:
        print(f"Error: {e}") 