"""
Process class definition for OS Scheduler Pro.
Represents a single process with its scheduling attributes.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Process:
    """
    Represents a process in the scheduling simulation.
    
    Attributes:
        pid: Process ID (unique identifier)
        arrival_time: Time when process arrives in the system (seconds)
        burst_time: Total CPU time required by the process (seconds)
        priority: Process priority (lower number = higher priority)
        remaining_time: Remaining CPU time (used for preemptive algorithms)
    """
    pid: str
    arrival_time: float
    burst_time: float
    priority: Optional[int] = None
    remaining_time: Optional[float] = None
    
    def __post_init__(self):
        """Initialize remaining_time to burst_time if not provided."""
        if self.remaining_time is None:
            self.remaining_time = self.burst_time
    
    def __str__(self):
        """String representation of the process."""
        priority_str = f", Priority: {self.priority}" if self.priority is not None else ""
        return (f"Process {self.pid} (Arrival: {self.arrival_time}s, "
                f"Burst: {self.burst_time}s{priority_str})")
    
    def is_completed(self) -> bool:
        """Check if the process has completed execution."""
        return self.remaining_time <= 0
    
    def execute(self, time_quantum: float) -> float:
        """
        Execute the process for a given time quantum.
        
        Args:
            time_quantum: Maximum time to execute (for Round Robin)
            
        Returns:
            Actual execution time
        """
        execution_time = min(time_quantum, self.remaining_time)
        self.remaining_time -= execution_time
        return execution_time
