"""
Test script for DC Shunt Generator Problem
Tests the mathematical solution without GUI
"""

import math

class DynamoProblemSolver:
    """Solves DC shunt generator problems"""

    def __init__(self, speed_rpm=1000, power_output_kw=20, terminal_voltage=220,
                 ra=0.04, rsh=110, rse=0.05, efficiency=0.85, machine_type='compound',
                 mech_core_loss=None):
        self.speed_rpm = speed_rpm
        self.power_output_w = power_output_kw * 1000
        self.V_t = terminal_voltage
        self.Ra = ra
        self.Rsh = rsh
        self.Rse = rse
        self.efficiency = efficiency
        self.machine_type = machine_type
        self.mech_core_loss = mech_core_loss
        self.results = {}

    def solve(self):
        """Solve the complete dynamo problem"""
        if self.machine_type == 'shunt':
            return self.solve_shunt()
        else:
            return self.solve_compound()

    def solve_shunt(self):
        """Solve DC shunt generator problem"""
        # Load current
        I_L = self.power_output_w / self.V_t

        # Shunt field current
        I_sh = self.V_t / self.Rsh

        # Armature current (for shunt generator: Ia = IL + Ish)
        I_a = I_L + I_sh

        # Back EMF
        E_b = self.V_t + I_a * self.Ra

        # Copper losses
        copper_loss_armature = I_a**2 * self.Ra
        copper_loss_shunt = I_sh**2 * self.Rsh
        total_copper_loss = copper_loss_armature + copper_loss_shunt

        # Calculate power and losses
        if self.mech_core_loss is not None:
            # Mechanical and core losses given
            iron_friction_loss = self.mech_core_loss
            total_losses = total_copper_loss + iron_friction_loss
            P_input = self.power_output_w + total_losses
            efficiency_calculated = (self.power_output_w / P_input) * 100 if P_input > 0 else 0
        else:
            # Efficiency given, calculate mechanical losses
            P_input = self.power_output_w / self.efficiency
            total_losses = P_input - self.power_output_w
            iron_friction_loss = total_losses - total_copper_loss
            efficiency_calculated = self.efficiency * 100

        # Torque calculations
        omega = (2 * math.pi * self.speed_rpm) / 60  # rad/s
        torque_prime_mover = P_input / omega if omega > 0 else 0
        torque_electromagnetic = E_b * I_a / omega if omega > 0 else 0

        self.results = {
            'load_current': I_L,
            'shunt_field_current': I_sh,
            'armature_current': I_a,
            'back_emf': E_b,
            'copper_loss_armature': copper_loss_armature,
            'copper_loss_shunt': copper_loss_shunt,
            'copper_loss_total': total_copper_loss,
            'iron_friction_loss': iron_friction_loss,
            'total_losses': total_losses,
            'input_power': P_input,
            'output_power': self.power_output_w,
            'shaft_power_kw': P_input / 1000,
            'efficiency_percent': efficiency_calculated,
            'torque_prime_mover': torque_prime_mover,
            'torque_electromagnetic': torque_electromagnetic,
            'speed_rad_s': omega
        }

        return self.results

    def get_formatted_results(self):
        """Get formatted string of results"""
        if not self.results:
            self.solve()

        output = "="*70 + "\n"
        output += f"DC {self.machine_type.upper()} GENERATOR PROBLEM SOLUTION\n"
        output += "="*70 + "\n\n"
        output += f"Given Parameters:\n"
        output += f"  Machine Type: DC {self.machine_type.title()} Generator\n"
        output += f"  Speed: {self.speed_rpm} RPM\n"
        output += f"  Power Output: {self.power_output_w/1000:.2f} kW\n"
        output += f"  Terminal Voltage: {self.V_t} V\n"
        output += f"  Armature Resistance (Ra): {self.Ra} Ω\n"
        output += f"  Shunt Field Resistance (Rsh): {self.Rsh} Ω\n"
        if self.mech_core_loss is not None:
            output += f"  Mechanical & Core Losses: {self.mech_core_loss} W\n"
        else:
            output += f"  Efficiency: {self.efficiency*100}%\n"
        output += "\n"

        output += f"Calculated Values:\n"
        output += f"  Load Current (IL): {self.results['load_current']:.3f} A\n"
        output += f"  Shunt Field Current (Ish): {self.results['shunt_field_current']:.3f} A\n"
        output += f"  Armature Current (Ia): {self.results['armature_current']:.3f} A\n"
        output += f"  Back EMF (Eb): {self.results['back_emf']:.3f} V\n\n"

        output += "="*70 + "\n"
        output += "KEY RESULTS:\n"
        output += "="*70 + "\n\n"

        output += f"(a) SHAFT POWER REQUIRED: {self.results['shaft_power_kw']:.3f} kW\n\n"

        output += f"(b) EFFICIENCY: {self.results['efficiency_percent']:.2f}%\n\n"

        output += f"(c) LOSSES BREAKDOWN:\n"
        output += f"    Armature Copper Loss (Ia²Ra): {self.results['copper_loss_armature']:.3f} W\n"
        output += f"    Shunt Field Copper Loss (Ish²Rsh): {self.results['copper_loss_shunt']:.3f} W\n"
        output += f"    Total Copper Loss: {self.results['copper_loss_total']:.3f} W ({self.results['copper_loss_total']/1000:.3f} kW)\n"
        output += f"    Mechanical & Core Loss: {self.results['iron_friction_loss']:.3f} W ({self.results['iron_friction_loss']/1000:.3f} kW)\n"
        output += f"    TOTAL LOSSES: {self.results['total_losses']:.3f} W ({self.results['total_losses']/1000:.3f} kW)\n\n"

        output += f"(d) TORQUE ANALYSIS:\n"
        output += f"    Torque at Driving Shaft: {self.results['torque_prime_mover']:.3f} N·m\n"
        output += f"    Electromagnetic Torque: {self.results['torque_electromagnetic']:.3f} N·m\n\n"

        output += f"Additional Information:\n"
        output += f"  Angular Speed: {self.results['speed_rad_s']:.3f} rad/s\n"
        output += f"  Input Power (Shaft): {self.results['input_power']/1000:.3f} kW\n"
        output += f"  Output Power (Electrical): {self.results['output_power']/1000:.3f} kW\n"

        return output


if __name__ == '__main__':
    print("="*70)
    print("DC SHUNT GENERATOR PROBLEM SOLUTION")
    print("="*70)
    print("\nProblem Statement:")
    print("A D.C. shunt generator has a full load output of 10 kW at a terminal")
    print("voltage of 240 V. The armature and the shunt field winding resistances")
    print("are 0.6 and 160 ohms respectively. The sum of the mechanical and core")
    print("losses is 500 W. Calculate:")
    print("(a) The power required, in kW, at the driving shaft at full load")
    print("(b) The corresponding efficiency")
    print("\n" + "="*70 + "\n")

    # Solve the specific DC shunt generator problem
    solver = DynamoProblemSolver(
        speed_rpm=1000,  # Assumed
        power_output_kw=10,
        terminal_voltage=240,
        ra=0.6,
        rsh=160,
        rse=0,
        efficiency=0.85,  # Not used when mech_core_loss is specified
        machine_type='shunt',
        mech_core_loss=500
    )
    print(solver.get_formatted_results())
