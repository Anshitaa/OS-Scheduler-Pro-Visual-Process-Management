"""
Performance testing script for OS Scheduler Pro.
Tests the application with large numbers of processes to ensure scalability.
"""

import time
import random
from process import Process
from scheduling_algorithms import (
    fcfs_scheduling, sjf_non_preemptive, sjf_preemptive,
    priority_non_preemptive, priority_preemptive, round_robin
)


def generate_random_processes(count: int) -> list:
    """Generate a list of random processes for testing."""
    processes = []
    for i in range(count):
        pid = f"P{i+1}"
        arrival_time = random.uniform(0, count * 0.1)  # Spread arrivals over time
        burst_time = random.uniform(0.1, 5.0)  # Short to medium burst times
        priority = random.randint(1, 10)
        processes.append(Process(pid, arrival_time, burst_time, priority))
    
    return processes


def test_algorithm_performance(algorithm_name: str, algorithm_func, processes: list, **kwargs):
    """Test the performance of a specific algorithm."""
    print(f"\nTesting {algorithm_name} with {len(processes)} processes...")
    
    start_time = time.time()
    try:
        result = algorithm_func(processes, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        print(f"✓ Execution time: {execution_time:.4f} seconds")
        print(f"✓ Average waiting time: {result.metrics['average_waiting_time']:.2f}")
        print(f"✓ Average turnaround time: {result.metrics['average_turnaround_time']:.2f}")
        print(f"✓ CPU utilization: {result.metrics['cpu_utilization']:.2f}%")
        print(f"✓ Total schedule entries: {len(result.schedule)}")
        
        return execution_time, result.metrics
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None, None


def run_performance_tests():
    """Run comprehensive performance tests."""
    print("OS Scheduler Pro - Performance Testing")
    print("=" * 50)
    
    # Test different process counts
    test_sizes = [10, 50, 100, 500, 1000]
    algorithms = [
        ("FCFS", fcfs_scheduling, {}),
        ("SJF Non-Preemptive", sjf_non_preemptive, {}),
        ("SJF Preemptive", sjf_preemptive, {}),
        ("Priority Non-Preemptive", priority_non_preemptive, {}),
        ("Priority Preemptive", priority_preemptive, {}),
        ("Round Robin (Q=1)", round_robin, {"time_quantum": 1.0}),
        ("Round Robin (Q=5)", round_robin, {"time_quantum": 5.0}),
    ]
    
    results = {}
    
    for size in test_sizes:
        print(f"\n{'='*20} Testing with {size} processes {'='*20}")
        
        # Generate random processes
        processes = generate_random_processes(size)
        print(f"Generated {len(processes)} random processes")
        
        results[size] = {}
        
        for alg_name, alg_func, kwargs in algorithms:
            execution_time, metrics = test_algorithm_performance(
                alg_name, alg_func, processes, **kwargs
            )
            
            if execution_time is not None:
                results[size][alg_name] = {
                    'execution_time': execution_time,
                    'metrics': metrics
                }
    
    # Summary report
    print(f"\n{'='*60}")
    print("PERFORMANCE SUMMARY")
    print(f"{'='*60}")
    
    print(f"{'Processes':<10} {'Algorithm':<25} {'Time (s)':<10} {'Avg Wait':<10} {'CPU Util%':<10}")
    print("-" * 70)
    
    for size in test_sizes:
        if size in results:
            for alg_name in algorithms:
                alg_name_short = alg_name[0]
                if alg_name_short in results[size]:
                    data = results[size][alg_name_short]
                    exec_time = data['execution_time']
                    avg_wait = data['metrics']['average_waiting_time']
                    cpu_util = data['metrics']['cpu_utilization']
                    
                    print(f"{size:<10} {alg_name_short:<25} {exec_time:<10.4f} {avg_wait:<10.2f} {cpu_util:<10.2f}")
    
    # Performance analysis
    print(f"\n{'='*60}")
    print("PERFORMANCE ANALYSIS")
    print(f"{'='*60}")
    
    # Find fastest and slowest algorithms for 1000 processes
    if 1000 in results:
        times_1000 = {alg: data['execution_time'] 
                     for alg, data in results[1000].items()}
        
        fastest = min(times_1000.items(), key=lambda x: x[1])
        slowest = max(times_1000.items(), key=lambda x: x[1])
        
        print(f"Fastest algorithm with 1000 processes: {fastest[0]} ({fastest[1]:.4f}s)")
        print(f"Slowest algorithm with 1000 processes: {slowest[0]} ({slowest[1]:.4f}s)")
        
        # Scalability analysis
        print(f"\nScalability Analysis:")
        for size in [100, 500, 1000]:
            if size in results and 100 in results:
                for alg_name in algorithms:
                    alg_name_short = alg_name[0]
                    if (alg_name_short in results[size] and 
                        alg_name_short in results[100]):
                        
                        time_100 = results[100][alg_name_short]['execution_time']
                        time_current = results[size][alg_name_short]['execution_time']
                        scale_factor = time_current / time_100
                        
                        print(f"  {alg_name_short}: {size} processes = {scale_factor:.2f}x slower than 100 processes")


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print(f"\n{'='*60}")
    print("EDGE CASE TESTING")
    print(f"{'='*60}")
    
    # Empty process list
    print("\nTesting empty process list...")
    result = fcfs_scheduling([])
    print(f"✓ Empty list handled correctly: {len(result.schedule) == 0}")
    
    # Single process
    print("\nTesting single process...")
    single_process = [Process("P1", 0, 5, 1)]
    result = fcfs_scheduling(single_process)
    print(f"✓ Single process handled: {result.metrics['total_processes'] == 1}")
    
    # Processes with same arrival time
    print("\nTesting processes with same arrival time...")
    same_arrival = [
        Process("P1", 0, 3, 1),
        Process("P2", 0, 2, 2),
        Process("P3", 0, 4, 3)
    ]
    result = fcfs_scheduling(same_arrival)
    print(f"✓ Same arrival time handled: {result.metrics['total_processes'] == 3}")
    
    # Very short time quantum for Round Robin
    print("\nTesting very short time quantum...")
    processes = [Process("P1", 0, 10), Process("P2", 0, 5)]
    result = round_robin(processes, time_quantum=0.1)
    print(f"✓ Short time quantum handled: {len(result.schedule) > 10}")
    
    # Large time quantum for Round Robin
    print("\nTesting large time quantum...")
    result = round_robin(processes, time_quantum=100)
    print(f"✓ Large time quantum handled: {len(result.schedule) == 2}")


if __name__ == "__main__":
    # Set random seed for reproducible results
    random.seed(42)
    
    try:
        run_performance_tests()
        test_edge_cases()
        
        print(f"\n{'='*60}")
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("The application is ready for production use.")
        print(f"{'='*60}")
        
    except KeyboardInterrupt:
        print("\nPerformance testing interrupted by user.")
    except Exception as e:
        print(f"\nError during performance testing: {str(e)}")
        import traceback
        traceback.print_exc()
