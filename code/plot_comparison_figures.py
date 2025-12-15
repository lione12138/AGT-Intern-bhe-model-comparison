# =============================================================================
# Comprehensive Comparison Figures for BHE Modeling Methods
# =============================================================================
# This script generates three comparison figures:
# 1. Point2 vs 2D MODFLOW vs EED (three groundwater scenarios)
# 2. 2D MODFLOW vs 3D MODFLOW vs EED (three groundwater scenarios)  
# 3. pygfunction vs EED (no groundwater flow)
# =============================================================================

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Set up paths
workspace_dir = Path(__file__).parent.parent / "workspace"
figures_dir = Path(__file__).parent.parent / "figures"
figures_dir.mkdir(exist_ok=True)

# =============================================================================
# Load Data
# =============================================================================
print("Loading data files...")

# Load Point2 results
with open(workspace_dir / "point2_gwflow_low_results.json", 'r') as f:
    point2_low = json.load(f)
with open(workspace_dir / "point2_gwflow_medium_results.json", 'r') as f:
    point2_medium = json.load(f)
with open(workspace_dir / "point2_gwflow_high_results.json", 'r') as f:
    point2_high = json.load(f)

# Load 2D MODFLOW results
with open(workspace_dir / "modflow_2d_low_results.json", 'r') as f:
    modflow2d_low = json.load(f)
with open(workspace_dir / "modflow_2d_medium_results.json", 'r') as f:
    modflow2d_medium = json.load(f)
with open(workspace_dir / "modflow_2d_high_results.json", 'r') as f:
    modflow2d_high = json.load(f)

# Load 3D MODFLOW results
with open(workspace_dir / "modflow_gwflow_low_results.json", 'r') as f:
    modflow3d_low = json.load(f)
with open(workspace_dir / "modflow_gwflow_medium_results.json", 'r') as f:
    modflow3d_medium = json.load(f)
with open(workspace_dir / "modflow_gwflow_high_results.json", 'r') as f:
    modflow3d_high = json.load(f)

print("All data loaded successfully.")

# =============================================================================
# EED Reference Data (no groundwater flow)
# =============================================================================
# EED Base load temperatures for Year 25 (JAN-DEC order)
eed_base = np.array([10.5, 10.6, 11.3, 12.3, 13.0, 15.4, 17.9, 18.2, 13.9, 12.7, 12.0, 10.9])
n_years = 25
n_months = n_years * 12
eed_25yr = np.tile(eed_base, n_years)

# =============================================================================
# Helper Functions
# =============================================================================
def calculate_metrics(pred, ref):
    """Calculate MAE and R² between prediction and reference."""
    mae = np.mean(np.abs(np.array(pred) - np.array(ref)))
    # R² calculation
    ss_res = np.sum((np.array(pred) - np.array(ref))**2)
    ss_tot = np.sum((np.array(ref) - np.mean(ref))**2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return mae, r2

def get_amplitude(temps):
    """Get temperature amplitude from Year 25 (last 12 months)."""
    y25 = temps[-12:]
    return max(y25) - min(y25)

# =============================================================================
# Figure 1: Point2 vs 2D MODFLOW vs EED
# =============================================================================
print("\nGenerating Figure 1: Point2 vs 2D MODFLOW vs EED...")

fig1, axes1 = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
x_years = np.arange(n_months) / 12.0

scenarios = ['LOW', 'MEDIUM', 'HIGH']
velocities = [0.001, 0.1, 1.0]
point2_data = [point2_low, point2_medium, point2_high]
modflow2d_data = [modflow2d_low, modflow2d_medium, modflow2d_high]

for i, (ax, scenario, v, p2, m2d) in enumerate(zip(axes1, scenarios, velocities, point2_data, modflow2d_data)):
    # Plot data with different line styles for clarity
    ax.plot(x_years, eed_25yr, 'k-', lw=2.0, alpha=0.9, label='EED (reference)')  # solid black
    ax.plot(x_years, p2['Tf_jan'], 'b--', lw=1.8, label='Point2')  # dashed blue
    ax.plot(x_years, m2d['Tf_jan'], 'r:', lw=2.0, label='2D MODFLOW')  # dotted red
    
    # Calculate metrics
    mae_p2, r2_p2 = calculate_metrics(p2['Tf_jan'], eed_25yr)
    mae_m2d, r2_m2d = calculate_metrics(m2d['Tf_jan'], eed_25yr)
    amp_p2 = get_amplitude(p2['Tf_jan'])
    amp_m2d = get_amplitude(m2d['Tf_jan'])
    amp_eed = get_amplitude(eed_25yr)
    
    # Labels and formatting
    ax.set_xlabel('Time (years)', fontsize=11)
    ax.set_title(f'{scenario} Flow (v = {v} m/d)', fontsize=12, fontweight='bold')
    ax.set_xlim(0, 25)
    ax.set_ylim(6, 22)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(range(0, 26, 5))
    
    # Metrics text box
    metrics_text = (f'Point2: MAE={mae_p2:.2f}°C, Amp={amp_p2:.1f}°C\n'
                    f'2D MODFLOW: MAE={mae_m2d:.2f}°C, Amp={amp_m2d:.1f}°C\n'
                    f'EED: Amp={amp_eed:.1f}°C')
    ax.text(0.03, 0.97, metrics_text, transform=ax.transAxes, fontsize=8,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    if i == 0:
        ax.set_ylabel('Fluid Temperature (°C)', fontsize=11)
        ax.legend(loc='lower right', fontsize=9)

fig1.suptitle('Comparison: Point2 vs 2D MODFLOW vs EED under Different Groundwater Flow Scenarios', 
              fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
fig1.savefig(figures_dir / 'comparison_point2_2Dmodflow_eed.png', dpi=200, bbox_inches='tight', facecolor='white')
print(f"  Saved: {figures_dir / 'comparison_point2_2Dmodflow_eed.png'}")

# =============================================================================
# Figure 2: 2D MODFLOW vs 3D MODFLOW vs EED
# =============================================================================
print("\nGenerating Figure 2: 2D MODFLOW vs 3D MODFLOW vs EED...")

fig2, axes2 = plt.subplots(1, 3, figsize=(16, 5), sharey=True)

modflow3d_data = [modflow3d_low, modflow3d_medium, modflow3d_high]

for i, (ax, scenario, v, m2d, m3d) in enumerate(zip(axes2, scenarios, velocities, modflow2d_data, modflow3d_data)):
    # Plot data with different line styles for clarity
    ax.plot(x_years, eed_25yr, 'k-', lw=2.0, alpha=0.9, label='EED (reference)')  # solid black
    ax.plot(x_years, m2d['Tf_jan'], 'b--', lw=1.8, label='2D MODFLOW')  # dashed blue
    ax.plot(x_years, m3d['Tf_jan'], 'g:', lw=2.0, label='3D MODFLOW')  # dotted green
    
    # Calculate metrics
    mae_m2d, r2_m2d = calculate_metrics(m2d['Tf_jan'], eed_25yr)
    mae_m3d, r2_m3d = calculate_metrics(m3d['Tf_jan'], eed_25yr)
    amp_m2d = get_amplitude(m2d['Tf_jan'])
    amp_m3d = get_amplitude(m3d['Tf_jan'])
    amp_eed = get_amplitude(eed_25yr)
    
    # Labels and formatting
    ax.set_xlabel('Time (years)', fontsize=11)
    ax.set_title(f'{scenario} Flow (v = {v} m/d)', fontsize=12, fontweight='bold')
    ax.set_xlim(0, 25)
    ax.set_ylim(3, 22)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(range(0, 26, 5))
    
    # Metrics text box
    metrics_text = (f'2D MODFLOW: MAE={mae_m2d:.2f}°C, Amp={amp_m2d:.1f}°C\n'
                    f'3D MODFLOW: MAE={mae_m3d:.2f}°C, Amp={amp_m3d:.1f}°C\n'
                    f'EED: Amp={amp_eed:.1f}°C')
    ax.text(0.03, 0.97, metrics_text, transform=ax.transAxes, fontsize=8,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.9))
    
    if i == 0:
        ax.set_ylabel('Fluid Temperature (°C)', fontsize=11)
        ax.legend(loc='lower right', fontsize=9)

fig2.suptitle('Comparison: 2D MODFLOW vs 3D MODFLOW vs EED under Different Groundwater Flow Scenarios', 
              fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
fig2.savefig(figures_dir / 'comparison_2Dmodflow_3Dmodflow_eed.png', dpi=200, bbox_inches='tight', facecolor='white')
print(f"  Saved: {figures_dir / 'comparison_2Dmodflow_3Dmodflow_eed.png'}")

# =============================================================================
# Figure 3: pygfunction vs EED (No Groundwater Flow)
# =============================================================================
print("\nGenerating Figure 3: pygfunction vs EED...")

# pygfunction calculation (same as pygfunction_final.ipynb)
import pygfunction as gt
from scipy import stats as scipy_stats

# Thermal parameters
k = 1.4              # Thermal conductivity [W/(m·K)]
rho_c = 2.83e6       # Volumetric heat capacity [J/(m³·K)]
alpha = k / rho_c    # Thermal diffusivity [m²/s]
T0_surf = 9.6        # Surface ground temperature [°C]
q_geo = 0.07         # Geothermal heat flux [W/m²]
grad = q_geo / k     # Geothermal gradient [°C/m]

# BHE configuration
n_x, n_y = 5, 8
n_bhe = 40
H = 147.0
B = 7.0
D = 0.0
r_b = 0.07
R_b = 0.1271

T0 = T0_surf + grad * H / 2

# Simulation parameters
hrs_per_mo = 730.0
sec_per_mo = hrs_per_mo * 3600.0
L_total = n_bhe * H

# g-function calculation
print("  Computing g-function (this may take a moment)...")
bhs = gt.boreholes.rectangle_field(n_x, n_y, B, B, H, D, r_b)
times = np.array([(i+1)*sec_per_mo for i in range(n_months)])
gf = gt.gfunction.gFunction(bhs, alpha, times, options={'nSegments': 8})
g = gf.gFunc

# Monthly loads (starting from SEP)
L_MWh_sep = np.array([0., 7.37, 12.3, 19.6, 22.1, 19.6, 12.3, 4.91, 0., -19.6, -39.2, -39.2])

def MWh_to_Wm(MWh):
    return MWh * 1e6 / hrs_per_mo / L_total

q_MWh = np.tile(L_MWh_sep, n_years)
q_Wm = np.array([MWh_to_Wm(x) for x in q_MWh])

# Temperature calculation using temporal superposition
Tf_pygf = np.zeros(n_months)
for i in range(n_months):
    dT_ground = 0.
    for j in range(i+1):
        dq = q_Wm[j] if j==0 else q_Wm[j]-q_Wm[j-1]
        if i-j < len(g):
            dT_ground += (-dq) * g[i-j] / (2*np.pi*k)
    dT_bh = (-q_Wm[i]) * R_b
    Tf_pygf[i] = T0 + dT_ground + dT_bh

# Reorder to JAN-DEC
Tf_jan_pygf = np.zeros(n_months)
for yr in range(n_years):
    start_sep = yr * 12
    idx_map = [4, 5, 6, 7, 8, 9, 10, 11, 0, 1, 2, 3]
    for m_new, m_old in enumerate(idx_map):
        Tf_jan_pygf[yr*12 + m_new] = Tf_pygf[start_sep + m_old]

# Peak loads
peak_power = 160 * 1000
peak_Wm = peak_power / L_total
delta_T_peak = peak_Wm * R_b

Tf_peak_heat = Tf_jan_pygf.copy()
Tf_peak_cool = Tf_jan_pygf.copy()
for yr in range(n_years):
    Tf_peak_heat[yr * 12 + 0] -= delta_T_peak
    Tf_peak_cool[yr * 12 + 7] += delta_T_peak

# EED peak temperatures
eed_peak_heat_jan = 6.91
eed_peak_cool_aug = 22.4
eed_peak_heat = eed_25yr.copy()
eed_peak_cool = eed_25yr.copy()
for yr in range(n_years):
    eed_peak_heat[yr * 12 + 0] = eed_peak_heat_jan
    eed_peak_cool[yr * 12 + 7] = eed_peak_cool_aug

# Calculate metrics
mae_pygf, r2_pygf = calculate_metrics(Tf_jan_pygf, eed_25yr)
amp_pygf = get_amplitude(Tf_jan_pygf)
amp_eed = get_amplitude(eed_25yr)

# Plot
fig3, ax = plt.subplots(figsize=(14, 6))
ax.set_facecolor('#f5f5ff')

# Base load curves
ax.plot(x_years, eed_25yr, 'k--', lw=1.5, alpha=0.8, label='EED Base Load')
ax.plot(x_years, Tf_jan_pygf, 'b-', lw=1.5, label='pygfunction Base Load')

# Peak heat (JAN) - vertical lines
for yr in range(n_years):
    jan_idx = yr * 12 + 0
    x_jan = x_years[jan_idx]
    # EED peak heat (dashed red)
    ax.plot([x_jan, x_jan], [eed_25yr[jan_idx], eed_peak_heat[jan_idx]], 
            color='lightcoral', ls='--', lw=1.5, alpha=0.7)
    # pygfunction peak heat (solid red)
    ax.plot([x_jan, x_jan], [Tf_jan_pygf[jan_idx], Tf_peak_heat[jan_idx]], 
            'r-', lw=2)

# Peak cool (AUG) - vertical lines
for yr in range(n_years):
    aug_idx = yr * 12 + 7
    x_aug = x_years[aug_idx]
    # EED peak cool (dashed blue)
    ax.plot([x_aug, x_aug], [eed_25yr[aug_idx], eed_peak_cool[aug_idx]], 
            color='cornflowerblue', ls='--', lw=1.5, alpha=0.7)
    # pygfunction peak cool (solid blue)
    ax.plot([x_aug, x_aug], [Tf_jan_pygf[aug_idx], Tf_peak_cool[aug_idx]], 
            'b-', lw=2)

# Legend entries for peak loads
ax.plot([], [], 'r-', lw=2, label='Peak Heat Load (JAN)')
ax.plot([], [], 'b-', lw=2, label='Peak Cool Load (AUG)')
ax.plot([], [], color='gray', ls='--', lw=1.5, label='EED Peak')

ax.set_xlabel('Time (years)', fontsize=12)
ax.set_ylabel('Fluid Temperature (°C)', fontsize=12)
ax.set_title('Comparison: pygfunction vs EED (No Groundwater Flow)', fontsize=14, fontweight='bold')
ax.set_xlim(0, 25)
ax.set_ylim(5, 24)
ax.set_xticks(range(0, 26, 2))
ax.grid(True, alpha=0.3)
ax.legend(loc='upper right', fontsize=10)

# Metrics text box
metrics_text = (f'Base Load Comparison:\n'
                f'  MAE = {mae_pygf:.2f}°C\n'
                f'  R² = {r2_pygf:.4f}\n\n'
                f'Amplitude (Year 25):\n'
                f'  pygfunction = {amp_pygf:.1f}°C\n'
                f'  EED = {amp_eed:.1f}°C\n\n'
                f'Peak Temperatures (Year 25):\n'
                f'  Heat (JAN): pygf={Tf_peak_heat[-12:].min():.2f}°C, EED={eed_peak_heat_jan:.2f}°C\n'
                f'  Cool (AUG): pygf={Tf_peak_cool[-12:].max():.2f}°C, EED={eed_peak_cool_aug:.2f}°C')
ax.text(0.02, 0.98, metrics_text, transform=ax.transAxes, fontsize=9,
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

# Configuration info
config_text = (f'Configuration: 40 boreholes (5×8)\n'
               f'Depth: 147 m, Spacing: 7 m\n'
               f'k = 1.4 W/(m·K), Rb = 0.127 (m·K)/W')
ax.text(0.98, 0.02, config_text, transform=ax.transAxes, fontsize=9,
        horizontalalignment='right', verticalalignment='bottom',
        fontstyle='italic', color='navy')

plt.tight_layout()
fig3.savefig(figures_dir / 'comparison_pygfunction_eed.png', dpi=200, bbox_inches='tight', facecolor='white')
print(f"  Saved: {figures_dir / 'comparison_pygfunction_eed.png'}")

# =============================================================================
# Summary Statistics
# =============================================================================
print("\n" + "="*70)
print("SUMMARY STATISTICS")
print("="*70)

print("\n--- Point2 vs EED ---")
for scenario, data in [('LOW', point2_low), ('MEDIUM', point2_medium), ('HIGH', point2_high)]:
    mae, r2 = calculate_metrics(data['Tf_jan'], eed_25yr)
    amp = get_amplitude(data['Tf_jan'])
    print(f"  {scenario}: MAE={mae:.3f}°C, R²={r2:.4f}, Amp={amp:.2f}°C")

print("\n--- 2D MODFLOW vs EED ---")
for scenario, data in [('LOW', modflow2d_low), ('MEDIUM', modflow2d_medium), ('HIGH', modflow2d_high)]:
    mae, r2 = calculate_metrics(data['Tf_jan'], eed_25yr)
    amp = get_amplitude(data['Tf_jan'])
    print(f"  {scenario}: MAE={mae:.3f}°C, R²={r2:.4f}, Amp={amp:.2f}°C")

print("\n--- 3D MODFLOW vs EED ---")
for scenario, data in [('LOW', modflow3d_low), ('MEDIUM', modflow3d_medium), ('HIGH', modflow3d_high)]:
    mae, r2 = calculate_metrics(data['Tf_jan'], eed_25yr)
    amp = get_amplitude(data['Tf_jan'])
    print(f"  {scenario}: MAE={mae:.3f}°C, R²={r2:.4f}, Amp={amp:.2f}°C")

print("\n--- pygfunction vs EED (No Flow) ---")
print(f"  MAE={mae_pygf:.3f}°C, R²={r2_pygf:.4f}, Amp={amp_pygf:.2f}°C")

print("\n" + "="*70)
print("All figures saved to:", figures_dir)
print("="*70)

plt.show()
