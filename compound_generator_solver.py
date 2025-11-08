#!/usr/bin/env python3
"""
Compound Generator Problem Solver
Solves the specific problem without requiring GUI libraries
Can run in any Python 3 environment
"""

import math


def solve_compound_generator_problem():
    """
    Solve the compound generator problem:
    - 110V compound generator
    - Ra = 0.06 Ω, Rsh = 25 Ω, Rse = 0.04 Ω
    - Load: 200 lamps × 55W @ 110V

    Calculate total EMF and armature current for:
    (i) Long shunt configuration
    (ii) Short shunt configuration
    """

    print("=" * 80)
    print("COMPOUND GENERATOR PROBLEM SOLUTION")
    print("=" * 80)

    # Given data
    V_terminal = 110  # Terminal voltage (V)
    Ra = 0.06  # Armature resistance (Ω)
    Rsh = 25  # Shunt field resistance (Ω)
    Rse = 0.04  # Series field resistance (Ω)

    # Load calculation
    n_lamps = 200
    P_lamp = 55  # W
    V_lamp = 110  # V

    P_load = n_lamps * P_lamp  # Total load power
    I_load = P_load / V_terminal  # Load current

    print(f"\nGiven Data:")
    print(f"  Terminal Voltage: {V_terminal} V")
    print(f"  Armature Resistance (Ra): {Ra} Ω")
    print(f"  Shunt Field Resistance (Rsh): {Rsh} Ω")
    print(f"  Series Field Resistance (Rse): {Rse} Ω")
    print(f"\nLoad Calculation:")
    print(f"  Number of lamps: {n_lamps}")
    print(f"  Power per lamp: {P_lamp} W")
    print(f"  Total load power: {P_load} W")
    print(f"  Load Current (IL): {I_load:.2f} A")

    # (i) LONG SHUNT CONNECTION
    print("\n" + "=" * 80)
    print("(i) LONG SHUNT CONNECTION")
    print("=" * 80)

    print("\nCircuit Configuration:")
    print("  In long shunt, the shunt field is connected across the armature terminals")
    print("  (i.e., parallel to both armature and series field)")
    print("\nCircuit Equation:")
    print("  Terminal voltage (Vt) appears across the shunt field")
    print("  EMF = Vt + Ise × Rse + Ia × Ra")
    print("\nCurrent Relations:")
    print("  Ia = Ise (armature and series field carry same current)")
    print("  Ise = IL + Ish (series current = load + shunt currents)")

    # Shunt field current
    I_sh_long = V_terminal / Rsh
    print(f"\nStep 1: Calculate shunt field current")
    print(f"  Ish = Vt / Rsh")
    print(f"  Ish = {V_terminal} / {Rsh}")
    print(f"  Ish = {I_sh_long:.3f} A")

    # Series field current
    I_se_long = I_load + I_sh_long
    print(f"\nStep 2: Calculate series field current")
    print(f"  Ise = IL + Ish")
    print(f"  Ise = {I_load:.2f} + {I_sh_long:.3f}")
    print(f"  Ise = {I_se_long:.3f} A")

    # Armature current (same as series current in long shunt)
    I_a_long = I_se_long
    print(f"\nStep 3: Armature current")
    print(f"  Ia = Ise = {I_a_long:.3f} A")

    # Voltage drops
    V_drop_se_long = I_se_long * Rse
    V_drop_a_long = I_a_long * Ra

    print(f"\nStep 4: Calculate voltage drops")
    print(f"  Voltage drop across series field:")
    print(f"    V_se = Ise × Rse = {I_se_long:.3f} × {Rse} = {V_drop_se_long:.4f} V")
    print(f"  Voltage drop across armature:")
    print(f"    V_a = Ia × Ra = {I_a_long:.3f} × {Ra} = {V_drop_a_long:.4f} V")

    # Total EMF
    E_long = V_terminal + V_drop_se_long + V_drop_a_long

    print(f"\nStep 5: Calculate total EMF")
    print(f"  E = Vt + V_se + V_a")
    print(f"  E = {V_terminal} + {V_drop_se_long:.4f} + {V_drop_a_long:.4f}")
    print(f"  E = {E_long:.4f} V")

    print(f"\n{'LONG SHUNT RESULTS':^80}")
    print(f"{'=' * 80}")
    print(f"  Total EMF (E):           {E_long:.4f} V")
    print(f"  Armature Current (Ia):   {I_a_long:.3f} A")
    print(f"  Shunt Current (Ish):     {I_sh_long:.3f} A")
    print(f"  Series Current (Ise):    {I_se_long:.3f} A")
    print(f"  Load Current (IL):       {I_load:.2f} A")
    print(f"{'=' * 80}")

    # (ii) SHORT SHUNT CONNECTION
    print("\n" + "=" * 80)
    print("(ii) SHORT SHUNT CONNECTION")
    print("=" * 80)

    print("\nCircuit Configuration:")
    print("  In short shunt, the shunt field is connected across armature only")
    print("  (i.e., parallel to armature, but not to series field)")
    print("\nCircuit Equation:")
    print("  Va = Vt + IL × Rse (voltage across armature)")
    print("  EMF = Va + Ia × Ra")
    print("\nCurrent Relations:")
    print("  Ise = IL (series field carries only load current)")
    print("  Ia = IL + Ish (armature current = load + shunt currents)")

    # Voltage across series field
    V_drop_se_short = I_load * Rse
    print(f"\nStep 1: Calculate voltage drop across series field")
    print(f"  V_se = IL × Rse")
    print(f"  V_se = {I_load:.2f} × {Rse}")
    print(f"  V_se = {V_drop_se_short:.4f} V")

    # Voltage across shunt field (across armature)
    V_sh_short = V_terminal + V_drop_se_short
    print(f"\nStep 2: Calculate voltage across shunt field (and armature)")
    print(f"  Va = Vt + V_se")
    print(f"  Va = {V_terminal} + {V_drop_se_short:.4f}")
    print(f"  Va = {V_sh_short:.4f} V")

    # Shunt field current
    I_sh_short = V_sh_short / Rsh
    print(f"\nStep 3: Calculate shunt field current")
    print(f"  Ish = Va / Rsh")
    print(f"  Ish = {V_sh_short:.4f} / {Rsh}")
    print(f"  Ish = {I_sh_short:.3f} A")

    # Series field current (equals load current in short shunt)
    I_se_short = I_load
    print(f"\nStep 4: Series field current")
    print(f"  Ise = IL = {I_se_short:.2f} A")

    # Armature current
    I_a_short = I_load + I_sh_short
    print(f"\nStep 5: Calculate armature current")
    print(f"  Ia = IL + Ish")
    print(f"  Ia = {I_load:.2f} + {I_sh_short:.3f}")
    print(f"  Ia = {I_a_short:.3f} A")

    # Voltage drop across armature
    V_drop_a_short = I_a_short * Ra
    print(f"\nStep 6: Calculate voltage drop across armature resistance")
    print(f"  V_a_drop = Ia × Ra")
    print(f"  V_a_drop = {I_a_short:.3f} × {Ra}")
    print(f"  V_a_drop = {V_drop_a_short:.4f} V")

    # Total EMF
    E_short = V_terminal + V_drop_se_short + V_drop_a_short

    print(f"\nStep 7: Calculate total EMF")
    print(f"  E = Vt + V_se + V_a_drop")
    print(f"  E = {V_terminal} + {V_drop_se_short:.4f} + {V_drop_a_short:.4f}")
    print(f"  E = {E_short:.4f} V")

    print(f"\n{'SHORT SHUNT RESULTS':^80}")
    print(f"{'=' * 80}")
    print(f"  Total EMF (E):           {E_short:.4f} V")
    print(f"  Armature Current (Ia):   {I_a_short:.3f} A")
    print(f"  Shunt Current (Ish):     {I_sh_short:.3f} A")
    print(f"  Series Current (Ise):    {I_se_short:.2f} A")
    print(f"  Load Current (IL):       {I_load:.2f} A")
    print(f"{'=' * 80}")

    # Comparison
    print("\n" + "=" * 80)
    print("COMPARISON: LONG SHUNT vs SHORT SHUNT")
    print("=" * 80)
    print(f"\n{'Parameter':<30} {'Long Shunt':<20} {'Short Shunt':<20} {'Difference':<20}")
    print(f"{'-' * 90}")
    print(f"{'Total EMF (V)':<30} {E_long:<20.4f} {E_short:<20.4f} {abs(E_long - E_short):<20.4f}")
    print(f"{'Armature Current (A)':<30} {I_a_long:<20.3f} {I_a_short:<20.3f} {abs(I_a_long - I_a_short):<20.3f}")
    print(f"{'Shunt Current (A)':<30} {I_sh_long:<20.3f} {I_sh_short:<20.3f} {abs(I_sh_long - I_sh_short):<20.3f}")
    print(f"{'Series Current (A)':<30} {I_se_long:<20.3f} {I_se_short:<20.3f} {abs(I_se_long - I_se_short):<20.3f}")
    print(f"{'Load Current (A)':<30} {I_load:<20.2f} {I_load:<20.2f} {0.0:<20.2f}")
    print(f"{'-' * 90}")

    # Additional analysis
    print("\n" + "=" * 80)
    print("POWER AND EFFICIENCY ANALYSIS")
    print("=" * 80)

    # Long shunt analysis
    print(f"\nLONG SHUNT:")
    P_out_long = V_terminal * I_load
    P_gen_long = E_long * I_a_long
    P_copper_arm_long = I_a_long**2 * Ra
    P_copper_shunt_long = I_sh_long**2 * Rsh
    P_copper_series_long = I_se_long**2 * Rse
    P_copper_total_long = P_copper_arm_long + P_copper_shunt_long + P_copper_series_long
    efficiency_long = (P_out_long / P_gen_long) * 100 if P_gen_long > 0 else 0

    print(f"  Output Power:              {P_out_long:.2f} W")
    print(f"  Generated Power:           {P_gen_long:.2f} W")
    print(f"  Copper Loss (Armature):    {P_copper_arm_long:.2f} W")
    print(f"  Copper Loss (Shunt):       {P_copper_shunt_long:.2f} W")
    print(f"  Copper Loss (Series):      {P_copper_series_long:.2f} W")
    print(f"  Total Copper Loss:         {P_copper_total_long:.2f} W")
    print(f"  Efficiency:                {efficiency_long:.2f}%")

    # Short shunt analysis
    print(f"\nSHORT SHUNT:")
    P_out_short = V_terminal * I_load
    P_gen_short = E_short * I_a_short
    P_copper_arm_short = I_a_short**2 * Ra
    P_copper_shunt_short = I_sh_short**2 * Rsh
    P_copper_series_short = I_se_short**2 * Rse
    P_copper_total_short = P_copper_arm_short + P_copper_shunt_short + P_copper_series_short
    efficiency_short = (P_out_short / P_gen_short) * 100 if P_gen_short > 0 else 0

    print(f"  Output Power:              {P_out_short:.2f} W")
    print(f"  Generated Power:           {P_gen_short:.2f} W")
    print(f"  Copper Loss (Armature):    {P_copper_arm_short:.2f} W")
    print(f"  Copper Loss (Shunt):       {P_copper_shunt_short:.2f} W")
    print(f"  Copper Loss (Series):      {P_copper_series_short:.2f} W")
    print(f"  Total Copper Loss:         {P_copper_total_short:.2f} W")
    print(f"  Efficiency:                {efficiency_short:.2f}%")

    print("\n" + "=" * 80)
    print("OBSERVATIONS")
    print("=" * 80)
    print("""
1. The EMF values are very close between long and short shunt configurations.

2. Long shunt has slightly higher armature current because the shunt field
   current adds to the series field current.

3. Short shunt has slightly higher shunt current because it experiences
   higher voltage (Vt + IL×Rse).

4. In long shunt, series field carries total generator current (IL + Ish).
   In short shunt, series field carries only load current (IL).

5. Both configurations produce nearly identical output power and efficiency
   for this particular set of parameters.

6. The choice between long and short shunt depends on:
   - Regulation requirements
   - Load characteristics
   - Installation convenience
   - Cost considerations

7. Total copper losses are similar in both configurations, with long shunt
   having slightly higher losses due to higher series field current.
    """)

    print("=" * 80)
    print("END OF ANALYSIS")
    print("=" * 80)

    return {
        'long_shunt': {
            'EMF': E_long,
            'Ia': I_a_long,
            'Ish': I_sh_long,
            'Ise': I_se_long,
            'IL': I_load,
            'P_out': P_out_long,
            'P_gen': P_gen_long,
            'efficiency': efficiency_long
        },
        'short_shunt': {
            'EMF': E_short,
            'Ia': I_a_short,
            'Ish': I_sh_short,
            'Ise': I_se_short,
            'IL': I_load,
            'P_out': P_out_short,
            'P_gen': P_gen_short,
            'efficiency': efficiency_short
        }
    }


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 15 + "COMPOUND GENERATOR PROBLEM SOLVER" + " " * 30 + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  Problem: Calculate EMF and armature current for a 110V compound generator" + " " * 2 + "║")
    print("║" + "  with load of 200 lamps × 55W each, in both long and short shunt configs" + " " * 3 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")

    results = solve_compound_generator_problem()

    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 30 + "SOLUTION COMPLETE" + " " * 31 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")
