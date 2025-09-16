"""
OS Scheduler Pro - Main Application
Interactive desktop application for visualizing OS scheduling algorithms.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import random
from typing import List, Optional
import threading

from process import Process
from scheduling_algorithms import (
    fcfs_scheduling, sjf_non_preemptive, sjf_preemptive,
    priority_non_preemptive, priority_preemptive, round_robin
)


class ProcessTable:
    """Widget for managing process input table."""
    
    def __init__(self, parent):
        self.parent = parent
        self.processes = []
        self.setup_table()
    
    def setup_table(self):
        """Set up the process input table."""
        # Frame for table and buttons
        table_frame = ttk.Frame(self.parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Table headers
        headers = ["Process ID", "Arrival Time", "Burst Time", "Priority"]
        self.tree = ttk.Treeview(table_frame, columns=headers, show="headings", height=8)
        
        # Configure columns
        for header in headers:
            self.tree.heading(header, text=header)
            self.tree.column(header, width=100, anchor=tk.CENTER)
        
        # Scrollbar for table
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack table and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Buttons
        ttk.Button(button_frame, text="Add Process", 
                  command=self.add_process_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit Process", 
                  command=self.edit_process_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove Process", 
                  command=self.remove_process).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear All", 
                  command=self.clear_all).pack(side=tk.LEFT, padx=5)
    
    def add_process_dialog(self):
        """Open dialog to add a new process."""
        dialog = ProcessDialog(self.parent, "Add Process")
        if dialog.result:
            self.add_process(dialog.result)
    
    def edit_process_dialog(self):
        """Open dialog to edit selected process."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a process to edit.")
            return
        
        # Get current values
        item = self.tree.item(selection[0])
        values = item['values']
        
        # Create process object for editing
        process = Process(values[0], values[1], values[2], values[3] if values[3] else None)
        
        dialog = ProcessDialog(self.parent, "Edit Process", process)
        if dialog.result:
            # Remove old item and add new one
            self.tree.delete(selection[0])
            self.add_process(dialog.result)
    
    def add_process(self, process: Process):
        """Add a process to the table."""
        priority_str = str(process.priority) if process.priority is not None else ""
        self.tree.insert("", tk.END, values=(
            process.pid, process.arrival_time, process.burst_time, priority_str
        ))
        self.processes.append(process)
    
    def remove_process(self):
        """Remove selected process from table."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a process to remove.")
            return
        
        # Get process ID to remove from processes list
        item = self.tree.item(selection[0])
        pid = item['values'][0]
        
        # Remove from tree and processes list
        self.tree.delete(selection[0])
        self.processes = [p for p in self.processes if p.pid != pid]
    
    def clear_all(self):
        """Clear all processes from table."""
        self.tree.delete(*self.tree.get_children())
        self.processes.clear()
    
    def get_processes(self) -> List[Process]:
        """Get list of processes from table."""
        return self.processes.copy()


class ProcessDialog:
    """Dialog for adding/editing processes."""
    
    def __init__(self, parent, title: str, process: Optional[Process] = None):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_widgets(process)
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def setup_widgets(self, process: Optional[Process] = None):
        """Set up dialog widgets."""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Process ID
        ttk.Label(main_frame, text="Process ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.pid_var = tk.StringVar(value=process.pid if process else "")
        ttk.Entry(main_frame, textvariable=self.pid_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Arrival Time
        ttk.Label(main_frame, text="Arrival Time:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.arrival_var = tk.StringVar(value=str(process.arrival_time) if process else "")
        ttk.Entry(main_frame, textvariable=self.arrival_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Burst Time
        ttk.Label(main_frame, text="Burst Time:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.burst_var = tk.StringVar(value=str(process.burst_time) if process else "")
        ttk.Entry(main_frame, textvariable=self.burst_var, width=20).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Priority
        ttk.Label(main_frame, text="Priority (optional):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.priority_var = tk.StringVar(value=str(process.priority) if process and process.priority is not None else "")
        ttk.Entry(main_frame, textvariable=self.priority_var, width=20).grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
    
    def ok_clicked(self):
        """Handle OK button click."""
        try:
            pid = self.pid_var.get().strip()
            arrival_time = float(self.arrival_var.get())
            burst_time = float(self.burst_var.get())
            priority = None
            
            priority_str = self.priority_var.get().strip()
            if priority_str:
                priority = int(priority_str)
            
            if not pid:
                raise ValueError("Process ID cannot be empty")
            if arrival_time < 0:
                raise ValueError("Arrival time cannot be negative")
            if burst_time <= 0:
                raise ValueError("Burst time must be positive")
            if priority is not None and priority < 0:
                raise ValueError("Priority cannot be negative")
            
            self.result = Process(pid, arrival_time, burst_time, priority)
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
    
    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.dialog.destroy()


class OSchedulerPro:
    """Main application class for OS Scheduler Pro."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OS Scheduler Pro - Visual Process Management")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Configure style
        self.setup_styles()
        
        # Initialize components
        self.process_table = None
        self.algorithm_var = None
        self.time_quantum_var = None
        self.metrics_frame = None
        self.figure = None
        self.canvas = None
        
        # Setup GUI
        self.setup_gui()
        
        # Center window
        self.center_window()
    
    def setup_styles(self):
        """Set up application styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Section.TLabel', font=('Arial', 12, 'bold'))
    
    def setup_gui(self):
        """Set up the main GUI layout."""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_container, text="OS Scheduler Pro", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Create three main sections
        self.setup_controls_section(main_container)
        self.setup_visualization_section(main_container)
        self.setup_metrics_section(main_container)
    
    def setup_controls_section(self, parent):
        """Set up the controls and inputs section."""
        # Controls frame
        controls_frame = ttk.LabelFrame(parent, text="Controls & Process Input", padding=10)
        controls_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Left panel for controls
        left_panel = ttk.Frame(controls_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Process table
        self.process_table = ProcessTable(left_panel)
        
        # Right panel for algorithm controls
        right_panel = ttk.Frame(controls_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
        
        # Algorithm selection
        ttk.Label(right_panel, text="Scheduling Algorithm:", style='Section.TLabel').pack(anchor=tk.W, pady=(0, 5))
        
        algorithms = [
            "First-Come, First-Served (FCFS)",
            "Shortest Job First (Non-Preemptive)",
            "Shortest Job First (Preemptive)",
            "Priority (Non-Preemptive)",
            "Priority (Preemptive)",
            "Round Robin"
        ]
        
        self.algorithm_var = tk.StringVar(value=algorithms[0])
        algorithm_combo = ttk.Combobox(right_panel, textvariable=self.algorithm_var, 
                                      values=algorithms, state="readonly", width=30)
        algorithm_combo.pack(anchor=tk.W, pady=(0, 15))
        
        # Time quantum (for Round Robin)
        ttk.Label(right_panel, text="Time Quantum (Round Robin):", style='Section.TLabel').pack(anchor=tk.W, pady=(0, 5))
        self.time_quantum_var = tk.StringVar(value="2.0")
        ttk.Entry(right_panel, textvariable=self.time_quantum_var, width=15).pack(anchor=tk.W, pady=(0, 15))
        
        # Control buttons
        ttk.Button(right_panel, text="Run Simulation", 
                  command=self.run_simulation, width=20).pack(pady=5)
        ttk.Button(right_panel, text="Generate Random Processes", 
                  command=self.generate_random_processes, width=20).pack(pady=5)
    
    def setup_visualization_section(self, parent):
        """Set up the visualization section."""
        viz_frame = ttk.LabelFrame(parent, text="Gantt Chart Visualization", padding=10)
        viz_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(10, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initial empty plot
        ax = self.figure.add_subplot(111)
        ax.set_title("No simulation run yet")
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Process ID")
        ax.grid(True, alpha=0.3)
        self.figure.tight_layout()
    
    def setup_metrics_section(self, parent):
        """Set up the metrics display section."""
        self.metrics_frame = ttk.LabelFrame(parent, text="Performance Metrics", padding=10)
        self.metrics_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create metrics labels
        self.metrics_labels = {}
        metrics = [
            "Average Waiting Time",
            "Average Turnaround Time", 
            "CPU Utilization",
            "Total Processes",
            "Total Time"
        ]
        
        for i, metric in enumerate(metrics):
            ttk.Label(self.metrics_frame, text=f"{metric}:", style='Section.TLabel').grid(
                row=i//3, column=(i%3)*2, sticky=tk.W, padx=(0, 5), pady=2)
            
            label = ttk.Label(self.metrics_frame, text="--", font=('Arial', 10))
            label.grid(row=i//3, column=(i%3)*2+1, sticky=tk.W, padx=(0, 20), pady=2)
            self.metrics_labels[metric] = label
    
    def center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def run_simulation(self):
        """Run the selected scheduling algorithm simulation."""
        processes = self.process_table.get_processes()
        
        if not processes:
            messagebox.showwarning("No Processes", "Please add at least one process before running simulation.")
            return
        
        # Get algorithm and time quantum
        algorithm = self.algorithm_var.get()
        try:
            time_quantum = float(self.time_quantum_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Time quantum must be a valid number.")
            return
        
        # Run simulation in a separate thread to prevent UI freezing
        threading.Thread(target=self._run_simulation_thread, 
                        args=(processes, algorithm, time_quantum), daemon=True).start()
    
    def _run_simulation_thread(self, processes: List[Process], algorithm: str, time_quantum: float):
        """Run simulation in separate thread."""
        try:
            # Select algorithm
            if algorithm == "First-Come, First-Served (FCFS)":
                result = fcfs_scheduling(processes)
            elif algorithm == "Shortest Job First (Non-Preemptive)":
                result = sjf_non_preemptive(processes)
            elif algorithm == "Shortest Job First (Preemptive)":
                result = sjf_preemptive(processes)
            elif algorithm == "Priority (Non-Preemptive)":
                result = priority_non_preemptive(processes)
            elif algorithm == "Priority (Preemptive)":
                result = priority_preemptive(processes)
            elif algorithm == "Round Robin":
                result = round_robin(processes, time_quantum)
            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")
            
            # Update UI in main thread
            self.root.after(0, self._update_simulation_results, result)
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Simulation Error", str(e))
    
    def _update_simulation_results(self, result):
        """Update UI with simulation results."""
        # Update metrics
        for metric, value in result.metrics.items():
            if metric in self.metrics_labels:
                self.metrics_labels[metric].config(text=str(value))
        
        # Update Gantt chart
        self._draw_gantt_chart(result.schedule, result.algorithm_name)
    
    def _draw_gantt_chart(self, schedule: List[tuple], algorithm_name: str):
        """Draw Gantt chart from schedule data."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not schedule:
            ax.set_title("No schedule generated")
            ax.set_xlabel("Time (seconds)")
            ax.set_ylabel("Process ID")
            ax.grid(True, alpha=0.3)
            self.figure.tight_layout()
            self.canvas.draw()
            return
        
        # Get unique processes and assign colors
        processes = list(set(pid for pid, _, _ in schedule if pid != "IDLE"))
        colors = plt.cm.Set3(range(len(processes)))
        color_map = {pid: colors[i] for i, pid in enumerate(processes)}
        
        # Plot schedule
        y_pos = 0
        y_labels = []
        y_positions = []
        
        for i, (pid, start_time, end_time) in enumerate(schedule):
            if pid == "IDLE":
                # Draw idle time in gray
                ax.barh(y_pos, end_time - start_time, left=start_time, 
                       height=0.8, color='lightgray', alpha=0.7)
                if i == 0 or schedule[i-1][0] != "IDLE":  # First idle or after non-idle
                    y_labels.append("IDLE")
                    y_positions.append(y_pos)
                    y_pos += 1
            else:
                # Draw process execution
                ax.barh(y_pos, end_time - start_time, left=start_time,
                       height=0.8, color=color_map[pid], alpha=0.8)
                
                # Add process label if this is a new process or new execution
                if i == 0 or schedule[i-1][0] != pid or schedule[i-1][2] != start_time:
                    y_labels.append(pid)
                    y_positions.append(y_pos)
                    y_pos += 1
        
        # Configure plot
        ax.set_title(f"Gantt Chart - {algorithm_name}")
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Process ID")
        ax.set_yticks(y_positions)
        ax.set_yticklabels(y_labels)
        ax.grid(True, alpha=0.3)
        
        # Set x-axis limits
        max_time = max(end_time for _, _, end_time in schedule)
        ax.set_xlim(0, max_time)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def generate_random_processes(self):
        """Generate random processes for testing."""
        try:
            num_processes = tk.simpledialog.askinteger(
                "Random Processes", 
                "Enter number of processes to generate (1-1000):",
                minvalue=1, maxvalue=1000, initialvalue=10
            )
            
            if num_processes:
                # Clear existing processes
                self.process_table.clear_all()
                
                # Generate random processes
                for i in range(num_processes):
                    pid = f"P{i+1}"
                    arrival_time = random.uniform(0, num_processes * 0.5)
                    burst_time = random.uniform(1, 10)
                    priority = random.randint(1, 10)
                    
                    process = Process(pid, arrival_time, burst_time, priority)
                    self.process_table.add_process(process)
                
                messagebox.showinfo("Random Processes", f"Generated {num_processes} random processes.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate random processes: {str(e)}")
    
    def run(self):
        """Start the application."""
        self.root.mainloop()


if __name__ == "__main__":
    # Import tkinter.simpledialog for random process generation
    import tkinter.simpledialog
    
    app = OSchedulerPro()
    app.run()
