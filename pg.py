import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from copy import deepcopy

# Global variables
algo_dropdown = None
priority_label = None
priority_entry = None
time_quantum_label = None
time_quantum_entry = None
processes = []  # Define processes globally

# Process class to store process data
class Process:
    def __init__(self, name, arrival_time, burst_time, priority=None):
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time  # For preemptive algorithms
        self.priority = priority
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.response_time = -1  # -1 indicates not yet responded

# Function to process the input
def process_input(arrival_times_data, burst_times_data, priority_data, time_quantum_data, algorithm):
    global processes

    # Validate the input fields
    if not arrival_times_data or not burst_times_data:
        messagebox.showerror("Input Error", "Please fill in all required fields (Arrival and Burst Times).")
        return

    arrival_times = list(map(int, arrival_times_data.split(',')))
    burst_times = list(map(int, burst_times_data.split(',')))
    priorities = []

    # Process Priorities if applicable
    if priority_data:
        priorities = list(map(int, priority_data.split(',')))

    # Process Time Quantum if applicable
    time_quantum = int(time_quantum_data) if time_quantum_data else None

    # Assign Process Names
    process_names = [chr(65 + i) for i in range(len(arrival_times))]

    # Populate processes list
    processes = [
        Process(name=process_names[i], arrival_time=arrival_times[i], burst_time=burst_times[i],
                priority=priorities[i] if priorities else None)
        for i in range(len(arrival_times))
    ]

    # Call the selected algorithm function
    if algorithm == "First Come First Serve, FCFS":
        gantt_chart = fcfs_scheduling(processes)
    elif algorithm == "Shortest Job First, SJF (non-preemptive)":
        gantt_chart = sjf_scheduling(processes)
    elif algorithm == "Shortest Remaining Time First, SRTF":
        gantt_chart = srtf_scheduling(processes)
    elif algorithm == "Round-Robin, RR":
        if time_quantum is None:
            messagebox.showerror("Input Error", "Please provide a valid Time Quantum for Round-Robin scheduling.")
            return
        gantt_chart = round_robin_scheduling(processes, time_quantum)
    elif algorithm == "Priority (non-preemptive)":
        gantt_chart = priority_scheduling(processes)
    elif algorithm == "Priority (preemptive)":
        gantt_chart = preemptive_priority_scheduling(processes)

    # Display results in a new window
    show_results(processes, gantt_chart, algorithm)

# Algorithm selection function
def algorithm_selected(algorithm):
    if "Priority" in algorithm:
        priority_label.grid(row=3, column=0, padx=5, pady=5)
        priority_entry.grid(row=3, column=1, padx=5, pady=5)
        time_quantum_label.grid_forget()
        time_quantum_entry.grid_forget()
    elif algorithm == "Round-Robin, RR":
        priority_label.grid_forget()
        priority_entry.grid_forget()
        time_quantum_label.grid(row=3, column=0, padx=5, pady=5)
        time_quantum_entry.grid(row=3, column=1, padx=5, pady=5)
    else:
        priority_label.grid_forget()
        priority_entry.grid_forget()
        time_quantum_label.grid_forget()
        time_quantum_entry.grid_forget()

# Function to create input fields based on the selected algorithm
def create_input_fields():
    global algo_dropdown  # Make algo_dropdown global to access in other functions

    # Clear previous widgets
    for widget in input_frame.winfo_children():
        widget.destroy()

    # Algorithm Selection
    algo_label = ctk.CTkLabel(input_frame, text="Algorithm")
    algo_label.grid(row=0, column=0, padx=5, pady=5)

    algo_dropdown = ctk.CTkOptionMenu(input_frame, values=algorithms, command=algorithm_selected)
    algo_dropdown.grid(row=0, column=1, padx=5, pady=5)

    # Arrival Times
    arrival_label = ctk.CTkLabel(input_frame, text="Arrival Times (comma-separated)")
    arrival_label.grid(row=1, column=0, padx=5, pady=5)

    arrival_entry = ctk.CTkEntry(input_frame)
    arrival_entry.grid(row=1, column=1, padx=5, pady=5)

    # Burst Times
    burst_label = ctk.CTkLabel(input_frame, text="Burst Times (comma-separated)")
    burst_label.grid(row=2, column=0, padx=5, pady=5)

    burst_entry = ctk.CTkEntry(input_frame)
    burst_entry.grid(row=2, column=1, padx=5, pady=5)

    # Priority (initially hidden)
    global priority_label, priority_entry
    priority_label = ctk.CTkLabel(input_frame, text="Priorities (comma-separated)")
    priority_entry = ctk.CTkEntry(input_frame)

    # Time Quantum (initially hidden)
    global time_quantum_label, time_quantum_entry
    time_quantum_label = ctk.CTkLabel(input_frame, text="Time Quantum")
    time_quantum_entry = ctk.CTkEntry(input_frame)

    # Submit Button
    submit_button = ctk.CTkButton(input_frame, text="Submit",
                                  command=lambda: process_input(arrival_entry.get(), burst_entry.get(),
                                                                priority_entry.get(), time_quantum_entry.get(),
                                                                algo_dropdown.get()))
    submit_button.grid(row=4, columnspan=2, padx=5, pady=10)

# Function to display results in a new window
def show_results(proc_list, gantt_chart, algorithm):
    result_window = ctk.CTkToplevel(root)
    result_window.title(f"{algorithm} Results")
    result_window.geometry("1200x700")

    # Gantt Chart Display
    gantt_frame = ctk.CTkFrame(result_window)
    gantt_frame.pack(fill='x', padx=10, pady=10)
    ctk.CTkLabel(gantt_frame, text="Gantt Chart:", font=("Arial", 16, "bold")).pack(anchor='w')
    gantt_canvas = ctk.CTkCanvas(gantt_frame, height=100)
    gantt_canvas.pack(fill='x', pady=5)

    # Drawing Gantt Chart
    start_x = 10
    start_y = 50
    height = 30
    scale = 5  # Adjusts the length scale of the chart
    for proc_name, duration in gantt_chart:
        end_x = start_x + duration * scale
        color = "#3498db" if proc_name != "Idle" else "#95a5a6"
        gantt_canvas.create_rectangle(start_x, start_y, end_x, start_y + height, fill=color, outline="black")
        gantt_canvas.create_text((start_x + end_x) / 2, start_y + height / 2, text=proc_name, fill="white")
        gantt_canvas.create_text(start_x, start_y + height + 10, text=str(int((start_x - 10) / scale)), anchor='n')
        start_x = end_x
    gantt_canvas.create_text(start_x, start_y + height + 10, text=str(int((start_x - 10) / scale)), anchor='n')

    # Process Table Display
    table_frame = ctk.CTkFrame(result_window)
    table_frame.pack(fill='both', expand=True, padx=10, pady=10)

    columns = (
        "Process", "Arrival Time", "Burst Time", "Priority", "Completion Time", "Turnaround Time", "Waiting Time",
        "Response Time")
    tree = ttk.Treeview(table_frame, columns=columns, show='headings')
    tree.pack(fill='both', expand=True)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')

    for proc in proc_list:
        tree.insert("", "end", values=(
            proc.name,
            proc.arrival_time,
            proc.burst_time,
            proc.priority,
            proc.completion_time,
            proc.turnaround_time,
            proc.waiting_time,
            proc.response_time
        ))

    # Averages Display
    if len(proc_list) > 0:
        avg_tat = sum(proc.turnaround_time for proc in proc_list) / len(proc_list)
        avg_wt = sum(proc.waiting_time for proc in proc_list) / len(proc_list)
    else:
        avg_tat = 0
        avg_wt = 0

    avg_frame = ctk.CTkFrame(result_window)
    avg_frame.pack(fill='x', padx=10, pady=10)

    ctk.CTkLabel(avg_frame, text=f"Average Turnaround Time: {avg_tat:.2f}", font=("Arial", 14)).pack(anchor='w')
    ctk.CTkLabel(avg_frame, text=f"Average Waiting Time: {avg_wt:.2f}", font=("Arial", 14)).pack(anchor='w')

# First-Come-First-Serve Scheduling
def fcfs_scheduling(proc_list):
    proc_list.sort(key=lambda p: p.arrival_time)
    time = 0
    gantt_chart = []
    for proc in proc_list:
        if time < proc.arrival_time:
            gantt_chart.append(("Idle", proc.arrival_time - time))
            time = proc.arrival_time
        proc.completion_time = time + proc.burst_time
        proc.turnaround_time = proc.completion_time - proc.arrival_time
        proc.waiting_time = proc.turnaround_time - proc.burst_time
        if proc.response_time == -1:
            proc.response_time = time - proc.arrival_time
        gantt_chart.append((proc.name, proc.burst_time))
        time = proc.completion_time
    return gantt_chart

# Shortest Job First Scheduling (Non-Preemptive)
def sjf_scheduling(proc_list):
    proc_list.sort(key=lambda p: (p.arrival_time, p.burst_time))
    time = 0
    gantt_chart = []
    completed = []
    while len(completed) < len(proc_list):
        available_procs = [p for p in proc_list if p.arrival_time <= time and p not in completed]
        if available_procs:
            proc = min(available_procs, key=lambda p: p.burst_time)
            proc.completion_time = time + proc.burst_time
            proc.turnaround_time = proc.completion_time - proc.arrival_time
            proc.waiting_time = proc.turnaround_time - proc.burst_time
            if proc.response_time == -1:
                proc.response_time = time - proc.arrival_time
            gantt_chart.append((proc.name, proc.burst_time))
            time = proc.completion_time
            completed.append(proc)
        else:
            time += 1
            gantt_chart.append(("Idle", 1))
    return gantt_chart

# Shortest Remaining Time First Scheduling (Preemptive)
# Shortest Remaining Time First Scheduling (Preemptive)
def srtf_scheduling(proc_list):
    time = 0
    completed = 0
    n = len(proc_list)
    gantt_chart = []
    proc_list.sort(key=lambda x: x.arrival_time)
    ready_queue = []
    prev_proc = None
    while completed != n:
        for proc in proc_list:
            if proc.arrival_time <= time and proc not in ready_queue and proc.remaining_time > 0:
                ready_queue.append(proc)
        if ready_queue:
            ready_queue.sort(key=lambda x: x.remaining_time)
            current_proc = ready_queue[0]
            if current_proc != prev_proc:
                if prev_proc is not None and time > 0:
                    gantt_chart.append((prev_proc.name, time - start_time))
                start_time = time
                prev_proc = current_proc
            if current_proc.response_time == -1:
                current_proc.response_time = time - current_proc.arrival_time
            current_proc.remaining_time -= 1
            time += 1
            if current_proc.remaining_time == 0:
                current_proc.completion_time = time
                current_proc.turnaround_time = current_proc.completion_time - current_proc.arrival_time
                current_proc.waiting_time = current_proc.turnaround_time - current_proc.burst_time
                ready_queue.remove(current_proc)
                completed += 1
        else:
            if prev_proc is not None and time > 0:
                gantt_chart.append((prev_proc.name, time - start_time))
                prev_proc = None
            gantt_chart.append(("Idle", 1))
            time += 1
    if prev_proc is not None:
        gantt_chart.append((prev_proc.name, time - start_time))
    return gantt_chart



# Round-Robin Scheduling
def round_robin_scheduling(proc_list, quantum=2):
    time = 0
    completed = 0
    n = len(proc_list)
    gantt_chart = []
    queue = []
    proc_list.sort(key=lambda x: x.arrival_time)
    queue.append(proc_list[0])
    i = 1
    while completed != n:
        if queue:
            current_proc = queue.pop(0)
            if current_proc.response_time == -1:
                current_proc.response_time = time - current_proc.arrival_time
            exec_time = min(quantum, current_proc.remaining_time)
            gantt_chart.append((current_proc.name, exec_time))
            time += exec_time
            current_proc.remaining_time -= exec_time
            # Add processes that have arrived during this time
            while i < n and proc_list[i].arrival_time <= time:
                queue.append(proc_list[i])
                i += 1
            if current_proc.remaining_time > 0:
                queue.append(current_proc)
            else:
                current_proc.completion_time = time
                current_proc.turnaround_time = current_proc.completion_time - current_proc.arrival_time
                current_proc.waiting_time = current_proc.turnaround_time - current_proc.burst_time
                completed += 1
            if not queue and i < n:
                queue.append(proc_list[i])
                if time < proc_list[i].arrival_time:
                    gantt_chart.append(("Idle", proc_list[i].arrival_time - time))
                    time = proc_list[i].arrival_time
                i += 1
        else:
            if i < n:
                queue.append(proc_list[i])
                if time < proc_list[i].arrival_time:
                    gantt_chart.append(("Idle", proc_list[i].arrival_time - time))
                    time = proc_list[i].arrival_time
                i += 1
    return gantt_chart


# Priority Scheduling (Non-Preemptive)
def priority_scheduling(proc_list):
    proc_list.sort(key=lambda p: (p.arrival_time, p.priority))
    time = 0
    gantt_chart = []
    completed = []
    while len(completed) < len(proc_list):
        available_procs = [p for p in proc_list if p.arrival_time <= time and p not in completed]
        if available_procs:
            proc = min(available_procs, key=lambda p: p.priority)
            proc.completion_time = time + proc.burst_time
            proc.turnaround_time = proc.completion_time - proc.arrival_time
            proc.waiting_time = proc.turnaround_time - proc.burst_time
            if proc.response_time == -1:
                proc.response_time = time - proc.arrival_time
            gantt_chart.append((proc.name, proc.burst_time))
            time = proc.completion_time
            completed.append(proc)
        else:
            time += 1
            gantt_chart.append(("Idle", 1))
    return gantt_chart

# Priority Scheduling (Non-Preemptive)
def priority_scheduling(proc_list):
    proc_list.sort(key=lambda p: (p.arrival_time, p.priority))
    time = 0
    gantt_chart = []
    completed = []
    while len(completed) < len(proc_list):
        available_procs = [p for p in proc_list if p.arrival_time <= time and p not in completed]
        if available_procs:
            proc = min(available_procs, key=lambda p: p.priority)
            proc.completion_time = time + proc.burst_time
            proc.turnaround_time = proc.completion_time - proc.arrival_time
            proc.waiting_time = proc.turnaround_time - proc.burst_time
            if proc.response_time == -1:
                proc.response_time = time - proc.arrival_time
            gantt_chart.append((proc.name, proc.burst_time))
            time = proc.completion_time
            completed.append(proc)
        else:
            time += 1
            gantt_chart.append(("Idle", 1))
    return gantt_chart

# Priority Scheduling (Preemptive)
def preemptive_priority_scheduling(proc_list):
    time = 0
    completed = 0
    n = len(proc_list)
    gantt_chart = []
    proc_list.sort(key=lambda x: x.arrival_time)
    ready_queue = []
    prev_proc = None
    while completed != n:
        for proc in proc_list:
            if proc.arrival_time <= time and proc not in ready_queue and proc.remaining_time > 0:
                ready_queue.append(proc)
        if ready_queue:
            ready_queue.sort(key=lambda x: x.priority)
            current_proc = ready_queue[0]
            if current_proc != prev_proc:
                if prev_proc is not None and time > 0:
                    gantt_chart.append((prev_proc.name, time - start_time))
                start_time = time
                prev_proc = current_proc
            if current_proc.response_time == -1:
                current_proc.response_time = time - current_proc.arrival_time
            current_proc.remaining_time -= 1
            time += 1
            if current_proc.remaining_time == 0:
                current_proc.completion_time = time
                current_proc.turnaround_time = current_proc.completion_time - current_proc.arrival_time
                current_proc.waiting_time = current_proc.turnaround_time - current_proc.burst_time
                ready_queue.remove(current_proc)
                completed += 1
        else:
            if prev_proc is not None and time > 0:
                gantt_chart.append((prev_proc.name, time - start_time))
                prev_proc = None
            gantt_chart.append(("Idle", 1))
            time += 1
    if prev_proc is not None:
        gantt_chart.append((prev_proc.name, time - start_time))
    return gantt_chart

# Main GUI Window Setup
root = ctk.CTk()
root.title("CPU Scheduling Simulator")
root.geometry("800x600")

input_frame = ctk.CTkFrame(root)
input_frame.pack(pady=20)

algorithms = ["First Come First Serve, FCFS", "Shortest Job First, SJF (non-preemptive)",
              "Shortest Remaining Time First, SRTF", "Round-Robin, RR",
              "Priority (non-preemptive)", "Priority (preemptive)"]

create_input_fields()

root.mainloop()
