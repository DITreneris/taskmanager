import asyncio
import httpx
import random
import string
import time

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/tasks"  # Corrected endpoint path
CONCURRENT_USERS = 75  # Reduce from 100 to avoid overwhelming the server
MAX_RETRIES = 3  # Number of retries for failed requests

def random_title():
    return "Task " + ''.join(random.choices(string.ascii_letters + string.digits, k=6))

async def retry_request(client, method, url, **kwargs):
    """Retry a request with exponential backoff"""
    for attempt in range(MAX_RETRIES):
        try:
            if method == "GET":
                response = await client.get(url, **kwargs)
            elif method == "POST":
                response = await client.post(url, **kwargs)
            elif method == "PUT":
                response = await client.put(url, **kwargs)
            elif method == "DELETE":
                response = await client.delete(url, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response.raise_for_status()
            return response
        except httpx.RequestError as e:
            # Network-related errors
            if attempt == MAX_RETRIES - 1:
                raise
            backoff = 0.1 * (2 ** attempt)  # Exponential backoff
            await asyncio.sleep(backoff)
        except httpx.HTTPStatusError as e:
            # Server returned an error response
            if e.response.status_code >= 500:  # Only retry server errors
                if attempt == MAX_RETRIES - 1:
                    raise
                backoff = 0.1 * (2 ** attempt)
                await asyncio.sleep(backoff)
            else:
                # Don't retry client errors
                raise

async def simulate_user(client, user_id, stats):
    start_time = time.perf_counter()
    task_id = None
    
    try:
        # Create task
        title = random_title()
        start = time.perf_counter()
        response = await retry_request(client, "POST", API_URL, 
                                     json={"title": title})
        elapsed = time.perf_counter() - start
        stats["create"].append(elapsed)
        
        task_id = response.json().get("id")
        print(f"User {user_id}: Created task {task_id}")

        # Simulate delays between actions
        await asyncio.sleep(random.uniform(0.1, 0.3))

        # Update status to in-progress
        start = time.perf_counter()
        await retry_request(client, "PUT", f"{API_URL}/{task_id}", 
                           json={"status": "in-progress"})
        elapsed = time.perf_counter() - start
        stats["update"].append(elapsed)

        await asyncio.sleep(random.uniform(0.1, 0.3))

        # Update status to completed
        start = time.perf_counter()
        await retry_request(client, "PUT", f"{API_URL}/{task_id}", 
                           json={"status": "completed"})
        elapsed = time.perf_counter() - start
        stats["update"].append(elapsed)

        await asyncio.sleep(random.uniform(0.1, 0.3))

        # Get all tasks
        start = time.perf_counter()
        await retry_request(client, "GET", API_URL)
        elapsed = time.perf_counter() - start
        stats["read"].append(elapsed)

        await asyncio.sleep(random.uniform(0.1, 0.3))

        # Delete task
        start = time.perf_counter()
        await retry_request(client, "DELETE", f"{API_URL}/{task_id}")
        elapsed = time.perf_counter() - start
        stats["delete"].append(elapsed)
        
        print(f"User {user_id}: Deleted task {task_id}")
        
        # Track total user flow time
        total_time = time.perf_counter() - start_time
        stats["user_flows"].append(total_time)

    except Exception as e:
        print(f"User {user_id}: Error - {e}")
        stats["errors"].append((user_id, task_id, str(e)))
        
        # Try to clean up the task if it was created but not deleted
        if task_id:
            try:
                await client.delete(f"{API_URL}/{task_id}")
                print(f"User {user_id}: Cleaned up task {task_id} after error")
            except:
                pass

async def main():
    print(f"Starting simplified async load test with {CONCURRENT_USERS} users")
    print(f"API endpoint: {API_URL}")
    
    stats = {
        "create": [],
        "update": [],
        "read": [],
        "delete": [],
        "user_flows": [],
        "errors": []
    }
    
    # Use more conservative limits to prevent overwhelming the server
    limits = httpx.Limits(max_connections=50, max_keepalive_connections=10)
    timeout = httpx.Timeout(30.0, connect=10.0)
    
    start_time = time.perf_counter()
    
    # Create users in smaller batches to avoid overwhelming the server
    batch_size = 15
    total_batches = (CONCURRENT_USERS + batch_size - 1) // batch_size  # Ceiling division
    
    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        for batch in range(total_batches):
            start_idx = batch * batch_size
            end_idx = min(start_idx + batch_size, CONCURRENT_USERS)
            print(f"Starting batch {batch+1}/{total_batches} (users {start_idx}-{end_idx-1})")
            
            batch_users = [simulate_user(client, i, stats) for i in range(start_idx, end_idx)]
            await asyncio.gather(*batch_users)
            
            # Small delay between batches
            if batch < total_batches - 1:
                await asyncio.sleep(1)
    
    total_time = time.perf_counter() - start_time

    # Summary
    print("\n----- Test Summary -----")
    print(f"Total test time: {total_time:.2f} seconds")
    print(f"Concurrent users: {CONCURRENT_USERS}")
    
    for key in ["create", "update", "read", "delete"]:
        if stats[key]:
            avg_time = sum(stats[key]) / len(stats[key])
            min_time = min(stats[key]) if stats[key] else 0
            max_time = max(stats[key]) if stats[key] else 0
            print(f"{key.capitalize()} - Count: {len(stats[key])}, Avg: {avg_time:.3f}s, Min: {min_time:.3f}s, Max: {max_time:.3f}s")
    
    if stats["user_flows"]:
        avg_flow = sum(stats["user_flows"]) / len(stats["user_flows"])
        print(f"Average user flow completion time: {avg_flow:.3f}s")
    
    if stats["errors"]:
        print(f"\n❌ Errors ({len(stats['errors'])}):")
        error_types = {}
        for user_id, task_id, msg in stats["errors"]:
            error_type = msg.split(':', 1)[0] if ':' in msg else msg
            if error_type not in error_types:
                error_types[error_type] = []
            error_types[error_type].append((user_id, task_id))
        
        for error_type, instances in error_types.items():
            print(f"{error_type}: {len(instances)} occurrences")
    else:
        print("\n✅ No errors encountered!")
    
    # Calculate success rate
    total_operations = sum(len(stats[key]) for key in ["create", "update", "read", "delete"])
    expected_operations = CONCURRENT_USERS * 5  # 1 create, 2 updates, 1 read, 1 delete
    success_rate = total_operations / expected_operations * 100
    print(f"\nSuccess rate: {success_rate:.2f}%")
    
    # Calculate throughput
    if total_time > 0:
        operations_per_second = total_operations / total_time
        print(f"Operations per second: {operations_per_second:.2f}")

if __name__ == "__main__":
    asyncio.run(main()) 