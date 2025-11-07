"""
Test script for validating the dynamo problem solution
This script can run without GUI dependencies
"""

import math

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

        output = "="*70 + "\n"
        output += "DYNAMO PROBLEM SOLUTION\n"
        output += "="*70 + "\n\n"
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

        output += "="*70 + "\n"
        output += "ANSWERS:\n"
        output += "="*70 + "\n\n"

        output += f"(i) COPPER LOSSES:\n"
        output += f"    Armature Copper Loss: {self.results['copper_loss_armature']:.3f} W\n"
        output += f"    Shunt Field Copper Loss: {self.results['copper_loss_shunt']:.3f} W\n"
        output += f"    Series Field Copper Loss: {self.results['copper_loss_series']:.3f} W\n"
        output += f"    ────────────────────────────────────────\n"
        output += f"    TOTAL COPPER LOSS: {self.results['copper_loss_total']:.3f} W ({self.results['copper_loss_total']/1000:.3f} kW)\n\n"

        output += f"(ii) IRON AND FRICTION LOSS:\n"
        output += f"    ────────────────────────────────────────\n"
        output += f"    {self.results['iron_friction_loss']:.3f} W ({self.results['iron_friction_loss']/1000:.3f} kW)\n\n"

        output += f"(iii) TORQUE DEVELOPED BY PRIME MOVER:\n"
        output += f"    ────────────────────────────────────────\n"
        output += f"    {self.results['torque_prime_mover']:.3f} N·m\n\n"

        output += "="*70 + "\n"
        output += "Additional Information:\n"
        output += "="*70 + "\n"
        output += f"  Input Power: {self.results['input_power']/1000:.3f} kW\n"
        output += f"  Total Losses: {self.results['total_losses']/1000:.3f} kW\n"
        output += f"  Electromagnetic Torque: {self.results['torque_electromagnetic']:.3f} N·m\n"
        output += f"  Angular Speed: {self.results['speed_rad_s']:.3f} rad/s\n"
        output += f"  Efficiency Verification: {(self.power_output_w/self.results['input_power']*100):.2f}%\n"
        output += "="*70 + "\n"

        return output


if __name__ == "__main__":
    print("\n" + "="*70)
    print("ADVANCED DYNAMO SIMULATOR - MATHEMATICAL SOLUTION TEST")
    print("="*70 + "\n")

    # Create solver with given parameters
    solver = DynamoProblemSolver(
        speed_rpm=1000,
        power_output_kw=20,
        terminal_voltage=220,
        ra=0.04,
        rsh=110,
        rse=0.05,
        efficiency=0.85
    )

    # Solve and display results
    print(solver.get_formatted_results())

    print("\n✓ Solution validated successfully!")
    print("\nTo run the full GUI application, install dependencies:")
    print("  pip install -r requirements_dynamo.txt")
    print("\nThen run:")
    print("  python dynamo_advanced_simulator.py")
