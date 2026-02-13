"""
Extension Examples - Building on the Digital Twin
==================================================

This file shows how to extend the digital twin with new features.
Each example is self-contained and can be run independently.

Perfect for showing recruiters you understand how to build modular,
extensible software.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

core_path = Path(__file__).parent.absolute() / "core"
sys.path.insert(0, str(core_path))

from physics_engine import ThreePhaseRectifier, AlternatorParams
from filter_module import CapacitorFilter


# ============================================================================
# EXTENSION 1: Temperature-Dependent Resistance
# ============================================================================

class TemperatureAwareAlternator(ThreePhaseRectifier):
    """
    Extended alternator model that accounts for temperature effects.
    
    Real alternators have temperature-dependent resistance:
    - Cold start: Lower resistance, better voltage regulation
    - Hot operation: Higher resistance, voltage sag increases
    
    This is a great example to show on LinkedIn:
    "Adding temperature-dependent effects to my digital twin..."
    """
    
    def __init__(self, params=None, initial_temp_celsius=25):
        super().__init__(params)
        self.temp_celsius = initial_temp_celsius
        self.temp_coefficient = 0.004  # 0.4% resistance change per °C
        self.base_inductance = self.params.source_inductance
    
    def set_temperature(self, temp_celsius):
        """
        Update temperature and adjust inductance/resistance accordingly.
        
        In reality, both resistance and inductance change with temperature.
        This simplified model shows the concept.
        """
        self.temp_celsius = temp_celsius
        
        # Temperature effect: inductance increases with temperature
        # (due to material properties changing)
        temp_delta = temp_celsius - 25  # Reference temp
        self.params.source_inductance = self.base_inductance * (1 + temp_delta * 0.001)
    
    def get_temperature_adjusted_metrics(self):
        """Get commutation metrics accounting for temperature."""
        u_deg, v_sag = self.calculate_commutation_angle()
        
        # Temperature factor (hotter = worse regulation)
        temp_factor = 1 + (self.temp_celsius - 25) * 0.01
        v_sag_adjusted = v_sag * temp_factor
        
        return u_deg, v_sag_adjusted, self.temp_celsius


def example_1_temperature_effects():
    """Demonstrate temperature-dependent behavior."""
    print("\n" + "="*70)
    print("EXTENSION 1: Temperature-Dependent System Model")
    print("="*70)
    
    # Create temperature-aware alternator
    alt = TemperatureAwareAlternator(initial_temp_celsius=25)
    
    temps = np.linspace(-20, 100, 13)  # -20°C to 100°C
    results = {
        'temp': [],
        'inductance': [],
        'voltage_sag': [],
    }
    
    for temp in temps:
        alt.set_temperature(temp)
        u_deg, v_sag, T = alt.get_temperature_adjusted_metrics()
        results['temp'].append(T)
        results['inductance'].append(alt.params.source_inductance * 1000)  # mH
        results['voltage_sag'].append(v_sag)
        
        print(f"  {T:6.1f}°C: Inductance = {alt.params.source_inductance*1000:.3f}mH, Sag = {v_sag:.3f}V")
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('Temperature Effects on Alternator Performance', fontsize=13, fontweight='bold')
    
    ax = axes[0]
    ax.plot(results['temp'], results['inductance'], 'b-o', linewidth=2, markersize=6)
    ax.set_xlabel('Temperature (°C)', fontweight='bold')
    ax.set_ylabel('Source Inductance (mH)', fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_title('Inductance vs Temperature')
    
    ax = axes[1]
    ax.plot(results['temp'], results['voltage_sag'], 'r-o', linewidth=2, markersize=6)
    ax.set_xlabel('Temperature (°C)', fontweight='bold')
    ax.set_ylabel('Voltage Sag (V)', fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_title('Voltage Regulation vs Temperature\n(Cold start better than hot!)')
    
    plt.tight_layout()
    current_dir = Path(__file__).parent.absolute()
    plt.savefig(current_dir / 'extension_1_temperature.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ Saved: extension_1_temperature.png")


# ============================================================================
# EXTENSION 2: Battery Voltage Droop
# ============================================================================

class SystemWithBattery:
    """
    Model the battery voltage droop effect.
    
    Real batteries have internal resistance:
    - When you draw current, voltage drops
    - V_battery = V_oc - I_load * R_internal
    
    This is why headlights dim when you start the engine!
    """
    
    def __init__(self, battery_voltage_oc=12.6, battery_internal_resistance=0.1):
        self.V_oc = battery_voltage_oc  # Open-circuit voltage
        self.R_int = battery_internal_resistance  # Internal resistance (ohms)
    
    def get_battery_voltage(self, load_current):
        """
        Calculate battery terminal voltage under load.
        
        V_terminal = V_oc - I_load * R_internal
        """
        return self.V_oc - (load_current * self.R_int)
    
    def get_voltage_drop(self, load_current):
        """Get the voltage drop due to internal resistance."""
        return load_current * self.R_int


def example_2_battery_effects():
    """Demonstrate battery droop effect."""
    print("\n" + "="*70)
    print("EXTENSION 2: Battery Voltage Droop (Why Headlights Dim)")
    print("="*70)
    
    battery = SystemWithBattery(battery_voltage_oc=12.6, battery_internal_resistance=0.1)
    
    currents = np.linspace(0, 200, 21)  # 0 to 200A (starter motor range!)
    v_terminal = [battery.get_battery_voltage(I) for I in currents]
    v_drop = [battery.get_voltage_drop(I) for I in currents]
    
    # Print some key points
    print(f"\n  Battery open-circuit voltage: {battery.V_oc:.2f}V")
    print(f"  Battery internal resistance: {battery.R_int:.2f}Ω")
    print(f"\n  At 0A:    V_terminal = {battery.get_battery_voltage(0):.2f}V (no drop)")
    print(f"  At 50A:   V_terminal = {battery.get_battery_voltage(50):.2f}V (drop: {battery.get_voltage_drop(50):.2f}V)")
    print(f"  At 100A:  V_terminal = {battery.get_battery_voltage(100):.2f}V (drop: {battery.get_voltage_drop(100):.2f}V)")
    print(f"  At 200A:  V_terminal = {battery.get_battery_voltage(200):.2f}V (drop: {battery.get_voltage_drop(200):.2f}V)")
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('Battery Voltage Droop: Why Your Lights Dim During Start', fontsize=13, fontweight='bold')
    
    ax = axes[0]
    ax.plot(currents, v_terminal, 'b-', linewidth=3, label='Terminal Voltage')
    ax.axhline(y=battery.V_oc, color='g', linestyle='--', linewidth=2, label='Open-Circuit Voltage')
    ax.fill_between(currents, v_terminal, battery.V_oc, alpha=0.2, color='red')
    ax.set_xlabel('Load Current (A)', fontweight='bold')
    ax.set_ylabel('Voltage (V)', fontweight='bold')
    ax.set_title('Battery Terminal Voltage vs Current')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    ax = axes[1]
    ax.plot(currents, v_drop, 'r-', linewidth=3)
    ax.fill_between(currents, v_drop, alpha=0.2, color='red')
    ax.set_xlabel('Load Current (A)', fontweight='bold')
    ax.set_ylabel('Voltage Drop (V)', fontweight='bold')
    ax.set_title('Voltage Drop Due to Internal Resistance\n(2V drop at starter current!)')
    ax.grid(True, alpha=0.3)
    
    # Add annotation for starter motor
    ax.annotate('Starter Motor\n(~150A)', xy=(150, 15), xytext=(150, 20),
               fontsize=10, ha='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5),
               arrowprops=dict(arrowstyle='->', color='red'))
    
    plt.tight_layout()
    current_dir = Path(__file__).parent.absolute()
    plt.savefig(current_dir / 'extension_2_battery_droop.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ Saved: extension_2_battery_droop.png")


# ============================================================================
# EXTENSION 3: Multi-Load Analysis (Different ECU Loads)
# ============================================================================

class ECULoadProfile:
    """
    Model different ECU power demands.
    
    Real ECUs have varying loads:
    - Idle: ~2A
    - Normal driving: ~5-8A
    - Aggressive (AC + headlights + fuel pump): 15-20A
    
    This profile affects the rectifier ripple and thermal dissipation.
    """
    
    def __init__(self):
        self.profiles = {
            'idle': 2,
            'normal': 6,
            'aggressive': 18,
            'maximum': 25,
        }
    
    def get_all_profiles(self):
        return self.profiles


def example_3_ecu_load_profiles():
    """Demonstrate different ECU operating scenarios."""
    print("\n" + "="*70)
    print("EXTENSION 3: ECU Load Profile Analysis")
    print("="*70)
    
    profile = ECULoadProfile()
    scenarios = profile.get_all_profiles()
    
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle('ECU Operating Modes: Power and Thermal Analysis', fontsize=13, fontweight='bold')
    
    t = np.linspace(0, 0.04, 2000)
    
    for (idx, (name, current)) in enumerate(scenarios.items()):
        params = AlternatorParams(load_current=current)
        rect = ThreePhaseRectifier(params)
        filt = CapacitorFilter()
        
        # Generate waveforms
        Va, Vb, Vc = rect.generate_three_phase_ac(t)
        V_rect = rect.rectify(Va, Vb, Vc)
        dt = t[1] - t[0]
        V_filt, I_cap = filt.apply_filter(V_rect, dt)
        
        # Calculate metrics
        u_deg, v_sag = rect.calculate_commutation_angle()
        v_dc = rect.get_actual_dc_voltage()
        v_avg, v_ripple, ripple_pct = filt.calculate_ripple(V_filt)
        p_esr, p_load, p_total = filt.power_dissipation(I_cap, V_filt)
        
        # Plot
        row, col = divmod(idx, 2)
        ax = axes[row, col]
        
        ax.plot(t*1000, V_filt, 'b-', linewidth=2, label='Filtered DC')
        ax.fill_between(t*1000, V_filt, alpha=0.2, color='blue')
        ax.axhline(y=13.5, color='r', linestyle='--', linewidth=1.5, label='ECU Min (13.5V)')
        
        ax.set_title(f'{name.upper()}: {current}A Load\nV_avg={v_dc:.2f}V, P={p_total*1000:.0f}mW', 
                    fontsize=11, fontweight='bold')
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('Voltage (V)')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)
        ax.set_ylim([10, 24])
        
        print(f"\n  {name.upper()}:")
        print(f"    Load current: {current}A")
        print(f"    DC voltage: {v_dc:.2f}V")
        print(f"    Ripple: {v_ripple:.3f}V ({ripple_pct:.2f}%)")
        print(f"    Power dissipation: {p_total*1000:.0f}mW")
    
    plt.tight_layout()
    current_dir = Path(__file__).parent.absolute()
    plt.savefig(current_dir / 'extension_3_ecu_profiles.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ Saved: extension_3_ecu_profiles.png")


# ============================================================================
# EXTENSION 4: Fourier Analysis (Harmonic Content)
# ============================================================================

def example_4_harmonic_analysis():
    """
    Analyze harmonic content of the rectified voltage.
    
    The 6-pulse rectifier output isn't pure DC—it contains harmonics.
    This is important for:
    - EMI (electromagnetic interference)
    - Filter design
    - Understanding noise sources
    """
    print("\n" + "="*70)
    print("EXTENSION 4: Harmonic Analysis (FFT of Rectified Output)")
    print("="*70)
    
    rect = ThreePhaseRectifier()
    t = np.linspace(0, 0.04, 2000)
    
    Va, Vb, Vc = rect.generate_three_phase_ac(t)
    V_rect = rect.rectify(Va, Vb, Vc)
    
    # Compute FFT
    fft_result = np.fft.fft(V_rect)
    frequencies = np.fft.fftfreq(len(V_rect), t[1] - t[0])
    magnitude = np.abs(fft_result) / len(fft_result)
    
    # Plot
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    fig.suptitle('Harmonic Analysis: Frequency Content of Rectified Output', fontsize=13, fontweight='bold')
    
    # Time domain
    ax = axes[0]
    ax.plot(t*1000, V_rect, 'b-', linewidth=1.5)
    ax.fill_between(t*1000, V_rect, alpha=0.2, color='blue')
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Voltage (V)')
    ax.set_title('Time Domain: 6-Pulse Rectified Waveform')
    ax.grid(True, alpha=0.3)
    
    # Frequency domain
    ax = axes[1]
    # Only plot positive frequencies up to 2kHz
    freq_limit = 2000
    idx_limit = np.where(frequencies <= freq_limit)[0]
    ax.stem(frequencies[idx_limit], magnitude[idx_limit], basefmt=' ')
    ax.set_xlabel('Frequency (Hz)', fontweight='bold')
    ax.set_ylabel('Magnitude (V)', fontweight='bold')
    ax.set_title('Frequency Domain: FFT showing harmonics at 6f, 12f, 18f, ...')
    ax.grid(True, alpha=0.3)
    
    # Annotate key harmonics
    fundamental_freq = 50  # Hz (our AC frequency)
    harmonic_positions = [fundamental_freq * n for n in [6, 12, 18]]
    for harm in harmonic_positions:
        if harm < freq_limit:
            ax.axvline(x=harm, color='r', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    current_dir = Path(__file__).parent.absolute()
    plt.savefig(current_dir / 'extension_4_harmonics.png', dpi=300, bbox_inches='tight')
    
    # Print harmonics
    print(f"\n  Fundamental frequency: {fundamental_freq}Hz")
    print(f"\n  Major harmonics (theoretical):")
    print(f"    6f  = {fundamental_freq*6}Hz")
    print(f"    12f = {fundamental_freq*12}Hz")
    print(f"    18f = {fundamental_freq*18}Hz")
    print(f"\n  (6-pulse rectifiers produce harmonics at 6n±1)")
    print(f"\n  ✓ Saved: extension_4_harmonics.png")


# ============================================================================
# MAIN: Run All Extensions
# ============================================================================

def main():
    """Run all extension examples."""
    print("\n" + "="*80)
    print("DIGITAL TWIN EXTENSIONS - Advanced Features")
    print("="*80)
    print("\nThese examples show how to extend the core digital twin.")
    print("Perfect for demonstrating software engineering skills to recruiters!")
    
    example_1_temperature_effects()
    example_2_battery_effects()
    example_3_ecu_load_profiles()
    example_4_harmonic_analysis()
    
    print("\n" + "="*80)
    print("ALL EXTENSIONS COMPLETE")
    print("="*80)
    print("""
Generated files:
  • extension_1_temperature.png - Temperature-dependent behavior
  • extension_2_battery_droop.png - Why lights dim during start
  • extension_3_ecu_profiles.png - Different operating scenarios
  • extension_4_harmonics.png - Frequency domain analysis

LinkedIn Value:
  These extensions show:
  ✓ Modular, extensible software design
  ✓ Deep understanding of systems complexity
  ✓ Ability to model real-world phenomena
  ✓ Professional visualization skills

Each one is a separate LinkedIn post opportunity!
    """)


if __name__ == "__main__":
    main()
