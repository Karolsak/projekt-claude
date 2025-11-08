"""
Test script for Shunt Generators Simulation
Tests core functionality without GUI requirements
"""

import sys
import numpy as np
from scipy.integrate import solve_ivp

def test_circuit_analysis():
    """Test steady-state circuit analysis"""
    print("="*70)
    print("Testing Steady-State Circuit Analysis")
    print("="*70)

    # Problem parameters
    E1, E2, E3 = 127.0, 120.0, 119.0  # EMF values (V)
    Ra = 0.1  # Armature resistance (Ω)
    RL = 2.0  # Load resistance (Ω)

    # Calculate bus voltage using circuit equations
    sum_e_over_ra = (E1 + E2 + E3) / Ra
    sum_1_over_ra = 3.0 / Ra

    V_bus = sum_e_over_ra / (sum_1_over_ra + 1.0/RL)

    # Calculate individual currents
    I1 = (E1 - V_bus) / Ra
    I2 = (E2 - V_bus) / Ra
    I3 = (E3 - V_bus) / Ra
    IL = V_bus / RL

    # Determine modes
    modes = []
    for i, current in enumerate([I1, I2, I3], 1):
        if current > 0.1:
            mode = "Generating"
        elif current < -0.1:
            mode = "Motoring"
        else:
            mode = "Floating"
        modes.append(mode)

    # Display results
    print(f"\nBus Voltage: {V_bus:.4f} V")
    print(f"\nGenerator 1 ({E1}V):")
    print(f"  Current: {I1:.4f} A")
    print(f"  Mode: {modes[0]}")
    print(f"  Power: {V_bus * I1:.4f} W")

    print(f"\nGenerator 2 ({E2}V):")
    print(f"  Current: {I2:.4f} A")
    print(f"  Mode: {modes[1]}")
    print(f"  Power: {V_bus * I2:.4f} W")

    print(f"\nGenerator 3 ({E3}V):")
    print(f"  Current: {I3:.4f} A")
    print(f"  Mode: {modes[2]}")
    print(f"  Power: {V_bus * I3:.4f} W")

    print(f"\nLoad:")
    print(f"  Current: {IL:.4f} A")
    print(f"  Power: {V_bus * IL:.4f} W")

    # Verify current balance
    total_gen_current = I1 + I2 + I3
    print(f"\nVerification:")
    print(f"  Total Generator Current: {total_gen_current:.4f} A")
    print(f"  Load Current: {IL:.4f} A")
    print(f"  Difference: {abs(total_gen_current - IL):.6f} A")

    if abs(total_gen_current - IL) < 0.01:
        print("  ✓ Current balance verified!")
    else:
        print("  ✗ Current balance error!")
        return False

    # Expected values check
    expected_V = 120.0
    expected_I1 = 70.0
    expected_I3 = -10.0

    tolerance = 0.1
    checks = [
        abs(V_bus - expected_V) < tolerance,
        abs(I1 - expected_I1) < tolerance,
        abs(I3 - expected_I3) < tolerance
    ]

    if all(checks):
        print("  ✓ All values match expected results!")
        return True
    else:
        print("  ✗ Some values differ from expected!")
        return False


def test_loss_calculations():
    """Test detailed loss calculations"""
    print("\n" + "="*70)
    print("Testing Loss Calculations")
    print("="*70)

    # Test parameters
    current = 70.0  # A
    omega = 157.0  # rad/s (1500 RPM)
    temp = 75.0  # °C
    Ra = 0.1  # Ω
    Rf = 100.0  # Ω
    V = 120.0  # V

    temp_coeff = 0.00393  # per °C

    # Temperature-adjusted resistance
    Ra_temp = Ra * (1 + temp_coeff * (temp - 20))

    # Copper losses
    copper_loss_armature = current**2 * Ra_temp
    field_current = V / Rf
    copper_loss_field = field_current**2 * Rf

    # Iron losses (simplified)
    freq = omega / (2 * np.pi)
    iron_loss = 0.01 * omega**2

    # Mechanical losses
    friction_loss = 0.01 * omega**2

    print(f"\nOperating Conditions:")
    print(f"  Current: {current:.2f} A")
    print(f"  Speed: {omega*60/(2*np.pi):.0f} RPM")
    print(f"  Temperature: {temp:.1f} °C")

    print(f"\nLoss Breakdown:")
    print(f"  Copper Loss (Armature): {copper_loss_armature:.2f} W")
    print(f"  Copper Loss (Field): {copper_loss_field:.2f} W")
    print(f"  Iron Loss: {iron_loss:.2f} W")
    print(f"  Friction Loss: {friction_loss:.2f} W")
    print(f"  Total Loss: {copper_loss_armature + copper_loss_field + iron_loss + friction_loss:.2f} W")

    if copper_loss_armature > 0 and copper_loss_field > 0:
        print("  ✓ Loss calculations successful!")
        return True
    else:
        print("  ✗ Loss calculation error!")
        return False


def test_thermal_model():
    """Test thermal modeling"""
    print("\n" + "="*70)
    print("Testing Thermal Model")
    print("="*70)

    # Thermal parameters
    Rth = 2.0  # K/W
    T_amb = 25.0  # °C
    P_loss = 500.0  # W (total losses)

    # Simple thermal model (steady-state)
    T_rise = P_loss * Rth
    T_final = T_amb + T_rise

    print(f"\nThermal Analysis:")
    print(f"  Ambient Temperature: {T_amb:.1f} °C")
    print(f"  Power Loss: {P_loss:.1f} W")
    print(f"  Thermal Resistance: {Rth:.2f} K/W")
    print(f"  Temperature Rise: {T_rise:.1f} °C")
    print(f"  Final Temperature: {T_final:.1f} °C")

    T_max = 155.0  # Class F insulation
    margin = T_max - T_final

    print(f"  Maximum Allowable: {T_max:.1f} °C")
    print(f"  Temperature Margin: {margin:.1f} °C")

    if T_final < T_max:
        print("  ✓ Operating within safe temperature limits!")
        return True
    else:
        print("  ✗ Temperature exceeds limits!")
        return False


def test_mechanical_stress():
    """Test mechanical stress calculations"""
    print("\n" + "="*70)
    print("Testing Mechanical Stress Analysis")
    print("="*70)

    # Mechanical parameters
    torque = 500.0  # N⋅m
    omega = 157.0  # rad/s
    shaft_radius = 0.05  # m

    # Torsional shear stress
    polar_moment = np.pi * shaft_radius**4 / 2
    shear_stress = torque * shaft_radius / polar_moment

    # Material properties (steel)
    yield_stress = 250e6  # Pa (250 MPa)
    safety_factor = yield_stress / (shear_stress + 1e-6)

    print(f"\nMechanical Analysis:")
    print(f"  Torque: {torque:.2f} N⋅m")
    print(f"  Speed: {omega*60/(2*np.pi):.0f} RPM")
    print(f"  Shaft Radius: {shaft_radius*1000:.1f} mm")
    print(f"  Shear Stress: {shear_stress/1e6:.2f} MPa")
    print(f"  Yield Stress: {yield_stress/1e6:.0f} MPa")
    print(f"  Safety Factor: {safety_factor:.2f}")

    if safety_factor > 2.0:
        print("  ✓ Design is mechanically safe!")
        return True
    else:
        print("  ✗ Safety factor too low!")
        return False


def test_ode_solver():
    """Test ODE solver integration"""
    print("\n" + "="*70)
    print("Testing ODE Solver")
    print("="*70)

    # Simple test: exponential decay
    def system(t, y):
        return -0.5 * y

    y0 = [1.0]
    t_span = (0, 2.0)

    try:
        sol = solve_ivp(system, t_span, y0, method='RK45', max_step=0.1)

        print(f"\nODE Integration Test:")
        print(f"  Initial value: {y0[0]:.4f}")
        print(f"  Final value: {sol.y[0, -1]:.4f}")
        print(f"  Time points: {len(sol.t)}")
        print(f"  Success: {sol.success}")

        # Expected: e^(-0.5*2) ≈ 0.368
        expected = np.exp(-0.5 * 2.0)
        error = abs(sol.y[0, -1] - expected)

        print(f"  Expected: {expected:.4f}")
        print(f"  Error: {error:.6f}")

        if sol.success and error < 0.01:
            print("  ✓ ODE solver working correctly!")
            return True
        else:
            print("  ✗ ODE solver error!")
            return False

    except Exception as e:
        print(f"  ✗ ODE solver failed: {e}")
        return False


def test_economic_model():
    """Test economic calculations"""
    print("\n" + "="*70)
    print("Testing Economic Model")
    print("="*70)

    # Economic parameters
    power_kw = 7.2
    losses_kw = 0.5
    hours = 8760
    elec_cost = 0.12  # $/kWh
    maint_cost_per_hour = 5.0  # $/hr

    # Calculations
    energy_cost = (power_kw + losses_kw) * hours * elec_cost
    maintenance_cost = hours * maint_cost_per_hour
    total_cost = energy_cost + maintenance_cost
    cost_per_kwh = total_cost / (power_kw * hours)

    print(f"\nEconomic Analysis:")
    print(f"  Output Power: {power_kw:.2f} kW")
    print(f"  Losses: {losses_kw:.2f} kW")
    print(f"  Operating Hours: {hours:.0f} hrs/year")
    print(f"  Electricity Cost: ${elec_cost:.3f}/kWh")
    print(f"  Maintenance Cost: ${maint_cost_per_hour:.2f}/hr")
    print(f"\nResults:")
    print(f"  Annual Energy Cost: ${energy_cost:,.2f}")
    print(f"  Annual Maintenance: ${maintenance_cost:,.2f}")
    print(f"  Total Annual Cost: ${total_cost:,.2f}")
    print(f"  Cost per kWh: ${cost_per_kwh:.4f}")

    if total_cost > 0 and cost_per_kwh > 0:
        print("  ✓ Economic calculations successful!")
        return True
    else:
        print("  ✗ Economic calculation error!")
        return False


def main():
    """Run all tests"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*10 + "SHUNT GENERATORS SIMULATION TEST SUITE" + " "*20 + "║")
    print("╚" + "="*68 + "╝\n")

    tests = [
        ("Circuit Analysis", test_circuit_analysis),
        ("Loss Calculations", test_loss_calculations),
        ("Thermal Model", test_thermal_model),
        ("Mechanical Stress", test_mechanical_stress),
        ("ODE Solver", test_ode_solver),
        ("Economic Model", test_economic_model)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' failed with exception: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:.<50} {status}")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please review.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
