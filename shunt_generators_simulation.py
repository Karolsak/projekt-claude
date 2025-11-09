"""
Advanced Three Shunt Generators Circuit Analysis and Simulation System
========================================================================
A comprehensive electrical engineering tool for analyzing shunt generators
with multi-physics simulation capabilities.

Features:
- Real-time circuit analysis
- Dynamic ODE simulation (RK45, Euler)
- Multi-physics modeling (electromagnetic, thermal, mechanical)
- Economic analysis
- Advanced control systems
- Auto-scaling GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.integrate import solve_ivp
import threading
import time
from dataclasses import dataclass
from typing import List, Tuple, Dict
import json


@dataclass
class GeneratorParameters:
    """Physical parameters for a shunt generator"""
    emf: float = 127.0  # Generated voltage (V)
    ra: float = 0.1     # Armature resistance (Ω)
    rf: float = 100.0   # Field resistance (Ω)
    la: float = 0.01    # Armature inductance (H)
    lf: float = 5.0     # Field inductance (H)
    j: float = 0.5      # Moment of inertia (kg⋅m²)
    b: float = 0.01     # Friction coefficient

    # Thermal parameters
    thermal_resistance: float = 2.0      # K/W
    thermal_capacitance: float = 500.0   # J/K
    ambient_temp: float = 25.0           # °C
    max_temp: float = 155.0              # °C (Class F insulation)

    # Physical dimensions
    length: float = 0.5       # m
    diameter: float = 0.3     # m
    winding_mass: float = 50.0  # kg
    core_mass: float = 100.0    # kg

    # Material properties
    copper_resistivity: float = 1.68e-8  # Ω⋅m at 20°C
    temp_coefficient: float = 0.00393    # per °C


@dataclass
class LoadParameters:
    """Load parameters"""
    resistance: float = 2.0  # Ω
    inductance: float = 0.05  # H
    active_power: float = 0.0  # W (calculated)


class CircuitAnalyzer:
    """Core circuit analysis engine"""

    def __init__(self):
        self.generators: List[GeneratorParameters] = []
        self.load = LoadParameters()
        self.bus_voltage = 0.0
        self.currents = []
        self.modes = []
        self.total_power = 0.0

    def add_generator(self, gen: GeneratorParameters):
        """Add a generator to the system"""
        self.generators.append(gen)

    def solve_steady_state(self) -> Dict:
        """
        Solve steady-state circuit equations using Kirchhoff's laws
        Returns: Dictionary with results
        """
        n = len(self.generators)
        if n == 0:
            return {}

        # Build system of equations: Sum of currents = Load current
        # (E1 - V)/Ra1 + (E2 - V)/Ra2 + ... = V/RL

        sum_e_over_ra = sum(gen.emf / gen.ra for gen in self.generators)
        sum_1_over_ra = sum(1.0 / gen.ra for gen in self.generators)

        # V * (sum(1/Ra) + 1/RL) = sum(E/Ra)
        self.bus_voltage = sum_e_over_ra / (sum_1_over_ra + 1.0 / self.load.resistance)

        # Calculate individual currents
        self.currents = []
        self.modes = []
        total_gen_current = 0.0

        for i, gen in enumerate(self.generators):
            current = (gen.emf - self.bus_voltage) / gen.ra
            self.currents.append(current)
            total_gen_current += current

            # Determine mode
            if current > 0.1:
                mode = "Generating"
            elif current < -0.1:
                mode = "Motoring"
            else:
                mode = "Floating"
            self.modes.append(mode)

        # Load current
        load_current = self.bus_voltage / self.load.resistance

        # Powers
        powers = [self.bus_voltage * I for I in self.currents]
        load_power = self.bus_voltage * load_current

        # Losses
        copper_losses = [I**2 * gen.ra for I, gen in zip(self.currents, self.generators)]

        results = {
            'bus_voltage': self.bus_voltage,
            'currents': self.currents,
            'modes': self.modes,
            'load_current': load_current,
            'powers': powers,
            'load_power': load_power,
            'copper_losses': copper_losses,
            'total_copper_loss': sum(copper_losses),
            'efficiency': load_power / sum(p for p in powers if p > 0) * 100 if sum(p for p in powers if p > 0) > 0 else 0
        }

        return results


class DynamicSimulator:
    """Dynamic simulation using ODE solvers"""

    def __init__(self, analyzer: CircuitAnalyzer):
        self.analyzer = analyzer
        self.time_history = []
        self.state_history = []
        self.solver_method = 'RK45'  # Default solver
        self.running = False

    def system_dynamics(self, t, y):
        """
        Define system differential equations
        State vector y = [Ia1, Ia2, Ia3, If1, If2, If3, IL, omega1, omega2, omega3, T1, T2, T3]
        where:
        - Ia: Armature currents
        - If: Field currents
        - IL: Load current
        - omega: Angular velocities
        - T: Temperatures
        """
        n = len(self.analyzer.generators)

        # Extract states
        ia = y[0:n]
        if_currents = y[n:2*n]
        il = y[2*n]
        omega = y[2*n+1:3*n+1]
        temps = y[3*n+1:4*n+1]

        # Derivatives
        dydt = np.zeros_like(y)

        # Voltage equations for armature circuits
        # La * dIa/dt = Ea - V - Ia*Ra
        v_bus = self.analyzer.bus_voltage  # Use current bus voltage

        for i, gen in enumerate(self.analyzer.generators):
            # Adjust Ra with temperature
            ra_temp = gen.ra * (1 + gen.temp_coefficient * (temps[i] - 20))

            # Back EMF proportional to field current and speed
            ke = 0.5  # EMF constant
            ea = ke * if_currents[i] * omega[i]

            # Armature current derivative
            dydt[i] = (ea - v_bus - ia[i] * ra_temp) / gen.la

            # Field current derivative
            # Lf * dIf/dt = V - If*Rf
            dydt[n + i] = (v_bus - if_currents[i] * gen.rf) / gen.lf

            # Mechanical equation
            # J * domega/dt = Tm - Te - B*omega
            kt = 0.5  # Torque constant
            te = kt * if_currents[i] * ia[i]  # Electromagnetic torque
            tm = ea * ia[i] / (omega[i] + 1e-6)  # Mechanical torque
            dydt[2*n + 1 + i] = (tm - te - gen.b * omega[i]) / gen.j

            # Thermal equation
            # C * dT/dt = Ploss - (T - Tamb)/Rth
            copper_loss = ia[i]**2 * ra_temp + if_currents[i]**2 * gen.rf
            iron_loss = 0.01 * omega[i]**2  # Simplified iron loss
            friction_loss = gen.b * omega[i]**2
            total_loss = copper_loss + iron_loss + friction_loss

            dydt[3*n + 1 + i] = (total_loss - (temps[i] - gen.ambient_temp) / gen.thermal_resistance) / gen.thermal_capacitance

        # Load current derivative
        # LL * dIL/dt = V - IL*RL
        dydt[2*n] = (v_bus - il * self.analyzer.load.resistance) / self.analyzer.load.inductance

        return dydt

    def simulate(self, t_span, y0, method='RK45'):
        """
        Run simulation using specified ODE solver
        """
        self.solver_method = method
        self.running = True

        if method == 'RK45':
            sol = solve_ivp(self.system_dynamics, t_span, y0, method='RK45',
                          max_step=0.01, dense_output=True)
        elif method == 'Euler':
            # Manual Euler integration
            t = np.arange(t_span[0], t_span[1], 0.001)
            y = np.zeros((len(y0), len(t)))
            y[:, 0] = y0

            for i in range(1, len(t)):
                if not self.running:
                    break
                dt = t[i] - t[i-1]
                dydt = self.system_dynamics(t[i-1], y[:, i-1])
                y[:, i] = y[:, i-1] + dydt * dt

            class Solution:
                def __init__(self, t, y):
                    self.t = t
                    self.y = y
            sol = Solution(t, y)

        self.time_history = sol.t
        self.state_history = sol.y
        self.running = False

        return sol


class MultiPhysicsEngine:
    """Advanced multi-physics simulation engine"""

    def __init__(self, analyzer: CircuitAnalyzer):
        self.analyzer = analyzer

    def calculate_detailed_losses(self, current, omega, temp, gen: GeneratorParameters):
        """Calculate detailed loss breakdown"""
        # Temperature-dependent resistance
        ra_temp = gen.ra * (1 + gen.temp_coefficient * (temp - 20))

        # Copper losses (I²R)
        copper_loss_armature = current**2 * ra_temp
        field_current = self.analyzer.bus_voltage / gen.rf
        copper_loss_field = field_current**2 * gen.rf

        # Iron losses (hysteresis + eddy current)
        # Ph = Kh * f * Bmax^2 * Volume
        # Pe = Ke * f^2 * Bmax^2 * Volume
        freq = omega / (2 * np.pi)
        volume = np.pi * (gen.diameter/2)**2 * gen.length
        b_max = 1.2  # Tesla (typical)
        kh = 0.001  # Hysteresis constant
        ke = 0.0001  # Eddy current constant

        hysteresis_loss = kh * freq * b_max**2 * volume * gen.core_mass
        eddy_loss = ke * freq**2 * b_max**2 * volume * gen.core_mass
        iron_loss = hysteresis_loss + eddy_loss

        # Mechanical losses
        # Friction loss = k * omega^2
        friction_loss = gen.b * omega**2

        # Windage loss (air friction)
        windage_loss = 0.001 * omega**2 * (gen.diameter**3)

        # Stray load loss (approx 1% of output)
        output_power = self.analyzer.bus_voltage * current
        stray_loss = 0.01 * abs(output_power)

        losses = {
            'copper_armature': copper_loss_armature,
            'copper_field': copper_loss_field,
            'hysteresis': hysteresis_loss,
            'eddy_current': eddy_loss,
            'friction': friction_loss,
            'windage': windage_loss,
            'stray': stray_loss,
            'total': (copper_loss_armature + copper_loss_field + iron_loss +
                     friction_loss + windage_loss + stray_loss)
        }

        return losses

    def calculate_thermal_distribution(self, loss, gen: GeneratorParameters, ambient=25.0):
        """Calculate steady-state thermal distribution"""
        # Simplified thermal network
        # Multiple thermal nodes: winding, core, frame, ambient

        # Thermal resistances
        r_winding_core = 0.5  # K/W
        r_core_frame = 1.0    # K/W
        r_frame_ambient = gen.thermal_resistance  # K/W

        # Assume losses distributed: 60% winding, 40% core
        q_winding = 0.6 * loss
        q_core = 0.4 * loss

        # Solve thermal network
        # T_winding = T_core + q_winding * R_winding_core
        # T_core = T_frame + (q_winding + q_core) * R_core_frame
        # T_frame = T_amb + (q_winding + q_core) * R_frame_ambient

        t_frame = ambient + (q_winding + q_core) * r_frame_ambient
        t_core = t_frame + (q_winding + q_core) * r_core_frame
        t_winding = t_core + q_winding * r_winding_core

        return {
            'winding': t_winding,
            'core': t_core,
            'frame': t_frame,
            'ambient': ambient,
            'hotspot': max(t_winding, t_core)
        }

    def calculate_mechanical_stress(self, torque, omega, gen: GeneratorParameters):
        """Calculate mechanical stress analysis"""
        # Shaft stress
        # Torsional shear stress: τ = T*r/J
        shaft_radius = 0.05  # m (assumed)
        polar_moment = np.pi * shaft_radius**4 / 2
        shear_stress = torque * shaft_radius / polar_moment

        # Bearing loads
        # Radial load from magnetic pull
        radial_load = 0.1 * torque / shaft_radius  # Simplified

        # Centrifugal force on rotor
        rotor_mass = gen.core_mass / 2  # Half of core mass
        centrifugal_force = rotor_mass * (gen.diameter/2) * omega**2

        return {
            'shear_stress': shear_stress,  # Pa
            'radial_load': radial_load,    # N
            'centrifugal_force': centrifugal_force,  # N
            'max_stress': shear_stress,    # Pa
            'safety_factor': 250e6 / (shear_stress + 1e-6)  # Assuming steel yield = 250 MPa
        }

    def calculate_efficiency_derating(self, temp, gen: GeneratorParameters):
        """Calculate derating factor based on temperature"""
        if temp <= gen.max_temp * 0.8:
            return 1.0
        elif temp <= gen.max_temp:
            # Linear derating from 80% to 100% of max temp
            return 1.0 - 0.5 * (temp - 0.8*gen.max_temp) / (0.2*gen.max_temp)
        else:
            # Severe derating above max temp
            return max(0.5, 1.0 - 0.02 * (temp - gen.max_temp))


class EconomicAnalyzer:
    """Economic and cost analysis"""

    def __init__(self):
        self.electricity_cost = 0.12  # $/kWh
        self.maintenance_cost_per_hour = 5.0  # $/hr
        self.capital_cost_per_kw = 500.0  # $/kW

    def calculate_operating_cost(self, power_kw, hours, losses_kw):
        """Calculate operating cost"""
        energy_cost = (power_kw + losses_kw) * hours * self.electricity_cost
        maintenance_cost = hours * self.maintenance_cost_per_hour
        total_cost = energy_cost + maintenance_cost

        return {
            'energy_cost': energy_cost,
            'maintenance_cost': maintenance_cost,
            'total_operating_cost': total_cost,
            'cost_per_kwh': total_cost / (power_kw * hours) if power_kw > 0 else 0
        }

    def calculate_lifecycle_cost(self, rated_power_kw, lifetime_years,
                                 capacity_factor, efficiency):
        """Calculate lifecycle cost analysis"""
        annual_hours = 8760 * capacity_factor
        total_hours = annual_hours * lifetime_years

        # Capital cost
        capital_cost = rated_power_kw * self.capital_cost_per_kw

        # Operating cost
        annual_energy = rated_power_kw * annual_hours / efficiency
        annual_energy_cost = annual_energy * self.electricity_cost
        annual_maintenance = annual_hours * self.maintenance_cost_per_hour

        total_operating_cost = (annual_energy_cost + annual_maintenance) * lifetime_years

        # Levelized cost
        total_cost = capital_cost + total_operating_cost
        total_energy = rated_power_kw * annual_hours * lifetime_years
        lcoe = total_cost / total_energy if total_energy > 0 else 0

        return {
            'capital_cost': capital_cost,
            'annual_operating_cost': annual_energy_cost + annual_maintenance,
            'total_lifecycle_cost': total_cost,
            'lcoe': lcoe,
            'payback_years': capital_cost / (annual_energy_cost * 0.2) if annual_energy_cost > 0 else 999
        }


class AdvancedGUI:
    """Advanced Tkinter GUI with auto-scaling and multiple tabs"""

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Three Shunt Generators Analysis System")
        self.root.geometry("1400x900")

        # Data structures
        self.analyzer = CircuitAnalyzer()
        self.simulator = DynamicSimulator(self.analyzer)
        self.multiphysics = MultiPhysicsEngine(self.analyzer)
        self.economics = EconomicAnalyzer()

        # Simulation state
        self.is_running = False
        self.simulation_thread = None

        # Configure grid weights for auto-scaling
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create main container
        self.main_container = ttk.Frame(root)
        self.main_container.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Title
        title_frame = ttk.Frame(self.main_container)
        title_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        ttk.Label(title_frame, text="⚡ Advanced Shunt Generators Analysis System",
                 font=('Arial', 16, 'bold')).pack()
        ttk.Label(title_frame, text="Multi-Physics Simulation with Economic Analysis",
                 font=('Arial', 10)).pack()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.grid(row=1, column=0, sticky='nsew')

        # Create tabs
        self.create_main_tab()
        self.create_dynamics_tab()
        self.create_multiphysics_tab()
        self.create_economics_tab()
        self.create_advanced_control_tab()

        # Initialize with default generators
        self.initialize_default_system()

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def on_window_resize(self, event):
        """Handle window resize for auto-scaling"""
        if event.widget == self.root:
            # Update canvas sizes
            if hasattr(self, 'canvas_main'):
                self.canvas_main.get_tk_widget().configure(width=event.width*0.6, height=event.height*0.4)
            if hasattr(self, 'canvas_dynamics'):
                self.canvas_dynamics.get_tk_widget().configure(width=event.width*0.9, height=event.height*0.7)

    def create_main_tab(self):
        """Create main analysis tab"""
        main_tab = ttk.Frame(self.notebook)
        self.notebook.add(main_tab, text='📊 Circuit Analysis')

        main_tab.grid_rowconfigure(1, weight=1)
        main_tab.grid_columnconfigure(0, weight=1)
        main_tab.grid_columnconfigure(1, weight=1)

        # Left panel - Input parameters
        left_panel = ttk.LabelFrame(main_tab, text="Generator Parameters", padding=10)
        left_panel.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Generator 1
        ttk.Label(left_panel, text="Generator 1", font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=3, pady=5)
        self.create_parameter_inputs(left_panel, 'gen1', 1)

        # Generator 2
        ttk.Label(left_panel, text="Generator 2", font=('Arial', 10, 'bold')).grid(row=6, column=0, columnspan=3, pady=5)
        self.create_parameter_inputs(left_panel, 'gen2', 7)

        # Generator 3
        ttk.Label(left_panel, text="Generator 3", font=('Arial', 10, 'bold')).grid(row=12, column=0, columnspan=3, pady=5)
        self.create_parameter_inputs(left_panel, 'gen3', 13)

        # Load parameters
        ttk.Label(left_panel, text="Load Parameters", font=('Arial', 10, 'bold')).grid(row=18, column=0, columnspan=3, pady=5)
        ttk.Label(left_panel, text="Load Resistance (Ω):").grid(row=19, column=0, sticky='w')
        self.load_r = tk.DoubleVar(value=2.0)
        ttk.Scale(left_panel, from_=0.1, to=10.0, variable=self.load_r, orient='horizontal').grid(row=19, column=1)
        ttk.Label(left_panel, textvariable=self.load_r).grid(row=19, column=2)

        # Buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.grid(row=20, column=0, columnspan=3, pady=10)
        ttk.Button(button_frame, text="🔍 Analyze", command=self.analyze_circuit).pack(side='left', padx=5)
        ttk.Button(button_frame, text="🔄 Reset", command=self.reset_parameters).pack(side='left', padx=5)

        # Right panel - Results
        right_panel = ttk.Frame(main_tab)
        right_panel.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=5, pady=5)
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        # Results text
        results_frame = ttk.LabelFrame(right_panel, text="Analysis Results", padding=10)
        results_frame.grid(row=0, column=0, sticky='nsew')
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, width=60, font=('Courier', 9))
        self.results_text.grid(row=0, column=0, sticky='nsew')

        # Visualization
        viz_frame = ttk.LabelFrame(right_panel, text="Circuit Visualization", padding=10)
        viz_frame.grid(row=1, column=0, sticky='nsew', pady=(5, 0))
        viz_frame.grid_rowconfigure(0, weight=1)
        viz_frame.grid_columnconfigure(0, weight=1)

        self.fig_main = Figure(figsize=(8, 5), dpi=80)
        self.canvas_main = FigureCanvasTkAgg(self.fig_main, master=viz_frame)
        self.canvas_main.get_tk_widget().grid(row=0, column=0, sticky='nsew')

    def create_parameter_inputs(self, parent, prefix, start_row):
        """Create parameter input controls"""
        # EMF
        ttk.Label(parent, text="EMF (V):").grid(row=start_row, column=0, sticky='w')
        var = tk.DoubleVar(value=127.0 if prefix == 'gen1' else (120.0 if prefix == 'gen2' else 119.0))
        setattr(self, f'{prefix}_emf', var)
        ttk.Scale(parent, from_=100, to=150, variable=var, orient='horizontal').grid(row=start_row, column=1)
        ttk.Label(parent, textvariable=var).grid(row=start_row, column=2)

        # Ra
        ttk.Label(parent, text="Ra (Ω):").grid(row=start_row+1, column=0, sticky='w')
        var = tk.DoubleVar(value=0.1)
        setattr(self, f'{prefix}_ra', var)
        ttk.Scale(parent, from_=0.01, to=1.0, variable=var, orient='horizontal').grid(row=start_row+1, column=1)
        ttk.Label(parent, textvariable=var).grid(row=start_row+1, column=2)

        # La
        ttk.Label(parent, text="La (H):").grid(row=start_row+2, column=0, sticky='w')
        var = tk.DoubleVar(value=0.01)
        setattr(self, f'{prefix}_la', var)
        ttk.Scale(parent, from_=0.001, to=0.1, variable=var, orient='horizontal').grid(row=start_row+2, column=1)
        ttk.Label(parent, textvariable=var).grid(row=start_row+2, column=2)

        # Rf
        ttk.Label(parent, text="Rf (Ω):").grid(row=start_row+3, column=0, sticky='w')
        var = tk.DoubleVar(value=100.0)
        setattr(self, f'{prefix}_rf', var)
        ttk.Scale(parent, from_=10, to=500, variable=var, orient='horizontal').grid(row=start_row+3, column=1)
        ttk.Label(parent, textvariable=var).grid(row=start_row+3, column=2)

    def create_dynamics_tab(self):
        """Create dynamic simulation tab"""
        dyn_tab = ttk.Frame(self.notebook)
        self.notebook.add(dyn_tab, text='🔄 Dynamic Simulation')

        dyn_tab.grid_rowconfigure(1, weight=1)
        dyn_tab.grid_columnconfigure(0, weight=1)

        # Control panel
        control_frame = ttk.LabelFrame(dyn_tab, text="Simulation Controls", padding=10)
        control_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        ttk.Label(control_frame, text="Solver Method:").grid(row=0, column=0, padx=5)
        self.solver_var = tk.StringVar(value='RK45')
        ttk.Combobox(control_frame, textvariable=self.solver_var,
                    values=['RK45', 'Euler'], width=10).grid(row=0, column=1, padx=5)

        ttk.Label(control_frame, text="Simulation Time (s):").grid(row=0, column=2, padx=5)
        self.sim_time = tk.DoubleVar(value=1.0)
        ttk.Entry(control_frame, textvariable=self.sim_time, width=10).grid(row=0, column=3, padx=5)

        ttk.Button(control_frame, text="▶ Start", command=self.start_simulation).grid(row=0, column=4, padx=5)
        ttk.Button(control_frame, text="⏸ Stop", command=self.stop_simulation).grid(row=0, column=5, padx=5)
        ttk.Button(control_frame, text="🔄 Reset", command=self.reset_simulation).grid(row=0, column=6, padx=5)

        # Progress bar
        self.progress = ttk.Progressbar(control_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, columnspan=7, sticky='ew', pady=5)

        # Plots
        plot_frame = ttk.Frame(dyn_tab)
        plot_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        plot_frame.grid_rowconfigure(0, weight=1)
        plot_frame.grid_columnconfigure(0, weight=1)

        self.fig_dynamics = Figure(figsize=(12, 8), dpi=80)
        self.canvas_dynamics = FigureCanvasTkAgg(self.fig_dynamics, master=plot_frame)
        self.canvas_dynamics.get_tk_widget().grid(row=0, column=0, sticky='nsew')

    def create_multiphysics_tab(self):
        """Create multi-physics analysis tab"""
        mp_tab = ttk.Frame(self.notebook)
        self.notebook.add(mp_tab, text='🔬 Multi-Physics')

        mp_tab.grid_rowconfigure(0, weight=1)
        mp_tab.grid_columnconfigure(0, weight=1)
        mp_tab.grid_columnconfigure(1, weight=1)

        # Left - Thermal analysis
        thermal_frame = ttk.LabelFrame(mp_tab, text="Thermal Analysis", padding=10)
        thermal_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        thermal_frame.grid_rowconfigure(1, weight=1)
        thermal_frame.grid_columnconfigure(0, weight=1)

        ttk.Button(thermal_frame, text="Calculate Thermal Distribution",
                  command=self.analyze_thermal).pack(pady=5)

        self.thermal_text = scrolledtext.ScrolledText(thermal_frame, height=20, width=50, font=('Courier', 9))
        self.thermal_text.pack(fill='both', expand=True)

        # Right - Mechanical analysis
        mech_frame = ttk.LabelFrame(mp_tab, text="Mechanical Stress Analysis", padding=10)
        mech_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        mech_frame.grid_rowconfigure(1, weight=1)
        mech_frame.grid_columnconfigure(0, weight=1)

        ttk.Button(mech_frame, text="Calculate Mechanical Stress",
                  command=self.analyze_mechanical).pack(pady=5)

        self.mechanical_text = scrolledtext.ScrolledText(mech_frame, height=20, width=50, font=('Courier', 9))
        self.mechanical_text.pack(fill='both', expand=True)

        # Bottom - Loss breakdown
        loss_frame = ttk.LabelFrame(mp_tab, text="Detailed Loss Breakdown", padding=10)
        loss_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        self.loss_text = scrolledtext.ScrolledText(loss_frame, height=10, width=100, font=('Courier', 9))
        self.loss_text.pack(fill='both', expand=True)

    def create_economics_tab(self):
        """Create economic analysis tab"""
        econ_tab = ttk.Frame(self.notebook)
        self.notebook.add(econ_tab, text='💰 Economic Analysis')

        econ_tab.grid_rowconfigure(1, weight=1)
        econ_tab.grid_columnconfigure(0, weight=1)

        # Input parameters
        input_frame = ttk.LabelFrame(econ_tab, text="Economic Parameters", padding=10)
        input_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        ttk.Label(input_frame, text="Electricity Cost ($/kWh):").grid(row=0, column=0, sticky='w', padx=5)
        self.elec_cost = tk.DoubleVar(value=0.12)
        ttk.Entry(input_frame, textvariable=self.elec_cost, width=15).grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Maintenance Cost ($/hr):").grid(row=0, column=2, sticky='w', padx=5)
        self.maint_cost = tk.DoubleVar(value=5.0)
        ttk.Entry(input_frame, textvariable=self.maint_cost, width=15).grid(row=0, column=3, padx=5)

        ttk.Label(input_frame, text="Operating Hours:").grid(row=1, column=0, sticky='w', padx=5)
        self.op_hours = tk.DoubleVar(value=8760)
        ttk.Entry(input_frame, textvariable=self.op_hours, width=15).grid(row=1, column=1, padx=5)

        ttk.Label(input_frame, text="Lifetime (years):").grid(row=1, column=2, sticky='w', padx=5)
        self.lifetime = tk.DoubleVar(value=20)
        ttk.Entry(input_frame, textvariable=self.lifetime, width=15).grid(row=1, column=3, padx=5)

        ttk.Button(input_frame, text="Calculate Economics",
                  command=self.analyze_economics).grid(row=2, column=0, columnspan=4, pady=10)

        # Results
        results_frame = ttk.LabelFrame(econ_tab, text="Economic Analysis Results", padding=10)
        results_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        self.econ_text = scrolledtext.ScrolledText(results_frame, height=25, width=100, font=('Courier', 10))
        self.econ_text.grid(row=0, column=0, sticky='nsew')

    def create_advanced_control_tab(self):
        """Create advanced control systems tab"""
        ctrl_tab = ttk.Frame(self.notebook)
        self.notebook.add(ctrl_tab, text='⚙️ Advanced Control')

        ctrl_tab.grid_rowconfigure(1, weight=1)
        ctrl_tab.grid_columnconfigure(0, weight=1)
        ctrl_tab.grid_columnconfigure(1, weight=1)

        # Voltage control
        voltage_frame = ttk.LabelFrame(ctrl_tab, text="Voltage Control", padding=10)
        voltage_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        ttk.Label(voltage_frame, text="Target Voltage (V):").grid(row=0, column=0, sticky='w')
        self.target_voltage = tk.DoubleVar(value=120.0)
        ttk.Scale(voltage_frame, from_=100, to=150, variable=self.target_voltage,
                 orient='horizontal').grid(row=0, column=1, sticky='ew')
        ttk.Label(voltage_frame, textvariable=self.target_voltage).grid(row=0, column=2)

        ttk.Label(voltage_frame, text="Control Mode:").grid(row=1, column=0, sticky='w')
        self.control_mode = tk.StringVar(value='Automatic')
        ttk.Combobox(voltage_frame, textvariable=self.control_mode,
                    values=['Manual', 'Automatic', 'PID', 'Fuzzy Logic']).grid(row=1, column=1, sticky='ew')

        # Load sharing control
        sharing_frame = ttk.LabelFrame(ctrl_tab, text="Load Sharing Control", padding=10)
        sharing_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        ttk.Label(sharing_frame, text="Sharing Strategy:").grid(row=0, column=0, sticky='w')
        self.sharing_strategy = tk.StringVar(value='Equal')
        ttk.Combobox(sharing_frame, textvariable=self.sharing_strategy,
                    values=['Equal', 'Proportional', 'Priority-based']).grid(row=0, column=1, sticky='ew')

        # Thermal derating
        derating_frame = ttk.LabelFrame(ctrl_tab, text="Thermal Derating", padding=10)
        derating_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
        derating_frame.grid_rowconfigure(1, weight=1)
        derating_frame.grid_columnconfigure(0, weight=1)

        ttk.Checkbutton(derating_frame, text="Enable Automatic Derating",
                       variable=tk.BooleanVar(value=True)).pack(anchor='w')

        self.derating_text = scrolledtext.ScrolledText(derating_frame, height=15, width=100, font=('Courier', 9))
        self.derating_text.pack(fill='both', expand=True, pady=5)

        # Power consumption monitoring
        power_frame = ttk.LabelFrame(ctrl_tab, text="Power Consumption Monitoring", padding=10)
        power_frame.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        self.power_label = ttk.Label(power_frame, text="Total Power: 0.0 kW | Efficiency: 0.0%",
                                     font=('Arial', 12, 'bold'))
        self.power_label.pack()

    def initialize_default_system(self):
        """Initialize with default three-generator system"""
        self.analyzer.generators = []

        gen1 = GeneratorParameters(emf=127.0, ra=0.1)
        gen2 = GeneratorParameters(emf=120.0, ra=0.1)
        gen3 = GeneratorParameters(emf=119.0, ra=0.1)

        self.analyzer.add_generator(gen1)
        self.analyzer.add_generator(gen2)
        self.analyzer.add_generator(gen3)

        self.analyzer.load.resistance = 2.0

    def update_generators_from_gui(self):
        """Update generator parameters from GUI inputs"""
        self.analyzer.generators = []

        for prefix in ['gen1', 'gen2', 'gen3']:
            gen = GeneratorParameters(
                emf=getattr(self, f'{prefix}_emf').get(),
                ra=getattr(self, f'{prefix}_ra').get(),
                la=getattr(self, f'{prefix}_la').get(),
                rf=getattr(self, f'{prefix}_rf').get()
            )
            self.analyzer.add_generator(gen)

        self.analyzer.load.resistance = self.load_r.get()

    def analyze_circuit(self):
        """Perform steady-state circuit analysis"""
        self.update_generators_from_gui()
        results = self.analyzer.solve_steady_state()

        # Display results
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "="*70 + "\n")
        self.results_text.insert(tk.END, "     THREE SHUNT GENERATORS CIRCUIT ANALYSIS RESULTS\n")
        self.results_text.insert(tk.END, "="*70 + "\n\n")

        self.results_text.insert(tk.END, f"Bus Voltage: {results['bus_voltage']:.2f} V\n\n")

        for i, (gen, current, mode) in enumerate(zip(self.analyzer.generators,
                                                     results['currents'],
                                                     results['modes']), 1):
            self.results_text.insert(tk.END, f"Generator {i}:\n")
            self.results_text.insert(tk.END, f"  EMF:         {gen.emf:.2f} V\n")
            self.results_text.insert(tk.END, f"  Current:     {current:.2f} A\n")
            self.results_text.insert(tk.END, f"  Mode:        {mode}\n")
            self.results_text.insert(tk.END, f"  Power:       {results['powers'][i-1]:.2f} W\n")
            self.results_text.insert(tk.END, f"  Cu Loss:     {results['copper_losses'][i-1]:.2f} W\n")
            self.results_text.insert(tk.END, "\n")

        self.results_text.insert(tk.END, f"Load:\n")
        self.results_text.insert(tk.END, f"  Current:     {results['load_current']:.2f} A\n")
        self.results_text.insert(tk.END, f"  Power:       {results['load_power']:.2f} W\n\n")

        self.results_text.insert(tk.END, f"System Efficiency: {results['efficiency']:.2f}%\n")
        self.results_text.insert(tk.END, f"Total Copper Loss: {results['total_copper_loss']:.2f} W\n")

        # Visualize
        self.visualize_circuit(results)

    def visualize_circuit(self, results):
        """Create circuit visualization"""
        self.fig_main.clear()

        # Create subplots
        gs = self.fig_main.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        ax1 = self.fig_main.add_subplot(gs[0, 0])
        ax2 = self.fig_main.add_subplot(gs[0, 1])
        ax3 = self.fig_main.add_subplot(gs[1, :])

        # Current distribution
        generators = [f"Gen{i+1}\n{self.analyzer.generators[i].emf:.0f}V"
                     for i in range(len(results['currents']))]
        currents = results['currents']
        colors = ['green' if c > 0 else ('red' if c < 0 else 'gray') for c in currents]

        ax1.bar(generators, currents, color=colors, alpha=0.7, edgecolor='black')
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax1.set_ylabel('Current (A)', fontsize=10, fontweight='bold')
        ax1.set_title('Current Distribution', fontsize=11, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # Power distribution
        powers = results['powers']
        ax2.bar(generators, powers, color=colors, alpha=0.7, edgecolor='black')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.set_ylabel('Power (W)', fontsize=10, fontweight='bold')
        ax2.set_title('Power Distribution', fontsize=11, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        # Operating modes pie chart
        mode_counts = {'Generating': 0, 'Motoring': 0, 'Floating': 0}
        for mode in results['modes']:
            mode_counts[mode] += 1

        active_modes = {k: v for k, v in mode_counts.items() if v > 0}
        colors_pie = {'Generating': 'lightgreen', 'Motoring': 'lightcoral', 'Floating': 'lightgray'}
        pie_colors = [colors_pie[mode] for mode in active_modes.keys()]

        wedges, texts, autotexts = ax3.pie(active_modes.values(), labels=active_modes.keys(),
                                           autopct='%1.0f%%', colors=pie_colors, startangle=90)
        ax3.set_title('Operating Modes Distribution', fontsize=11, fontweight='bold')

        for text in texts:
            text.set_fontsize(10)
            text.set_fontweight('bold')
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)

        self.canvas_main.draw()

    def start_simulation(self):
        """Start dynamic simulation"""
        if self.is_running:
            messagebox.showwarning("Warning", "Simulation already running!")
            return

        self.is_running = True
        self.progress.start()

        # Run simulation in separate thread
        self.simulation_thread = threading.Thread(target=self.run_dynamic_simulation)
        self.simulation_thread.start()

    def run_dynamic_simulation(self):
        """Execute dynamic simulation"""
        try:
            self.update_generators_from_gui()

            # Initial conditions
            n = len(self.analyzer.generators)
            y0 = np.zeros(4*n + 1)

            # Initial currents (from steady-state)
            results = self.analyzer.solve_steady_state()
            y0[0:n] = results['currents']

            # Initial field currents
            y0[n:2*n] = [self.analyzer.bus_voltage / gen.rf for gen in self.analyzer.generators]

            # Initial load current
            y0[2*n] = results['load_current']

            # Initial angular velocities (assume rated speed)
            y0[2*n+1:3*n+1] = [157.0] * n  # 1500 RPM ≈ 157 rad/s

            # Initial temperatures
            y0[3*n+1:4*n+1] = [25.0] * n  # Ambient

            # Simulate
            t_span = (0, self.sim_time.get())
            sol = self.simulator.simulate(t_span, y0, method=self.solver_var.get())

            # Plot results
            self.root.after(0, self.plot_dynamic_results, sol)

        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"Simulation failed: {str(e)}")
        finally:
            self.is_running = False
            self.root.after(0, self.progress.stop)

    def plot_dynamic_results(self, sol):
        """Plot dynamic simulation results"""
        self.fig_dynamics.clear()

        n = len(self.analyzer.generators)
        t = sol.t

        # Create subplots
        ax1 = self.fig_dynamics.add_subplot(3, 2, 1)
        ax2 = self.fig_dynamics.add_subplot(3, 2, 2)
        ax3 = self.fig_dynamics.add_subplot(3, 2, 3)
        ax4 = self.fig_dynamics.add_subplot(3, 2, 4)
        ax5 = self.fig_dynamics.add_subplot(3, 2, 5)
        ax6 = self.fig_dynamics.add_subplot(3, 2, 6)

        # Armature currents
        for i in range(n):
            ax1.plot(t, sol.y[i, :], label=f'Gen {i+1}', linewidth=2)
        ax1.set_ylabel('Armature Current (A)', fontweight='bold')
        ax1.set_title('Armature Currents vs Time', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Field currents
        for i in range(n):
            ax2.plot(t, sol.y[n+i, :], label=f'Gen {i+1}', linewidth=2)
        ax2.set_ylabel('Field Current (A)', fontweight='bold')
        ax2.set_title('Field Currents vs Time', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Load current
        ax3.plot(t, sol.y[2*n, :], 'r-', linewidth=2, label='Load')
        ax3.set_ylabel('Load Current (A)', fontweight='bold')
        ax3.set_title('Load Current vs Time', fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Angular velocities
        for i in range(n):
            ax4.plot(t, sol.y[2*n+1+i, :] * 60 / (2*np.pi), label=f'Gen {i+1}', linewidth=2)
        ax4.set_ylabel('Speed (RPM)', fontweight='bold')
        ax4.set_title('Rotor Speeds vs Time', fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        # Temperatures
        for i in range(n):
            ax5.plot(t, sol.y[3*n+1+i, :], label=f'Gen {i+1}', linewidth=2)
        ax5.axhline(y=155, color='r', linestyle='--', label='Max Temp', linewidth=1.5)
        ax5.set_xlabel('Time (s)', fontweight='bold')
        ax5.set_ylabel('Temperature (°C)', fontweight='bold')
        ax5.set_title('Winding Temperatures vs Time', fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)

        # Power
        for i in range(n):
            power = self.analyzer.bus_voltage * sol.y[i, :]
            ax6.plot(t, power / 1000, label=f'Gen {i+1}', linewidth=2)
        ax6.set_xlabel('Time (s)', fontweight='bold')
        ax6.set_ylabel('Power (kW)', fontweight='bold')
        ax6.set_title('Generator Powers vs Time', fontweight='bold')
        ax6.legend()
        ax6.grid(True, alpha=0.3)

        self.fig_dynamics.tight_layout()
        self.canvas_dynamics.draw()

    def stop_simulation(self):
        """Stop running simulation"""
        self.is_running = False
        self.simulator.running = False
        self.progress.stop()

    def reset_simulation(self):
        """Reset simulation"""
        self.stop_simulation()
        self.fig_dynamics.clear()
        self.canvas_dynamics.draw()

    def analyze_thermal(self):
        """Perform thermal analysis"""
        self.update_generators_from_gui()
        results = self.analyzer.solve_steady_state()

        self.thermal_text.delete(1.0, tk.END)
        self.thermal_text.insert(tk.END, "="*60 + "\n")
        self.thermal_text.insert(tk.END, "        THERMAL ANALYSIS RESULTS\n")
        self.thermal_text.insert(tk.END, "="*60 + "\n\n")

        for i, (gen, current) in enumerate(zip(self.analyzer.generators, results['currents']), 1):
            # Calculate losses
            omega = 157.0  # rad/s (assume rated speed)
            temp = 75.0    # Assume 75°C operating temperature

            losses = self.multiphysics.calculate_detailed_losses(current, omega, temp, gen)
            thermal = self.multiphysics.calculate_thermal_distribution(losses['total'], gen)
            derating = self.multiphysics.calculate_efficiency_derating(thermal['hotspot'], gen)

            self.thermal_text.insert(tk.END, f"Generator {i}:\n")
            self.thermal_text.insert(tk.END, f"-" * 60 + "\n")
            self.thermal_text.insert(tk.END, f"  Winding Temperature:    {thermal['winding']:.2f} °C\n")
            self.thermal_text.insert(tk.END, f"  Core Temperature:       {thermal['core']:.2f} °C\n")
            self.thermal_text.insert(tk.END, f"  Frame Temperature:      {thermal['frame']:.2f} °C\n")
            self.thermal_text.insert(tk.END, f"  Hotspot Temperature:    {thermal['hotspot']:.2f} °C\n")
            self.thermal_text.insert(tk.END, f"  Max Allowable Temp:     {gen.max_temp:.2f} °C\n")
            self.thermal_text.insert(tk.END, f"  Temperature Margin:     {gen.max_temp - thermal['hotspot']:.2f} °C\n")
            self.thermal_text.insert(tk.END, f"  Derating Factor:        {derating:.3f}\n")

            status = "SAFE" if thermal['hotspot'] < gen.max_temp else "OVERHEATING!"
            self.thermal_text.insert(tk.END, f"  Status:                 {status}\n\n")

    def analyze_mechanical(self):
        """Perform mechanical stress analysis"""
        self.update_generators_from_gui()
        results = self.analyzer.solve_steady_state()

        self.mechanical_text.delete(1.0, tk.END)
        self.mechanical_text.insert(tk.END, "="*60 + "\n")
        self.mechanical_text.insert(tk.END, "    MECHANICAL STRESS ANALYSIS RESULTS\n")
        self.mechanical_text.insert(tk.END, "="*60 + "\n\n")

        for i, (gen, current, power) in enumerate(zip(self.analyzer.generators,
                                                      results['currents'],
                                                      results['powers']), 1):
            omega = 157.0  # rad/s
            torque = power / (omega + 1e-6)

            stress = self.multiphysics.calculate_mechanical_stress(torque, omega, gen)

            self.mechanical_text.insert(tk.END, f"Generator {i}:\n")
            self.mechanical_text.insert(tk.END, f"-" * 60 + "\n")
            self.mechanical_text.insert(tk.END, f"  Torque:                 {torque:.2f} N⋅m\n")
            self.mechanical_text.insert(tk.END, f"  Speed:                  {omega*60/(2*np.pi):.0f} RPM\n")
            self.mechanical_text.insert(tk.END, f"  Shaft Shear Stress:     {stress['shear_stress']/1e6:.2f} MPa\n")
            self.mechanical_text.insert(tk.END, f"  Radial Bearing Load:    {stress['radial_load']:.2f} N\n")
            self.mechanical_text.insert(tk.END, f"  Centrifugal Force:      {stress['centrifugal_force']:.2f} N\n")
            self.mechanical_text.insert(tk.END, f"  Safety Factor:          {stress['safety_factor']:.2f}\n")

            status = "SAFE" if stress['safety_factor'] > 2.0 else "CHECK DESIGN"
            self.mechanical_text.insert(tk.END, f"  Status:                 {status}\n\n")

        # Also show detailed losses
        self.loss_text.delete(1.0, tk.END)
        self.loss_text.insert(tk.END, "="*100 + "\n")
        self.loss_text.insert(tk.END, "                              DETAILED LOSS BREAKDOWN\n")
        self.loss_text.insert(tk.END, "="*100 + "\n\n")

        header = f"{'Generator':<12} {'Cu-Arm':<10} {'Cu-Field':<10} {'Hysteresis':<12} {'Eddy':<10} {'Friction':<10} {'Windage':<10} {'Stray':<10} {'Total':<10}\n"
        self.loss_text.insert(tk.END, header)
        self.loss_text.insert(tk.END, "-" * 100 + "\n")

        total_system_loss = 0
        for i, (gen, current) in enumerate(zip(self.analyzer.generators, results['currents']), 1):
            omega = 157.0
            temp = 75.0
            losses = self.multiphysics.calculate_detailed_losses(current, omega, temp, gen)

            row = f"Gen {i:<8} {losses['copper_armature']:<10.2f} {losses['copper_field']:<10.2f} "
            row += f"{losses['hysteresis']:<12.2f} {losses['eddy_current']:<10.2f} "
            row += f"{losses['friction']:<10.2f} {losses['windage']:<10.2f} "
            row += f"{losses['stray']:<10.2f} {losses['total']:<10.2f}\n"
            self.loss_text.insert(tk.END, row)
            total_system_loss += losses['total']

        self.loss_text.insert(tk.END, "-" * 100 + "\n")
        self.loss_text.insert(tk.END, f"{'TOTAL SYSTEM LOSS:':<92} {total_system_loss:.2f} W\n")

    def analyze_economics(self):
        """Perform economic analysis"""
        self.update_generators_from_gui()
        results = self.analyzer.solve_steady_state()

        # Update economic parameters
        self.economics.electricity_cost = self.elec_cost.get()
        self.economics.maintenance_cost_per_hour = self.maint_cost.get()

        # Calculate operating costs
        total_power_kw = sum(p for p in results['powers'] if p > 0) / 1000
        total_loss_kw = results['total_copper_loss'] / 1000
        hours = self.op_hours.get()

        operating = self.economics.calculate_operating_cost(total_power_kw, hours, total_loss_kw)

        # Calculate lifecycle costs
        lifecycle = self.economics.calculate_lifecycle_cost(
            total_power_kw,
            self.lifetime.get(),
            0.85,  # Capacity factor
            results['efficiency'] / 100
        )

        # Display results
        self.econ_text.delete(1.0, tk.END)
        self.econ_text.insert(tk.END, "="*90 + "\n")
        self.econ_text.insert(tk.END, "                        ECONOMIC ANALYSIS RESULTS\n")
        self.econ_text.insert(tk.END, "="*90 + "\n\n")

        self.econ_text.insert(tk.END, "OPERATING COST ANALYSIS:\n")
        self.econ_text.insert(tk.END, "-" * 90 + "\n")
        self.econ_text.insert(tk.END, f"  Operating Hours:                  {hours:.0f} hrs\n")
        self.econ_text.insert(tk.END, f"  Electricity Cost Rate:            ${self.economics.electricity_cost:.3f}/kWh\n")
        self.econ_text.insert(tk.END, f"  Maintenance Cost Rate:            ${self.economics.maintenance_cost_per_hour:.2f}/hr\n\n")

        self.econ_text.insert(tk.END, f"  Total Output Power:               {total_power_kw:.2f} kW\n")
        self.econ_text.insert(tk.END, f"  Total Losses:                     {total_loss_kw:.2f} kW\n")
        self.econ_text.insert(tk.END, f"  System Efficiency:                {results['efficiency']:.2f}%\n\n")

        self.econ_text.insert(tk.END, f"  Energy Cost:                      ${operating['energy_cost']:,.2f}\n")
        self.econ_text.insert(tk.END, f"  Maintenance Cost:                 ${operating['maintenance_cost']:,.2f}\n")
        self.econ_text.insert(tk.END, f"  Total Operating Cost:             ${operating['total_operating_cost']:,.2f}\n")
        self.econ_text.insert(tk.END, f"  Cost per kWh Generated:           ${operating['cost_per_kwh']:.4f}/kWh\n\n")

        self.econ_text.insert(tk.END, "\nLIFECYCLE COST ANALYSIS:\n")
        self.econ_text.insert(tk.END, "-" * 90 + "\n")
        self.econ_text.insert(tk.END, f"  Project Lifetime:                 {self.lifetime.get():.0f} years\n")
        self.econ_text.insert(tk.END, f"  Capacity Factor:                  85%\n\n")

        self.econ_text.insert(tk.END, f"  Capital Cost:                     ${lifecycle['capital_cost']:,.2f}\n")
        self.econ_text.insert(tk.END, f"  Annual Operating Cost:            ${lifecycle['annual_operating_cost']:,.2f}/year\n")
        self.econ_text.insert(tk.END, f"  Total Lifecycle Cost:             ${lifecycle['total_lifecycle_cost']:,.2f}\n")
        self.econ_text.insert(tk.END, f"  Levelized Cost of Energy (LCOE):  ${lifecycle['lcoe']:.4f}/kWh\n")
        self.econ_text.insert(tk.END, f"  Payback Period:                   {lifecycle['payback_years']:.1f} years\n\n")

        # Cost breakdown per generator
        self.econ_text.insert(tk.END, "\nCOST BREAKDOWN BY GENERATOR:\n")
        self.econ_text.insert(tk.END, "-" * 90 + "\n")

        for i, (gen, power) in enumerate(zip(self.analyzer.generators, results['powers']), 1):
            if power > 0:
                gen_power_kw = power / 1000
                gen_loss_kw = results['copper_losses'][i-1] / 1000
                gen_operating = self.economics.calculate_operating_cost(gen_power_kw, hours, gen_loss_kw)

                self.econ_text.insert(tk.END, f"\n  Generator {i}:\n")
                self.econ_text.insert(tk.END, f"    Output Power:                   {gen_power_kw:.2f} kW\n")
                self.econ_text.insert(tk.END, f"    Operating Cost:                 ${gen_operating['total_operating_cost']:,.2f}\n")
                self.econ_text.insert(tk.END, f"    Cost per kWh:                   ${gen_operating['cost_per_kwh']:.4f}/kWh\n")

        # ROI Analysis
        self.econ_text.insert(tk.END, "\n\nRETURN ON INVESTMENT (ROI) ANALYSIS:\n")
        self.econ_text.insert(tk.END, "-" * 90 + "\n")

        annual_revenue = total_power_kw * hours * 0.15  # Assume $0.15/kWh selling price
        annual_profit = annual_revenue - lifecycle['annual_operating_cost']
        roi = (annual_profit * self.lifetime.get()) / lifecycle['capital_cost'] * 100

        self.econ_text.insert(tk.END, f"  Annual Revenue (@ $0.15/kWh):     ${annual_revenue:,.2f}\n")
        self.econ_text.insert(tk.END, f"  Annual Profit:                    ${annual_profit:,.2f}\n")
        self.econ_text.insert(tk.END, f"  ROI over {self.lifetime.get():.0f} years:              {roi:.1f}%\n")

    def reset_parameters(self):
        """Reset all parameters to default"""
        self.gen1_emf.set(127.0)
        self.gen2_emf.set(120.0)
        self.gen3_emf.set(119.0)

        for prefix in ['gen1', 'gen2', 'gen3']:
            getattr(self, f'{prefix}_ra').set(0.1)
            getattr(self, f'{prefix}_la').set(0.01)
            getattr(self, f'{prefix}_rf').set(100.0)

        self.load_r.set(2.0)
        self.results_text.delete(1.0, tk.END)
        self.fig_main.clear()
        self.canvas_main.draw()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = AdvancedGUI(root)

    # Display welcome message
    welcome = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║  ADVANCED THREE SHUNT GENERATORS ANALYSIS SYSTEM                 ║
    ║                                                                  ║
    ║  Features:                                                       ║
    ║  • Steady-state circuit analysis                                ║
    ║  • Dynamic ODE simulation (RK45, Euler)                         ║
    ║  • Multi-physics modeling (EM, Thermal, Mechanical)             ║
    ║  • Detailed loss breakdown                                      ║
    ║  • Economic analysis with lifecycle costs                       ║
    ║  • Advanced control systems                                     ║
    ║  • Real-time visualization                                      ║
    ║  • Auto-scaling responsive GUI                                  ║
    ║                                                                  ║
    ║  Default Problem:                                               ║
    ║  Three generators (127V, 120V, 119V) with Ra = 0.1Ω            ║
    ║  Connected to a 2Ω load                                         ║
    ╚══════════════════════════════════════════════════════════════════╝
    """

    print(welcome)
    print("\n🚀 Starting GUI application...\n")

    root.mainloop()


if __name__ == "__main__":
    main()
