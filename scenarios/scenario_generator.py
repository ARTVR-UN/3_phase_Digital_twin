"""
LinkedIn Post Template Generator
=================================

This script generates different scenarios and analyses that are perfect
for LinkedIn posts. Use these to showcase different aspects of the project.

Each scenario emphasizes a different engineering challenge.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add core to path
import sys
core_path = Path(__file__).parent.absolute() / "core"
sys.path.insert(0, str(core_path))

from physics_engine import ThreePhaseRectifier, AlternatorParams
from filter_module import CapacitorFilter


def scenario_1_cold_start():
    """
    Scenario 1: Cold Engine Start (High Inrush Current)
    
    Shows how the alternator struggles to maintain voltage during
    high-current engine start. Perfect for automotive-focused LinkedIn post.
    """
    print("\n" + "="*70)
    print("SCENARIO 1: Cold Engine Start (Inrush Current Analysis)")
    print("="*70)
    
    t = np.linspace(0, 0.04, 2000)
    
    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle('Cold Start Scenario: How Alternator Voltage Collapses\nUnder High Current Demand', 
                 fontsize=14, fontweight='bold')
    
    currents = [5, 10, 15, 20]
    colors = ['green', 'orange', 'red', 'darkred']
    
    for idx, (I_load, color) in enumerate(zip(currents, colors)):
        params = AlternatorParams(load_current=I_load)
        rect = ThreePhaseRectifier(params)
        
        Va, Vb, Vc = rect.generate_three_phase_ac(t)
        V_rect = rect.rectify(Va, Vb, Vc)
        
        u_deg, v_sag = rect.calculate_commutation_angle()
        v_dc = rect.get_actual_dc_voltage()
        
        # Plot rectified voltage
        row, col = divmod(idx, 2)
        ax = axes[row, col]
        
        ax.plot(t*1000, V_rect, color=color, linewidth=2.5)
        ax.fill_between(t*1000, V_rect, alpha=0.2, color=color)
        ax.axhline(y=13.5, color='r', linestyle='--', linewidth=1.5, 
                  label='ECU Min Spec')
        ax.set_title(f'{I_load}A Load Current\nAvg DC: {v_dc:.2f}V | Sag: {v_sag:.2f}V', 
                    fontsize=11, fontweight='bold', color=color)
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('Voltage (V)')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)
        ax.set_ylim([10, 25])
        
        print(f"  {I_load}A load: DC voltage = {v_dc:.2f}V (sag = {v_sag:.2f}V, µ = {u_deg:.1f}°)")
    
    plt.tight_layout()
    current_dir = Path(__file__).parent.absolute()
    plt.savefig(current_dir / 'scenario_1_cold_start.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ Saved: scenario_1_cold_start.png")
    return fig


def scenario_2_sustained_load():
    """
    Scenario 2: Sustained Heavy Load (AC Compressor Running)
    
    Shows steady-state operation under continuous heavy load.
    Demonstrates thermal stability concerns.
    """
    print("\n" + "="*70)
    print("SCENARIO 2: Sustained Heavy Load (AC Compressor Analysis)")
    print("="*70)
    
    t = np.linspace(0, 0.1, 5000)  # Longer time window
    
    params = AlternatorParams(load_current=18)  # High sustained load
    rect = ThreePhaseRectifier(params)
    filt = CapacitorFilter()
    
    Va, Vb, Vc = rect.generate_three_phase_ac(t)
    V_rect = rect.rectify(Va, Vb, Vc)
    dt = t[1] - t[0]
    V_filt, I_cap = filt.apply_filter(V_rect, dt)
    
    u_deg, v_sag = rect.calculate_commutation_angle()
    v_dc = rect.get_actual_dc_voltage()
    v_avg, v_ripple, ripple_pct = filt.calculate_ripple(V_filt)
    p_esr, p_load, p_total = filt.power_dissipation(I_cap, V_filt)
    
    # Create figure
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    fig.suptitle('Sustained Load Analysis: AC Compressor at 18A\n(Thermal Stability & Load Regulation)', 
                 fontsize=14, fontweight='bold')
    
    # Plot 1: Raw rectified voltage (first 20ms for detail)
    ax1 = fig.add_subplot(gs[0, 0])
    idx_end = np.where(t <= 0.02)[0][-1]
    ax1.plot(t[:idx_end]*1000, V_rect[:idx_end], 'b-', linewidth=1.5)
    ax1.set_title('6-Pulse Rectified Output (Detail)', fontweight='bold')
    ax1.set_ylabel('Voltage (V)')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Filtered voltage over full time window
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(t*1000, V_filt, 'darkgreen', linewidth=2)
    ax2.fill_between(t*1000, V_filt, alpha=0.2, color='darkgreen')
    ax2.set_title('Filtered DC Output (Full Duration)', fontweight='bold')
    ax2.set_ylabel('Voltage (V)')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Capacitor current
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(t*1000, I_cap*1000, 'r-', linewidth=1.5, alpha=0.7)
    ax3.fill_between(t*1000, I_cap*1000, alpha=0.2, color='red')
    ax3.set_title('Capacitor Discharge Current', fontweight='bold')
    ax3.set_ylabel('Current (mA)')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Instantaneous power
    P_inst = V_filt * I_cap
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(t*1000, P_inst*1000, 'orange', linewidth=1, alpha=0.7)
    ax4.fill_between(t*1000, P_inst*1000, alpha=0.2, color='orange')
    ax4.axhline(y=p_total*1000, color='r', linestyle='--', linewidth=2,
               label=f'Avg: {p_total*1000:.1f}mW')
    ax4.set_title('Instantaneous Power Dissipation (Heat)', fontweight='bold')
    ax4.set_ylabel('Power (mW)')
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)
    
    # Plot 5: Energy over time
    energy = np.cumsum(P_inst) * (t[1] - t[0])
    ax5 = fig.add_subplot(gs[2, :])
    ax5.plot(t*1000, energy/1000, 'purple', linewidth=2)
    ax5.fill_between(t*1000, energy/1000, alpha=0.2, color='purple')
    ax5.set_title('Cumulative Energy Dissipated (Heat Generation)', fontweight='bold')
    ax5.set_xlabel('Time (ms)')
    ax5.set_ylabel('Energy (mJ)')
    ax5.grid(True, alpha=0.3)
    
    # Add text summary
    summary_text = f"""
PERFORMANCE METRICS @ 18A Load:
  • Commutation angle: {u_deg:.1f}°
  • Voltage sag: {v_sag:.2f}V
  • Average DC voltage: {v_dc:.2f}V
  • Filtered ripple: {ripple_pct:.2f}%
  • Total power dissipation: {p_total*1000:.1f}mW
  • Total energy (100ms): {energy[-1]/1000:.2f}mJ
  
This energy becomes heat on the ECU board!
    """
    ax5.text(0.02, 0.95, summary_text, transform=ax5.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
            family='monospace')
    
    plt.tight_layout()
    current_dir = Path(__file__).parent.absolute()
    plt.savefig(current_dir / 'scenario_2_sustained_load.png', dpi=300, bbox_inches='tight')
    print(f"\n  Load current: 18A (AC compressor maximum)")
    print(f"  Average DC voltage: {v_dc:.2f}V")
    print(f"  Ripple (peak-to-peak): {v_ripple:.3f}V ({ripple_pct:.2f}%)")
    print(f"  Total thermal dissipation: {p_total*1000:.1f}mW")
    print(f"  Energy over 100ms: {energy[-1]/1000:.2f}mJ")
    print(f"\n  ✓ Saved: scenario_2_sustained_load.png")
    return fig


def scenario_3_efficiency_analysis():
    """
    Scenario 3: System Efficiency vs Load
    
    Shows how system efficiency changes with current draw.
    Demonstrates the trade-off between load regulation and losses.
    """
    print("\n" + "="*70)
    print("SCENARIO 3: System Efficiency Analysis (Load vs Voltage)")
    print("="*70)
    
    loads = np.linspace(1, 25, 25)
    metrics = {
        'load': [],
        'commutation_angle': [],
        'voltage_sag': [],
        'dc_voltage': [],
        'ripple': [],
    }
    
    for I in loads:
        params = AlternatorParams(load_current=I)
        rect = ThreePhaseRectifier(params)
        filt = CapacitorFilter()
        
        # Quick calculation
        u_deg, v_sag = rect.calculate_commutation_angle()
        v_dc = rect.get_actual_dc_voltage()
        
        # Filter characteristics (simplified)
        t = np.linspace(0, 0.04, 1000)
        Va, Vb, Vc = rect.generate_three_phase_ac(t)
        V_rect = rect.rectify(Va, Vb, Vc)
        dt = t[1] - t[0]
        V_filt, _ = filt.apply_filter(V_rect, dt)
        v_avg, v_ripple, _ = filt.calculate_ripple(V_filt)
        
        metrics['load'].append(I)
        metrics['commutation_angle'].append(u_deg)
        metrics['voltage_sag'].append(v_sag)
        metrics['dc_voltage'].append(v_dc)
        metrics['ripple'].append(v_ripple)
    
    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('System Efficiency: How Performance Degrades Under Load', 
                 fontsize=14, fontweight='bold')
    
    # Plot 1: Commutation angle
    ax = axes[0, 0]
    ax.plot(metrics['load'], metrics['commutation_angle'], 'bo-', linewidth=2, markersize=6)
    ax.fill_between(metrics['load'], metrics['commutation_angle'], alpha=0.2, color='blue')
    ax.set_xlabel('Load Current (A)', fontweight='bold')
    ax.set_ylabel('Commutation Angle µ (°)', fontweight='bold')
    ax.set_title('Commutation Overlap Increases\nwith Current Demand', fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Voltage sag
    ax = axes[0, 1]
    ax.plot(metrics['load'], metrics['voltage_sag'], 'ro-', linewidth=2.5, markersize=6)
    ax.fill_between(metrics['load'], metrics['voltage_sag'], alpha=0.2, color='red')
    ax.set_xlabel('Load Current (A)', fontweight='bold')
    ax.set_ylabel('Voltage Sag (V)', fontweight='bold')
    ax.set_title('DC Voltage Drop Due to\nCommutation (Physics!)', fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Plot 3: DC voltage regulation
    ax = axes[1, 0]
    ax.plot(metrics['load'], metrics['dc_voltage'], 'go-', linewidth=2.5, markersize=6)
    ax.axhline(y=13.5, color='orange', linestyle='--', linewidth=2, label='ECU Min (13.5V)')
    ax.fill_between(metrics['load'], metrics['dc_voltage'], alpha=0.2, color='green')
    ax.set_xlabel('Load Current (A)', fontweight='bold')
    ax.set_ylabel('Average DC Voltage (V)', fontweight='bold')
    ax.set_title('Load Regulation Performance\n(Key ECU Specification)', fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([11, 20])
    
    # Plot 4: Ripple
    ax = axes[1, 1]
    ax.plot(metrics['load'], metrics['ripple'], 'mo-', linewidth=2.5, markersize=6)
    ax.fill_between(metrics['load'], metrics['ripple'], alpha=0.2, color='magenta')
    ax.set_xlabel('Load Current (A)', fontweight='bold')
    ax.set_ylabel('Residual Ripple (V)', fontweight='bold')
    ax.set_title('Capacitor Filter Effectiveness\n(Reduces Noise)', fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    current_dir = Path(__file__).parent.absolute()
    plt.savefig(current_dir / 'scenario_3_efficiency.png', dpi=300, bbox_inches='tight')
    
    print(f"\n  At 5A load:  DC voltage = {metrics['dc_voltage'][4]:.2f}V")
    print(f"  At 10A load: DC voltage = {metrics['dc_voltage'][9]:.2f}V")
    print(f"  At 20A load: DC voltage = {metrics['dc_voltage'][19]:.2f}V")
    print(f"  At 25A load: DC voltage = {metrics['dc_voltage'][-1]:.2f}V")
    print(f"\n  ✓ Saved: scenario_3_efficiency.png")
    return fig


def main():
    """Generate all scenario analyses."""
    print("\n" + "="*80)
    print("LINKEDIN PORTFOLIO SCENARIO GENERATOR")
    print("="*80)
    print("\nGenerating detailed scenario analyses for LinkedIn posts...")
    
    scenario_1_cold_start()
    scenario_2_sustained_load()
    scenario_3_efficiency_analysis()
    
    print("\n" + "="*80)
    print("ALL SCENARIOS COMPLETE")
    print("="*80)
    print("""
Generated files:
  • scenario_1_cold_start.png - High inrush current during engine start
  • scenario_2_sustained_load.png - AC compressor running continuously
  • scenario_3_efficiency.png - Full load range analysis

LinkedIn Post Ideas:
  1. "Why Your Car's Lights Dim When You Turn On the AC"
     Use scenario_1_cold_start.png to show voltage collapse
  
  2. "The Physics Behind Automotive Power Systems"
     Use scenario_2_sustained_load.png to show thermal analysis
  
  3. "System Efficiency Across Operating Range"
     Use scenario_3_efficiency.png to demonstrate engineering trade-offs

All visualizations are 300 DPI, ready for LinkedIn publishing! 📊
    """)


if __name__ == "__main__":
    main()
