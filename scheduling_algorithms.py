"""
Scheduling algorithms implementation for OS Scheduler Pro.
Contains all the core scheduling algorithms and performance metrics calculations.
"""

from typing import List, Tuple, Dict, Any
from process import Process
import heapq
from collections import deque


class SchedulingResult:
    """Container for scheduling algorithm results."""
    
    def __init__(self, schedule: List[Tuple[str, float, float]], 
                 metrics: Dict[str, float], algorithm_name: str):
        self.schedule = schedule  # List of (process_id, start_time, end_time)
        self.metrics = metrics    # Dictionary of performance metrics
        self.algorithm_name = algorithm_name


def calculate_metrics(processes: List[Process], 
                     schedule: List[Tuple[str, float, float]]) -> Dict[str, float]:
    """
    Calculate performance metrics from the scheduling result.
    
    Args:
        processes: Original list of processes
        schedule: List of (process_id, start_time, end_time) tuples
        
    Returns:
        Dictionary containing performance metrics
    """
    # Create a mapping of process ID to process object
    process_map = {p.pid: p for p in processes}
    
    # Calculate completion time for each process
    completion_times = {}
    for pid, start_time, end_time in schedule:
        if pid != "IDLE":
            completion_times[pid] = end_time
    
    # Calculate turnaround time and waiting time for each process
    turnaround_times = []
    waiting_times = []
    
    for process in processes:
        if process.pid in completion_times:
            completion_time = completion_times[process.pid]
            turnaround_time = completion_time - process.arrival_time
            waiting_time = turnaround_time - process.burst_time
            
            turnaround_times.append(turnaround_time)
            waiting_times.append(waiting_time)
    
    # Calculate averages
    avg_turnaround_time = sum(turnaround_times) / len(turnaround_times) if turnaround_times else 0
    avg_waiting_time = sum(waiting_times) / len(waiting_times) if waiting_times else 0
    
    # Calculate CPU utilization
    total_time = max(end_time for _, _, end_time in schedule) if schedule else 0
    cpu_time = sum(end_time - start_time for _, start_time, end_time in schedule 
                   if _ != "IDLE")
    cpu_utilization = (cpu_time / total_time * 100) if total_time > 0 else 0
    
    return {
        "average_turnaround_time": round(avg_turnaround_time, 2),
        "average_waiting_time": round(avg_waiting_time, 2),
        "cpu_utilization": round(cpu_utilization, 2),
        "total_processes": len(processes),
        "total_time": round(total_time, 2)
    }


def fcfs_scheduling(processes: List[Process]) -> SchedulingResult:
    """
    First-Come, First-Served scheduling algorithm.
    
    Args:
        processes: List of processes to schedule
        
    Returns:
        SchedulingResult containing schedule and metrics
    """
    if not processes:
        return SchedulingResult([], {}, "FCFS")
    
    # Sort processes by arrival time
    sorted_processes = sorted(processes, key=lambda p: (p.arrival_time, p.pid))
    
    schedule = []
    current_time = 0
    
    for process in sorted_processes:
        # If process hasn't arrived yet, wait
        if current_time < process.arrival_time:
            schedule.append(("IDLE", current_time, process.arrival_time))
            current_time = process.arrival_time
        
        # Execute the process
        start_time = current_time
        end_time = current_time + process.burst_time
        schedule.append((process.pid, start_time, end_time))
        current_time = end_time
    
    metrics = calculate_metrics(processes, schedule)
    return SchedulingResult(schedule, metrics, "First-Come, First-Served (FCFS)")


def sjf_non_preemptive(processes: List[Process]) -> SchedulingResult:
    """
    Shortest Job First scheduling algorithm (non-preemptive).
    
    Args:
        processes: List of processes to schedule
        
    Returns:
        SchedulingResult containing schedule and metrics
    """
    if not processes:
        return SchedulingResult([], {}, "SJF Non-Preemptive")
    
    # Create copies to avoid modifying original processes
    processes_copy = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) 
                     for p in processes]
    
    schedule = []
    current_time = 0
    completed_processes = set()
    
    while len(completed_processes) < len(processes_copy):
        # Find processes that have arrived and not completed
        available_processes = [
            p for p in processes_copy 
            if p.pid not in completed_processes and p.arrival_time <= current_time
        ]
        
        if not available_processes:
            # No processes available, find the next arriving process
            next_process = min(
                [p for p in processes_copy if p.pid not in completed_processes],
                key=lambda p: p.arrival_time
            )
            schedule.append(("IDLE", current_time, next_process.arrival_time))
            current_time = next_process.arrival_time
            continue
        
        # Select the process with shortest burst time
        selected_process = min(available_processes, key=lambda p: (p.burst_time, p.pid))
        
        # Execute the process completely
        start_time = current_time
        end_time = current_time + selected_process.burst_time
        schedule.append((selected_process.pid, start_time, end_time))
        current_time = end_time
        completed_processes.add(selected_process.pid)
    
    metrics = calculate_metrics(processes, schedule)
    return SchedulingResult(schedule, metrics, "Shortest Job First (Non-Preemptive)")


def sjf_preemptive(processes: List[Process]) -> SchedulingResult:
    """
    Shortest Job First scheduling algorithm (preemptive).
    
    Args:
        processes: List of processes to schedule
        
    Returns:
        SchedulingResult containing schedule and metrics
    """
    if not processes:
        return SchedulingResult([], {}, "SJF Preemptive")
    
    # Create copies to avoid modifying original processes
    processes_copy = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) 
                     for p in processes]
    
    schedule = []
    current_time = 0
    ready_queue = []  # Min-heap based on remaining time
    completed_processes = set()
    
    # Sort processes by arrival time
    processes_copy.sort(key=lambda p: (p.arrival_time, p.pid))
    
    i = 0  # Index for processes not yet arrived
    current_process = None
    
    while len(completed_processes) < len(processes_copy):
        # Add newly arrived processes to ready queue
        while i < len(processes_copy) and processes_copy[i].arrival_time <= current_time:
            heapq.heappush(ready_queue, (processes_copy[i].remaining_time, processes_copy[i].pid, processes_copy[i]))
            i += 1
        
        # Determine which process should run next
        next_process = None
        if ready_queue:
            _, _, next_process = heapq.heappop(ready_queue)
        
        # If current process is different, switch context
        if current_process is None or (next_process and current_process and next_process.pid != current_process.pid):
            if current_process and not current_process.is_completed():
                # Put current process back in queue
                heapq.heappush(ready_queue, (current_process.remaining_time, current_process.pid, current_process))
            
            current_process = next_process
        
        if current_process is None:
            # No processes ready, wait for next arrival
            if i < len(processes_copy):
                next_arrival = processes_copy[i].arrival_time
                schedule.append(("IDLE", current_time, next_arrival))
                current_time = next_arrival
            else:
                break
        
        # Execute current process for 1 time unit
        execution_time = current_process.execute(1.0)
        start_time = current_time
        end_time = current_time + execution_time
        
        # Add to schedule if this is a new execution or continuation
        if not schedule or schedule[-1][0] != current_process.pid or schedule[-1][2] != start_time:
            schedule.append((current_process.pid, start_time, end_time))
        else:
            # Extend the last schedule entry
            schedule[-1] = (current_process.pid, schedule[-1][1], end_time)
        
        current_time = end_time
        
        # Check if process completed
        if current_process.is_completed():
            completed_processes.add(current_process.pid)
            current_process = None
    
    metrics = calculate_metrics(processes, schedule)
    return SchedulingResult(schedule, metrics, "Shortest Job First (Preemptive)")


def priority_non_preemptive(processes: List[Process]) -> SchedulingResult:
    """
    Priority scheduling algorithm (non-preemptive).
    
    Args:
        processes: List of processes to schedule
        
    Returns:
        SchedulingResult containing schedule and metrics
    """
    if not processes:
        return SchedulingResult([], {}, "Priority Non-Preemptive")
    
    # Validate that all processes have priorities
    for process in processes:
        if process.priority is None:
            raise ValueError(f"Process {process.pid} does not have a priority assigned")
    
    # Create copies to avoid modifying original processes
    processes_copy = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) 
                     for p in processes]
    
    schedule = []
    current_time = 0
    completed_processes = set()
    
    while len(completed_processes) < len(processes_copy):
        # Find processes that have arrived and not completed
        available_processes = [
            p for p in processes_copy 
            if p.pid not in completed_processes and p.arrival_time <= current_time
        ]
        
        if not available_processes:
            # No processes available, find the next arriving process
            next_process = min(
                [p for p in processes_copy if p.pid not in completed_processes],
                key=lambda p: p.arrival_time
            )
            schedule.append(("IDLE", current_time, next_process.arrival_time))
            current_time = next_process.arrival_time
            continue
        
        # Select the process with highest priority (lowest priority number)
        selected_process = min(available_processes, key=lambda p: (p.priority, p.pid))
        
        # Execute the process completely
        start_time = current_time
        end_time = current_time + selected_process.burst_time
        schedule.append((selected_process.pid, start_time, end_time))
        current_time = end_time
        completed_processes.add(selected_process.pid)
    
    metrics = calculate_metrics(processes, schedule)
    return SchedulingResult(schedule, metrics, "Priority (Non-Preemptive)")


def priority_preemptive(processes: List[Process]) -> SchedulingResult:
    """
    Priority scheduling algorithm (preemptive).
    
    Args:
        processes: List of processes to schedule
        
    Returns:
        SchedulingResult containing schedule and metrics
    """
    if not processes:
        return SchedulingResult([], {}, "Priority Preemptive")
    
    # Validate that all processes have priorities
    for process in processes:
        if process.priority is None:
            raise ValueError(f"Process {process.pid} does not have a priority assigned")
    
    # Create copies to avoid modifying original processes
    processes_copy = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) 
                     for p in processes]
    
    schedule = []
    current_time = 0
    ready_queue = []  # Min-heap based on priority
    completed_processes = set()
    
    # Sort processes by arrival time
    processes_copy.sort(key=lambda p: (p.arrival_time, p.pid))
    
    i = 0  # Index for processes not yet arrived
    current_process = None
    
    while len(completed_processes) < len(processes_copy):
        # Add newly arrived processes to ready queue
        while i < len(processes_copy) and processes_copy[i].arrival_time <= current_time:
            heapq.heappush(ready_queue, (processes_copy[i].priority, processes_copy[i].pid, processes_copy[i]))
            i += 1
        
        # Determine which process should run next
        next_process = None
        if ready_queue:
            _, _, next_process = heapq.heappop(ready_queue)
        
        # If current process is different, switch context
        if current_process is None or (next_process and current_process and next_process.pid != current_process.pid):
            if current_process and not current_process.is_completed():
                # Put current process back in queue
                heapq.heappush(ready_queue, (current_process.priority, current_process.pid, current_process))
            
            current_process = next_process
        
        if current_process is None:
            # No processes ready, wait for next arrival
            if i < len(processes_copy):
                next_arrival = processes_copy[i].arrival_time
                schedule.append(("IDLE", current_time, next_arrival))
                current_time = next_arrival
            else:
                break
        
        # Execute current process for 1 time unit
        execution_time = current_process.execute(1.0)
        start_time = current_time
        end_time = current_time + execution_time
        
        # Add to schedule if this is a new execution or continuation
        if not schedule or schedule[-1][0] != current_process.pid or schedule[-1][2] != start_time:
            schedule.append((current_process.pid, start_time, end_time))
        else:
            # Extend the last schedule entry
            schedule[-1] = (current_process.pid, schedule[-1][1], end_time)
        
        current_time = end_time
        
        # Check if process completed
        if current_process.is_completed():
            completed_processes.add(current_process.pid)
            current_process = None
    
    metrics = calculate_metrics(processes, schedule)
    return SchedulingResult(schedule, metrics, "Priority (Preemptive)")


def round_robin(processes: List[Process], time_quantum: float = 2.0) -> SchedulingResult:
    """
    Round Robin scheduling algorithm.
    
    Args:
        processes: List of processes to schedule
        time_quantum: Time quantum for Round Robin scheduling
        
    Returns:
        SchedulingResult containing schedule and metrics
    """
    if not processes:
        return SchedulingResult([], {}, "Round Robin")
    
    if time_quantum <= 0:
        raise ValueError("Time quantum must be positive")
    
    # Create copies to avoid modifying original processes
    processes_copy = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) 
                     for p in processes]
    
    schedule = []
    current_time = 0
    ready_queue = deque()
    completed_processes = set()
    
    # Sort processes by arrival time
    processes_copy.sort(key=lambda p: (p.arrival_time, p.pid))
    
    i = 0  # Index for processes not yet arrived
    
    # Add all processes that arrive at time 0
    while i < len(processes_copy) and processes_copy[i].arrival_time <= current_time:
        ready_queue.append(processes_copy[i])
        i += 1
    
    while len(completed_processes) < len(processes_copy):
        if not ready_queue:
            # No processes ready, wait for next arrival
            if i < len(processes_copy):
                next_arrival = processes_copy[i].arrival_time
                schedule.append(("IDLE", current_time, next_arrival))
                current_time = next_arrival
                
                # Add newly arrived processes
                while i < len(processes_copy) and processes_copy[i].arrival_time <= current_time:
                    ready_queue.append(processes_copy[i])
                    i += 1
            else:
                break
        
        # Get the next process from the queue
        current_process = ready_queue.popleft()
        
        # Execute the process for the time quantum or until completion
        execution_time = current_process.execute(time_quantum)
        start_time = current_time
        end_time = current_time + execution_time
        
        # Add to schedule if this is a new execution or continuation
        if not schedule or schedule[-1][0] != current_process.pid or schedule[-1][2] != start_time:
            schedule.append((current_process.pid, start_time, end_time))
        else:
            # Extend the last schedule entry
            schedule[-1] = (current_process.pid, schedule[-1][1], end_time)
        
        current_time = end_time
        
        # Add newly arrived processes during execution
        while i < len(processes_copy) and processes_copy[i].arrival_time <= current_time:
            ready_queue.append(processes_copy[i])
            i += 1
        
        # Check if process completed
        if current_process.is_completed():
            completed_processes.add(current_process.pid)
        else:
            # Process not completed, add it back to the queue
            ready_queue.append(current_process)
    
    metrics = calculate_metrics(processes, schedule)
    return SchedulingResult(schedule, metrics, f"Round Robin (Quantum: {time_quantum})")
