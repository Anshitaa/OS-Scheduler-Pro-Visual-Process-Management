# OS Scheduler Pro - Visual Process Management

An interactive desktop application that demystifies complex operating system process scheduling algorithms through real-time Gantt chart visualizations and performance metrics.

## Features

### 🎯 Core Functionality
- **Interactive Process Management**: Add, edit, and remove processes with arrival times, burst times, and priorities
- **Multiple Scheduling Algorithms**: 
  - First-Come, First-Served (FCFS)
  - Shortest Job First (Non-Preemptive & Preemptive)
  - Priority Scheduling (Non-Preemptive & Preemptive)
  - Round Robin with customizable time quantum
- **Real-time Visualization**: Dynamic Gantt charts showing process execution timeline
- **Performance Metrics**: Average waiting time, turnaround time, CPU utilization, and more
- **Random Process Generation**: Generate up to 1,000 random processes for stress testing

### 🎨 User Interface
- **Clean, Modern Design**: Intuitive three-panel layout
- **Process Input Table**: Easy-to-use table for managing process data
- **Interactive Controls**: Dropdown algorithm selection and parameter inputs
- **Color-coded Gantt Charts**: Each process gets a unique color for easy identification
- **Real-time Metrics Display**: Performance statistics updated after each simulation

## Installation

### Prerequisites
- Python 3.7 or higher
- tkinter (usually included with Python)

### Setup
1. Clone or download this repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Usage

### Adding Processes
1. Click "Add Process" to open the process dialog
2. Enter:
   - **Process ID**: Unique identifier (e.g., P1, P2)
   - **Arrival Time**: When the process arrives in the system (seconds)
   - **Burst Time**: CPU time required by the process (seconds)
   - **Priority**: Process priority (optional, lower number = higher priority)

### Running Simulations
1. Select a scheduling algorithm from the dropdown
2. For Round Robin, set the desired time quantum
3. Click "Run Simulation" to execute and visualize
4. View results in the Gantt chart and metrics panel

### Generating Random Processes
1. Click "Generate Random Processes"
2. Enter the number of processes (1-1000)
3. Random processes will be generated with random arrival times, burst times, and priorities

## Scheduling Algorithms

### First-Come, First-Served (FCFS)
- Processes are executed in the order they arrive
- Non-preemptive algorithm
- Simple but may lead to poor performance with varying burst times

### Shortest Job First (SJF)
- **Non-Preemptive**: Once started, a process runs to completion
- **Preemptive**: Process can be interrupted if a shorter job arrives
- Optimal for minimizing average waiting time

### Priority Scheduling
- **Non-Preemptive**: Process runs to completion once started
- **Preemptive**: Higher priority process can preempt lower priority ones
- Lower priority number = higher priority

### Round Robin
- Each process gets equal CPU time (time quantum)
- Processes are scheduled in a circular manner
- Fair scheduling but may have higher turnaround times

## Performance Metrics

- **Average Waiting Time**: Average time processes wait in the ready queue
- **Average Turnaround Time**: Average time from process arrival to completion
- **CPU Utilization**: Percentage of time CPU is busy executing processes
- **Total Processes**: Number of processes in the simulation
- **Total Time**: Total simulation time including idle periods

## Technical Details

### Architecture
- **Frontend**: Tkinter for GUI components
- **Visualization**: Matplotlib for Gantt chart generation
- **Backend**: Pure Python scheduling algorithms
- **Threading**: Simulation runs in separate thread to prevent UI freezing

### Performance
- Optimized for handling up to 1,000 processes
- Efficient data structures (heaps, queues) for preemptive algorithms
- Memory-efficient process management

## Testing

Run the test suite to verify algorithm correctness:
```bash
python test_algorithms.py
```

## File Structure

```
OS Scheduler/
├── main.py                    # Main application entry point
├── process.py                 # Process data structure
├── scheduling_algorithms.py   # All scheduling algorithms
├── test_algorithms.py         # Unit tests
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Contributing

This project follows a structured development approach:
- **Sprint 1**: Core algorithms and data structures
- **Sprint 2**: Basic UI and FCFS integration
- **Sprint 3**: Gantt chart visualization
- **Sprint 4**: Advanced algorithms and UI refinements
- **Sprint 5**: Optimization and final polish

## Educational Value

OS Scheduler Pro serves as an excellent learning tool for:
- Understanding scheduling algorithm behavior
- Comparing algorithm performance
- Visualizing process execution patterns
- Analyzing the impact of different parameters
- Hands-on experience with OS concepts

## License

This project is open source and available under the MIT License.

---

**OS Scheduler Pro** - Making Operating System Concepts Visual and Interactive! 🚀
