# 🖥️ CPU Scheduling Algorithm Simulator

A modern, visually appealing GUI application for simulating and visualizing various CPU scheduling algorithms. Built with CustomTkinter for a professional user interface.

## ✨ Features

### 🎯 Supported Algorithms
- **First Come First Serve (FCFS)**
- **Shortest Job First (SJF) - Non-preemptive**
- **Shortest Remaining Time First (SRTF) - Preemptive**
- **Round-Robin (RR)**
- **Priority Scheduling - Non-preemptive**
- **Priority Scheduling - Preemptive**

### 🎨 Visual Features
- **Modern Dark/Light Theme** support
- **Colorful Gantt Charts** with distinct colors for each process
- **Interactive Legend** and process color reference
- **Professional Statistics Dashboard** with key metrics
- **Enhanced Process Table** with alternating row colors
- **Single Window Interface** with scrollable results

### 📊 Comprehensive Results
- **Gantt Chart Visualization** with gradient effects and shadows
- **Process Statistics Table** showing all timing details
- **Performance Metrics**:
  - Average Turnaround Time
  - Average Waiting Time
  - Average Response Time
  - CPU Utilization
  - Total Processes

### 🚀 User Experience
- **Input Validation** with helpful error messages
- **Example Data Loader** for quick testing
- **Built-in Help System** with comprehensive documentation
- **Keyboard Shortcuts** (Escape to go back)
- **Responsive Design** that adapts to window resizing

## 🛠️ Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup
1. Clone the repository:
```bash
git clone https://github.com/Charan-1007/CPU-scheduling-Algorithm-Simulation-GUI.git
cd CPU-scheduling-Algorithm-Simulation-GUI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python pg.py
```

## 📖 Usage

### Basic Usage
1. **Select Algorithm**: Choose from the dropdown menu
2. **Enter Process Data**:
   - Arrival Times (comma-separated): `0,1,2,3`
   - Burst Times (comma-separated): `5,3,8,6`
   - Priorities (if needed): `2,1,4,3`
   - Time Quantum (for Round-Robin): `2`
3. **Run Simulation**: Click "🚀 Run Simulation"
4. **View Results**: Analyze the Gantt chart and statistics

### Quick Start
- Click "📝 Load Example" to populate fields with sample data
- Click "❓" for comprehensive help documentation

### Navigation
- **⬅️ Back**: Return to input form
- **🔄 New Simulation**: Clear fields and start over
- **Escape Key**: Quick navigation back to input

## 🎨 Visual Design

### Color-Coded Processes
Each process is assigned a unique color from a carefully selected palette:
- Process A: Red (`#FF6B6B`)
- Process B: Teal (`#4ECDC4`)
- Process C: Blue (`#45B7D1`)
- Process D: Green (`#96CEB4`)
- And 4 more vibrant colors...

### Professional Styling
- **Gradient Effects**: Subtle gradients on process blocks
- **Shadow Effects**: 3D appearance with professional shadows
- **Grid System**: Clean organization with proper spacing
- **Typography**: Consistent font hierarchy with icons

## 🔧 Technical Details

### Architecture
- **Single File Application**: All functionality in `pg.py`
- **Object-Oriented Design**: Clean Process class structure
- **Modern GUI Framework**: CustomTkinter for professional appearance
- **Responsive Layout**: Grid-based responsive design

### Algorithms Implementation
- **Accurate Scheduling**: Proper implementation of all algorithms
- **Preemptive Support**: Handles context switching correctly
- **Edge Cases**: Robust handling of various input scenarios
- **Performance Metrics**: Precise calculation of all timing values

## 📚 Educational Value

Perfect for:
- **Computer Science Students** learning operating systems
- **Educators** demonstrating scheduling concepts
- **Researchers** analyzing scheduling performance
- **Anyone** interested in understanding CPU scheduling

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 📞 Support

If you encounter any issues or have questions, please create an issue on GitHub.

---

**Made with ❤️ for learning and education**