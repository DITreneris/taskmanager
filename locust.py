from locust import HttpUser, task, between
import random
import string

def random_task_title():
    return 'Task ' + ''.join(random.choices(string.ascii_letters, k=5))

class TempoUser(HttpUser):
    wait_time = between(0.1, 0.5)  # 100–500ms delay

    @task
    def task_flow(self):
        # Step 1: Create task
        title = random_task_title()
        with self.client.post("/api/tasks", 
                              json={
                                  "title": title,
                                  "status": "pending",
                                  "priority": random.choice(["low", "medium", "high"]),
                                  "due_date": "2025-04-30"
                              }, 
                              catch_response=True) as response:
            if response.status_code == 200:
                task_id = response.json().get("id")
            else:
                response.failure(f"Failed to create task: {response.text}")
                return

        # Step 2: Update status to in-progress
        self.client.put(f"/api/tasks/{task_id}", json={"status": "in-progress"})

        # Step 3: Update status to completed
        self.client.put(f"/api/tasks/{task_id}", json={"status": "completed"})

        # Step 4: Get all tasks with different filters
        self.client.get("/api/tasks")
        self.client.get("/api/tasks?sort=due_date")
        self.client.get("/api/tasks?status=completed")
        
        # Step 5: Delete the task
        self.client.delete(f"/api/tasks/{task_id}")