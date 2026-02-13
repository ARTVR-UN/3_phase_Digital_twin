"""
Filter Module for 3-Phase Rectifier DC Output
==============================================

This module implements realistic power supply filtering:
- Capacitive filtering (smoothing the 6-pulse ripple)
- Load-dependent ripple characteristics
- RC discharge during commutation gaps

The capacitor fills the "scalloped" gaps in the rectified voltage,
reducing ripple and stabilizing the DC bus for automotive ECU loads.

Author: Digital Twin Project
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class FilterParams:
    """Capacitor filter parameters."""
    capacitance: float = 100e-6  # Farads (100 µF typical for automotive)
    esr: float = 0.1             # Equivalent Series Resistance (ohms)
    load_resistance: float = 14.0  # Ohms (output voltage / current: 14V / 1A = 14Ω equivalent)


class CapacitorFilter:
    """Simulates a capacitive filter for the rectified DC output."""
    
    def __init__(self, params: FilterParams = None):
        """Initialize filter with electrical parameters."""
        self.params = params or FilterParams()
    
    def apply_filter(self, v_rectified, dt, simulate_discharge=True):
        """
        Simulate capacitor charging and discharging.
        
        During rectifier output peaks: Capacitor charges to peak voltage.
        During gaps: Capacitor discharges through load resistance.
        
        Args:
            v_rectified: Input rectified voltage array
            dt: Time step (seconds)
            simulate_discharge: If True, model RC discharge; if False, ideal capacitor
            
        Returns:
            v_filtered: Output voltage after capacitive filtering
            i_capacitor: Current flowing into capacitor (for thermal analysis)
        """
        v_filtered = np.zeros_like(v_rectified)
        i_capacitor = np.zeros_like(v_rectified)
        
        v_cap = 0  # Start with discharged capacitor
        tau = self.params.load_resistance * self.params.capacitance  # Time constant RC
        
        for i in range(len(v_rectified)):
            # Diode conducts when rectified voltage exceeds capacitor voltage
            # (ideal diode has zero forward drop for simplification; add 0.7V if needed)
            if v_rectified[i] > v_cap:
                # Charging phase: rectified source rapidly charges capacitor
                # Assuming ideal diode (zero resistance): instant charge to source voltage
                v_cap = v_rectified[i]
                i_capacitor[i] = 0  # Idealized: instantaneous charge
            else:
                # Discharging phase: capacitor discharges through load resistance
                # Exponential decay: V(t) = V0 * exp(-t/tau)
                if simulate_discharge:
                    # Continuous RC discharge
                    v_cap = v_cap * np.exp(-dt / tau)
                    
                    # Capacitor discharge current: i = -C * dV/dt = V/R
                    if v_cap > 0:
                        i_capacitor[i] = v_cap / self.params.load_resistance
                else:
                    # Ideal case: no discharge, capacitor holds voltage perfectly
                    i_capacitor[i] = 0
            
            v_filtered[i] = v_cap
        
        return v_filtered, i_capacitor
    
    def calculate_ripple(self, v_filtered):
        """
        Calculate DC output ripple characteristics.
        
        Returns:
            v_avg: Average DC voltage
            v_ripple_pp: Peak-to-peak ripple voltage
            ripple_percent: Ripple as % of average voltage
        """
        v_avg = np.mean(v_filtered)
        v_ripple_pp = np.max(v_filtered) - np.min(v_filtered)
        ripple_percent = (v_ripple_pp / v_avg) * 100 if v_avg > 0 else 0
        
        return v_avg, v_ripple_pp, ripple_percent
    
    def power_dissipation(self, i_capacitor, v_filtered):
        """
        Calculate power dissipation in capacitor ESR and load.
        
        This is needed for thermal simulation of the ECU board.
        
        Args:
            i_capacitor: Capacitor current array
            v_filtered: Filtered voltage array
            
        Returns:
            p_esr: Power dissipated in ESR (Watts)
            p_load: Power dissipated in load (Watts)
            p_total: Total power (Watts)
        """
        # ESR dissipation: P = I² * R
        p_esr = np.mean(i_capacitor**2 * self.params.esr)
        
        # Load dissipation: P = V² / R
        p_load = np.mean(v_filtered**2 / self.params.load_resistance)
        
        p_total = p_esr + p_load
        
        return p_esr, p_load, p_total


def main():
    """Demo: Show filtering effect on rectified output."""
    from physics_engine import ThreePhaseRectifier
    
    # Generate rectified voltage
    rect = ThreePhaseRectifier()
    t = np.linspace(0, 0.04, 2000)
    Va, Vb, Vc = rect.generate_three_phase_ac(t)
    V_rectified = rect.rectify(Va, Vb, Vc)
    
    # Apply filtering
    filt = CapacitorFilter()
    dt = t[1] - t[0]
    V_filtered, I_cap = filt.apply_filter(V_rectified, dt, simulate_discharge=True)
    
    # Calculate characteristics
    v_avg, v_ripple_pp, ripple_pct = filt.calculate_ripple(V_filtered)
    p_esr, p_load, p_total = filt.power_dissipation(I_cap, V_filtered)
    
    print("=" * 60)
    print("CAPACITOR FILTER ANALYSIS")
    print("=" * 60)
    print(f"Filter Capacitance:     {filt.params.capacitance*1e6:.0f} µF")
    print(f"Load Resistance:        {filt.params.load_resistance:.2f} Ω")
    print(f"\nFiltered DC Voltage:    {v_avg:.2f} V")
    print(f"Ripple (peak-to-peak):  {v_ripple_pp:.3f} V")
    print(f"Ripple (% of avg):      {ripple_pct:.2f}%")
    print(f"\nPower Dissipation:")
    print(f"  ESR losses:           {p_esr*1000:.2f} mW")
    print(f"  Load dissipation:     {p_load:.2f} W")
    print(f"  Total:                {p_total:.2f} W")
    print("=" * 60)
    
    return t, V_rectified, V_filtered


if __name__ == "__main__":
    main()