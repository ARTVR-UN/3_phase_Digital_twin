"""
Main Integration Script
======================

This script demonstrates the complete digital twin simulation,
integrating physics engine, filtering, and visualization.

Run this to generate all analysis outputs.
"""

import numpy as np
import sys
from pathlib import Path

# Add core module to path
current_dir = Path(__file__).parent.absolute()
core_path = current_dir / "core"
sys.path.insert(0, str(core_path))

from physics_engine import ThreePhaseRectifier, AlternatorParams
from filter_module import CapacitorFilter, FilterParams
from visualization import (plot_rectification_stages, 
                           plot_load_variation_analysis,
                           plot_power_dissipation_heatmap)


def run_complete_simulation():
    """Execute full digital twin simulation with output analysis."""
    
    print("\n" + "="*70)
    print("3-PHASE ALTERNATOR DIGITAL TWIN - COMPLETE SIMULATION")
    print("="*70 + "\n")
    
    # === STAGE 1: Physics Engine ===
    print("[1/4] Initializing Physics Engine...")
    rect = ThreePhaseRectifier()
    
    print(f"      Frequency: {rect.params.frequency} Hz")
    print(f"      AC Peak Voltage: {rect.params.v_peak} V")
    print(f"      Source Inductance: {rect.params.source_inductance*1000:.2f} mH")
    print(f"      Load Current: {rect.params.load_current} A")
    
    # Calculate commutation effects
    u_deg, v_sag = rect.calculate_commutation_angle()
    v_dc_ideal = rect.get_ideal_dc_voltage()
    v_dc_actual = rect.get_actual_dc_voltage()
    
    print(f"\n      Commutation Angle (µ): {u_deg:.2f}°")
    print(f"      Voltage Sag: {v_sag:.3f} V")
    print(f"      Ideal DC Voltage: {v_dc_ideal:.2f} V")
    print(f"      Actual DC Voltage (with load effects): {v_dc_actual:.2f} V")
    
    # === STAGE 2: Generate Waveforms ===
    print("\n[2/4] Generating 3-Phase Waveforms...")
    t = np.linspace(0, 0.04, 2000)  # 2 cycles at 50 Hz
    Va, Vb, Vc = rect.generate_three_phase_ac(t)
    V_rectified = rect.rectify(Va, Vb, Vc)
    
    v_rect_min = np.min(V_rectified[V_rectified > 0])
    v_rect_max = np.max(V_rectified)
    v_rect_ripple = v_rect_max - v_rect_min
    
    print(f"      Generated time array: {len(t)} samples over {t[-1]*1000:.1f} ms")
    print(f"      Rectified output - Min: {v_rect_min:.2f}V, Max: {v_rect_max:.2f}V")
    print(f"      Rectified ripple (peak-to-peak): {v_rect_ripple:.3f} V")
    
    # === STAGE 3: Filtering ===
    print("\n[3/4] Applying Capacitive Filtering...")
    filt = CapacitorFilter()
    dt = t[1] - t[0]
    V_filtered, I_capacitor = filt.apply_filter(V_rectified, dt, simulate_discharge=True)
    
    v_avg, v_ripple_pp, ripple_pct = filt.calculate_ripple(V_filtered)
    p_esr, p_load, p_total = filt.power_dissipation(I_capacitor, V_filtered)
    
    print(f"      Filter Capacitance: {filt.params.capacitance*1e6:.0f} µF")
    print(f"      Load Resistance: {filt.params.load_resistance:.2f} Ω")
    print(f"      Filtered DC voltage: {v_avg:.2f} V")
    print(f"      Residual ripple: {v_ripple_pp:.3f} V ({ripple_pct:.2f}%)")
    print(f"      Power dissipation: {p_total*1000:.2f} mW (ESR: {p_esr*1000:.2f}mW, Load: {p_load*1000:.2f}mW)")
    
    # === STAGE 4: Visualization ===
    print("\n[4/4] Generating Visualizations...")
    
    # Main rectification stages
    fig1 = plot_rectification_stages(t, Va, Vb, Vc, V_rectified, V_filtered)
    fig1.savefig(current_dir / 'rectification_stages.png', dpi=300, bbox_inches='tight')
    print("      ✓ Saved: rectification_stages.png")
    
    # Load variation analysis
    fig2, fig3 = plot_load_variation_analysis([5, 10, 15, 20])
    fig2.savefig(current_dir / 'load_variation_waveforms.png', dpi=300, bbox_inches='tight')
    fig3.savefig(current_dir / 'load_regulation_analysis.png', dpi=300, bbox_inches='tight')
    print("      ✓ Saved: load_variation_waveforms.png")
    print("      ✓ Saved: load_regulation_analysis.png")
    
    # Power dissipation
    fig4 = plot_power_dissipation_heatmap(t, V_filtered, I_capacitor)
    fig4.savefig(current_dir / 'power_dissipation.png', dpi=300, bbox_inches='tight')
    print("      ✓ Saved: power_dissipation.png")
    
    # === Summary Report ===
    print("\n" + "="*70)
    print("SIMULATION SUMMARY")
    print("="*70)
    print(f"""
System Performance Metrics:
  • Commutation effects reduce DC voltage by {v_sag:.3f}V ({(v_sag/v_dc_ideal)*100:.2f}%)
  • Capacitor filter reduces ripple from {v_rect_ripple:.3f}V to {v_ripple_pp:.3f}V
  • Ripple suppression ratio: {(v_rect_ripple/v_ripple_pp):.1f}×
  • Thermal dissipation: {p_total*1000:.2f} mW (suitable for ECU cooling design)

Key Insights for LinkedIn Portfolio:
  ✓ Modeled real-world alternator physics (commutation, leakage inductance)
  ✓ Demonstrated load regulation degradation (higher current → lower voltage)
  ✓ Designed capacitor filter for ECU power stability
  ✓ Calculated thermal footprint for PCB heat dissipation analysis
  
Next Steps:
  → Integrate thermal simulation (2D/3D heat conduction on ECU board)
  → Wrap in ROS 2 node for real-time control (PWM compensation)
  → Add battery voltage droop simulation (cold-start scenarios)
    """)
    print("="*70 + "\n")
    
    return {
        'rect': rect,
        'filt': filt,
        't': t,
        'Va': Va, 'Vb': Vb, 'Vc': Vc,
        'V_rectified': V_rectified,
        'V_filtered': V_filtered,
        'I_capacitor': I_capacitor,
    }


if __name__ == "__main__":
    results = run_complete_simulation()
