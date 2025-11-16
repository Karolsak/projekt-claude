# DC Shunt Generator - Advanced Simulation & Analysis System

A comprehensive Python + Tkinter application for DC generator analysis with multi-physics simulation, designed for practical use in electrical engineering education and research.

## Problem Solved

**DC Shunt Generator Problem:**
A D.C. shunt generator has a full load output of 10 kW at a terminal voltage of 240 V. The armature and the shunt field winding resistances are 0.6 and 160 ohms respectively. The sum of the mechanical and core-losses is 500 W.

**Solution:**
- **(a) Shaft Power Required:** 11.978 kW
- **(b) Efficiency:** 83.49%

## Features

### 1. Mathematical Problem Solver
- Solves DC shunt and compound generator problems
- Calculates shaft power, efficiency, losses, and torque
- Supports both efficiency-based and loss-based problem formulations
- Interactive GUI with parameter sliders

### 2. Dynamic Simulation
- **ODE Solvers:** Multiple integration methods
  - RK45 (Runge-Kutta 4th/5th order) - Default
  - RK23 (Runge-Kutta 2nd/3rd order)
  - DOP853 (8th order Runge-Kutta)
  - Radau (Implicit Runge-Kutta)
  - BDF (Backward Differentiation Formula)
  - LSODA (Automatic stiff/non-stiff)
  - Euler (Simple forward Euler)

- **State Variables:**
  - Armature current (Ia)
  - Field current (Ish)
  - Angular velocity (ω)
  - Angular position (θ)
  - Armature temperature
  - Field temperature

- **RMS Values:** All voltage and current calculations use RMS values for accurate simulation

### 3. Multi-Physics Simulation

#### Electromagnetic Model
- Differential equations for armature and field circuits
- Back EMF calculation: Eb = Ke × ω × Ish
- Electromagnetic torque: T_em = Kt × Ia × Ish

#### Thermal Model
- Coupled thermal equations for armature and field windings
- Temperature-dependent resistance
- Heat transfer equations: dT/dt = (P_loss - Q_dissipated) / C_thermal
- Thermal resistance and capacitance modeling

#### Mechanical Model
- Shaft dynamics: J × dω/dt = T_em - B×ω - T_load
- Torsional stress analysis
- Bearing load calculation
- Safety factor computation

#### Detailed Loss Analysis
- **Copper Losses:**
  - Armature: Ia²Ra (temperature-dependent)
  - Shunt field: Ish²Rsh
  - Series field: Ise²Rse

- **Iron Losses:**
  - Hysteresis loss: k_h × f × B^1.6 (Steinmetz equation)
  - Eddy current loss: k_e × f² × B²

- **Mechanical Losses:**
  - Friction loss: B × ω²
  - Windage loss: k_w × ω³

- **Stray Load Losses:** ~1% of output power

### 4. Advanced Controls

#### Control Methods
1. **Voltage Control** - Adjust applied voltage
2. **Field Control** - Vary field current
3. **Armature Resistance Control** - External resistance
4. **Ward-Leonard Control** - Motor-generator set
5. **Thyristor Control** - Modern electronic control

#### Thermal Derating
- Temperature-based derating factor
- Altitude compensation (air density)
- Rated temperature: 40°C reference
- Derating: 1% per °C above rated temperature

### 5. Economic Analysis
- **Operating Costs:**
  - Energy consumption (electricity cost per kWh)
  - Maintenance costs

- **Lifecycle Analysis:**
  - Net Present Value (NPV) calculation
  - Levelized cost of energy
  - Discount rate consideration

- **Payback Analysis:**
  - Payback period calculation
  - Return on Investment (ROI)
  - Annual profit projection

### 6. Visualization
- **Real-time Graphs:**
  - Armature and field currents
  - Speed and torque
  - Temperature profiles
  - Efficiency curves
  - Power flow diagrams
  - Loss breakdown (pie charts)

- **Auto-scaling:** Responsive GUI with automatic width/height adjustment

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd projekt-claude

# Install dependencies
pip install -r requirements_dynamo.txt

# For GUI (requires tkinter)
# On Ubuntu/Debian:
sudo apt-get install python3-tk

# On macOS (with Homebrew):
brew install python-tk

# On Windows:
# Tkinter is usually included with Python
```

## Usage

### Run the Full Application
```bash
python3 dynamo_advanced_simulator.py
```

This will:
1. Print the solution to the DC shunt generator problem to console
2. Launch the interactive GUI application

### Run Test (No GUI Required)
```bash
python3 test_shunt_generator.py
```

### GUI Tabs

1. **Problem Solver**
   - Select machine type (Shunt/Compound)
   - Enter parameters
   - View detailed results

2. **Dynamic Simulation**
   - Adjust voltage, torque, speed
   - Select ODE solver method
   - Start/Stop/Reset controls
   - View 6 real-time plots

3. **Multi-Physics Analysis**
   - Loss breakdown visualization
   - Thermal analysis
   - Power flow analysis
   - Mechanical stress analysis

4. **Economic Analysis**
   - Operating cost calculation
   - Lifecycle cost analysis
   - Payback period

5. **Advanced Controls**
   - Control method selection
   - Thermal derating calculator
   - Power consumption monitoring

## Technical Details

### Differential Equations

**Armature Circuit:**
```
La × dIa/dt = V_applied - Eb - Ia×(Ra + Rse)
```

**Field Circuit:**
```
Lsh × dIsh/dt = V_applied - Ish×Rsh
```

**Mechanical:**
```
J × dω/dt = Kt×Ia×Ish - B×ω - T_load
```

**Thermal:**
```
C_th × dT/dt = P_loss - (T - T_ambient)/R_th
```

### Default Parameters

- Armature resistance (Ra): 0.6 Ω
- Armature inductance (La): 0.01 H
- Shunt field resistance (Rsh): 160 Ω
- Shunt field inductance (Lsh): 5.0 H
- Moment of inertia (J): 0.5 kg·m²
- Damping coefficient (B): 0.01 N·m·s
- Torque constant (Kt): 1.2 N·m/A
- Back EMF constant (Ke): 1.2 V·s/rad

## File Structure

```
projekt-claude/
├── dynamo_advanced_simulator.py  # Main application with GUI
├── test_shunt_generator.py       # Test script (no GUI)
├── test_dynamo_solution.py       # Original test file
├── requirements_dynamo.txt        # Python dependencies
├── README.md                      # This file
└── README_DYNAMO_SIMULATOR.md    # Detailed documentation
```

## Dependencies

- Python 3.7+
- numpy - Numerical computations
- scipy - ODE solvers and interpolation
- matplotlib - Plotting and visualization
- tkinter - GUI framework (usually included with Python)

## Results for Given Problem

**Problem:** 10 kW output at 240 V, Ra = 0.6Ω, Rsh = 160Ω, Mech+Core loss = 500W

**Calculated:**
- Load Current: 41.667 A
- Field Current: 1.500 A
- Armature Current: 43.167 A
- Back EMF: 265.900 V
- Armature Copper Loss: 1118.017 W
- Shunt Copper Loss: 360.000 W
- **Shaft Power: 11.978 kW** ← Answer (a)
- **Efficiency: 83.49%** ← Answer (b)

## Educational Value

This application is designed for:
- Electrical engineering students learning about DC machines
- Laboratory exercises and experiments
- Research on generator performance optimization
- Control system design and testing
- Economic feasibility studies
- Multi-physics analysis training

## License

See LICENSE file for details.

## Author

Created for electrical engineering education and research.

## Support

For issues or questions, please open an issue in the repository.
