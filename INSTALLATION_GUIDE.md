# Installation and Usage Guide
## Advanced Compound Generator Simulation System

---

## Quick Start (No Installation Required)

For the **problem solution only** (no GUI), you can run immediately:

```bash
python3 compound_generator_solver.py
```

This will display:
- Complete solution for Long Shunt configuration
- Complete solution for Short Shunt configuration
- Detailed step-by-step calculations
- Power and efficiency analysis
- Comparison between configurations

**No external libraries required!**

---

## Full Installation (For GUI Application)

### System Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows, Linux, or macOS
- **RAM**: Minimum 2GB (4GB recommended)
- **Display**: 1280x800 or higher resolution

### Step 1: Check Python Installation

```bash
python3 --version
```

If Python is not installed:
- **Windows**: Download from https://www.python.org/downloads/
- **Linux**: `sudo apt-get install python3 python3-pip`
- **macOS**: `brew install python3`

### Step 2: Install Required Packages

#### Option A: Using pip (Recommended)

```bash
pip3 install -r requirements.txt
```

#### Option B: Manual Installation

```bash
pip3 install numpy scipy matplotlib
```

#### Option C: Using Anaconda

```bash
conda create -n generator python=3.9
conda activate generator
conda install numpy scipy matplotlib
```

### Step 3: Install Tkinter (GUI Library)

Tkinter usually comes with Python, but if missing:

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3-tk
```

**Linux (Fedora):**
```bash
sudo dnf install python3-tkinter
```

**macOS:**
```bash
brew install python-tk
```

**Windows:**
Usually included with Python installation. If not, reinstall Python with "tcl/tk" option checked.

### Step 4: Verify Installation

```bash
python3 -c "import tkinter; import numpy; import scipy; import matplotlib; print('All packages installed successfully!')"
```

---

## Running the Applications

### Option 1: Problem Solver (Command Line)

Simple solution without GUI:

```bash
python3 compound_generator_solver.py
```

**Output includes:**
- Detailed calculations
- Step-by-step solutions
- Results comparison
- Power analysis

### Option 2: Full GUI Application

Complete simulation with visualization:

```bash
python3 compound_generator_advanced_simulation.py
```

**Features:**
- Interactive parameter adjustment
- Real-time simulation
- Multi-physics analysis
- Protection systems
- Economic analysis
- Data export capabilities

---

## Usage Instructions

### Basic Operation

1. **Launch Application**
   ```bash
   python3 compound_generator_advanced_simulation.py
   ```

2. **Main Dashboard**
   - Select connection type (Long Shunt / Short Shunt)
   - Adjust load current slider (0-200A)
   - Adjust speed slider (0-3000 RPM)
   - Click "▶ Start" to begin simulation

3. **Monitor Results**
   - Watch real-time graphs update
   - Check voltage, current, and temperature displays
   - View protection status

4. **Advanced Features**
   - Switch between tabs for different analyses
   - Modify parameters in "Advanced Controls"
   - Run multi-physics simulations
   - Calculate economic analysis

### Keyboard Shortcuts

- **F11**: Toggle fullscreen
- **Ctrl+S**: Save configuration
- **Ctrl+O**: Load configuration
- **Ctrl+E**: Export results
- **Ctrl+Q**: Quit application

---

## File Descriptions

| File | Purpose | Dependencies |
|------|---------|-------------|
| `compound_generator_solver.py` | Simple problem solver | None (standard library only) |
| `compound_generator_advanced_simulation.py` | Full GUI application | numpy, scipy, matplotlib, tkinter |
| `requirements.txt` | Python package requirements | - |
| `README_COMPOUND_GENERATOR.md` | Complete documentation | - |
| `INSTALLATION_GUIDE.md` | This file | - |

---

## Troubleshooting

### Issue: "No module named 'tkinter'"

**Solution:**
```bash
# Linux
sudo apt-get install python3-tk

# macOS
brew install python-tk
```

### Issue: "No module named 'numpy'"

**Solution:**
```bash
pip3 install numpy
```

Or install all requirements:
```bash
pip3 install -r requirements.txt
```

### Issue: "ImportError: cannot import name '_tkagg'"

**Solution:**
```bash
pip3 install --upgrade matplotlib
```

### Issue: Display too small / GUI elements overlapping

**Solution:**
- Maximize the window
- Use fullscreen mode (F11 or View → Full Screen)
- Increase screen resolution
- Use zoom controls in your OS

### Issue: Graphs not updating

**Solution:**
- Stop and restart simulation
- Reset simulation (click "↻ Reset")
- Check that sliders are being moved
- Ensure solver is set to "RK45" or "Euler"

### Issue: Protection trips immediately

**Solution:**
- Check protection settings in "Protection Systems" tab
- Increase protection limits if needed
- Ensure parameters are realistic
- Reset simulation before starting

---

## Performance Optimization

### For Faster Simulations

1. **Use Euler Solver**
   - Faster than RK45
   - Less accurate but sufficient for many cases

2. **Reduce Update Frequency**
   - Modify `time.sleep(0.05)` in code to larger value
   - Trade-off: less smooth visualization

3. **Limit History Length**
   - Large histories slow down plotting
   - Export data periodically and reset

### For Better Accuracy

1. **Use RK45 or DOP853 Solver**
   - More accurate integration
   - Adaptive step size

2. **Smaller Time Steps**
   - Modify `self.dt = 0.001` to smaller value
   - Slower but more accurate

---

## Example Workflows

### Workflow 1: Quick Problem Solution

```bash
# Just get the answer
python3 compound_generator_solver.py > solution.txt
cat solution.txt
```

### Workflow 2: Parameter Study

1. Launch GUI application
2. Go to "Advanced Controls" tab
3. Modify armature resistance
4. Click "Apply Parameters"
5. Start simulation
6. Record efficiency
7. Repeat for different resistances
8. Export all results

### Workflow 3: Protection Testing

1. Start simulation with normal parameters
2. Go to "Protection Systems" tab
3. Set overcurrent limit to 110A
4. Return to main dashboard
5. Increase load current to 120A
6. Observe protection trip
7. Check trip log

### Workflow 4: Economic Analysis

1. Run simulation for typical operating conditions
2. Go to "Economic Analysis" tab
3. Enter electricity cost ($/kWh)
4. Enter maintenance costs
5. Click "Calculate Economics"
6. Review LCOE and annual costs
7. Export report

---

## Data Export

### Export Simulation Results

1. **During Simulation**
   - File → Export Results
   - Choose CSV format
   - Select save location

2. **CSV File Contains**
   - Time stamps
   - All voltages (Vt, EMF)
   - All currents (Ia, Ish, Ise)
   - Speed
   - Temperatures
   - Efficiency

3. **Analysis in Excel/Python**
   ```python
   import pandas as pd
   data = pd.read_csv('results.csv')
   print(data.describe())
   data.plot(x='Time', y=['Vt', 'EMF'])
   ```

### Save/Load Configurations

1. **Save Current Setup**
   - File → Save Configuration
   - Creates JSON file with all parameters

2. **Load Previous Setup**
   - File → Load Configuration
   - Restores all settings instantly

3. **Configuration File Format**
   ```json
   {
     "params": {
       "V_rated": 110.0,
       "Ra": 0.06,
       "Rsh": 25.0,
       ...
     },
     "protection": {
       "overcurrent_limit": 150.0,
       ...
     }
   }
   ```

---

## Educational Use

### For Students

1. **Understand Configurations**
   - Run both long and short shunt
   - Compare EMF and currents
   - Observe differences

2. **Parameter Effects**
   - Change resistances
   - See impact on efficiency
   - Learn relationships

3. **Protection Learning**
   - Trigger different protections
   - Understand ANSI codes
   - Study trip characteristics

### For Instructors

1. **Demonstrations**
   - Project GUI on screen
   - Live parameter changes
   - Real-time response

2. **Lab Assignments**
   - Parameter study exercises
   - Efficiency optimization
   - Protection coordination

3. **Assessment**
   - Export student results
   - Compare configurations
   - Verify understanding

---

## Advanced Features

### Custom Modifications

The code is well-structured for modifications:

1. **Add New Parameters**
   - Edit `GeneratorParameters` class
   - Add entries in GUI
   - Update equations

2. **New Visualization**
   - Add subplot to figure
   - Update `update_plots()` method
   - Add to history dictionary

3. **Custom Protection**
   - Add to `ProtectionSettings`
   - Implement check in `check_protections()`
   - Add status label

### Integration with Other Tools

1. **MATLAB/Simulink**
   - Export CSV data
   - Import into MATLAB
   - Compare results

2. **Python Analysis**
   ```python
   from compound_generator_advanced_simulation import CompoundGeneratorModel
   from compound_generator_advanced_simulation import GeneratorParameters

   params = GeneratorParameters()
   model = CompoundGeneratorModel(params)
   result = model.simulate_steady_state(100, 1500)
   print(result)
   ```

3. **Web Integration**
   - Convert to Flask/Django app
   - Use matplotlib for web
   - Add REST API

---

## Support and Documentation

### Built-in Help

- **Help → Documentation**: Quick reference guide
- **Help → About**: Application information
- **Tool tips**: Hover over controls for hints

### Additional Resources

1. **README_COMPOUND_GENERATOR.md**: Complete technical documentation
2. **Code Comments**: Extensive inline documentation
3. **Console Output**: Problem solution with explanations

### Getting Help

1. Check error messages carefully
2. Review console output for debugging
3. Verify all dependencies installed
4. Check parameter ranges are realistic
5. Try resetting simulation

---

## System Architecture

### Code Organization

```
compound_generator_advanced_simulation.py
├── Part 1: Problem Solution (lines 1-150)
├── Part 2: Data Structures (lines 151-250)
├── Part 3: Circuit Model (lines 251-500)
├── Part 4: Protection System (lines 501-600)
└── Part 5: GUI Application (lines 601-end)
```

### Key Classes

- `GeneratorParameters`: Equipment specifications
- `ProtectionSettings`: Protection configuration
- `CompoundGeneratorModel`: Physics and equations
- `ProtectionSystem`: Safety monitoring
- `CompoundGeneratorSimulator`: Main GUI application

---

## Best Practices

### For Accurate Simulations

1. Use realistic parameters
2. Start with rated conditions
3. Allow thermal steady state
4. Check protection settings
5. Validate against analytical solution

### For Performance

1. Use appropriate solver
2. Don't run too long without reset
3. Export data periodically
4. Close unused tabs
5. Limit graph history

### For Learning

1. Start with problem solver
2. Understand analytical solution
3. Then use GUI for exploration
4. Try different configurations
5. Compare with textbook values

---

## Version History

- **v1.0** (2025): Initial release
  - Long and short shunt simulation
  - Multi-physics coupling
  - Protection systems
  - Economic analysis

---

## License

Educational use. Free for academic and research purposes.

---

## Credits

Developed for electrical engineering education and practical analysis.
Based on fundamental electrical machine theory and IEEE standards.

---

**End of Installation Guide**
