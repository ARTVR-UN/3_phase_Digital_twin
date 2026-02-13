"""
Visualization Module for Digital Twin
======================================

Creates publication-quality plots showing:
1. 3-Phase AC source
2. Rectified output with commutation sag
3. Filtered DC output and ripple
4. Load-dependent effects

Perfect for LinkedIn portfolio showcase.

Author: Digital Twin Project
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches


def plot_rectification_stages(t, Va, Vb, Vc, V_rectified, V_filtered, 
                               title_suffix=""):
    """
    Create a comprehensive 3-subplot figure showing all stages of rectification.
    
    Args:
        t: Time array
        Va, Vb, Vc: Phase voltages
        V_rectified: Rectified output (before filtering)
        V_filtered: Filtered output (after capacitor)
        title_suffix: Additional text for title
    """
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle("3-Phase Alternator Rectification System" + title_suffix, 
                 fontsize=14, fontweight='bold')
    
    # --- Subplot 1: 3-Phase AC Source ---
    ax1 = axes[0]
    ax1.plot(t*1000, Va, 'r-', label='Phase A', linewidth=2, alpha=0.8)
    ax1.plot(t*1000, Vb, 'g-', label='Phase B', linewidth=2, alpha=0.8)
    ax1.plot(t*1000, Vc, 'b-', label='Phase C', linewidth=2, alpha=0.8)
    ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3, linewidth=0.5)
    ax1.set_ylabel('Voltage (V)', fontweight='bold')
    ax1.set_title('Stage 1: 3-Phase AC Source from Alternator (120° Phase Shift)', 
                  fontsize=11, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle=':')
    ax1.legend(loc='upper right', fontsize=10)
    ax1.set_ylim([-20, 20])
    
    # --- Subplot 2: Rectified Output (6-pulse ripple) ---
    ax2 = axes[1]
    ax2.plot(t*1000, V_rectified, 'darkblue', linewidth=2.5, label='Rectified Output')
    ax2.fill_between(t*1000, V_rectified, alpha=0.2, color='darkblue')
    ax2.set_ylabel('Voltage (V)', fontweight='bold')
    ax2.set_title('Stage 2: 6-Diode Bridge Rectification (Notice Scalloped Ripple)', 
                  fontsize=11, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle=':')
    ax2.legend(loc='upper right', fontsize=10)
    
    # Annotate ripple characteristics
    v_max = np.max(V_rectified)
    v_min = np.min(V_rectified)
    ripple = v_max - v_min
    ax2.annotate(f'Peak: {v_max:.2f}V', xy=(t[-1]*1000*0.8, v_max), 
                xytext=(t[-1]*1000*0.7, v_max + 1),
                fontsize=9, ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3))
    ax2.annotate(f'Min: {v_min:.2f}V\nRipple: {ripple:.2f}V', 
                xy=(t[-1]*1000*0.8, v_min), 
                xytext=(t[-1]*1000*0.7, v_min - 1.5),
                fontsize=9, ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='orange', alpha=0.3))
    
    # --- Subplot 3: Filtered DC Output ---
    ax3 = axes[2]
    ax3.plot(t*1000, V_rectified, 'lightgray', linewidth=1, label='Rectified (unfiltered)', 
            linestyle='--', alpha=0.7)
    ax3.plot(t*1000, V_filtered, 'darkgreen', linewidth=2.5, label='Filtered (with capacitor)')
    ax3.fill_between(t*1000, V_filtered, alpha=0.2, color='darkgreen')
    ax3.set_xlabel('Time (ms)', fontweight='bold')
    ax3.set_ylabel('Voltage (V)', fontweight='bold')
    ax3.set_title('Stage 3: Capacitor Filtered DC Output (Smooth for ECU)', 
                  fontsize=11, fontweight='bold')
    ax3.grid(True, alpha=0.3, linestyle=':')
    ax3.legend(loc='upper right', fontsize=10)
    
    # Annotate filtering improvement
    v_filtered_avg = np.mean(V_filtered)
    v_filtered_ripple = np.max(V_filtered) - np.min(V_filtered)
    ax3.annotate(f'Avg DC: {v_filtered_avg:.2f}V\nResidual Ripple: {v_filtered_ripple:.3f}V', 
                xy=(t[-1]*1000*0.2, v_filtered_avg), 
                xytext=(t[-1]*1000*0.05, v_filtered_avg + 1),
                fontsize=9, ha='left',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.5),
                arrowprops=dict(arrowstyle='->', color='darkgreen', lw=1.5))
    
    plt.tight_layout()
    return fig


def plot_load_variation_analysis(load_currents=[5, 10, 15, 20]):
    """
    Show how commutation effects vary with load current.
    
    This demonstrates your understanding of how real-world alternators behave
    as the vehicle demands more electrical power.
    
    Args:
        load_currents: Array of load currents to simulate (Amps)
    """
    from physics_engine import ThreePhaseRectifier, AlternatorParams
    
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle('Load Regulation Analysis: Effects of Current Draw on DC Output', 
                 fontsize=14, fontweight='bold')
    
    results = {
        'current': [],
        'commutation_angle': [],
        'voltage_sag': [],
        'avg_dc_voltage': [],
    }
    
    # Simulate for each load current
    t = np.linspace(0, 0.02, 1000)
    
    for idx, I_load in enumerate(load_currents):
        # Update parameters
        params = AlternatorParams(load_current=I_load)
        rect = ThreePhaseRectifier(params)
        
        # Generate signals
        Va, Vb, Vc = rect.generate_three_phase_ac(t)
        V_rect = rect.rectify(Va, Vb, Vc)
        
        # Calculate metrics
        u_deg, v_sag = rect.calculate_commutation_angle()
        v_dc = rect.get_actual_dc_voltage()
        
        # Store results
        results['current'].append(I_load)
        results['commutation_angle'].append(u_deg)
        results['voltage_sag'].append(v_sag)
        results['avg_dc_voltage'].append(v_dc)
        
        # Plot rectified waveform
        row, col = divmod(idx, 2)
        ax = axes[row, col]
        ax.plot(t*1000, V_rect, 'b-', linewidth=2)
        ax.fill_between(t*1000, V_rect, alpha=0.2, color='blue')
        ax.set_title(f'Load Current: {I_load}A | µ = {u_deg:.2f}° | V_sag = {v_sag:.3f}V', 
                    fontweight='bold')
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('Voltage (V)')
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 22])
    
    plt.tight_layout()
    
    # Create analysis figure
    fig2, axes2 = plt.subplots(1, 3, figsize=(14, 4))
    fig2.suptitle('Load Regulation: How System Parameters Degrade with Current', 
                  fontsize=13, fontweight='bold')
    
    # Plot 1: Commutation Angle vs Load
    ax = axes2[0]
    ax.plot(results['current'], results['commutation_angle'], 'ro-', linewidth=2, markersize=8)
    ax.set_xlabel('Load Current (A)', fontweight='bold')
    ax.set_ylabel('Commutation Angle µ (degrees)', fontweight='bold')
    ax.set_title('Commutation Overlap Increases\nwith Load Current', fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.fill_between(results['current'], results['commutation_angle'], alpha=0.2, color='red')
    
    # Plot 2: Voltage Sag vs Load
    ax = axes2[1]
    ax.plot(results['current'], results['voltage_sag'], 'go-', linewidth=2, markersize=8)
    ax.set_xlabel('Load Current (A)', fontweight='bold')
    ax.set_ylabel('Voltage Sag (V)', fontweight='bold')
    ax.set_title('DC Voltage Drops\nas Load Increases', fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.fill_between(results['current'], results['voltage_sag'], alpha=0.2, color='green')
    
    # Plot 3: Actual DC Voltage vs Load
    ax = axes2[2]
    ax.plot(results['current'], results['avg_dc_voltage'], 'mo-', linewidth=2.5, markersize=8)
    ax.axhline(y=13.5, color='r', linestyle='--', linewidth=1.5, label='ECU Min Spec (13.5V)')
    ax.set_xlabel('Load Current (A)', fontweight='bold')
    ax.set_ylabel('Average DC Voltage (V)', fontweight='bold')
    ax.set_title('System Voltage Regulation\n(Key for ECU Stability)', fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)
    ax.fill_between(results['current'], results['avg_dc_voltage'], alpha=0.2, color='magenta')
    
    plt.tight_layout()
    return fig, fig2


def plot_power_dissipation_heatmap(t, V_filtered, I_capacitor, 
                                   time_window=None, title_suffix=""):
    """
    Create a visualization showing power dissipation over time.
    
    This is a precursor to thermal analysis on the ECU PCB.
    
    Args:
        t: Time array
        V_filtered: Filtered voltage
        I_capacitor: Capacitor current
        time_window: Tuple of (t_start, t_end) to zoom into, or None for full view
        title_suffix: Additional title text
    """
    # Calculate power
    P_instantaneous = V_filtered * I_capacitor
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle("Power Dissipation Analysis" + title_suffix, 
                 fontsize=14, fontweight='bold')
    
    # Plot 1: Voltage and Current
    ax1 = axes[0]
    ax1_twin = ax1.twinx()
    
    line1 = ax1.plot(t*1000, V_filtered, 'b-', linewidth=2, label='Filtered Voltage')
    line2 = ax1_twin.plot(t*1000, I_capacitor*1000, 'r-', linewidth=2, label='Capacitor Current')
    
    ax1.set_xlabel('Time (ms)', fontweight='bold')
    ax1.set_ylabel('Voltage (V)', fontweight='bold', color='b')
    ax1_twin.set_ylabel('Current (mA)', fontweight='bold', color='r')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1_twin.tick_params(axis='y', labelcolor='r')
    ax1.grid(True, alpha=0.3)
    ax1.set_title('Voltage and Current Waveforms', fontweight='bold')
    
    # Combined legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper right', fontsize=10)
    
    # Plot 2: Power Dissipation
    ax2 = axes[1]
    ax2.fill_between(t*1000, P_instantaneous*1000, alpha=0.3, color='orange', label='Instantaneous Power')
    ax2.plot(t*1000, P_instantaneous*1000, 'orange', linewidth=2)
    
    P_avg = np.mean(P_instantaneous)
    ax2.axhline(y=P_avg*1000, color='r', linestyle='--', linewidth=2, 
               label=f'Average Power: {P_avg*1000:.2f} mW')
    
    ax2.set_xlabel('Time (ms)', fontweight='bold')
    ax2.set_ylabel('Power (mW)', fontweight='bold')
    ax2.set_title('Power Dissipation (Heat Generation on PCB)', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)
    
    plt.tight_layout()
    return fig


def main():
    """Generate all visualization plots."""
    from physics_engine import ThreePhaseRectifier
    from filter_module import CapacitorFilter
    
    print("Generating visualizations...")
    
    # Generate base signals
    rect = ThreePhaseRectifier()
    t = np.linspace(0, 0.04, 2000)
    Va, Vb, Vc = rect.generate_three_phase_ac(t)
    V_rect = rect.rectify(Va, Vb, Vc)
    
    # Filter
    filt = CapacitorFilter()
    dt = t[1] - t[0]
    V_filt, I_cap = filt.apply_filter(V_rect, dt)
    
    # Generate plots
    fig1 = plot_rectification_stages(t, Va, Vb, Vc, V_rect, V_filt)
    fig1.savefig('rectification_stages.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: rectification_stages.png")
    
    fig2, fig3 = plot_load_variation_analysis([5, 10, 15, 20])
    fig2.savefig('load_variation_waveforms.png', dpi=300, bbox_inches='tight')
    fig3.savefig('load_regulation_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: load_variation_waveforms.png")
    print("✓ Saved: load_regulation_analysis.png")
    
    fig4 = plot_power_dissipation_heatmap(t, V_filt, I_cap)
    fig4.savefig('power_dissipation.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: power_dissipation.png")
    
    print("\nAll visualizations created successfully!")
    print("Ready for you,Mr. OUSSAMA")


if __name__ == "__main__":
    main()
