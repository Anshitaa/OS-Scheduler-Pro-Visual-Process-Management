"""
Unit tests for scheduling algorithms.
Tests the correctness of all implemented scheduling algorithms.
"""

import unittest
from process import Process
from scheduling_algorithms import (
    fcfs_scheduling, sjf_non_preemptive, sjf_preemptive,
    priority_non_preemptive, priority_preemptive, round_robin,
    calculate_metrics
)


class TestSchedulingAlgorithms(unittest.TestCase):
    """Test cases for scheduling algorithms."""
    
    def setUp(self):
        """Set up test data."""
        # Sample processes for testing
        self.test_processes = [
            Process("P1", 0, 8, 3),
            Process("P2", 1, 4, 1),
            Process("P3", 2, 9, 2),
            Process("P4", 3, 5, 4)
        ]
        
        # Simple test case
        self.simple_processes = [
            Process("P1", 0, 3),
            Process("P2", 1, 1),
            Process("P3", 2, 2)
        ]
    
    def test_fcfs_scheduling(self):
        """Test FCFS scheduling algorithm."""
        result = fcfs_scheduling(self.simple_processes)
        
        # Verify schedule order (should be by arrival time)
        self.assertEqual(result.algorithm_name, "First-Come, First-Served (FCFS)")
        self.assertEqual(len(result.schedule), 3)
        
        # First process should start at arrival time
        self.assertEqual(result.schedule[0], ("P1", 0, 3))
        self.assertEqual(result.schedule[1], ("P2", 3, 4))
        self.assertEqual(result.schedule[2], ("P3", 4, 6))
        
        # Verify metrics
        self.assertIn("average_waiting_time", result.metrics)
        self.assertIn("average_turnaround_time", result.metrics)
        self.assertIn("cpu_utilization", result.metrics)
    
    def test_sjf_non_preemptive(self):
        """Test SJF non-preemptive scheduling algorithm."""
        result = sjf_non_preemptive(self.simple_processes)
        
        self.assertEqual(result.algorithm_name, "Shortest Job First (Non-Preemptive)")
        
        # Verify that shortest jobs are scheduled first when available
        # P1 starts first (arrives at 0), then P2 (shortest), then P3
        self.assertEqual(result.schedule[0], ("P1", 0, 3))
        self.assertEqual(result.schedule[1], ("P2", 3, 4))  # Shortest remaining
        self.assertEqual(result.schedule[2], ("P3", 4, 6))
    
    def test_sjf_preemptive(self):
        """Test SJF preemptive scheduling algorithm."""
        # Test case where preemption should occur
        processes = [
            Process("P1", 0, 8),  # Long process
            Process("P2", 2, 4),  # Shorter, arrives later
            Process("P3", 4, 2)   # Shortest, arrives later
        ]
        
        result = sjf_preemptive(processes)
        self.assertEqual(result.algorithm_name, "Shortest Job First (Preemptive)")
        
        # Should have multiple schedule entries due to preemption
        self.assertGreater(len(result.schedule), 3)
        
        # Verify metrics are calculated correctly
        self.assertIn("average_waiting_time", result.metrics)
        self.assertIn("average_turnaround_time", result.metrics)
    
    def test_priority_non_preemptive(self):
        """Test Priority non-preemptive scheduling algorithm."""
        result = priority_non_preemptive(self.test_processes)
        
        self.assertEqual(result.algorithm_name, "Priority (Non-Preemptive)")
        
        # P1 arrives first at time 0, so it starts first (non-preemptive)
        # P2 has highest priority (1) but arrives later
        self.assertEqual(result.schedule[0], ("P1", 0, 8))
        
        # Verify metrics
        self.assertIn("average_waiting_time", result.metrics)
    
    def test_priority_preemptive(self):
        """Test Priority preemptive scheduling algorithm."""
        result = priority_preemptive(self.test_processes)
        
        self.assertEqual(result.algorithm_name, "Priority (Preemptive)")
        
        # Should have multiple schedule entries due to preemption
        self.assertGreater(len(result.schedule), 4)
        
        # Verify metrics
        self.assertIn("average_waiting_time", result.metrics)
    
    def test_round_robin(self):
        """Test Round Robin scheduling algorithm."""
        result = round_robin(self.simple_processes, time_quantum=2.0)
        
        self.assertIn("Round Robin", result.algorithm_name)
        self.assertIn("Quantum: 2.0", result.algorithm_name)
        
        # Should have multiple schedule entries due to time quantum
        self.assertGreater(len(result.schedule), 3)
        
        # Verify metrics
        self.assertIn("average_waiting_time", result.metrics)
    
    def test_empty_process_list(self):
        """Test handling of empty process list."""
        result = fcfs_scheduling([])
        self.assertEqual(result.schedule, [])
        self.assertEqual(result.metrics, {})
    
    def test_single_process(self):
        """Test scheduling with single process."""
        single_process = [Process("P1", 0, 5)]
        result = fcfs_scheduling(single_process)
        
        self.assertEqual(len(result.schedule), 1)
        self.assertEqual(result.schedule[0], ("P1", 0, 5))
        
        # Metrics should be calculated correctly
        self.assertEqual(result.metrics["average_waiting_time"], 0)
        self.assertEqual(result.metrics["average_turnaround_time"], 5)
        self.assertEqual(result.metrics["cpu_utilization"], 100.0)
    
    def test_processes_with_idle_time(self):
        """Test scheduling when there are gaps between process arrivals."""
        processes = [
            Process("P1", 0, 2),
            Process("P2", 5, 3)  # Gap between arrivals
        ]
        
        result = fcfs_scheduling(processes)
        
        # Should have idle time between processes
        idle_found = any(pid == "IDLE" for pid, _, _ in result.schedule)
        self.assertTrue(idle_found)
        
        # Verify total time includes idle time
        total_time = max(end_time for _, _, end_time in result.schedule)
        self.assertEqual(total_time, 8)  # 2 + 3 + 3 idle
    
    def test_calculate_metrics(self):
        """Test metrics calculation function."""
        processes = [
            Process("P1", 0, 3),
            Process("P2", 1, 2)
        ]
        
        schedule = [
            ("P1", 0, 3),
            ("P2", 3, 5)
        ]
        
        metrics = calculate_metrics(processes, schedule)
        
        # P1: turnaround = 3, waiting = 0
        # P2: turnaround = 4, waiting = 2
        expected_avg_turnaround = (3 + 4) / 2
        expected_avg_waiting = (0 + 2) / 2
        expected_cpu_utilization = 5 / 5 * 100  # 100% utilization
        
        self.assertEqual(metrics["average_turnaround_time"], expected_avg_turnaround)
        self.assertEqual(metrics["average_waiting_time"], expected_avg_waiting)
        self.assertEqual(metrics["cpu_utilization"], expected_cpu_utilization)
        self.assertEqual(metrics["total_processes"], 2)
        self.assertEqual(metrics["total_time"], 5)
    
    def test_round_robin_time_quantum(self):
        """Test Round Robin with different time quantum."""
        processes = [Process("P1", 0, 5), Process("P2", 0, 3)]
        
        result1 = round_robin(processes, time_quantum=1.0)
        result2 = round_robin(processes, time_quantum=3.0)
        
        # Smaller quantum should result in more schedule entries
        self.assertGreater(len(result1.schedule), len(result2.schedule))
        
        # Both should complete all processes
        self.assertEqual(result1.metrics["total_processes"], 2)
        self.assertEqual(result2.metrics["total_processes"], 2)
    
    def test_priority_without_priority_assigned(self):
        """Test that priority algorithms raise error when priority is missing."""
        processes_no_priority = [
            Process("P1", 0, 3),  # No priority assigned
            Process("P2", 1, 2, 1)
        ]
        
        with self.assertRaises(ValueError):
            priority_non_preemptive(processes_no_priority)
        
        with self.assertRaises(ValueError):
            priority_preemptive(processes_no_priority)
    
    def test_round_robin_invalid_quantum(self):
        """Test Round Robin with invalid time quantum."""
        with self.assertRaises(ValueError):
            round_robin(self.simple_processes, time_quantum=0)
        
        with self.assertRaises(ValueError):
            round_robin(self.simple_processes, time_quantum=-1)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
