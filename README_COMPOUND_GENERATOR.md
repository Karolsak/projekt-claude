# Advanced Compound Generator Simulation & Analysis System

## Overview

This is a comprehensive Python application for simulating and analyzing compound DC generators with advanced multi-physics capabilities. The system solves the specific compound generator problem and provides a full-featured GUI for real-time simulation, analysis, and visualization.

## Problem Solution

### Given Problem
- **110V compound generator**
- Armature resistance (Ra): 0.06 Ω
- Shunt field resistance (Rsh): 25 Ω
- Series field resistance (Rse): 0.04 Ω
- Load: 200 lamps × 55W @ 110V = 11,000W
- Load current: 100A

### Solutions

#### (i) Long Shunt Configuration
- **Total EMF**: 116.5200 V
- **Armature Current**: 104.400 A
- Shunt field current: 4.400 A
- Series field current: 104.400 A

#### (ii) Short Shunt Configuration
- **Total EMF**: 116.5360 V
- **Armature Current**: 104.360 A
- Shunt field current: 4.360 A
- Series field current: 100.000 A

## Features

### 1. User Interface (Tkinter GUI)
- **Main Dashboard**: Real-time monitoring and control
- **7 Specialized Tabs**: Main, Advanced Controls, Loss Analysis, Thermal Analysis, Protection Systems, Economic Analysis, Multi-Physics
- **Responsive Design**: Auto-scaling with window resize
- **Professional Layout**: Organized panels with clear information display

### 2. Circuit Modeling
- **Differential Equations**: Full electromagnetic circuit model
- **Two Configurations**: Long shunt and short shunt
- **RMS Values**: All simulations use RMS values for practical accuracy
- **Dynamic Simulation**: Real-time ODE solving

### 3. ODE Solvers
- **RK45** (Runge-Kutta 4-5): Adaptive step size, recommended for most cases
- **Euler**: Simple explicit method, fast but less accurate
- **RK23** (Runge-Kutta 2-3): Lower-order adaptive method
- **DOP853**: High-accuracy Dormand-Prince 8th order

### 4. Multi-Physics Simulation

#### Electromagnetic Model
- Magnetic field distribution visualization
- EMF calculation based on flux and speed
- Armature reaction effects

#### Thermal Model
- Heat transfer equations coupled with electrical equations
- Temperature distribution visualization
- Armature and field winding temperature tracking
- Ambient temperature effects
- Thermal time constants

#### Mechanical Model
- Shaft torque calculation and transients
- Bearing load analysis (radial and axial)
- Mechanical stress distribution
- Safety factor calculation
- Moment of inertia and damping effects

### 5. Loss Analysis

Detailed breakdown of all losses:
- **Copper Losses**: I²R losses in armature, shunt, and series windings
- **Iron Losses**:
  - Hysteresis losses (proportional to frequency and B²)
  - Eddy current losses (proportional to f² and B²)
- **Mechanical Losses**: Friction and windage (proportional to speed²)
- **Stray Load Losses**: Approximately 1% of output power
- **Efficiency Calculation**: Real-time and efficiency curves

### 6. Machine Protection Systems

All protections follow ANSI/IEEE standards:

| Protection | ANSI Code | Function |
|------------|-----------|----------|
| Overcurrent | 50/51 | Instantaneous and time-delayed overcurrent |
| Overvoltage | 59 | High voltage protection |
| Undervoltage | 27 | Low voltage protection |
| Overtemperature | 49 | Thermal overload protection |
| Overspeed | 12 | Speed monitoring and trip |

Features:
- Configurable trip settings
- Real-time monitoring
- Trip log with timestamps
- Visual status indicators

### 7. Economic Analysis

Comprehensive cost analysis including:
- Annual energy consumption (kWh)
- Energy costs ($/kWh)
- Maintenance costs
- Total operating costs
- Levelized Cost of Energy (LCOE)
- Simple payback period calculation
- Net Present Value (NPV) analysis
- Equipment lifecycle costs

### 8. Advanced Controls

#### Operating Parameters
- Load current control: 0-200A with real-time slider
- Speed control: 0-3000 RPM
- Connection type switching (long/short shunt)

#### Machine Parameters (Adjustable)
- Electrical: Ra, Rsh, Rse, La, Lsh, Lse
- Mechanical: J, B, poles, Kφ
- Thermal: Thermal resistance, capacitance, max temperature

### 9. Real-Time Visualization

#### Main Dashboard Graphs
1. **Voltages & Currents**: Vt, EMF, Ia vs time
2. **Power & Efficiency**: Output power and efficiency vs time
3. **Temperature**: Armature and field temperature vs time

#### Analysis Graphs
- Efficiency vs load current curve
- Temperature distribution (2D contour)
- Electromagnetic field distribution
- Thermal field visualization
- Mechanical stress distribution

### 10. Thermal Analysis & Derating

- Real-time temperature monitoring
- Thermal resistance and capacitance modeling
- Heat dissipation calculations
- Derating factor display
- Temperature distribution visualization
- Maximum temperature limits with warnings

## Installation

### Requirements
```bash
pip install numpy scipy matplotlib
```

Standard libraries used: tkinter, json, datetime, threading, time

### Running the Application
```bash
python compound_generator_advanced_simulation.py
```

## Usage Guide

### Quick Start
1. **Launch Application**: Run the Python script
2. **View Problem Solution**: Console displays the analytical solution
3. **Select Configuration**: Choose Long Shunt or Short Shunt
4. **Adjust Parameters**: Use sliders to set load current and speed
5. **Start Simulation**: Click "▶ Start" button
6. **Monitor**: Watch real-time graphs and displays
7. **Analyze**: Switch to other tabs for detailed analysis

### Main Dashboard

**Control Panel** (Left):
- Connection type selection
- Simulation controls (Start, Pause, Stop, Reset)
- Load current slider (0-200A)
- Speed slider (0-3000 RPM)
- ODE solver selection

**Real-Time Monitoring** (Right):
- Terminal voltage, EMF
- All currents (Ia, Ish, Ise, IL)
- Speed and torque
- Temperatures

**Graphs** (Bottom):
- Live plotting of key parameters
- Auto-scaling axes
- Multiple series on each plot

### Advanced Controls Tab
- Modify all electrical parameters (resistances, inductances)
- Adjust mechanical parameters (inertia, damping, poles)
- Apply changes with "Apply Parameters" button

### Loss Analysis Tab
- View real-time loss breakdown
- Calculate efficiency vs load curve
- Identify optimal operating point
- Maximum efficiency annotation

### Thermal Analysis Tab
- Set thermal parameters
- View temperature distribution
- Monitor derating factor
- Check thermal limits

### Protection Systems Tab
- Configure all protection limits
- View real-time protection status
- Monitor trip log
- ANSI standard compliance

### Economic Analysis Tab
- Enter cost parameters
- Calculate annual costs
- Determine LCOE
- Evaluate economic viability

### Multi-Physics Tab
- Run coupled field analysis
- View electromagnetic field
- Analyze thermal distribution
- Calculate mechanical stress
- Check bearing loads and safety factors

## Menu Options

### File Menu
- **Load Configuration**: Load saved parameters from JSON
- **Save Configuration**: Save current parameters to JSON
- **Export Results**: Export simulation data to CSV
- **Exit**: Close application

### Simulation Menu
- **Start**: Begin simulation
- **Pause**: Pause/resume simulation
- **Stop**: Stop simulation
- **Reset**: Reset to initial conditions

### View Menu
- **Full Screen**: Toggle fullscreen mode

### Help Menu
- **About**: Application information
- **Documentation**: Quick reference guide

## Technical Details

### Circuit Equations

#### Long Shunt
```
EMF = Vt + Ise×Rse + Ia×Ra
Ia = Ise = IL + Ish
Vshunt = Vt
Ish = Vt / Rsh
```

#### Short Shunt
```
EMF = Va + Ia×Ra
Va = Vt + Ise×Rse
Ia = IL + Ish
Ise = IL
Ish = Va / Rsh
```

### Differential Equations

State vector: `[Ia, Ish, Ise, θ, ω, T_arm, T_field]`

**Electrical:**
```
La × dIa/dt = EMF - Ia×Ra - Ise×Rse - Vt
Lsh × dIsh/dt = Vt - Ish×Rsh
```

**Mechanical:**
```
J × dω/dt = T_em - T_load - B×ω
T_em = Kφ × Ish × Ia
```

**Thermal:**
```
C_th × dT/dt = P_loss - (T - T_amb)/R_th
```

### Loss Calculations

**Copper Losses:**
```
P_cu = Ia²×Ra + Ish²×Rsh + Ise²×Rse
```

**Iron Losses:**
```
P_iron = k_h×f×B² + k_e×f²×B²
```

**Mechanical Losses:**
```
P_mech = k_mech×ω²
```

## Data Export

Simulation results can be exported to CSV with columns:
- Time
- Terminal Voltage (Vt)
- EMF
- Armature Current (Ia)
- Shunt Current (Ish)
- Series Current (Ise)
- Speed (RPM)
- Armature Temperature
- Field Temperature
- Efficiency

## Educational Value

This application is designed for:
- **Electrical Engineering Students**: Understanding DC machine operation
- **Laboratory Work**: Virtual experiments and parameter studies
- **Research**: Multi-physics analysis and optimization
- **Professional Training**: Protection system understanding
- **Design Work**: Performance prediction and analysis

## Key Learning Outcomes

1. **Circuit Analysis**: Understanding compound generator configurations
2. **Dynamic Behavior**: Transient response and steady-state operation
3. **Loss Mechanisms**: Identifying and quantifying losses
4. **Protection Philosophy**: Implementing standard protection schemes
5. **Economic Analysis**: Cost-benefit evaluation
6. **Multi-Physics**: Coupled field interactions
7. **Optimization**: Finding optimal operating points

## Future Enhancements

Potential additions:
- [ ] Field weakening control
- [ ] Automatic voltage regulation (AVR)
- [ ] Load sharing between parallel generators
- [ ] Fault simulation (short circuits, open circuits)
- [ ] 3D visualization of fields
- [ ] Real-time data logging to database
- [ ] Remote monitoring capabilities
- [ ] AI-based optimization

## License

This educational software is provided as-is for academic and research purposes.

## Author

Created for electrical engineering education and practical analysis.

## References

1. Electric Machinery Fundamentals - Stephen Chapman
2. Electrical Machines, Drives and Power Systems - Theodore Wildi
3. IEEE/ANSI Standards for Generator Protection
4. Power System Analysis - Grainger & Stevenson

## Support

For issues, improvements, or questions:
- Review the built-in documentation (Help → Documentation)
- Check the console output for the analytical solution
- Experiment with different parameters to understand behavior
- Export data for external analysis

---

**Version**: 1.0
**Last Updated**: 2025
**Platform**: Cross-platform (Windows, Linux, macOS)
**Python Version**: 3.7+
