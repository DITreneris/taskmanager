import asyncio
import httpx
import random
import string
import time
import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/tasks" # Corrected endpoint path
CONCURRENT_USERS = 50  # Number of simulated users
TIMEOUT = 15.0  # Longer timeout for requests

def random_title():
    """Generate a random task title"""
    prefixes = ["Review", "Complete", "Update", "Prepare", "Analyze", "Draft", "Schedule", "Research"]
    subjects = ["report", "document", "presentation", "meeting", "project", "code", "data", "analysis"]
    return f"{random.choice(prefixes)} {random.choice(subjects)} {random.randint(1, 100)}"

def random_due_date():
    """Generate a random future date within next 30 days"""
    days_ahead = random.randint(1, 30)
    future_date = datetime.datetime.now() + datetime.timedelta(days=days_ahead)
    return future_date.strftime("%Y-%m-%d")

async def simulate_user(client, user_id, stats):
    """Simulate a user interacting with the Tempo Task Manager API"""
    try:
        # 1. Create a new task
        title = random_title()
        task_data = {
            "title": title,
            "status": "pending",
            "priority": random.choice(["low", "medium", "high"]),
            "due_date": random_due_date()
        }
        
        start = time.perf_counter()
        res = await client.post(API_URL, json=task_data)
        elapsed = time.perf_counter() - start
        stats["create"].append(elapsed)
        res.raise_for_status()
        task_id = res.json().get("id")
        print(f"User {user_id}: Created task {task_id}")

        # 2. Update task to in-progress
        await asyncio.sleep(random.uniform(0.1, 0.5))
        start = time.perf_counter()
        res = await client.put(f"{API_URL}/{task_id}", json={"status": "in-progress"})
        elapsed = time.perf_counter() - start
        stats["update"].append(elapsed)
        res.raise_for_status()
        print(f"User {user_id}: Updated task {task_id} to in-progress")

        # 3. Update task to completed
        await asyncio.sleep(random.uniform(0.1, 0.5))
        start = time.perf_counter()
        res = await client.put(f"{API_URL}/{task_id}", json={"status": "completed"})
        elapsed = time.perf_counter() - start
        stats["update"].append(elapsed)
        res.raise_for_status()
        print(f"User {user_id}: Updated task {task_id} to completed")

        # 4. Get all tasks with different filters
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # 4.1 Get all tasks
        start = time.perf_counter()
        res = await client.get(API_URL)
        elapsed = time.perf_counter() - start
        stats["read"].append(elapsed)
        res.raise_for_status()
        
        # 4.2 Get tasks filtered by status
        start = time.perf_counter()
        res = await client.get(f"{API_URL}?status=completed")
        elapsed = time.perf_counter() - start
        stats["read_filtered"].append(elapsed)
        res.raise_for_status()
        
        # 4.3 Get tasks sorted by due date
        start = time.perf_counter()
        res = await client.get(f"{API_URL}?sort=due_date")
        elapsed = time.perf_counter() - start
        stats["read_sorted"].append(elapsed)
        res.raise_for_status()
        
        print(f"User {user_id}: Retrieved tasks with filters")

        # 5. Delete own task
        await asyncio.sleep(random.uniform(0.1, 0.5))
        start = time.perf_counter()
        res = await client.delete(f"{API_URL}/{task_id}")
        elapsed = time.perf_counter() - start
        stats["delete"].append(elapsed)
        res.raise_for_status()
        print(f"User {user_id}: Deleted task {task_id}")

    except Exception as e:
        stats["errors"].append((user_id, str(e)))
        print(f"User {user_id}: Error - {str(e)}")

async def main():
    """Main function to run the load test"""
    print(f"Starting async load test with {CONCURRENT_USERS} concurrent users...")
    print(f"API endpoint: {API_URL}")
    
    stats = {
        "create": [], 
        "update": [], 
        "read": [], 
        "read_filtered": [], 
        "read_sorted": [], 
        "delete": [], 
        "errors": []
    }
    
    start_time = time.perf_counter()
    
    # Use limits and timeouts to prevent overwhelming the server
    limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
    async with httpx.AsyncClient(timeout=TIMEOUT, limits=limits) as client:
        tasks = [simulate_user(client, i, stats) for i in range(CONCURRENT_USERS)]
        await asyncio.gather(*tasks)
    
    total_time = time.perf_counter() - start_time

    # Summary
    print("\n----- Test Summary -----")
    print(f"Total test time: {total_time:.2f} seconds")
    print(f"Concurrent users: {CONCURRENT_USERS}")
    
    for key in ["create", "update", "read", "read_filtered", "read_sorted", "delete"]:
        if stats[key]:
            avg_time = sum(stats[key]) / len(stats[key])
            min_time = min(stats[key])
            max_time = max(stats[key])
            print(f"{key.capitalize().replace('_', ' ')} - Count: {len(stats[key])}, Avg: {avg_time:.3f}s, Min: {min_time:.3f}s, Max: {max_time:.3f}s")
    
    if stats["errors"]:
        print(f"\n❌ Errors ({len(stats['errors'])}):")
        # Group errors by type
        error_types = {}
        for user_id, msg in stats["errors"]:
            error_type = msg.split(':', 1)[0] if ':' in msg else msg
            if error_type not in error_types:
                error_types[error_type] = []
            error_types[error_type].append(user_id)
        
        for error_type, user_ids in error_types.items():
            print(f"{error_type}: {len(user_ids)} occurrences")
            if len(user_ids) <= 5:  # Show details for a few examples
                for user_id in user_ids:
                    print(f"  User {user_id}")
    else:
        print("\n✅ No errors encountered.")
    
    # Calculate success rate
    total_operations = sum(len(stats[key]) for key in ["create", "update", "read", "read_filtered", "read_sorted", "delete"])
    if total_operations > 0:
        success_rate = (total_operations - len(stats["errors"])) / total_operations * 100
        print(f"\nSuccess rate: {success_rate:.2f}%")
    
    # Calculate throughput
    if total_time > 0:
        operations_per_second = total_operations / total_time
        print(f"Operations per second: {operations_per_second:.2f}")

if __name__ == "__main__":
    asyncio.run(main()) 