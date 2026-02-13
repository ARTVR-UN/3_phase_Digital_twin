"""
Physics Engine for 3-Phase Alternator Rectification System
=========================================================

This module models the real-world behavior of a 6-diode bridge rectifier
used in automotive alternators (e.g., Mazda MX-5). It accounts for:
- 3-phase AC generation from the alternator
- 6-pulse rectification (Max Selector logic)
- Commutation effects (voltage sag due to source inductance)
- Load-dependent ripple characteristics

Author: Digital Twin Project
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class AlternatorParams:
    """Physical parameters of the alternator and load."""
    frequency: float = 50          # Hz (electrical frequency)
    v_peak: float = 14.5           # Volts (nominal AC peak from alternator)
    source_inductance: float = 0.001  # Henry (Leakage inductance Lc)
    load_current: float = 10       # Amps (typical automotive load)
    diode_forward_drop: float = 0.7  # Volts (typical Si diode)


class ThreePhaseRectifier:
    """
    Simulates a 6-diode bridge rectifier for 3-phase AC input.
    
    The "Max Selector" logic:
        V_out = MAX(|Va - Vb|, |Vb - Vc|, |Vc - Va|)
    
    This represents the rectifier continuously selecting the highest
    voltage pair available across the three phases.
    """
    
    def __init__(self, params: AlternatorParams = None):
        """Initialize with alternator parameters."""
        self.params = params or AlternatorParams()
        self.omega = 2 * np.pi * self.params.frequency
        
    def generate_three_phase_ac(self, t):
        """
        Generate 3-phase AC source with 120-degree phase separation.
        
        Args:
            t: Time array (numpy array in seconds)
            
        Returns:
            Va, Vb, Vc: Phase voltages (numpy arrays)
        """
        Va = self.params.v_peak * np.sin(self.omega * t)
        Vb = self.params.v_peak * np.sin(self.omega * t - 2 * np.pi / 3)
        Vc = self.params.v_peak * np.sin(self.omega * t - 4 * np.pi / 3)
        return Va, Vb, Vc
    
    def rectify(self, Va, Vb, Vc):
        """
        Perform 6-pulse rectification using the Max Selector logic.
        
        The 6-diode bridge topology outputs the highest line-to-line
        voltage at any instant, producing 6 pulses per AC cycle.
        
        Args:
            Va, Vb, Vc: Phase voltages
            
        Returns:
            V_rectified: Rectified output (numpy array)
        """
        V_rectified = np.maximum.reduce([
            np.abs(Va - Vb),
            np.abs(Vb - Vc),
            np.abs(Vc - Va)
        ])
        
        # Account for diode forward voltage drop
        V_rectified = np.maximum(0, V_rectified - 2 * self.params.diode_forward_drop)
        
        return V_rectified
    
    def calculate_commutation_angle(self):
        """
        Calculate commutation delay angle (overlap angle) µ.
        
        This represents the voltage sag caused by source inductance during
        diode commutation. As load current increases, µ increases, and the
        average DC voltage decreases.
        
        Formula:
            cos(µ) = 1 - (2 * ω * Lc * Id) / (√3 * V_peak)
        
        Returns:
            u_deg: Commutation angle in degrees
            voltage_sag: Expected DC voltage reduction in volts
        """
        numerator = 2 * self.omega * self.params.source_inductance * self.params.load_current
        denominator = np.sqrt(3) * self.params.v_peak
        
        cos_u = 1 - (numerator / denominator)
        cos_u = np.clip(cos_u, -1, 1)  # Ensure valid range for arccos
        
        u_rad = np.arccos(cos_u)
        u_deg = np.degrees(u_rad)
        
        # Voltage sag ≈ (3 * V_peak / π) * (cos(µ) - 1)
        v_sag = (3 * self.params.v_peak / np.pi) * (cos_u - 1)
        
        return u_deg, abs(v_sag)
    
    def get_ideal_dc_voltage(self):
        """
        Calculate the ideal average DC output voltage.
        
        For a 6-pulse rectifier:
            V_dc_ideal = (3 * √2 / π) * V_ac_peak ≈ 1.35 * V_ac_peak
        
        Returns:
            V_dc: Average DC voltage (volts)
        """
        return (3 * np.sqrt(2) / np.pi) * self.params.v_peak
    
    def get_actual_dc_voltage(self):
        """
        Calculate actual DC voltage accounting for commutation sag.
        
        Returns:
            V_dc_actual: Average DC voltage with load effects (volts)
        """
        V_dc_ideal = self.get_ideal_dc_voltage()
        u_deg, v_sag = self.calculate_commutation_angle()
        return V_dc_ideal - v_sag


def main():
    """Demo: Show 3-phase rectification and commutation effects."""
    
    # Create alternator model
    alt = ThreePhaseRectifier()
    
    # Time array: 2 cycles at 50 Hz = 0.04 seconds
    t = np.linspace(0, 0.04, 2000)
    
    # Generate phases
    Va, Vb, Vc = alt.generate_three_phase_ac(t)
    
    # Rectify
    V_rectified = alt.rectify(Va, Vb, Vc)
    
    # Calculate commutation effects
    u_deg, v_sag = alt.calculate_commutation_angle()
    v_dc_ideal = alt.get_ideal_dc_voltage()
    v_dc_actual = alt.get_actual_dc_voltage()
    
    # Print analysis
    print("=" * 60)
    print("3-PHASE RECTIFIER ANALYSIS")
    print("=" * 60)
    print(f"AC Peak Voltage:        {alt.params.v_peak:.2f} V")
    print(f"Load Current:           {alt.params.load_current:.2f} A")
    print(f"Source Inductance:      {alt.params.source_inductance*1000:.2f} mH")
    print(f"\nCommutation Angle (µ):  {u_deg:.2f}°")
    print(f"Voltage Sag:            {v_sag:.3f} V")
    print(f"\nIdeal DC Voltage:       {v_dc_ideal:.2f} V")
    print(f"Actual DC Voltage:      {v_dc_actual:.2f} V")
    print(f"Load Regulation Loss:   {(1 - v_dc_actual/v_dc_ideal)*100:.2f}%")
    print("=" * 60)
    
    return t, Va, Vb, Vc, V_rectified


if __name__ == "__main__":
    main()