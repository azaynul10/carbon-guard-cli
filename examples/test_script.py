#!/usr/bin/env python3
"""Example script for testing local carbon auditing."""

import time
import random
import math

def cpu_intensive_task():
    """Simulate CPU-intensive computation."""
    print("Starting CPU-intensive task...")
    
    # Calculate prime numbers
    primes = []
    for num in range(2, 10000):
        is_prime = True
        for i in range(2, int(math.sqrt(num)) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    
    print(f"Found {len(primes)} prime numbers")
    return primes

def memory_intensive_task():
    """Simulate memory-intensive operations."""
    print("Starting memory-intensive task...")
    
    # Create large data structures
    data = []
    for i in range(100000):
        data.append([random.random() for _ in range(100)])
    
    # Process the data
    processed = []
    for row in data:
        processed.append(sum(row) / len(row))
    
    print(f"Processed {len(processed)} data points")
    return processed

def io_intensive_task():
    """Simulate I/O intensive operations."""
    print("Starting I/O intensive task...")
    
    # Write temporary files
    for i in range(10):
        filename = f"/tmp/test_file_{i}.txt"
        with open(filename, 'w') as f:
            for j in range(1000):
                f.write(f"Line {j}: {random.random()}\n")
    
    # Read files back
    total_lines = 0
    for i in range(10):
        filename = f"/tmp/test_file_{i}.txt"
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
                total_lines += len(lines)
        except FileNotFoundError:
            pass
    
    print(f"Read {total_lines} total lines")
    return total_lines

def main():
    """Main function that runs various tasks."""
    print("Starting carbon footprint test script...")
    
    # Run different types of tasks
    start_time = time.time()
    
    # CPU task
    primes = cpu_intensive_task()
    time.sleep(2)
    
    # Memory task
    averages = memory_intensive_task()
    time.sleep(2)
    
    # I/O task
    lines = io_intensive_task()
    time.sleep(2)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\nScript completed in {duration:.2f} seconds")
    print(f"Results: {len(primes)} primes, {len(averages)} averages, {lines} lines")
    
    return {
        'duration': duration,
        'primes_count': len(primes),
        'averages_count': len(averages),
        'lines_count': lines
    }

if __name__ == "__main__":
    results = main()
    print(f"Final results: {results}")
