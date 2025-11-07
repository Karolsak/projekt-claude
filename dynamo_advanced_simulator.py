"""
Advanced Dynamo Simulation and Analysis System
A comprehensive electrical engineering tool for dynamo analysis with multi-physics simulation
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from scipy.integrate import solve_ivp, odeint
from scipy.interpolate import interp1d
import math
from datetime import datetime
import json

# ============================================================================
# PART 1: MATHEMATICAL SOLUTION FOR THE GIVEN PROBLEM
# ============================================================================

class DynamoProblemSolver:
    """Solves the specific dynamo problem given in the requirements"""

    def __init__(self, speed_rpm=1000, power_output_kw=20, terminal_voltage=220,
                 ra=0.04, rsh=110, rse=0.05, efficiency=0.85):
        self.speed_rpm = speed_rpm
        self.power_output_w = power_output_kw * 1000
        self.V_t = terminal_voltage
        self.Ra = ra
        self.Rsh = rsh
        self.Rse = rse
        self.efficiency = efficiency
        self.results = {}

    def solve(self):
        """Solve the complete dynamo problem"""
        # Load current
        I_L = self.power_output_w / self.V_t

        # Shunt field current
        I_sh = self.V_t / self.Rsh

        # For long shunt: Series field carries armature current
        I_a = I_L + I_sh

        # Series field current
        I_se = I_a

        # Voltage drop across series field
        V_se = I_se * self.Rse

        # Voltage across armature
        V_a = self.V_t + V_se

        # Back EMF
        E_b = V_a + I_a * self.Ra

        # Copper losses
        copper_loss_armature = I_a**2 * self.Ra
        copper_loss_shunt = I_sh**2 * self.Rsh
        copper_loss_series = I_se**2 * self.Rse
        total_copper_loss = copper_loss_armature + copper_loss_shunt + copper_loss_series

        # Input power
        P_input = self.power_output_w / self.efficiency

        # Total losses
        total_losses = P_input - self.power_output_w

        # Iron and friction losses
        iron_friction_loss = total_losses - total_copper_loss

        # Torque developed by prime mover
        omega = (2 * math.pi * self.speed_rpm) / 60  # rad/s
        torque_prime_mover = P_input / omega

        # Electromagnetic torque
        torque_electromagnetic = E_b * I_a / omega

        self.results = {
            'load_current': I_L,
            'shunt_field_current': I_sh,
            'armature_current': I_a,
            'series_field_current': I_se,
            'back_emf': E_b,
            'copper_loss_total': total_copper_loss,
            'copper_loss_armature': copper_loss_armature,
            'copper_loss_shunt': copper_loss_shunt,
            'copper_loss_series': copper_loss_series,
            'iron_friction_loss': iron_friction_loss,
            'total_losses': total_losses,
            'input_power': P_input,
            'torque_prime_mover': torque_prime_mover,
            'torque_electromagnetic': torque_electromagnetic,
            'speed_rad_s': omega
        }

        return self.results

    def get_formatted_results(self):
        """Get formatted string of results"""
        if not self.results:
            self.solve()

        output = "="*60 + "\n"
        output += "DYNAMO PROBLEM SOLUTION\n"
        output += "="*60 + "\n\n"
        output += f"Given Parameters:\n"
        output += f"  Speed: {self.speed_rpm} RPM\n"
        output += f"  Power Output: {self.power_output_w/1000:.2f} kW\n"
        output += f"  Terminal Voltage: {self.V_t} V\n"
        output += f"  Ra = {self.Ra} Ω, Rsh = {self.Rsh} Ω, Rse = {self.Rse} Ω\n"
        output += f"  Efficiency: {self.efficiency*100}%\n\n"

        output += f"Calculated Values:\n"
        output += f"  Load Current (IL): {self.results['load_current']:.3f} A\n"
        output += f"  Shunt Field Current (Ish): {self.results['shunt_field_current']:.3f} A\n"
        output += f"  Armature Current (Ia): {self.results['armature_current']:.3f} A\n"
        output += f"  Back EMF (Eb): {self.results['back_emf']:.3f} V\n\n"

        output += "="*60 + "\n"
        output += "ANSWERS:\n"
        output += "="*60 + "\n\n"

        output += f"(i) COPPER LOSSES:\n"
        output += f"    Armature Copper Loss: {self.results['copper_loss_armature']:.3f} W\n"
        output += f"    Shunt Field Copper Loss: {self.results['copper_loss_shunt']:.3f} W\n"
        output += f"    Series Field Copper Loss: {self.results['copper_loss_series']:.3f} W\n"
        output += f"    TOTAL COPPER LOSS: {self.results['copper_loss_total']:.3f} W ({self.results['copper_loss_total']/1000:.3f} kW)\n\n"

        output += f"(ii) IRON AND FRICTION LOSS: {self.results['iron_friction_loss']:.3f} W ({self.results['iron_friction_loss']/1000:.3f} kW)\n\n"

        output += f"(iii) TORQUE DEVELOPED BY PRIME MOVER: {self.results['torque_prime_mover']:.3f} N·m\n\n"

        output += f"Additional Information:\n"
        output += f"  Input Power: {self.results['input_power']/1000:.3f} kW\n"
        output += f"  Total Losses: {self.results['total_losses']/1000:.3f} kW\n"
        output += f"  Electromagnetic Torque: {self.results['torque_electromagnetic']:.3f} N·m\n"
        output += f"  Angular Speed: {self.results['speed_rad_s']:.3f} rad/s\n"

        return output


# ============================================================================
# PART 2: ADVANCED CIRCUIT MODEL WITH DIFFERENTIAL EQUATIONS
# ============================================================================

class DynamoCircuitModel:
    """Advanced circuit model with differential equations for dynamic simulation"""

    def __init__(self, Ra=0.04, La=0.01, Rsh=110, Lsh=5.0, Rse=0.05, Lse=0.005,
                 J=0.5, B=0.01, Kt=1.2, Ke=1.2):
        """
        Initialize circuit parameters
        Ra, Rsh, Rse: Resistances (Ω)
        La, Lsh, Lse: Inductances (H)
        J: Moment of inertia (kg·m²)
        B: Damping coefficient (N·m·s)
        Kt: Torque constant (N·m/A)
        Ke: Back EMF constant (V·s/rad)
        """
        self.Ra = Ra
        self.La = La
        self.Rsh = Rsh
        self.Lsh = Lsh
        self.Rse = Rse
        self.Lse = Lse
        self.J = J
        self.B = B
        self.Kt = Kt
        self.Ke = Ke

        # Thermal parameters
        self.thermal_resistance_armature = 2.0  # K/W
        self.thermal_capacitance_armature = 500  # J/K
        self.thermal_resistance_field = 3.0  # K/W
        self.thermal_capacitance_field = 800  # J/K
        self.ambient_temperature = 25.0  # °C

    def differential_equations(self, t, y, V_applied, T_load):
        """
        Differential equations for the dynamo system
        State vector y = [Ia, Ish, omega, theta, T_armature, T_field]
        Ia: Armature current
        Ish: Shunt field current
        omega: Angular velocity (rad/s)
        theta: Angular position (rad)
        T_armature: Armature temperature (°C)
        T_field: Field temperature (°C)
        """
        Ia, Ish, omega, theta, T_armature, T_field = y

        # Back EMF (proportional to speed and field flux)
        Eb = self.Ke * omega * Ish

        # Armature circuit: V_applied = Eb + Ia*Ra + La*dIa/dt + Ise*Rse + Lse*dIse/dt
        # For long shunt: Ise = Ia
        dIa_dt = (V_applied - Eb - Ia * (self.Ra + self.Rse)) / (self.La + self.Lse)

        # Shunt field circuit: V_applied = Ish*Rsh + Lsh*dIsh/dt
        dIsh_dt = (V_applied - Ish * self.Rsh) / self.Lsh

        # Electromagnetic torque
        T_em = self.Kt * Ia * Ish

        # Mechanical equation: J*domega/dt = T_em - B*omega - T_load
        domega_dt = (T_em - self.B * omega - T_load) / self.J

        # Angular position
        dtheta_dt = omega

        # Thermal equations
        # Armature heat generation (copper losses)
        P_copper_armature = Ia**2 * self.Ra
        dT_armature_dt = ((P_copper_armature - (T_armature - self.ambient_temperature) /
                          self.thermal_resistance_armature) / self.thermal_capacitance_armature)

        # Field heat generation
        P_copper_field = Ish**2 * self.Rsh
        dT_field_dt = ((P_copper_field - (T_field - self.ambient_temperature) /
                       self.thermal_resistance_field) / self.thermal_capacitance_field)

        return [dIa_dt, dIsh_dt, domega_dt, dtheta_dt, dT_armature_dt, dT_field_dt]

    def simulate_transient(self, t_span, y0, V_applied_func, T_load_func, method='RK45',
                          max_step=0.01):
        """
        Simulate transient response
        t_span: (t_start, t_end)
        y0: Initial conditions [Ia0, Ish0, omega0, theta0, T_armature0, T_field0]
        V_applied_func: Function of time returning applied voltage
        T_load_func: Function of time returning load torque
        method: 'RK45', 'RK23', 'DOP853', 'Radau', 'BDF', 'LSODA', or 'euler'
        """
        if method.lower() == 'euler':
            return self._euler_method(t_span, y0, V_applied_func, T_load_func, max_step)
        else:
            sol = solve_ivp(
                lambda t, y: self.differential_equations(t, y, V_applied_func(t), T_load_func(t)),
                t_span, y0, method=method, max_step=max_step, dense_output=True
            )
            return sol

    def _euler_method(self, t_span, y0, V_applied_func, T_load_func, dt):
        """Simple Euler method for comparison"""
        t_start, t_end = t_span
        t = np.arange(t_start, t_end, dt)
        y = np.zeros((len(t), len(y0)))
        y[0] = y0

        for i in range(1, len(t)):
            dy = self.differential_equations(t[i-1], y[i-1], V_applied_func(t[i-1]),
                                            T_load_func(t[i-1]))
            y[i] = y[i-1] + np.array(dy) * dt

        # Create solution object similar to solve_ivp
        class Solution:
            pass
        sol = Solution()
        sol.t = t
        sol.y = y.T
        sol.success = True
        return sol

    def calculate_rms(self, signal, time):
        """Calculate RMS value of a signal"""
        return np.sqrt(np.mean(signal**2))

    def calculate_losses(self, Ia, Ish, omega, T_armature, T_field):
        """Calculate detailed losses"""
        # Temperature-dependent resistance (typical copper temp coefficient: 0.00393/°C)
        alpha = 0.00393
        Ra_temp = self.Ra * (1 + alpha * (T_armature - 20))
        Rsh_temp = self.Rsh * (1 + alpha * (T_field - 20))

        # Copper losses
        copper_loss_armature = Ia**2 * Ra_temp
        copper_loss_shunt = Ish**2 * Rsh_temp
        copper_loss_series = Ia**2 * self.Rse

        # Iron losses (hysteresis + eddy current)
        # Hysteresis loss ∝ f * B^1.6 (Steinmetz equation)
        # Eddy current loss ∝ f^2 * B^2
        f = omega / (2 * np.pi)  # Frequency in Hz
        B_flux = Ish * 0.01  # Simplified flux density

        k_h = 50  # Hysteresis loss coefficient
        k_e = 5   # Eddy current loss coefficient

        hysteresis_loss = k_h * f * (B_flux ** 1.6)
        eddy_current_loss = k_e * (f ** 2) * (B_flux ** 2)
        iron_loss = hysteresis_loss + eddy_current_loss

        # Mechanical losses (friction and windage)
        friction_loss = self.B * omega**2
        windage_loss = 0.001 * omega**3  # Proportional to speed cubed
        mechanical_loss = friction_loss + windage_loss

        # Stray load loss (approximately 1% of output power)
        output_power = self.Kt * Ia * Ish * omega
        stray_load_loss = 0.01 * abs(output_power)

        return {
            'copper_armature': copper_loss_armature,
            'copper_shunt': copper_loss_shunt,
            'copper_series': copper_loss_series,
            'copper_total': copper_loss_armature + copper_loss_shunt + copper_loss_series,
            'hysteresis': hysteresis_loss,
            'eddy_current': eddy_current_loss,
            'iron_total': iron_loss,
            'friction': friction_loss,
            'windage': windage_loss,
            'mechanical_total': mechanical_loss,
            'stray_load': stray_load_loss,
            'total_loss': (copper_loss_armature + copper_loss_shunt + copper_loss_series +
                          iron_loss + mechanical_loss + stray_load_loss)
        }


# ============================================================================
# PART 3: MULTI-PHYSICS SIMULATION
# ============================================================================

class MultiPhysicsSimulator:
    """Coupled electromagnetic-thermal-mechanical simulation"""

    def __init__(self, circuit_model):
        self.circuit_model = circuit_model

    def coupled_simulation(self, t_span, initial_conditions, V_applied_func, T_load_func,
                          method='RK45'):
        """
        Perform coupled multi-physics simulation
        Electromagnetic, thermal, and mechanical domains are solved simultaneously
        """
        sol = self.circuit_model.simulate_transient(
            t_span, initial_conditions, V_applied_func, T_load_func, method=method
        )

        # Extract results
        t = sol.t
        Ia = sol.y[0]
        Ish = sol.y[1]
        omega = sol.y[2]
        theta = sol.y[3]
        T_armature = sol.y[4]
        T_field = sol.y[5]

        # Calculate derived quantities
        results = {
            'time': t,
            'armature_current': Ia,
            'field_current': Ish,
            'angular_velocity': omega,
            'speed_rpm': omega * 60 / (2 * np.pi),
            'angular_position': theta,
            'temperature_armature': T_armature,
            'temperature_field': T_field,
            'back_emf': self.circuit_model.Ke * omega * Ish,
            'electromagnetic_torque': self.circuit_model.Kt * Ia * Ish,
            'output_power': self.circuit_model.Kt * Ia * Ish * omega,
            'efficiency': np.zeros_like(t)
        }

        # Calculate efficiency at each time point
        for i in range(len(t)):
            V_applied = V_applied_func(t[i])
            P_in = V_applied * (Ia[i] + Ish[i])
            P_out = results['output_power'][i]
            if P_in > 0:
                results['efficiency'][i] = (P_out / P_in) * 100
            else:
                results['efficiency'][i] = 0

        # RMS values
        results['Ia_rms'] = self.circuit_model.calculate_rms(Ia, t)
        results['Ish_rms'] = self.circuit_model.calculate_rms(Ish, t)

        # Calculate losses over time
        losses_over_time = []
        for i in range(len(t)):
            losses = self.circuit_model.calculate_losses(
                Ia[i], Ish[i], omega[i], T_armature[i], T_field[i]
            )
            losses_over_time.append(losses)

        results['losses'] = losses_over_time

        return results

    def mechanical_stress_analysis(self, torque_data, time_data, shaft_diameter=0.05):
        """
        Analyze mechanical stress on the shaft
        shaft_diameter: Shaft diameter in meters
        """
        # Torsional stress: τ = (16 * T) / (π * d^3)
        torsional_stress = (16 * np.array(torque_data)) / (np.pi * shaft_diameter**3)

        # Maximum stress
        max_stress = np.max(np.abs(torsional_stress))

        # Fatigue analysis (simplified)
        # Count stress cycles and compare to material fatigue limit
        mean_stress = np.mean(np.abs(torsional_stress))
        stress_amplitude = np.std(torsional_stress)

        # Typical steel shaft fatigue limit: ~200 MPa
        fatigue_limit = 200e6  # Pa
        safety_factor = fatigue_limit / max_stress if max_stress > 0 else np.inf

        return {
            'torsional_stress': torsional_stress,
            'max_stress': max_stress,
            'mean_stress': mean_stress,
            'stress_amplitude': stress_amplitude,
            'safety_factor': safety_factor
        }


# ============================================================================
# PART 4: ECONOMIC ANALYSIS
# ============================================================================

class EconomicAnalyzer:
    """Economic analysis for dynamo operation"""

    def __init__(self, electricity_cost_per_kwh=0.12, maintenance_cost_per_hour=5.0,
                 initial_cost=50000, lifetime_years=20):
        self.electricity_cost = electricity_cost_per_kwh
        self.maintenance_cost = maintenance_cost_per_hour
        self.initial_cost = initial_cost
        self.lifetime_years = lifetime_years

    def calculate_operating_cost(self, power_input_kw, operating_hours):
        """Calculate operating cost"""
        energy_cost = power_input_kw * operating_hours * self.electricity_cost
        maintenance = operating_hours * self.maintenance_cost
        return {
            'energy_cost': energy_cost,
            'maintenance_cost': maintenance,
            'total_operating_cost': energy_cost + maintenance
        }

    def calculate_lifecycle_cost(self, annual_operating_hours, average_power_kw,
                                 discount_rate=0.05):
        """Calculate lifecycle cost with discounting"""
        annual_costs = []
        npv = self.initial_cost  # Start with initial investment

        for year in range(1, self.lifetime_years + 1):
            annual_op_cost = self.calculate_operating_cost(
                average_power_kw, annual_operating_hours
            )['total_operating_cost']

            # Discount to present value
            pv = annual_op_cost / ((1 + discount_rate) ** year)
            npv += pv
            annual_costs.append(annual_op_cost)

        return {
            'total_lifecycle_cost': npv,
            'annual_costs': annual_costs,
            'levelized_cost': npv / (annual_operating_hours * self.lifetime_years)
        }

    def payback_analysis(self, annual_revenue, annual_operating_cost):
        """Calculate payback period"""
        annual_profit = annual_revenue - annual_operating_cost
        if annual_profit > 0:
            payback_period = self.initial_cost / annual_profit
        else:
            payback_period = np.inf

        return {
            'annual_profit': annual_profit,
            'payback_period_years': payback_period,
            'roi_percent': (annual_profit / self.initial_cost) * 100
        }


# ============================================================================
# PART 5: ADVANCED GUI APPLICATION
# ============================================================================

class DynamoSimulatorGUI:
    """Main GUI application with comprehensive features"""

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Dynamo Simulation & Analysis System")
        self.root.geometry("1400x900")

        # Initialize models
        self.problem_solver = DynamoProblemSolver()
        self.circuit_model = DynamoCircuitModel()
        self.multi_physics = MultiPhysicsSimulator(self.circuit_model)
        self.economic_analyzer = EconomicAnalyzer()

        # Simulation state
        self.simulation_running = False
        self.simulation_data = None

        # Configure grid weights for auto-scaling
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create main container
        self.main_container = ttk.Frame(root)
        self.main_container.grid(row=0, column=0, sticky='nsew')
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Create tabs
        self.create_problem_solver_tab()
        self.create_dynamic_simulation_tab()
        self.create_multiphysics_tab()
        self.create_economic_analysis_tab()
        self.create_advanced_controls_tab()

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def on_window_resize(self, event):
        """Handle window resize for auto-scaling"""
        # Update plots if they exist
        if hasattr(self, 'simulation_data') and self.simulation_data:
            pass  # Matplotlib handles this automatically with tight_layout

    # ========================================================================
    # TAB 1: PROBLEM SOLVER
    # ========================================================================

    def create_problem_solver_tab(self):
        """Create the problem solver tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Problem Solver')

        # Configure grid
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Input frame
        input_frame = ttk.LabelFrame(tab, text='Input Parameters', padding=10)
        input_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        # Create input fields
        self.ps_inputs = {}
        params = [
            ('Speed (RPM)', 'speed_rpm', 1000),
            ('Power Output (kW)', 'power_kw', 20),
            ('Terminal Voltage (V)', 'voltage', 220),
            ('Armature Resistance (Ω)', 'ra', 0.04),
            ('Shunt Field Resistance (Ω)', 'rsh', 110),
            ('Series Field Resistance (Ω)', 'rse', 0.05),
            ('Efficiency (%)', 'efficiency', 85)
        ]

        for i, (label, key, default) in enumerate(params):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            entry = ttk.Entry(input_frame, width=15)
            entry.insert(0, str(default))
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.ps_inputs[key] = entry

        # Solve button
        ttk.Button(input_frame, text='Solve Problem',
                  command=self.solve_problem).grid(row=len(params), column=0,
                                                   columnspan=2, pady=10)

        # Results frame
        results_frame = ttk.LabelFrame(tab, text='Results', padding=10)
        results_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        # Results text widget
        self.ps_results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD,
                                                         font=('Courier', 10))
        self.ps_results_text.grid(row=0, column=0, sticky='nsew')

    def solve_problem(self):
        """Solve the dynamo problem with current inputs"""
        try:
            # Get inputs
            speed = float(self.ps_inputs['speed_rpm'].get())
            power_kw = float(self.ps_inputs['power_kw'].get())
            voltage = float(self.ps_inputs['voltage'].get())
            ra = float(self.ps_inputs['ra'].get())
            rsh = float(self.ps_inputs['rsh'].get())
            rse = float(self.ps_inputs['rse'].get())
            efficiency = float(self.ps_inputs['efficiency'].get()) / 100

            # Create solver and solve
            solver = DynamoProblemSolver(speed, power_kw, voltage, ra, rsh, rse, efficiency)
            results_text = solver.get_formatted_results()

            # Display results
            self.ps_results_text.delete(1.0, tk.END)
            self.ps_results_text.insert(1.0, results_text)

        except Exception as e:
            messagebox.showerror("Error", f"Error solving problem: {str(e)}")

    # ========================================================================
    # TAB 2: DYNAMIC SIMULATION
    # ========================================================================

    def create_dynamic_simulation_tab(self):
        """Create dynamic simulation tab with real-time ODE solver"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Dynamic Simulation')

        # Configure grid
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Control panel
        control_frame = ttk.LabelFrame(tab, text='Simulation Controls', padding=10)
        control_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        # Simulation parameters
        param_frame = ttk.Frame(control_frame)
        param_frame.grid(row=0, column=0, columnspan=3, sticky='ew', pady=5)

        self.sim_params = {}
        params = [
            ('Applied Voltage (V)', 'voltage', 220, 0, 300),
            ('Load Torque (N·m)', 'torque', 100, 0, 500),
            ('Simulation Time (s)', 'time', 5, 0.1, 20),
            ('Initial Speed (RPM)', 'init_speed', 1000, 0, 3000)
        ]

        for i, (label, key, default, min_val, max_val) in enumerate(params):
            ttk.Label(param_frame, text=label).grid(row=i, column=0, sticky='w', padx=5)

            var = tk.DoubleVar(value=default)
            self.sim_params[key] = var

            scale = ttk.Scale(param_frame, from_=min_val, to=max_val,
                            variable=var, orient='horizontal', length=200)
            scale.grid(row=i, column=1, padx=5)

            entry = ttk.Entry(param_frame, textvariable=var, width=10)
            entry.grid(row=i, column=2, padx=5)

        # ODE Solver selection
        ttk.Label(control_frame, text='ODE Solver:').grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.solver_var = tk.StringVar(value='RK45')
        solver_combo = ttk.Combobox(control_frame, textvariable=self.solver_var,
                                    values=['RK45', 'RK23', 'DOP853', 'Radau', 'BDF',
                                           'LSODA', 'euler'], width=15)
        solver_combo.grid(row=1, column=1, padx=5, pady=5)

        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)

        ttk.Button(button_frame, text='Start Simulation',
                  command=self.start_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='Stop',
                  command=self.stop_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='Reset',
                  command=self.reset_simulation).pack(side=tk.LEFT, padx=5)

        # Results frame with matplotlib
        results_frame = ttk.LabelFrame(tab, text='Simulation Results', padding=5)
        results_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        # Create matplotlib figure
        self.sim_fig = Figure(figsize=(12, 8), dpi=100)
        self.sim_canvas = FigureCanvasTkAgg(self.sim_fig, results_frame)
        self.sim_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

    def start_simulation(self):
        """Run dynamic simulation"""
        try:
            self.simulation_running = True

            # Get parameters
            V_applied = self.sim_params['voltage'].get()
            T_load = self.sim_params['torque'].get()
            sim_time = self.sim_params['time'].get()
            init_speed_rpm = self.sim_params['init_speed'].get()
            solver_method = self.solver_var.get()

            # Initial conditions
            init_speed_rad = init_speed_rpm * 2 * np.pi / 60
            y0 = [0, 0, init_speed_rad, 0, 25.0, 25.0]  # [Ia, Ish, omega, theta, T_arm, T_field]

            # Define input functions
            V_applied_func = lambda t: V_applied
            T_load_func = lambda t: T_load if t > 0.5 else 0  # Step load at 0.5s

            # Run simulation
            self.simulation_data = self.multi_physics.coupled_simulation(
                (0, sim_time), y0, V_applied_func, T_load_func, method=solver_method
            )

            # Plot results
            self.plot_simulation_results()

            messagebox.showinfo("Success", "Simulation completed successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Simulation error: {str(e)}")
        finally:
            self.simulation_running = False

    def stop_simulation(self):
        """Stop running simulation"""
        self.simulation_running = False

    def reset_simulation(self):
        """Reset simulation"""
        self.simulation_data = None
        self.sim_fig.clear()
        self.sim_canvas.draw()

    def plot_simulation_results(self):
        """Plot simulation results"""
        if not self.simulation_data:
            return

        self.sim_fig.clear()

        data = self.simulation_data
        t = data['time']

        # Create subplots
        ax1 = self.sim_fig.add_subplot(3, 2, 1)
        ax1.plot(t, data['armature_current'], 'b-', linewidth=2)
        ax1.set_ylabel('Armature Current (A)', fontsize=9)
        ax1.set_xlabel('Time (s)', fontsize=9)
        ax1.grid(True, alpha=0.3)
        ax1.set_title('Armature Current vs Time', fontsize=10)

        ax2 = self.sim_fig.add_subplot(3, 2, 2)
        ax2.plot(t, data['field_current'], 'r-', linewidth=2)
        ax2.set_ylabel('Field Current (A)', fontsize=9)
        ax2.set_xlabel('Time (s)', fontsize=9)
        ax2.grid(True, alpha=0.3)
        ax2.set_title('Field Current vs Time', fontsize=10)

        ax3 = self.sim_fig.add_subplot(3, 2, 3)
        ax3.plot(t, data['speed_rpm'], 'g-', linewidth=2)
        ax3.set_ylabel('Speed (RPM)', fontsize=9)
        ax3.set_xlabel('Time (s)', fontsize=9)
        ax3.grid(True, alpha=0.3)
        ax3.set_title('Speed vs Time', fontsize=10)

        ax4 = self.sim_fig.add_subplot(3, 2, 4)
        ax4.plot(t, data['electromagnetic_torque'], 'm-', linewidth=2)
        ax4.set_ylabel('Torque (N·m)', fontsize=9)
        ax4.set_xlabel('Time (s)', fontsize=9)
        ax4.grid(True, alpha=0.3)
        ax4.set_title('Electromagnetic Torque vs Time', fontsize=10)

        ax5 = self.sim_fig.add_subplot(3, 2, 5)
        ax5.plot(t, data['temperature_armature'], 'orange', linewidth=2, label='Armature')
        ax5.plot(t, data['temperature_field'], 'brown', linewidth=2, label='Field')
        ax5.set_ylabel('Temperature (°C)', fontsize=9)
        ax5.set_xlabel('Time (s)', fontsize=9)
        ax5.legend(fontsize=8)
        ax5.grid(True, alpha=0.3)
        ax5.set_title('Temperature vs Time', fontsize=10)

        ax6 = self.sim_fig.add_subplot(3, 2, 6)
        ax6.plot(t, data['efficiency'], 'c-', linewidth=2)
        ax6.set_ylabel('Efficiency (%)', fontsize=9)
        ax6.set_xlabel('Time (s)', fontsize=9)
        ax6.grid(True, alpha=0.3)
        ax6.set_title('Efficiency vs Time', fontsize=10)

        self.sim_fig.tight_layout()
        self.sim_canvas.draw()

    # ========================================================================
    # TAB 3: MULTI-PHYSICS ANALYSIS
    # ========================================================================

    def create_multiphysics_tab(self):
        """Create multi-physics simulation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Multi-Physics Analysis')

        # Configure grid
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Control frame
        control_frame = ttk.LabelFrame(tab, text='Analysis Controls', padding=10)
        control_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        ttk.Button(control_frame, text='Run Multi-Physics Analysis',
                  command=self.run_multiphysics_analysis).pack(pady=5)
        ttk.Button(control_frame, text='Mechanical Stress Analysis',
                  command=self.run_stress_analysis).pack(pady=5)

        # Results frame
        results_frame = ttk.LabelFrame(tab, text='Multi-Physics Results', padding=5)
        results_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        # Create matplotlib figure
        self.mp_fig = Figure(figsize=(12, 8), dpi=100)
        self.mp_canvas = FigureCanvasTkAgg(self.mp_fig, results_frame)
        self.mp_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

    def run_multiphysics_analysis(self):
        """Run comprehensive multi-physics analysis"""
        if not self.simulation_data:
            messagebox.showwarning("Warning", "Please run dynamic simulation first!")
            return

        try:
            self.mp_fig.clear()

            data = self.simulation_data
            t = data['time']

            # Extract loss data at final time
            final_losses = data['losses'][-1]

            # Create loss breakdown pie chart
            ax1 = self.mp_fig.add_subplot(2, 2, 1)
            loss_labels = ['Copper\nArmature', 'Copper\nShunt', 'Copper\nSeries',
                          'Iron', 'Mechanical', 'Stray Load']
            loss_values = [
                final_losses['copper_armature'],
                final_losses['copper_shunt'],
                final_losses['copper_series'],
                final_losses['iron_total'],
                final_losses['mechanical_total'],
                final_losses['stray_load']
            ]
            colors = ['#ff9999', '#ff6666', '#ff3333', '#66b3ff', '#99ff99', '#ffcc99']
            ax1.pie(loss_values, labels=loss_labels, autopct='%1.1f%%', colors=colors,
                   startangle=90)
            ax1.set_title('Loss Breakdown', fontsize=10)

            # Total losses over time
            ax2 = self.mp_fig.add_subplot(2, 2, 2)
            total_losses = [loss['total_loss'] for loss in data['losses']]
            copper_losses = [loss['copper_total'] for loss in data['losses']]
            iron_losses = [loss['iron_total'] for loss in data['losses']]
            mech_losses = [loss['mechanical_total'] for loss in data['losses']]

            ax2.plot(t, total_losses, 'k-', linewidth=2, label='Total')
            ax2.plot(t, copper_losses, 'r-', linewidth=1.5, label='Copper')
            ax2.plot(t, iron_losses, 'b-', linewidth=1.5, label='Iron')
            ax2.plot(t, mech_losses, 'g-', linewidth=1.5, label='Mechanical')
            ax2.set_xlabel('Time (s)', fontsize=9)
            ax2.set_ylabel('Loss (W)', fontsize=9)
            ax2.set_title('Losses vs Time', fontsize=10)
            ax2.legend(fontsize=8)
            ax2.grid(True, alpha=0.3)

            # Thermal map
            ax3 = self.mp_fig.add_subplot(2, 2, 3)
            ax3.plot(t, data['temperature_armature'], 'r-', linewidth=2, label='Armature')
            ax3.plot(t, data['temperature_field'], 'b-', linewidth=2, label='Field')
            ax3.axhline(y=125, color='orange', linestyle='--', label='Temp Limit')
            ax3.set_xlabel('Time (s)', fontsize=9)
            ax3.set_ylabel('Temperature (°C)', fontsize=9)
            ax3.set_title('Thermal Analysis', fontsize=10)
            ax3.legend(fontsize=8)
            ax3.grid(True, alpha=0.3)

            # Power flow Sankey-style representation (simplified)
            ax4 = self.mp_fig.add_subplot(2, 2, 4)

            # Calculate average power values
            P_in_avg = np.mean(data['armature_current'] * self.sim_params['voltage'].get())
            P_out_avg = np.mean(data['output_power'])
            P_loss_avg = np.mean(total_losses)

            # Create bar chart for power flow
            categories = ['Input\nPower', 'Output\nPower', 'Total\nLoss']
            values = [P_in_avg, P_out_avg, P_loss_avg]
            colors_bar = ['#4CAF50', '#2196F3', '#F44336']

            bars = ax4.bar(categories, values, color=colors_bar, alpha=0.7, edgecolor='black')
            ax4.set_ylabel('Power (W)', fontsize=9)
            ax4.set_title('Power Flow Analysis', fontsize=10)
            ax4.grid(True, alpha=0.3, axis='y')

            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'{value:.1f} W',
                        ha='center', va='bottom', fontsize=8)

            self.mp_fig.tight_layout()
            self.mp_canvas.draw()

            messagebox.showinfo("Success", "Multi-physics analysis completed!")

        except Exception as e:
            messagebox.showerror("Error", f"Analysis error: {str(e)}")

    def run_stress_analysis(self):
        """Run mechanical stress analysis"""
        if not self.simulation_data:
            messagebox.showwarning("Warning", "Please run dynamic simulation first!")
            return

        try:
            data = self.simulation_data
            t = data['time']
            torque = data['electromagnetic_torque']

            # Perform stress analysis
            stress_results = self.multi_physics.mechanical_stress_analysis(torque, t)

            # Create stress plot
            self.mp_fig.clear()

            ax1 = self.mp_fig.add_subplot(2, 1, 1)
            ax1.plot(t, stress_results['torsional_stress'] / 1e6, 'b-', linewidth=2)
            ax1.set_xlabel('Time (s)', fontsize=10)
            ax1.set_ylabel('Torsional Stress (MPa)', fontsize=10)
            ax1.set_title('Shaft Torsional Stress vs Time', fontsize=11)
            ax1.grid(True, alpha=0.3)
            ax1.axhline(y=200, color='r', linestyle='--', label='Fatigue Limit')
            ax1.legend()

            ax2 = self.mp_fig.add_subplot(2, 1, 2)
            info_text = f"""
Mechanical Stress Analysis Results:

Maximum Stress: {stress_results['max_stress']/1e6:.2f} MPa
Mean Stress: {stress_results['mean_stress']/1e6:.2f} MPa
Stress Amplitude: {stress_results['stress_amplitude']/1e6:.2f} MPa
Safety Factor: {stress_results['safety_factor']:.2f}

Assessment: {'SAFE' if stress_results['safety_factor'] > 2 else 'REVIEW REQUIRED'}
            """
            ax2.text(0.1, 0.5, info_text, fontsize=10, family='monospace',
                    verticalalignment='center', transform=ax2.transAxes)
            ax2.axis('off')

            self.mp_fig.tight_layout()
            self.mp_canvas.draw()

            messagebox.showinfo("Success", "Stress analysis completed!")

        except Exception as e:
            messagebox.showerror("Error", f"Stress analysis error: {str(e)}")

    # ========================================================================
    # TAB 4: ECONOMIC ANALYSIS
    # ========================================================================

    def create_economic_analysis_tab(self):
        """Create economic analysis tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Economic Analysis')

        # Configure grid
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Input frame
        input_frame = ttk.LabelFrame(tab, text='Economic Parameters', padding=10)
        input_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.econ_inputs = {}
        params = [
            ('Electricity Cost ($/kWh)', 'elec_cost', 0.12),
            ('Maintenance Cost ($/hr)', 'maint_cost', 5.0),
            ('Initial Cost ($)', 'init_cost', 50000),
            ('Lifetime (years)', 'lifetime', 20),
            ('Operating Hours/Year', 'op_hours', 8760),
            ('Average Power (kW)', 'avg_power', 20),
            ('Annual Revenue ($)', 'revenue', 100000),
            ('Discount Rate (%)', 'discount', 5)
        ]

        for i, (label, key, default) in enumerate(params):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            entry = ttk.Entry(input_frame, width=15)
            entry.insert(0, str(default))
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.econ_inputs[key] = entry

        # Analyze button
        ttk.Button(input_frame, text='Run Economic Analysis',
                  command=self.run_economic_analysis).grid(row=len(params), column=0,
                                                          columnspan=2, pady=10)

        # Results frame
        results_frame = ttk.LabelFrame(tab, text='Economic Analysis Results', padding=5)
        results_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        # Create matplotlib figure
        self.econ_fig = Figure(figsize=(12, 6), dpi=100)
        self.econ_canvas = FigureCanvasTkAgg(self.econ_fig, results_frame)
        self.econ_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

    def run_economic_analysis(self):
        """Run economic analysis"""
        try:
            # Get inputs
            elec_cost = float(self.econ_inputs['elec_cost'].get())
            maint_cost = float(self.econ_inputs['maint_cost'].get())
            init_cost = float(self.econ_inputs['init_cost'].get())
            lifetime = int(self.econ_inputs['lifetime'].get())
            op_hours = float(self.econ_inputs['op_hours'].get())
            avg_power = float(self.econ_inputs['avg_power'].get())
            revenue = float(self.econ_inputs['revenue'].get())
            discount_rate = float(self.econ_inputs['discount'].get()) / 100

            # Create analyzer
            analyzer = EconomicAnalyzer(elec_cost, maint_cost, init_cost, lifetime)

            # Calculate costs
            op_cost_annual = analyzer.calculate_operating_cost(avg_power, op_hours)
            lifecycle = analyzer.calculate_lifecycle_cost(op_hours, avg_power, discount_rate)
            payback = analyzer.payback_analysis(revenue, op_cost_annual['total_operating_cost'])

            # Plot results
            self.econ_fig.clear()

            # Annual cost breakdown
            ax1 = self.econ_fig.add_subplot(1, 3, 1)
            costs = [op_cost_annual['energy_cost'], op_cost_annual['maintenance_cost']]
            labels = ['Energy Cost', 'Maintenance Cost']
            colors = ['#FF6B6B', '#4ECDC4']
            ax1.pie(costs, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
            ax1.set_title(f'Annual Operating Cost\nTotal: ${sum(costs):,.0f}', fontsize=10)

            # Lifecycle cost
            ax2 = self.econ_fig.add_subplot(1, 3, 2)
            years = list(range(lifetime + 1))
            cumulative_cost = [init_cost]
            for i in range(1, lifetime + 1):
                annual_pv = op_cost_annual['total_operating_cost'] / ((1 + discount_rate) ** i)
                cumulative_cost.append(cumulative_cost[-1] + annual_pv)

            ax2.plot(years, cumulative_cost, 'b-', linewidth=2, marker='o', markersize=4)
            ax2.set_xlabel('Year', fontsize=9)
            ax2.set_ylabel('Cumulative Cost ($)', fontsize=9)
            ax2.set_title(f'Lifecycle Cost (NPV)\nTotal: ${lifecycle["total_lifecycle_cost"]:,.0f}',
                         fontsize=10)
            ax2.grid(True, alpha=0.3)

            # Payback analysis
            ax3 = self.econ_fig.add_subplot(1, 3, 3)
            info_text = f"""
Economic Analysis Summary

Annual Operating Cost:
  Energy: ${op_cost_annual['energy_cost']:,.0f}
  Maintenance: ${op_cost_annual['maintenance_cost']:,.0f}
  Total: ${op_cost_annual['total_operating_cost']:,.0f}

Lifecycle Analysis:
  Total NPV: ${lifecycle['total_lifecycle_cost']:,.0f}
  Levelized Cost: ${lifecycle['levelized_cost']:.4f}/kWh

Payback Analysis:
  Annual Profit: ${payback['annual_profit']:,.0f}
  Payback Period: {payback['payback_period_years']:.1f} years
  ROI: {payback['roi_percent']:.2f}% per year

Assessment: {'ECONOMICAL' if payback['payback_period_years'] < lifetime/2 else 'MARGINAL'}
            """
            ax3.text(0.05, 0.5, info_text, fontsize=9, family='monospace',
                    verticalalignment='center', transform=ax3.transAxes)
            ax3.axis('off')

            self.econ_fig.tight_layout()
            self.econ_canvas.draw()

            messagebox.showinfo("Success", "Economic analysis completed!")

        except Exception as e:
            messagebox.showerror("Error", f"Economic analysis error: {str(e)}")

    # ========================================================================
    # TAB 5: ADVANCED CONTROLS
    # ========================================================================

    def create_advanced_controls_tab(self):
        """Create advanced controls tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Advanced Controls')

        # Configure grid
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Control methods frame
        methods_frame = ttk.LabelFrame(tab, text='Control Methods', padding=10)
        methods_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.control_method = tk.StringVar(value='Voltage Control')
        methods = ['Voltage Control', 'Field Control', 'Armature Resistance Control',
                  'Ward-Leonard Control', 'Thyristor Control']

        for i, method in enumerate(methods):
            ttk.Radiobutton(methods_frame, text=method, variable=self.control_method,
                          value=method).grid(row=i, column=0, sticky='w', padx=5, pady=2)

        # Thermal and derating frame
        thermal_frame = ttk.LabelFrame(tab, text='Thermal & Derating Analysis', padding=10)
        thermal_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=5)

        ttk.Label(thermal_frame, text='Ambient Temperature (°C):').grid(row=0, column=0,
                                                                        sticky='w', padx=5)
        self.ambient_temp = ttk.Entry(thermal_frame, width=10)
        self.ambient_temp.insert(0, '25')
        self.ambient_temp.grid(row=0, column=1, padx=5)

        ttk.Label(thermal_frame, text='Altitude (m):').grid(row=1, column=0, sticky='w', padx=5)
        self.altitude = ttk.Entry(thermal_frame, width=10)
        self.altitude.insert(0, '0')
        self.altitude.grid(row=1, column=1, padx=5)

        ttk.Button(thermal_frame, text='Calculate Derating Factor',
                  command=self.calculate_derating).grid(row=2, column=0, columnspan=2, pady=10)

        # Results display
        self.derating_result = tk.StringVar(value='')
        ttk.Label(thermal_frame, textvariable=self.derating_result,
                 font=('Arial', 10, 'bold')).grid(row=3, column=0, columnspan=2)

        # Power consumption monitoring
        monitor_frame = ttk.LabelFrame(tab, text='Power Consumption Monitor', padding=10)
        monitor_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=5)

        ttk.Button(monitor_frame, text='Show Power Consumption Analysis',
                  command=self.show_power_consumption).pack(pady=5)

        # Info frame
        info_frame = ttk.LabelFrame(tab, text='Control Methods Information', padding=10)
        info_frame.grid(row=3, column=0, sticky='nsew', padx=10, pady=5)
        info_frame.grid_rowconfigure(0, weight=1)
        info_frame.grid_columnconfigure(0, weight=1)

        self.control_info_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD,
                                                           height=10, font=('Courier', 9))
        self.control_info_text.grid(row=0, column=0, sticky='nsew')

        # Display initial control info
        self.update_control_info()
        self.control_method.trace('w', lambda *args: self.update_control_info())

    def update_control_info(self):
        """Update control method information"""
        info = {
            'Voltage Control': """
Voltage Control Method:
- Adjust applied voltage to control speed
- Simple and economical
- Applicable for small motors
- Speed decreases with load
- Suitable for applications with constant load
            """,
            'Field Control': """
Field Control Method:
- Vary field current to control speed
- Speed control above rated speed
- Constant power operation
- Most economical for speed control above base speed
- Commonly used in traction applications
            """,
            'Armature Resistance Control': """
Armature Resistance Control:
- Add external resistance in armature circuit
- Speed decreases with load
- Poor speed regulation
- Low efficiency due to resistance losses
- Used for starting and temporary speed control
            """,
            'Ward-Leonard Control': """
Ward-Leonard Control System:
- Motor-generator set provides variable voltage
- Excellent speed control and regulation
- Wide speed range (both directions)
- Smooth acceleration and deceleration
- High initial cost but very efficient
- Used in elevators, cranes, rolling mills
            """,
            'Thyristor Control': """
Thyristor (SCR) Control:
- Modern electronic control method
- Precise speed and torque control
- High efficiency
- Fast response
- Can provide both rectification and control
- Used in industrial drives and traction
            """
        }

        method = self.control_method.get()
        self.control_info_text.delete(1.0, tk.END)
        self.control_info_text.insert(1.0, info.get(method, ''))

    def calculate_derating(self):
        """Calculate derating factor based on temperature and altitude"""
        try:
            ambient = float(self.ambient_temp.get())
            alt = float(self.altitude.get())

            # Temperature derating
            rated_temp = 40  # °C
            if ambient > rated_temp:
                temp_derating = 1 - 0.01 * (ambient - rated_temp)
            else:
                temp_derating = 1.0

            # Altitude derating (air density decreases with altitude)
            # Typically 1% derating per 100m above 1000m
            if alt > 1000:
                alt_derating = 1 - 0.01 * ((alt - 1000) / 100)
            else:
                alt_derating = 1.0

            # Combined derating
            total_derating = temp_derating * alt_derating

            result = f"Derating Factor: {total_derating:.3f}\n"
            result += f"Temperature Factor: {temp_derating:.3f}\n"
            result += f"Altitude Factor: {alt_derating:.3f}\n"
            result += f"Derated Capacity: {total_derating*100:.1f}%"

            self.derating_result.set(result)

        except Exception as e:
            messagebox.showerror("Error", f"Derating calculation error: {str(e)}")

    def show_power_consumption(self):
        """Show power consumption analysis"""
        if not self.simulation_data:
            messagebox.showwarning("Warning", "Please run dynamic simulation first!")
            return

        try:
            data = self.simulation_data
            t = data['time']

            # Calculate power consumption
            P_in = data['armature_current'] * self.sim_params['voltage'].get()
            P_out = data['output_power']
            P_loss = P_in - P_out

            # Energy consumption
            energy_in = np.trapz(P_in, t) / 3600  # Wh
            energy_out = np.trapz(P_out, t) / 3600  # Wh
            energy_loss = energy_in - energy_out

            # Create figure
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))

            # Power vs time
            axes[0, 0].plot(t, P_in/1000, 'r-', linewidth=2, label='Input Power')
            axes[0, 0].plot(t, P_out/1000, 'g-', linewidth=2, label='Output Power')
            axes[0, 0].plot(t, P_loss/1000, 'b-', linewidth=2, label='Loss')
            axes[0, 0].set_xlabel('Time (s)')
            axes[0, 0].set_ylabel('Power (kW)')
            axes[0, 0].set_title('Power Consumption vs Time')
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)

            # Efficiency vs time
            axes[0, 1].plot(t, data['efficiency'], 'purple', linewidth=2)
            axes[0, 1].set_xlabel('Time (s)')
            axes[0, 1].set_ylabel('Efficiency (%)')
            axes[0, 1].set_title('Efficiency vs Time')
            axes[0, 1].grid(True, alpha=0.3)

            # Energy breakdown
            energy_labels = ['Input\nEnergy', 'Output\nEnergy', 'Energy\nLoss']
            energy_values = [energy_in, energy_out, energy_loss]
            colors = ['#FF6B6B', '#4ECDC4', '#95E1D3']
            axes[1, 0].bar(energy_labels, energy_values, color=colors, edgecolor='black')
            axes[1, 0].set_ylabel('Energy (Wh)')
            axes[1, 0].set_title('Energy Consumption Breakdown')
            axes[1, 0].grid(True, alpha=0.3, axis='y')

            # Add value labels
            for i, (label, value) in enumerate(zip(energy_labels, energy_values)):
                axes[1, 0].text(i, value, f'{value:.2f} Wh',
                              ha='center', va='bottom', fontsize=9)

            # Statistics
            stats_text = f"""
Power Consumption Statistics:

Average Input Power: {np.mean(P_in)/1000:.2f} kW
Average Output Power: {np.mean(P_out)/1000:.2f} kW
Average Loss: {np.mean(P_loss)/1000:.2f} kW

Peak Input Power: {np.max(P_in)/1000:.2f} kW
Peak Output Power: {np.max(P_out)/1000:.2f} kW

Total Energy Input: {energy_in:.2f} Wh
Total Energy Output: {energy_out:.2f} Wh
Total Energy Loss: {energy_loss:.2f} Wh

Average Efficiency: {np.mean(data['efficiency']):.2f}%
            """
            axes[1, 1].text(0.1, 0.5, stats_text, fontsize=10, family='monospace',
                          verticalalignment='center', transform=axes[1, 1].transAxes)
            axes[1, 1].axis('off')

            plt.tight_layout()
            plt.show()

        except Exception as e:
            messagebox.showerror("Error", f"Power consumption analysis error: {str(e)}")


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = DynamoSimulatorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    # Print solution to console as well
    print("="*70)
    print("INITIAL PROBLEM SOLUTION")
    print("="*70)
    solver = DynamoProblemSolver()
    print(solver.get_formatted_results())
    print("\nStarting GUI application...")
    print("="*70)

    # Launch GUI
    main()
