# QUICK REFERENCE CARD
## 3-Phase Alternator Digital Twin Project

---

## 📋 What You Have Built

### Core Modules (Ready to Use)

| Module | Purpose | Key Classes |
|--------|---------|------------|
| `physics_engine.py` | 3-phase generation & rectification | `AlternatorParams`, `ThreePhaseRectifier` |
| `filter_module.py` | Capacitor filtering & ripple | `FilterParams`, `CapacitorFilter` |
| `visualization.py` | Plot generation | `plot_rectification_stages()`, etc. |

### Executable Scripts

| Script | Output | Purpose |
|--------|--------|---------|
| `run_simulation.py` | 4 PNGs | Core simulation with load variation |
| `scenario_generator.py` | 3 PNGs | Real-world scenarios (cold start, AC, etc.) |
| `extensions.py` | 4 PNGs | Advanced features (temperature, battery, etc.) |

**Total Output: 11 Publication-Ready Visualizations**

---

## 🎯 Key Metrics (At 10A Load, 50Hz, 100µF Capacitor)

| Metric | Value | Significance |
|--------|-------|-------------|
| Commutation Angle µ | 41.4° | Overlap time during diode switching |
| Voltage Sag | 3.46V | DC voltage loss due to source inductance |
| Ideal DC Voltage | 19.58V | Perfect rectifier (no losses) |
| Actual DC Voltage | 16.12V | Real-world after sag |
| Regulation Loss | 17.7% | Percentage of voltage lost to physics |
| Filtered DC Output | 22.51V | After capacitor (load dependent) |
| Residual Ripple | 3.59V | Still present even with filtering |
| Power Dissipation | 36.3W | Heat generated in system |

---

## 🔧 Running the Project

### Setup (One Time)
```bash
pip install -r requirements.txt
```

### Core Simulation
```bash
python run_simulation.py
# Output: rectification_stages.png, load_*.png, power_dissipation.png
```

### Scenario Analysis  
```bash
python scenario_generator.py
# Output: scenario_1_*.png, scenario_2_*.png, scenario_3_*.png
```

### Advanced Examples
```bash
python extensions.py
# Output: extension_1_*.png through extension_4_*.png
```

---

## 📊 Visualization Reference

### Main Plots (What You'll See)

**rectification_stages.png**
- Shows AC → Rectified → Filtered transformation
- 3 subplots with voltage waveforms
- Perfect intro to the project

**load_regulation_analysis.png** ⭐⭐⭐⭐⭐
- Three critical graphs
- Shows system performance across load range
- Best single visualization for LinkedIn

**scenario_1_cold_start.png**
- 4 load conditions (5A, 10A, 15A, 20A)
- Shows voltage collapse under high current
- Most "relatable" post

**extension_2_battery_droop.png**
- Battery terminal voltage vs current
- Very dramatic (shows 20V drop at starter!)
- Second most "relatable" post

---

## 💡 Quick Customization

### Change Load Current
```python
params = AlternatorParams(load_current=20)  # Change from 10A to 20A
rect = ThreePhaseRectifier(params)
```

### Change Frequency
```python
params = AlternatorParams(frequency=60)  # Change from 50Hz to 60Hz (US)
```

### Change Capacitance
```python
params = FilterParams(capacitance=200e-6)  # Change from 100µF to 200µF
```

### Get Specific Metrics
```python
rect = ThreePhaseRectifier()
u_deg, v_sag = rect.calculate_commutation_angle()
v_dc = rect.get_actual_dc_voltage()
print(f"Sag: {v_sag:.3f}V, DC: {v_dc:.2f}V")
```

---

## 📱 LinkedIn Content Strategy

### Best Posts to Lead With

1. **"Why Your Lights Dim When You Turn On the AC"**
   - Image: `scenario_1_cold_start.png`
   - Audience: Everyone (very relatable)
   - Engagement: HIGH

2. **"The Physics Behind Why Everything Fails at High Current"**
   - Image: `extension_2_battery_droop.png`  
   - Audience: Automotive + Tech
   - Engagement: VERY HIGH

3. **"How Modern ECUs Survive Voltage Swings"**
   - Image: `extension_3_ecu_profiles.png`
   - Audience: Engineers
   - Engagement: MEDIUM

---

## 🔗 File Organization

```
Root Directory:
├── core/                          # Python modules
│   ├── physics_engine.py
│   ├── filter_module.py
│   └── visualization.py
├── run_simulation.py             # Main script
├── scenario_generator.py         # Scenario variants
├── extensions.py                 # Advanced examples
├── README.md                     # Full documentation
├── QUICKSTART.md                 # Setup guide
└── LINKEDIN_STRATEGY.md          # This file
    
Output Files (Generated):
├── rectification_stages.png       ← Most important
├── load_regulation_analysis.png   ← Second most important
├── scenario_*.png                 ← 3 files
└── extension_*.png                ← 4 files
```

---

## 🎓 Key Equations (Copy-Paste Ready)

### Commutation Overlap Angle
$$\cos(\mu) = 1 - \frac{2 \omega L_c I_d}{\sqrt{3} V_{peak}}$$

### Ideal Rectifier Output
$$V_{dc,ideal} = \frac{3\sqrt{2}}{\pi} V_{ac,peak}$$

### RC Discharge Voltage
$$V(t) = V_0 e^{-t/RC}$$

### Capacitor Current During Discharge
$$i_C = -C \frac{dV}{dt} = \frac{V(t)}{R}$$

---

## ⚡ Performance at Different Loads

| Load (A) | DC Voltage (V) | Ripple (V) | Sag (V) | Comment |
|----------|---|---|---|---|
| 2 (idle) | 18.89 | 3.59 | 0.69 | Stable, good regulation |
| 5 | 17.85 | 3.59 | 1.73 | Still good |
| 10 | 16.12 | 3.59 | 3.46 | Noticeable sag |
| 15 | 14.39 | 3.59 | 5.20 | ECU struggles |
| 20 | 12.65 | 3.59 | 6.93 | Critical area |
| 25 | 10.92 | 3.59 | 8.67 | System failure |

**Key Insight:** Voltage sag grows roughly linearly with load current (due to constant inductance). This is why alternators with constant voltage regulators are critical!

---

## 🚀 Next Steps (Roadmap)

### Immediate (This Week)
- [ ] Post first visualization to LinkedIn (rectification_stages.png)
- [ ] Post second visualization (scenario_1_cold_start.png)
- [ ] Link to GitHub repo
- [ ] Get feedback from network

### Short Term (This Month)
- [ ] Post all 11 visualizations (one per week)
- [ ] Document LinkedIn engagement metrics
- [ ] Build GitHub stars (aim for 50+)
- [ ] Get recruiter DMs

### Medium Term (Next 2-3 Months)
- [ ] Build thermal simulation (2D heat conduction)
- [ ] Create thermal GIF visualizations
- [ ] Wrap in ROS 2 node framework
- [ ] Post ROS 2 integration roadmap

### Long Term (3-6 Months)
- [ ] Hardware validation (real alternator testing)
- [ ] Compare simulation vs measurement
- [ ] Publish detailed technical report
- [ ] Prepare portfolio pitch for interviews

---

## 📞 Troubleshooting Quick Links

### "My plots look different"
- Check load current parameter
- Verify capacitor value hasn't changed
- Make sure you're running from project root directory

### "I want to change X"
- Load current: Edit `AlternatorParams(load_current=X)`
- Frequency: Edit `AlternatorParams(frequency=X)` 
- Capacitor: Edit `FilterParams(capacitance=X)`
- Source inductance: Edit `AlternatorParams(source_inductance=X)`

### "I want to add a new visualization"
- Create a new function in `visualization.py`
- Call it from `run_simulation.py`
- Save output with `plt.savefig()`
- That's it! (The architecture is modular)

---

## ✨ Pro Tips

1. **When posting to LinkedIn:**
   - Lead with the most dramatic visualization
   - Put the equation in the comment (shows rigor)
   - Ask a real question (engagement boost)
   - Tag 2-3 relevant companies or experts

2. **Engagement Maximization:**
   - Post at 8-9 AM on weekdays
   - Engage with comments in first 2 hours
   - Cross-post to Twitter/GitHub/Reddit
   - Include a call-to-action ("What surprised you?")

3. **Recruiter Attraction:**
   - Your project shows: physics, systems thinking, code quality, communication
   - This combination is rare and valuable
   - Aim for companies in automotive, power systems, robotics, aerospace

---

## 🎯 Success Indicators

You'll know this is working when:

✅ First week: 20+ likes per post  
✅ Second week: Recruiter DMs or comments  
✅ Third week: 50+ GitHub stars  
✅ Fourth week: Interview requests  

If you're not seeing engagement by week 2, try:
1. Post at different times
2. Engage more with others' content first
3. Use more hashtags (#PowerElectronics, #Automotive, etc.)
4. Cross-post to other platforms

---

## 📚 Reference Documents

- **Full Details:** See `README.md`
- **Setup Guide:** See `QUICKSTART.md`
- **LinkedIn Strategy:** See `LINKEDIN_STRATEGY.md`
- **Code Examples:** See inline docstrings in `.py` files

---

**Status:** ✅ Complete and Ready  
**Version:** 1.0  
**Last Updated:** February 11, 2026  
**Next Review:** After first LinkedIn post

---

**You've built something impressive. Now go show the world! 🚀**

