import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from copy import deepcopy
import random
import math

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Global variables
algo_dropdown = None
priority_label = None
priority_entry = None
time_quantum_label = None
time_quantum_entry = None
processes = []  # Define processes globally
results_frame = None  # For managing results display

# Modern color palette
COLORS = {
    'primary': '#2563EB',
    'secondary': '#10B981',
    'accent': '#F59E0B',
    'danger': '#EF4444',
    'info': '#3B82F6',
    'success': '#059669',
    'warning': '#D97706',
    'light': '#F3F4F6',
    'dark': '#1F2937',
    'process_colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
}

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
        show_error_dialog("Input Error", "Please fill in all required fields (Arrival and Burst Times).")
        return

    try:
        arrival_times = list(map(int, arrival_times_data.split(',')))
        burst_times = list(map(int, burst_times_data.split(',')))
        
        # Validate that lists have the same length
        if len(arrival_times) != len(burst_times):
            show_error_dialog("Input Error", "Arrival times and burst times must have the same number of values.")
            return
        
        # Validate positive values
        if any(x < 0 for x in arrival_times) or any(x <= 0 for x in burst_times):
            show_error_dialog("Input Error", "Arrival times must be non-negative and burst times must be positive.")
            return
            
        priorities = []

        # Process Priorities if applicable
        if priority_data:
            try:
                priorities = list(map(int, priority_data.split(',')))
                if len(priorities) != len(arrival_times):
                    show_error_dialog("Input Error", "Number of priorities must match the number of processes.")
                    return
                if any(x <= 0 for x in priorities):
                    show_error_dialog("Input Error", "Priorities must be positive integers.")
                    return
            except ValueError:
                show_error_dialog("Input Error", "Priorities must be valid integers.")
                return

        # Process Time Quantum if applicable
        time_quantum = None
        if time_quantum_data:
            try:
                time_quantum = int(time_quantum_data)
                if time_quantum <= 0:
                    show_error_dialog("Input Error", "Time quantum must be a positive integer.")
                    return
            except ValueError:
                show_error_dialog("Input Error", "Time quantum must be a valid integer.")
                return

    except ValueError:
        show_error_dialog("Input Error", "Please enter valid integers separated by commas.")
        return

    # Assign Process Names
    process_names = [chr(65 + i) for i in range(len(arrival_times))]

    # Populate processes list
    processes = [
        Process(name=process_names[i], arrival_time=arrival_times[i], burst_time=burst_times[i],
                priority=priorities[i] if priorities else None)
        for i in range(len(arrival_times))
    ]

    # Call the selected algorithm function
    try:
        if algorithm == "First Come First Serve, FCFS":
            gantt_chart = fcfs_scheduling(processes)
        elif algorithm == "Shortest Job First, SJF (non-preemptive)":
            gantt_chart = sjf_scheduling(processes)
        elif algorithm == "Shortest Remaining Time First, SRTF":
            gantt_chart = srtf_scheduling(processes)
        elif algorithm == "Round-Robin, RR":
            if time_quantum is None:
                show_error_dialog("Input Error", "Please provide a valid Time Quantum for Round-Robin scheduling.")
                return
            gantt_chart = round_robin_scheduling(processes, time_quantum)
        elif algorithm == "Priority (non-preemptive)":
            gantt_chart = priority_scheduling(processes)
        elif algorithm == "Priority (preemptive)":
            gantt_chart = preemptive_priority_scheduling(processes)

        # Display results in a new window
        show_results(processes, gantt_chart, algorithm)
        
    except Exception as e:
        show_error_dialog("Simulation Error", f"An error occurred during simulation: {str(e)}")

# Function to show enhanced error dialog
def show_error_dialog(title, message):
    error_window = ctk.CTkToplevel(root)
    error_window.title(title)
    error_window.geometry("400x200")
    error_window.configure(fg_color=("white", "gray20"))
    error_window.resizable(False, False)
    
    # Center the error window
    error_window.update_idletasks()
    x = (error_window.winfo_screenwidth() // 2) - (200)
    y = (error_window.winfo_screenheight() // 2) - (100)
    error_window.geometry(f"400x200+{x}+{y}")
    
    # Error icon and message
    icon_label = ctk.CTkLabel(error_window, text="❌", font=ctk.CTkFont(size=40))
    icon_label.pack(pady=(20, 10))
    
    title_label = ctk.CTkLabel(error_window, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS['danger'])
    title_label.pack(pady=(0, 10))
    
    message_label = ctk.CTkLabel(error_window, text=message, font=ctk.CTkFont(size=12), wraplength=350)
    message_label.pack(pady=(0, 20))
    
    ok_button = ctk.CTkButton(
        error_window, 
        text="OK", 
        command=error_window.destroy,
        fg_color=COLORS['danger'],
        hover_color=COLORS['warning'],
        width=100
    )
    ok_button.pack(pady=10)

# Algorithm selection function
def algorithm_selected(algorithm):
    if "Priority" in algorithm:
        priority_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        priority_entry.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        time_quantum_label.grid_forget()
        time_quantum_entry.grid_forget()
    elif algorithm == "Round-Robin, RR":
        priority_label.grid_forget()
        priority_entry.grid_forget()
        time_quantum_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        time_quantum_entry.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
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

    # Title Section
    title_label = ctk.CTkLabel(
        input_frame, 
        text="🖥️ CPU Scheduling Algorithm Simulator", 
        font=ctk.CTkFont(size=28, weight="bold"),
        text_color=COLORS['primary']
    )
    title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 30), sticky="ew")

    # Algorithm Selection with enhanced styling
    algo_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
    algo_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
    
    algo_label = ctk.CTkLabel(
        algo_frame, 
        text="🎯 Select Scheduling Algorithm:", 
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color=COLORS['secondary']
    )
    algo_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    algo_dropdown = ctk.CTkOptionMenu(
        algo_frame, 
        values=algorithms, 
        command=algorithm_selected,
        font=ctk.CTkFont(size=14),
        dropdown_font=ctk.CTkFont(size=12),
        width=350,
        height=35,
        corner_radius=10,
        button_color=COLORS['primary'],
        button_hover_color=COLORS['info']
    )
    algo_dropdown.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

    # Input Section Frame
    input_section = ctk.CTkFrame(input_frame, corner_radius=15, fg_color=("gray90", "gray20"))
    input_section.grid(row=2, column=0, columnspan=3, padx=20, pady=20, sticky="ew")

    # Section Title
    section_title = ctk.CTkLabel(
        input_section,
        text="📊 Process Information",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color=COLORS['accent']
    )
    section_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 15))

    # Arrival Times
    arrival_label = ctk.CTkLabel(
        input_section, 
        text="⏰ Arrival Times (comma-separated):", 
        font=ctk.CTkFont(size=14, weight="bold")
    )
    arrival_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")

    arrival_entry = ctk.CTkEntry(
        input_section,
        font=ctk.CTkFont(size=14),
        width=300,
        height=35,
        corner_radius=10,
        placeholder_text="e.g., 0,1,2,3"
    )
    arrival_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")

    # Burst Times
    burst_label = ctk.CTkLabel(
        input_section, 
        text="⚡ Burst Times (comma-separated):", 
        font=ctk.CTkFont(size=14, weight="bold")
    )
    burst_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")

    burst_entry = ctk.CTkEntry(
        input_section,
        font=ctk.CTkFont(size=14),
        width=300,
        height=35,
        corner_radius=10,
        placeholder_text="e.g., 5,3,8,6"
    )
    burst_entry.grid(row=2, column=1, padx=20, pady=10, sticky="ew")

    # Priority (initially hidden)
    global priority_label, priority_entry
    priority_label = ctk.CTkLabel(
        input_section, 
        text="🎯 Priorities (comma-separated):", 
        font=ctk.CTkFont(size=14, weight="bold")
    )
    priority_entry = ctk.CTkEntry(
        input_section,
        font=ctk.CTkFont(size=14),
        width=300,
        height=35,
        corner_radius=10,
        placeholder_text="e.g., 1,4,2,3 (lower = higher priority)"
    )

    # Time Quantum (initially hidden)
    global time_quantum_label, time_quantum_entry
    time_quantum_label = ctk.CTkLabel(
        input_section, 
        text="🕐 Time Quantum:", 
        font=ctk.CTkFont(size=14, weight="bold")
    )
    time_quantum_entry = ctk.CTkEntry(
        input_section,
        font=ctk.CTkFont(size=14),
        width=300,
        height=35,
        corner_radius=10,
        placeholder_text="e.g., 2"
    )

    # Submit Button with gradient effect
    button_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
    button_frame.grid(row=3, column=0, columnspan=3, padx=20, pady=30)
    
    # Example data button
    example_button = ctk.CTkButton(
        button_frame, 
        text="📝 Load Example",
        command=lambda: load_example_data(arrival_entry, burst_entry, priority_entry, time_quantum_entry),
        font=ctk.CTkFont(size=14),
        width=150,
        height=40,
        corner_radius=20,
        fg_color="transparent",
        border_width=2,
        border_color=COLORS['info'],
        text_color=COLORS['info'],
        hover_color=COLORS['info']
    )
    example_button.pack(side="left", padx=(0, 20))
    
    submit_button = ctk.CTkButton(
        button_frame, 
        text="🚀 Run Simulation",
        command=lambda: process_input(
            arrival_entry.get(), 
            burst_entry.get(),
            priority_entry.get(), 
            time_quantum_entry.get(),
            algo_dropdown.get()
        ),
        font=ctk.CTkFont(size=18, weight="bold"),
        width=250,
        height=50,
        corner_radius=25,
        fg_color=COLORS['success'],
        hover_color=COLORS['secondary'],
        text_color="white"
    )
    submit_button.pack(side="left")

    # Help button
    help_button = ctk.CTkButton(
        button_frame,
        text="❓",
        command=show_help_dialog,
        font=ctk.CTkFont(size=16, weight="bold"),
        width=50,
        height=40,
        corner_radius=20,
        fg_color=COLORS['accent'],
        hover_color=COLORS['warning']
    )
    help_button.pack(side="left", padx=(20, 0))

    # Configure grid weights for responsive design
    input_frame.grid_columnconfigure(0, weight=1)
    input_frame.grid_columnconfigure(1, weight=1)
    input_frame.grid_columnconfigure(2, weight=1)
    input_section.grid_columnconfigure(1, weight=1)

# Function to load example data
def load_example_data(arrival_entry, burst_entry, priority_entry, time_quantum_entry):
    # Clear existing data
    arrival_entry.delete(0, 'end')
    burst_entry.delete(0, 'end')
    priority_entry.delete(0, 'end')
    time_quantum_entry.delete(0, 'end')
    
    # Insert example data
    arrival_entry.insert(0, "0,1,2,3")
    burst_entry.insert(0, "5,3,8,6")
    priority_entry.insert(0, "2,1,4,3")
    time_quantum_entry.insert(0, "2")

# Function to show help dialog
def show_help_dialog():
    help_window = ctk.CTkToplevel(root)
    help_window.title("📚 Help - CPU Scheduling Simulator")
    help_window.geometry("600x500")
    help_window.configure(fg_color=("white", "gray15"))
    help_window.resizable(True, True)
    
    # Center the help window
    help_window.update_idletasks()
    x = (help_window.winfo_screenwidth() // 2) - (300)
    y = (help_window.winfo_screenheight() // 2) - (250)
    help_window.geometry(f"600x500+{x}+{y}")
    
    # Create scrollable frame
    help_scrollable = ctk.CTkScrollableFrame(help_window)
    help_scrollable.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Help content
    help_title = ctk.CTkLabel(
        help_scrollable,
        text="📚 CPU Scheduling Simulator Help",
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color=COLORS['primary']
    )
    help_title.pack(pady=(0, 20))
    
    help_sections = [
        ("🔢 Input Format", 
         "• Arrival Times: Enter comma-separated integers (e.g., 0,1,2,3)\n"
         "• Burst Times: Enter comma-separated integers (e.g., 5,3,8,6)\n"
         "• All values must be positive integers\n"
         "• Number of arrival times must equal number of burst times"),
        
        ("🎯 Priority Scheduling",
         "• Required for Priority algorithms\n"
         "• Lower numbers indicate higher priority\n"
         "• Example: 1,4,2,3 (Process A has highest priority)\n"
         "• Must provide same number of priorities as processes"),
        
        ("🕐 Time Quantum",
         "• Required for Round-Robin scheduling\n"
         "• Specifies the time slice for each process\n"
         "• Must be a positive integer\n"
         "• Common values: 1, 2, 3, 4"),
        
        ("🖥️ Scheduling Algorithms",
         "• FCFS: Processes run in arrival order\n"
         "• SJF: Shortest job runs first (non-preemptive)\n"
         "• SRTF: Shortest remaining time first (preemptive)\n"
         "• Round-Robin: Time quantum-based scheduling\n"
         "• Priority: Based on priority values (preemptive/non-preemptive)"),
        
        ("📊 Results Explanation",
         "• Gantt Chart: Visual timeline of process execution\n"
         "• Completion Time: When process finishes\n"
         "• Turnaround Time: Completion - Arrival time\n"
         "• Waiting Time: Turnaround - Burst time\n"
         "• Response Time: First execution - Arrival time")
    ]
    
    for section_title, section_content in help_sections:
        section_frame = ctk.CTkFrame(help_scrollable, corner_radius=10)
        section_frame.pack(fill="x", pady=10)
        
        title_label = ctk.CTkLabel(
            section_frame,
            text=section_title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['secondary']
        )
        title_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        content_label = ctk.CTkLabel(
            section_frame,
            text=section_content,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        content_label.pack(anchor="w", padx=15, pady=(0, 15))
    
    # Close button
    close_button = ctk.CTkButton(
        help_window,
        text="✅ Got it!",
        command=help_window.destroy,
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color=COLORS['success'],
        hover_color=COLORS['secondary'],
        width=120,
        height=35
    )
    close_button.pack(pady=10)

# Function to clear input fields
def clear_input_fields():
    # This will be called when creating input fields, so we don't need to do anything here
    # The fields will be recreated fresh when create_input_fields() is called
    create_input_fields()

# Function to show input form (hide results and show input)
def show_input_form():
    global results_frame
    if 'results_frame' in globals() and results_frame is not None:
        results_frame.pack_forget()
        results_frame.destroy()
        results_frame = None
    input_frame.pack(fill="both", expand=True, padx=10, pady=10)
    # Update window title
    root.title("🖥️ CPU Scheduling Algorithm Simulator")

# Function to display results in the same window
def show_results(proc_list, gantt_chart, algorithm):
    # Hide input frame and show results
    input_frame.pack_forget()
    
    # Update window title
    root.title(f"🖥️ {algorithm} - Results")
    
    # Create results frame
    global results_frame
    results_frame = ctk.CTkFrame(
        main_container, 
        corner_radius=20,
        fg_color=("white", "gray20"),
        border_width=2,
        border_color=("gray80", "gray30")
    )
    results_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create main scrollable frame
    main_scrollable = ctk.CTkScrollableFrame(results_frame, corner_radius=0)
    main_scrollable.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Header Section with Back Button
    header_frame = ctk.CTkFrame(main_scrollable, corner_radius=15, height=120)
    header_frame.pack(fill='x', padx=10, pady=(10, 20))
    header_frame.pack_propagate(False)
    
    # Back button and New Simulation button
    button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    button_frame.place(x=20, y=15)
    
    back_button = ctk.CTkButton(
        button_frame,
        text="⬅️ Back",
        command=show_input_form,
        font=ctk.CTkFont(size=14, weight="bold"),
        width=100,
        height=35,
        corner_radius=20,
        fg_color=COLORS['info'],
        hover_color=COLORS['primary']
    )
    back_button.pack(side="left", padx=(0, 10))
    
    new_sim_button = ctk.CTkButton(
        button_frame,
        text="🔄 New Simulation",
        command=lambda: [show_input_form(), clear_input_fields()],
        font=ctk.CTkFont(size=14, weight="bold"),
        width=140,
        height=35,
        corner_radius=20,
        fg_color=COLORS['secondary'],
        hover_color=COLORS['success']
    )
    new_sim_button.pack(side="left")
    
    # Algorithm title with icon
    title_label = ctk.CTkLabel(
        header_frame, 
        text=f"🖥️ {algorithm}",
        font=ctk.CTkFont(size=28, weight="bold"),
        text_color=COLORS['primary']
    )
    title_label.pack(pady=(20, 5))
    
    subtitle_label = ctk.CTkLabel(
        header_frame,
        text="CPU Scheduling Simulation Results",
        font=ctk.CTkFont(size=16),
        text_color=("gray60", "gray40")
    )
    subtitle_label.pack()

    # Gantt Chart Section
    gantt_frame = ctk.CTkFrame(main_scrollable, corner_radius=15)
    gantt_frame.pack(fill='x', padx=10, pady=10)
    
    # Gantt Chart Header
    gantt_header = ctk.CTkFrame(gantt_frame, corner_radius=10, height=60, fg_color=COLORS['primary'])
    gantt_header.pack(fill='x', padx=15, pady=(15, 10))
    gantt_header.pack_propagate(False)
    
    ctk.CTkLabel(
        gantt_header, 
        text="📈 Gantt Chart Visualization", 
        font=ctk.CTkFont(size=22, weight="bold"),
        text_color="white"
    ).pack(pady=15)
    
    # Enhanced Gantt Chart Canvas
    canvas_frame = ctk.CTkFrame(gantt_frame, corner_radius=10, fg_color=("white", "gray25"))
    canvas_frame.pack(fill='x', padx=15, pady=(0, 15))
    
    gantt_canvas = tk.Canvas(
        canvas_frame, 
        height=200,  # Increased height to accommodate legend
        bg=("white" if ctk.get_appearance_mode() == "Light" else "#2b2b2b"),
        highlightthickness=0
    )
    gantt_canvas.pack(fill='x', padx=10, pady=10)

    # Drawing Enhanced Gantt Chart
    draw_enhanced_gantt_chart(gantt_canvas, gantt_chart)

    # Statistics Cards Section
    stats_frame = ctk.CTkFrame(main_scrollable, corner_radius=15, fg_color="transparent")
    stats_frame.pack(fill='x', padx=10, pady=10)
    
    # Calculate averages
    if len(proc_list) > 0:
        avg_tat = sum(proc.turnaround_time for proc in proc_list) / len(proc_list)
        avg_wt = sum(proc.waiting_time for proc in proc_list) / len(proc_list)
        avg_rt = sum(proc.response_time for proc in proc_list if proc.response_time != -1) / len([p for p in proc_list if p.response_time != -1]) if any(p.response_time != -1 for p in proc_list) else 0
        total_completion_time = max(proc.completion_time for proc in proc_list) if proc_list else 0
        cpu_utilization = (sum(proc.burst_time for proc in proc_list) / total_completion_time * 100) if total_completion_time > 0 else 0
    else:
        avg_tat = avg_wt = avg_rt = cpu_utilization = 0

    # Create statistics cards
    create_stats_cards(stats_frame, avg_tat, avg_wt, avg_rt, cpu_utilization, len(proc_list))

    # Process Details Table Section
    table_frame = ctk.CTkFrame(main_scrollable, corner_radius=15)
    table_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Table Header
    table_header = ctk.CTkFrame(table_frame, corner_radius=10, height=60, fg_color=COLORS['secondary'])
    table_header.pack(fill='x', padx=15, pady=(15, 10))
    table_header.pack_propagate(False)
    
    ctk.CTkLabel(
        table_header, 
        text="📋 Process Details", 
        font=ctk.CTkFont(size=22, weight="bold"),
        text_color="white"
    ).pack(pady=15)

    # Enhanced Process Table
    create_enhanced_table(table_frame, proc_list)
    
    # Add Process Color Reference Card
    color_ref_frame = ctk.CTkFrame(main_scrollable, corner_radius=15)
    color_ref_frame.pack(fill='x', padx=10, pady=10)
    
    # Color reference header
    color_header = ctk.CTkFrame(color_ref_frame, corner_radius=10, height=50, fg_color=COLORS['accent'])
    color_header.pack(fill='x', padx=15, pady=(15, 10))
    color_header.pack_propagate(False)
    
    ctk.CTkLabel(
        color_header, 
        text="🎨 Process Color Reference", 
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="white"
    ).pack(pady=10)
    
    # Color reference content
    color_content = ctk.CTkFrame(color_ref_frame, corner_radius=10, fg_color=("white", "gray25"))
    color_content.pack(fill='x', padx=15, pady=(0, 15))
    
    create_color_reference(color_content, proc_list)
    
    # Add keyboard shortcut for going back (Escape key)
    results_frame.bind("<Key>", lambda e: show_input_form() if e.keysym == "Escape" else None)
    results_frame.focus_set()

# Function to create color reference
def create_color_reference(parent_frame, proc_list):
    # Get unique process names and assign colors
    unique_processes = list(set(proc.name for proc in proc_list))
    process_colors = {}
    for i, proc_name in enumerate(sorted(unique_processes)):
        process_colors[proc_name] = COLORS['process_colors'][i % len(COLORS['process_colors'])]
    
    # Create color reference grid
    ref_canvas = tk.Canvas(
        parent_frame,
        height=80,
        bg=("white" if ctk.get_appearance_mode() == "Light" else "#2b2b2b"),
        highlightthickness=0
    )
    ref_canvas.pack(fill='x', padx=15, pady=15)
    
    # Draw color reference
    start_x = 20
    start_y = 40
    box_size = 30
    spacing = 150
    
    for i, (proc_name, color) in enumerate(process_colors.items()):
        x = start_x + i * spacing
        
        # Draw color box
        ref_canvas.create_rectangle(
            x, start_y - box_size//2, 
            x + box_size, start_y + box_size//2,
            fill=color, outline="black", width=2
        )
        
        # Draw process label
        ref_canvas.create_text(
            x + box_size + 10, start_y,
            text=f"Process {proc_name}",
            fill=("black" if ctk.get_appearance_mode() == "Light" else "white"),
            font=("Arial", 12, "bold"),
            anchor="w"
        )

# Function to draw enhanced Gantt chart
def draw_enhanced_gantt_chart(canvas, gantt_chart):
    canvas.delete("all")
    
    # Calculate dimensions
    canvas.update_idletasks()
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    
    if canvas_width <= 1:  # Canvas not yet rendered
        canvas_width = 800
    
    # Chart parameters
    start_x = 60
    chart_width = canvas_width - 120
    start_y = 40
    height = 60
    
    # Calculate total time
    total_time = sum(duration for _, duration in gantt_chart)
    if total_time == 0:
        return
    
    scale = chart_width / total_time
    
    # Create a mapping of process names to colors
    unique_processes = list(set(proc_name for proc_name, _ in gantt_chart if proc_name != "Idle"))
    process_colors = {}
    for i, proc_name in enumerate(sorted(unique_processes)):
        process_colors[proc_name] = COLORS['process_colors'][i % len(COLORS['process_colors'])]
    
    # Add idle color
    process_colors["Idle"] = "#BDC3C7"
    
    # Draw chart background
    canvas.create_rectangle(
        start_x - 5, start_y - 5, 
        start_x + chart_width + 5, start_y + height + 5,
        fill=("gray95" if ctk.get_appearance_mode() == "Light" else "gray30"),
        outline=("gray80" if ctk.get_appearance_mode() == "Light" else "gray50"),
        width=2
    )
    
    # Draw legend
    legend_y = start_y + height + 50
    legend_x = start_x
    canvas.create_text(legend_x, legend_y, text="Legend:", fill=("black" if ctk.get_appearance_mode() == "Light" else "white"), font=("Arial", 10, "bold"), anchor="w")
    legend_x += 60
    
    for proc_name in sorted(process_colors.keys()):
        if proc_name != "Idle":  # Show idle separately
            color = process_colors[proc_name]
            # Draw color box
            canvas.create_rectangle(legend_x, legend_y - 8, legend_x + 15, legend_y + 8, fill=color, outline="black")
            # Draw process name
            canvas.create_text(legend_x + 20, legend_y, text=f"Process {proc_name}", fill=("black" if ctk.get_appearance_mode() == "Light" else "white"), font=("Arial", 9), anchor="w")
            legend_x += 100
    
    # Add idle to legend
    if "Idle" in process_colors:
        canvas.create_rectangle(legend_x, legend_y - 8, legend_x + 15, legend_y + 8, fill=process_colors["Idle"], outline="black", stipple="gray50")
        canvas.create_text(legend_x + 20, legend_y, text="Idle Time", fill=("black" if ctk.get_appearance_mode() == "Light" else "white"), font=("Arial", 9), anchor="w")
    
    # Draw processes
    current_x = start_x
    time_position = 0
    
    for i, (proc_name, duration) in enumerate(gantt_chart):
        end_x = current_x + duration * scale
        
        if proc_name == "Idle":
            color = process_colors["Idle"]
            text_color = "#2C3E50"
            pattern = "diagonal"
        else:
            color = process_colors[proc_name]
            text_color = "white"
            pattern = "solid"
        
        # Create gradient effect for better visual appeal
        if pattern == "solid":
            # Draw main rectangle with gradient effect
            canvas.create_rectangle(
                current_x, start_y, end_x, start_y + height,
                fill=color, outline="white", width=2,
                tags=f"process_{i}"
            )
            
            # Add subtle gradient by drawing a lighter rectangle on top
            gradient_color = lighten_color(color, 0.3)
            canvas.create_rectangle(
                current_x, start_y, end_x, start_y + height//3,
                fill=gradient_color, outline="", stipple="gray25",
                tags=f"gradient_{i}"
            )
        else:
            # Draw diagonal stripes for idle time
            canvas.create_rectangle(
                current_x, start_y, end_x, start_y + height,
                fill=color, outline="gray", width=1,
                tags=f"process_{i}"
            )
            # Add diagonal pattern
            stripe_spacing = 8
            for stripe_x in range(int(current_x), int(end_x), stripe_spacing):
                canvas.create_line(
                    stripe_x, start_y, 
                    min(stripe_x + height, end_x), start_y + min(height, end_x - stripe_x),
                    fill="gray60", width=2
                )
        
        # Add shadow effect
        canvas.create_rectangle(
            current_x + 2, start_y + 2, end_x + 2, start_y + height + 2,
            fill="gray40", outline="", stipple="gray50",
            tags=f"shadow_{i}"
        )
        canvas.tag_lower(f"shadow_{i}")
        
        # Process name and duration
        rect_width = end_x - current_x
        if rect_width > 40:  # Only show text if rectangle is wide enough
            canvas.create_text(
                (current_x + end_x) / 2, start_y + height / 2 - 8,
                text=proc_name, fill=text_color, 
                font=("Arial", 11, "bold")
            )
            # Show duration inside the rectangle
            canvas.create_text(
                (current_x + end_x) / 2, start_y + height / 2 + 8,
                text=f"({duration})", fill=text_color, 
                font=("Arial", 9)
            )
        elif rect_width > 20:  # Show only process name if medium width
            canvas.create_text(
                (current_x + end_x) / 2, start_y + height / 2,
                text=proc_name, fill=text_color, 
                font=("Arial", 10, "bold")
            )
        
        # Time markers
        canvas.create_text(
            current_x, start_y + height + 20,
            text=str(time_position), fill=("black" if ctk.get_appearance_mode() == "Light" else "white"),
            font=("Arial", 10, "bold")
        )
        
        # Add vertical grid lines
        canvas.create_line(
            current_x, start_y - 5,
            current_x, start_y + height + 5,
            fill=("gray70" if ctk.get_appearance_mode() == "Light" else "gray60"),
            width=1
        )
        
        current_x = end_x
        time_position += duration
    
    # Final time marker and grid line
    canvas.create_text(
        current_x, start_y + height + 20,
        text=str(time_position), fill=("black" if ctk.get_appearance_mode() == "Light" else "white"),
        font=("Arial", 10, "bold")
    )
    canvas.create_line(
        current_x, start_y - 5,
        current_x, start_y + height + 5,
        fill=("gray70" if ctk.get_appearance_mode() == "Light" else "gray60"),
        width=1
    )
    
    # Time axis line
    canvas.create_line(
        start_x, start_y + height + 15,
        current_x, start_y + height + 15,
        fill=("gray50" if ctk.get_appearance_mode() == "Light" else "gray70"),
        width=2
    )
    
    # Add axis labels
    canvas.create_text(
        (start_x + current_x) / 2, start_y + height + 35,
        text="Time →", fill=("black" if ctk.get_appearance_mode() == "Light" else "white"),
        font=("Arial", 10, "bold")
    )

# Helper function to lighten colors for gradient effect
def lighten_color(color, factor):
    """Lighten a hex color by a given factor (0.0 to 1.0)"""
    # Convert hex to RGB
    color = color.lstrip('#')
    rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    
    # Lighten each component
    lightened_rgb = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
    
    # Convert back to hex
    return '#%02x%02x%02x' % lightened_rgb

# Function to create statistics cards
def create_stats_cards(parent_frame, avg_tat, avg_wt, avg_rt, cpu_util, num_processes):
    # Create grid of stat cards
    stats = [
        ("⏱️", "Avg Turnaround Time", f"{avg_tat:.2f}", COLORS['primary']),
        ("⏳", "Avg Waiting Time", f"{avg_wt:.2f}", COLORS['warning']),
        ("🚀", "Avg Response Time", f"{avg_rt:.2f}", COLORS['info']),
        ("📊", "CPU Utilization", f"{cpu_util:.1f}%", COLORS['success']),
        ("🔢", "Total Processes", str(num_processes), COLORS['accent'])
    ]
    
    cards_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    cards_frame.pack(fill='x', padx=0, pady=10)
    
    for i, (icon, label, value, color) in enumerate(stats):
        card = ctk.CTkFrame(cards_frame, corner_radius=15, height=120)
        card.grid(row=0, column=i, padx=8, pady=5, sticky="ew")
        card.grid_propagate(False)
        
        # Icon
        icon_label = ctk.CTkLabel(
            card, text=icon, 
            font=ctk.CTkFont(size=32)
        )
        icon_label.pack(pady=(15, 5))
        
        # Value
        value_label = ctk.CTkLabel(
            card, text=value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=color
        )
        value_label.pack()
        
        # Label
        label_label = ctk.CTkLabel(
            card, text=label,
            font=ctk.CTkFont(size=11),
            text_color=("gray60", "gray40")
        )
        label_label.pack(pady=(0, 15))
        
        cards_frame.grid_columnconfigure(i, weight=1)

# Function to create enhanced table
def create_enhanced_table(parent_frame, proc_list):
    table_container = ctk.CTkFrame(parent_frame, corner_radius=10, fg_color=("white", "gray25"))
    table_container.pack(fill='both', expand=True, padx=15, pady=(0, 15))
    
    # Create Treeview with custom styling
    style = ttk.Style()
    style.theme_use("clam")
    
    # Configure Treeview colors
    bg_color = "white" if ctk.get_appearance_mode() == "Light" else "#2b2b2b"
    fg_color = "black" if ctk.get_appearance_mode() == "Light" else "white"
    select_color = COLORS['primary']
    
    style.configure("Custom.Treeview",
                   background=bg_color,
                   foreground=fg_color,
                   fieldbackground=bg_color,
                   selectbackground=select_color,
                   selectforeground="white",
                   rowheight=35)
    
    style.configure("Custom.Treeview.Heading",
                   background=COLORS['secondary'],
                   foreground="white",
                   font=("Arial", 11, "bold"),
                   relief="flat")
    
    columns = (
        "Process", "Arrival Time", "Burst Time", "Priority", 
        "Completion Time", "Turnaround Time", "Waiting Time", "Response Time"
    )
    
    tree = ttk.Treeview(
        table_container, 
        columns=columns, 
        show='headings',
        style="Custom.Treeview",
        height=len(proc_list) + 2
    )
    
    # Configure column headings and widths
    column_configs = {
        "Process": (80, "center"),
        "Arrival Time": (100, "center"),
        "Burst Time": (100, "center"),
        "Priority": (80, "center"),
        "Completion Time": (120, "center"),
        "Turnaround Time": (120, "center"),
        "Waiting Time": (110, "center"),
        "Response Time": (110, "center")
    }
    
    for col in columns:
        width, anchor = column_configs.get(col, (100, "center"))
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor=anchor, minwidth=60)
    
    # Add data to table
    for i, proc in enumerate(proc_list):
        # Alternate row colors
        tags = ("evenrow",) if i % 2 == 0 else ("oddrow",)
        
        tree.insert("", "end", values=(
            proc.name,
            proc.arrival_time,
            proc.burst_time,
            proc.priority if proc.priority is not None else "N/A",
            proc.completion_time,
            proc.turnaround_time,
            proc.waiting_time,
            proc.response_time if proc.response_time != -1 else "N/A"
        ), tags=tags)
    
    # Configure row tags
    tree.tag_configure("evenrow", background=("gray95" if ctk.get_appearance_mode() == "Light" else "gray20"))
    tree.tag_configure("oddrow", background=("white" if ctk.get_appearance_mode() == "Light" else "gray25"))
    
    # Add scrollbars
    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    
    # Pack table and scrollbars
    tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    v_scrollbar.pack(side="right", fill="y", pady=10)
    h_scrollbar.pack(side="bottom", fill="x", padx=10)

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
root.title("🖥️ CPU Scheduling Algorithm Simulator")
root.geometry("1200x800")  # Increased width to accommodate results
root.configure(fg_color=("gray95", "gray10"))

# Set window icon (if available)
try:
    root.iconbitmap("")  # Add icon path if available
except:
    pass

# Make window resizable
root.resizable(True, True)

# Center window on screen
root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f"{width}x{height}+{x}+{y}")

# Create main container with padding
main_container = ctk.CTkFrame(root, corner_radius=0, fg_color="transparent")
main_container.pack(fill="both", expand=True, padx=20, pady=20)

# Input frame with enhanced styling
input_frame = ctk.CTkFrame(
    main_container, 
    corner_radius=20,
    fg_color=("white", "gray20"),
    border_width=2,
    border_color=("gray80", "gray30")
)
input_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Configure grid weights for responsive design
input_frame.grid_columnconfigure(0, weight=1)
input_frame.grid_columnconfigure(1, weight=1)
input_frame.grid_columnconfigure(2, weight=1)

algorithms = [
    "First Come First Serve, FCFS", 
    "Shortest Job First, SJF (non-preemptive)",
    "Shortest Remaining Time First, SRTF", 
    "Round-Robin, RR",
    "Priority (non-preemptive)", 
    "Priority (preemptive)"
]

create_input_fields()

root.mainloop()
