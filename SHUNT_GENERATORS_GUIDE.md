# Advanced Three Shunt Generators Simulation System

## Quick Start Guide

### Problem Statement

Three shunt generators, each having an armature resistance of 0.1 ohm, are connected across a common bus feeding a 2 ohms load. Their generated voltages are 127 V, 120 V, and 119 V. Neglecting field currents, calculate the bus voltage and modes of operations of the three machines.

### Solution

**Mathematical Analysis:**

Using Kirchhoff's Current Law at the common bus:
- Current from each generator: `I = (E - V) / Ra`
- Total generator current = Load current

**Results:**
- **Bus Voltage**: 120.00 V
- **Generator 1** (127V): Current = 70 A, Mode = **Generating**, Power = 8400 W
- **Generator 2** (120V): Current = 0 A, Mode = **Floating**, Power = 0 W
- **Generator 3** (119V): Current = -10 A, Mode = **Motoring**, Power = -1200 W
- **Load**: Current = 60 A, Power = 7200 W

**Verification:** 70 + 0 - 10 = 60 A ✓

---

## Installation & Requirements

```bash
# Install required packages
pip install numpy scipy matplotlib tkinter

# Run the application
python shunt_generators_simulation.py
```

### Required Libraries:
- Python 3.7+
- NumPy (numerical computations)
- SciPy (ODE solvers)
- Matplotlib (visualization)
- Tkinter (GUI - usually pre-installed)

---

## Application Features

### 1. Circuit Analysis Tab (📊)

**Features:**
- Real-time parameter adjustment with sliders
- Instant steady-state analysis
- Visual current and power distribution
- Operating mode identification (Generating/Motoring/Floating)
- Efficiency calculations

**How to Use:**
1. Adjust generator EMF values (100-150V)
2. Modify armature resistances (0.01-1.0Ω)
3. Set load resistance (0.1-10Ω)
4. Click "🔍 Analyze" button
5. View results in text panel and graphs

### 2. Dynamic Simulation Tab (🔄)

**Features:**
- Real-time ODE simulation
- Multiple solver methods (RK45, Euler)
- Time-domain analysis
- Six simultaneous plots:
  - Armature currents
  - Field currents
  - Load current
  - Rotor speeds
  - Winding temperatures
  - Generator powers

**How to Use:**
1. Select solver method (RK45 recommended for accuracy)
2. Set simulation time (0.1-10 seconds)
3. Click "▶ Start" to begin simulation
4. Click "⏸ Stop" to halt
5. Click "🔄 Reset" to clear results

**Solver Comparison:**
- **RK45**: Runge-Kutta 4th-5th order, adaptive step, high accuracy
- **Euler**: Forward Euler, fixed step, faster but less accurate

### 3. Multi-Physics Tab (🔬)

**Features:**

#### Thermal Analysis:
- Winding temperature calculation
- Core and frame temperatures
- Thermal distribution modeling
- Hotspot identification
- Derating factor calculation
- Overheating detection

#### Mechanical Stress Analysis:
- Shaft torsional shear stress
- Bearing radial loads
- Centrifugal forces
- Safety factor calculation
- Material stress limits

#### Detailed Loss Breakdown:
- **Copper Losses**: I²R losses in armature and field
- **Hysteresis Loss**: Magnetic hysteresis in core
- **Eddy Current Loss**: Induced current losses
- **Friction Loss**: Bearing friction
- **Windage Loss**: Air resistance
- **Stray Load Loss**: Additional losses under load

**How to Use:**
1. Navigate to Multi-Physics tab
2. Click "Calculate Thermal Distribution"
3. Click "Calculate Mechanical Stress"
4. Review detailed results and safety margins

### 4. Economic Analysis Tab (💰)

**Features:**
- Operating cost calculation
- Lifecycle cost analysis (LCOA)
- Levelized Cost of Energy (LCOE)
- Return on Investment (ROI)
- Payback period estimation
- Cost breakdown by generator

**Parameters:**
- Electricity cost ($/kWh)
- Maintenance cost ($/hr)
- Operating hours
- Project lifetime

**Calculations:**
- Energy cost = (Power + Losses) × Hours × Rate
- Maintenance cost = Hours × Rate
- Capital cost = Rated Power × $/kW
- LCOE = Total Cost / Total Energy
- ROI = (Revenue - Cost) / Capital × 100%

### 5. Advanced Control Tab (⚙️)

**Features:**
- Voltage control systems
- Load sharing strategies
- Thermal derating
- Power consumption monitoring
- Control mode selection:
  - Manual control
  - Automatic regulation
  - PID control
  - Fuzzy logic control

**Load Sharing Strategies:**
- **Equal**: All generators share load equally
- **Proportional**: Based on rated capacity
- **Priority-based**: Optimize efficiency

---

## Technical Details

### Circuit Equations

**Steady-State:**
```
Bus voltage: V = Σ(Ei/Rai) / [Σ(1/Rai) + 1/RL]
Generator current: Ii = (Ei - V) / Rai
Load current: IL = V / RL
```

**Dynamic (Differential Equations):**

1. **Armature Circuit:**
   ```
   La·dIa/dt = Ea - V - Ia·Ra
   ```

2. **Field Circuit:**
   ```
   Lf·dIf/dt = V - If·Rf
   ```

3. **Mechanical Equation:**
   ```
   J·dω/dt = Tm - Te - B·ω
   ```

4. **Thermal Equation:**
   ```
   C·dT/dt = Ploss - (T - Tamb)/Rth
   ```

### Multi-Physics Models

**Electromagnetic:**
- EMF: `Ea = Ke·If·ω`
- Torque: `Te = Kt·If·Ia`

**Thermal Network:**
- Multiple nodes: winding, core, frame, ambient
- Thermal resistances and capacitances
- Heat transfer by conduction, convection, radiation

**Mechanical:**
- Torsional shear stress: `τ = T·r/J`
- Bearing loads from magnetic pull
- Centrifugal forces: `F = m·r·ω²`

**Loss Models:**
- Copper: `Pcu = I²·R(T)`
- Hysteresis: `Ph = Kh·f·Bmax²·V·m`
- Eddy current: `Pe = Ke·f²·Bmax²·V·m`
- Friction: `Pf = B·ω²`
- Windage: `Pw = Kw·ω²·d³`

---

## Auto-Scaling Features

The GUI automatically adjusts to window size changes:
- Responsive layout with grid weights
- Canvas auto-resize on window events
- Proportional scaling of all elements
- Maintains aspect ratios

**To resize:**
- Drag window edges
- Maximize/minimize window
- All plots and controls scale automatically

---

## Practical Applications

### 1. Power Plant Operations
- Parallel generator operation
- Load distribution optimization
- Stability analysis

### 2. Marine Engineering
- Ship power systems
- Emergency generator coordination

### 3. Industrial Facilities
- Co-generation systems
- Backup power analysis

### 4. Grid Integration
- Distributed generation
- Microgrid operation

### 5. Educational Use
- Electrical engineering labs
- Power systems courses
- Research projects

---

## Advanced Features

### Real-Time Simulation
- Thread-based computation
- Non-blocking GUI updates
- Progress indication
- Cancelable operations

### Scientific Computing
- NumPy for matrix operations
- SciPy for ODE integration
- Adaptive time-stepping
- Numerical stability

### Professional Visualization
- Matplotlib integration
- Multiple synchronized plots
- Color-coded operating modes
- Publication-quality graphics

---

## Troubleshooting

### Common Issues:

**1. Import Errors:**
```bash
# Install missing packages
pip install numpy scipy matplotlib
```

**2. Tkinter Not Found:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS (included with Python)
# Windows (included with Python)
```

**3. Simulation Doesn't Start:**
- Check that parameters are valid
- Ensure no other simulation is running
- Try resetting parameters

**4. Window Doesn't Resize:**
- Click and drag edges
- Use maximize button
- Restart application if needed

---

## Operating Modes Explained

### Generating Mode (Current > 0)
- Generator supplies power to bus
- EMF > Bus Voltage
- Normal operation
- Positive power output

### Motoring Mode (Current < 0)
- Generator draws power from bus
- EMF < Bus Voltage
- Acting as motor
- Negative power (consuming)

### Floating Mode (Current ≈ 0)
- Generator connected but not loaded
- EMF ≈ Bus Voltage
- No power exchange
- Standby operation

---

## Performance Tips

1. **For Fast Analysis:**
   - Use steady-state tab
   - Adjust parameters with sliders
   - Instant results

2. **For Detailed Dynamics:**
   - Use RK45 solver
   - Shorter time spans (0.1-1s)
   - Monitor all variables

3. **For Accuracy:**
   - Include inductances
   - Consider thermal effects
   - Use multi-physics analysis

4. **For Economics:**
   - Input realistic costs
   - Consider full lifetime
   - Compare different scenarios

---

## Validation & Accuracy

### Mathematical Verification:
- Kirchhoff's laws satisfied
- Power balance maintained
- Energy conservation checked

### Numerical Stability:
- Adaptive time-stepping
- Error tolerance control
- Stiff equation handling

### Physical Realism:
- Temperature limits enforced
- Material properties accurate
- Loss models validated

---

## Future Enhancements

Potential additions:
- Voltage regulator modeling
- Fault analysis (short circuits)
- Harmonics analysis
- Network export (JSON, CSV)
- Report generation (PDF)
- Database integration
- Cloud simulation

---

## References

1. Electric Machinery Fundamentals - Stephen J. Chapman
2. Power System Analysis - Hadi Saadat
3. Electrical Machines, Drives, and Power Systems - Theodore Wildi
4. IEEE Standards for Rotating Electrical Machines
5. Thermal Analysis of Electrical Machines - COMSOL

---

## License & Support

Created for electrical engineering education and professional use.

**Contact:**
- For bugs: Report via GitHub issues
- For features: Submit pull requests
- For questions: Check documentation

---

## Quick Reference

### Keyboard Shortcuts:
- `Ctrl+R`: Reset parameters
- `Ctrl+S`: Start simulation
- `Ctrl+Q`: Quit application

### Default Values:
- Generator 1: 127V, 0.1Ω
- Generator 2: 120V, 0.1Ω
- Generator 3: 119V, 0.1Ω
- Load: 2.0Ω

### Typical Results:
- Bus Voltage: 120V
- System Efficiency: 85-95%
- Temperature Rise: 50-100°C
- Operating Speed: 1500-1800 RPM

---

**Version:** 1.0.0
**Last Updated:** 2025-01-08
**Author:** Advanced Electrical Engineering Simulation Lab
