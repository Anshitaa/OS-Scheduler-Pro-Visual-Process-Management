"""
Demo script for OS Scheduler Pro.
Demonstrates the application with sample process data and algorithm comparisons.
"""

from process import Process
from scheduling_algorithms import (
    fcfs_scheduling, sjf_non_preemptive, sjf_preemptive,
    priority_non_preemptive, priority_preemptive, round_robin
)


def create_sample_processes():
    """Create sample processes for demonstration."""
    return [
        Process("P1", 0, 8, 3),
        Process("P2", 1, 4, 1),
        Process("P3", 2, 9, 2),
        Process("P4", 3, 5, 4),
        Process("P5", 4, 2, 5)
    ]


def run_algorithm_comparison():
    """Run all algorithms on sample data and compare results."""
    print("OS Scheduler Pro - Algorithm Comparison Demo")
    print("=" * 60)
    
    processes = create_sample_processes()
    
    print("Sample Processes:")
    for process in processes:
        print(f"  {process}")
    print()
    
    algorithms = [
        ("First-Come, First-Served", fcfs_scheduling, {}),
        ("Shortest Job First (Non-Preemptive)", sjf_non_preemptive, {}),
        ("Shortest Job First (Preemptive)", sjf_preemptive, {}),
        ("Priority (Non-Preemptive)", priority_non_preemptive, {}),
        ("Priority (Preemptive)", priority_preemptive, {}),
        ("Round Robin (Q=2)", round_robin, {"time_quantum": 2.0}),
        ("Round Robin (Q=4)", round_robin, {"time_quantum": 4.0}),
    ]
    
    results = {}
    
    print("Algorithm Results:")
    print("-" * 60)
    print(f"{'Algorithm':<30} {'Avg Wait':<10} {'Avg Turn':<10} {'CPU Util%':<10}")
    print("-" * 60)
    
    for name, func, kwargs in algorithms:
        try:
            result = func(processes, **kwargs)
            results[name] = result
            
            avg_wait = result.metrics['average_waiting_time']
            avg_turn = result.metrics['average_turnaround_time']
            cpu_util = result.metrics['cpu_utilization']
            
            print(f"{name:<30} {avg_wait:<10.2f} {avg_turn:<10.2f} {cpu_util:<10.2f}")
            
        except Exception as e:
            print(f"{name:<30} ERROR: {str(e)}")
    
    print()
    
    # Detailed analysis
    print("Detailed Analysis:")
    print("-" * 60)
    
    for name, result in results.items():
        print(f"\n{name}:")
        print(f"  Schedule entries: {len(result.schedule)}")
        print(f"  Average waiting time: {result.metrics['average_waiting_time']:.2f}")
        print(f"  Average turnaround time: {result.metrics['average_turnaround_time']:.2f}")
        print(f"  CPU utilization: {result.metrics['cpu_utilization']:.2f}%")
        print(f"  Total time: {result.metrics['total_time']:.2f}")
        
        # Show first few schedule entries
        print("  Schedule preview:")
        for i, (pid, start, end) in enumerate(result.schedule[:5]):
            print(f"    {pid}: {start:.1f} - {end:.1f}")
        if len(result.schedule) > 5:
            print(f"    ... and {len(result.schedule) - 5} more entries")


def demonstrate_algorithm_behavior():
    """Demonstrate specific algorithm behaviors."""
    print("\n" + "=" * 60)
    print("Algorithm Behavior Demonstrations")
    print("=" * 60)
    
    # Test case 1: FCFS vs SJF
    print("\n1. FCFS vs SJF Comparison:")
    print("-" * 30)
    
    test_processes = [
        Process("P1", 0, 10, 1),  # Long process arrives first
        Process("P2", 1, 1, 2),   # Short process arrives second
        Process("P3", 2, 2, 3)    # Medium process arrives third
    ]
    
    fcfs_result = fcfs_scheduling(test_processes)
    sjf_result = sjf_non_preemptive(test_processes)
    
    print(f"FCFS Average Waiting Time: {fcfs_result.metrics['average_waiting_time']:.2f}")
    print(f"SJF Average Waiting Time:  {sjf_result.metrics['average_waiting_time']:.2f}")
    print(f"Improvement: {((fcfs_result.metrics['average_waiting_time'] - sjf_result.metrics['average_waiting_time']) / fcfs_result.metrics['average_waiting_time'] * 100):.1f}%")
    
    # Test case 2: Preemptive vs Non-Preemptive
    print("\n2. Preemptive vs Non-Preemptive Priority:")
    print("-" * 40)
    
    priority_processes = [
        Process("P1", 0, 8, 3),   # Low priority, arrives first
        Process("P2", 2, 4, 1),   # High priority, arrives later
        Process("P3", 4, 6, 2)    # Medium priority, arrives last
    ]
    
    non_preemptive_result = priority_non_preemptive(priority_processes)
    preemptive_result = priority_preemptive(priority_processes)
    
    print(f"Non-Preemptive Avg Waiting: {non_preemptive_result.metrics['average_waiting_time']:.2f}")
    print(f"Preemptive Avg Waiting:     {preemptive_result.metrics['average_waiting_time']:.2f}")
    print(f"Improvement: {((non_preemptive_result.metrics['average_waiting_time'] - preemptive_result.metrics['average_waiting_time']) / non_preemptive_result.metrics['average_waiting_time'] * 100):.1f}%")
    
    # Test case 3: Round Robin with different time quanta
    print("\n3. Round Robin Time Quantum Impact:")
    print("-" * 35)
    
    rr_processes = [
        Process("P1", 0, 10),
        Process("P2", 0, 8),
        Process("P3", 0, 6),
        Process("P4", 0, 4)
    ]
    
    for quantum in [1, 2, 4, 8]:
        result = round_robin(rr_processes, time_quantum=quantum)
        print(f"Quantum {quantum}: Avg Waiting = {result.metrics['average_waiting_time']:.2f}, "
              f"Schedule entries = {len(result.schedule)}")


def show_gantt_chart_example():
    """Show a simple Gantt chart representation."""
    print("\n" + "=" * 60)
    print("Gantt Chart Example (FCFS)")
    print("=" * 60)
    
    simple_processes = [
        Process("P1", 0, 3),
        Process("P2", 1, 2),
        Process("P3", 2, 4)
    ]
    
    result = fcfs_scheduling(simple_processes)
    
    print("Process execution timeline:")
    print("Time: 0    1    2    3    4    5    6    7    8    9")
    print("      |----|----|----|----|----|----|----|----|----|")
    
    # Create a simple text-based Gantt chart
    timeline = {}
    for pid, start, end in result.schedule:
        if pid != "IDLE":
            for t in range(int(start), int(end)):
                timeline[t] = pid
    
    chart_line = ""
    for t in range(10):
        if t in timeline:
            chart_line += f"{timeline[t]:<4}"
        else:
            chart_line += "    "
    
    print(f"      {chart_line}")
    print(f"\nSchedule details:")
    for pid, start, end in result.schedule:
        print(f"  {pid}: {start:.1f} - {end:.1f} (duration: {end-start:.1f})")


if __name__ == "__main__":
    try:
        run_algorithm_comparison()
        demonstrate_algorithm_behavior()
        show_gantt_chart_example()
        
        print("\n" + "=" * 60)
        print("Demo completed! Run 'python main.py' to start the GUI application.")
        print("=" * 60)
        
    except Exception as e:
        print(f"Demo error: {str(e)}")
        import traceback
        traceback.print_exc()
