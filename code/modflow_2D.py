# =====================================================
# MODFLOW 2D Model for BHE Simulation
# =====================================================
# 2D (single layer) MODFLOW model for comparing with:
# - 3D MODFLOW (33 layers)
# - EED analytical solution
#
# Runs three scenarios: LOW, MEDIUM, HIGH groundwater flow
# Simulation period: 25 years
# =====================================================

import numpy as np
import flopy
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
import json
import warnings
warnings.filterwarnings('ignore')

# === MODFLOW 6 executable path ===
mf6_exe = r"D:\Program Files\USGS\mf6.6.2_win64\bin\mf6.exe"

# === Workspace setup ===
workspace_base = Path("../workspace")
figures_path = Path("../figures")
workspace_base.mkdir(parents=True, exist_ok=True)
figures_path.mkdir(parents=True, exist_ok=True)

print("="*70)
print("MODFLOW 2D Model - Three Scenarios (25 Years)")
print("="*70)

# === Thermal parameters (matching EED) ===
k_ground = 1.4          # Thermal conductivity [W/(m·K)]
rho_c = 2.83e6          # Volumetric heat capacity [J/(m³·K)]

# Derive solid properties
rho_w = 1000.0          # Water density [kg/m³]
c_w = 4184.0            # Water specific heat [J/(kg·K)]
k_w = 0.59              # Water thermal conductivity [W/(m·K)]
k_s = k_ground          # Solid thermal conductivity [W/(m·K)]
rho_s = 2650.0          # Solid density [kg/m³]
c_s = rho_c / rho_s     # Solid specific heat [J/(kg·K)]

# === Ground temperature ===
T0_surf = 9.6           # Surface temperature [°C]
q_geo = 0.07            # Geothermal heat flux [W/m²]
grad_T = q_geo / k_ground  # Geothermal gradient [°C/m]

# === BHE field configuration ===
n_x, n_y = 5, 8         # Borehole array dimensions
n_bhe = n_x * n_y       # Total boreholes = 40
H = 147.0               # Borehole depth [m]
B = 7.0                 # Borehole spacing [m]
r_b = 0.07              # Borehole radius [m]
R_b = 0.1271            # Borehole thermal resistance [(m·K)/W]

# Effective ground temperature at mid-depth
T0_eff = T0_surf + grad_T * H / 2

# === Simulation time ===
n_yr = 25               # Simulation period [years]
n_mo = n_yr * 12        # Total months = 300
sec_per_mo = 730 * 3600 # Seconds per month
L_total = n_bhe * H     # Total borehole length [m]
hrs_per_mo = 730.0

# === Hydraulic parameters ===
K_hydraulic = 10.0      # Hydraulic conductivity [m/d] - matching 3D model

# === Scenario configurations (matching 3D MODFLOW) ===
# All scenarios use n=0.2 porosity to match 3D model
scenarios = {
    'low': {'v_md': 0.001, 'n': 0.2},     # Essentially pure conduction
    'medium': {'v_md': 0.1, 'n': 0.2},    # Medium groundwater flow
    'high': {'v_md': 1.0, 'n': 0.2},      # High groundwater flow
}

print(f"\nThermal parameters:")
print(f"  k = {k_ground} W/(m·K)")
print(f"  rho_c = {rho_c/1e6:.2f} MJ/(m³·K)")
print(f"  T0_eff = {T0_eff:.2f} °C")
print(f"\nHydraulic parameters:")
print(f"  K = {K_hydraulic} m/d")
print(f"\nBHE configuration:")
print(f"  {n_x} x {n_y} = {n_bhe} boreholes")
print(f"  H = {H} m, B = {B} m")
print(f"  R_b = {R_b} (m·K)/W")
print(f"\nSimulation: {n_yr} years ({n_mo} months)")

# =====================================================
# 2D Grid Setup (SINGLE LAYER)
# =====================================================
# KEY INSIGHT from teacher's ex-gwe-bhe.py:
# - Use 1m "unit depth" layer (not 147m!)
# - This way, W/m load directly applies to the cell
# - Cell thermal mass is proportional to layer thickness
# - If we use 147m, thermal mass is 147x too large!

buffer = 50.0
field_x = (n_x - 1) * B
field_y = (n_y - 1) * B
Lx = field_x + 2 * buffer
Ly = field_y + 2 * buffer

nlay = 1
dx, dy = 1.0, 1.0
ncol = int(Lx / dx)
nrow = int(Ly / dy)

# KEY: Use 1m unit depth (like teacher's example)
# This makes the 2D model physically correct for BHE simulation
layer_thickness = 1.0  # 1m unit depth
top = 0.0
botm = [top - layer_thickness]

# BHE positions
x_offset = buffer + field_x / 2
y_offset = buffer + field_y / 2

bhe_x_pos, bhe_y_pos = [], []
for i in range(n_x):
    for j in range(n_y):
        bhe_x_pos.append(x_offset + (i - (n_x-1)/2) * B)
        bhe_y_pos.append(y_offset + (j - (n_y-1)/2) * B)

bhe_x_pos = np.array(bhe_x_pos)
bhe_y_pos = np.array(bhe_y_pos)
bhe_cols = (bhe_x_pos / dx).astype(int)
bhe_rows = (bhe_y_pos / dy).astype(int)

r_eq = np.sqrt(dx * dy / np.pi)
R_grid = np.log(r_eq / r_b) / (2 * np.pi * k_ground)

print(f"\n2D Grid: {nrow} x {ncol} = {nrow * ncol} cells")
print(f"  Layer thickness = {layer_thickness}m (unit depth, like teacher's example)")
print(f"  r_eq = {r_eq:.3f}m, R_grid = {R_grid:.4f} (m·K)/W")

# =====================================================
# Monthly Loads
# =====================================================
# Building load convention:
#   Positive = building needs heating = extract heat FROM ground
#   Negative = building needs cooling = inject heat TO ground
L_MWh_sep = np.array([0., 7.37, 12.3, 19.6, 22.1, 19.6, 12.3, 4.91, 0., -19.6, -39.2, -39.2])

def MWh_to_Wm(MWh):
    return MWh * 1e6 / hrs_per_mo / L_total

# For MODFLOW ESL: positive = add heat to ground, negative = remove heat
# So we need to NEGATE the building load!
# For T_fluid conversion: keep original sign for q * R_b calculation
q_Wm_sep_building = np.array([MWh_to_Wm(x) for x in L_MWh_sep])  # Building convention
q_Wm_sep_bhe = -q_Wm_sep_building  # BHE convention (for R_b conversion)
q_Wm_all_building = np.tile(q_Wm_sep_building, n_yr)
q_Wm_all_bhe = np.tile(q_Wm_sep_bhe, n_yr)

eed_base = np.array([10.5, 10.6, 11.3, 12.3, 13.0, 15.4, 17.9, 18.2, 13.9, 12.7, 12.0, 10.9])
eed_25yr = np.tile(eed_base, n_yr)


def run_scenario(scenario_name, v_md, porosity):
    """Run 2D MODFLOW simulation for a given scenario."""
    
    print(f"\n{'='*70}")
    print(f"Running {scenario_name.upper()} scenario (v = {v_md} m/d, n = {porosity})")
    print("="*70)
    
    sim_name = f"modflow-2d-{scenario_name}"
    gwf_name = f"gwf-2d-{scenario_name}"
    gwe_name = f"gwe-2d-{scenario_name}"
    workspace = workspace_base / f"modflow_2d_{scenario_name}"
    workspace.mkdir(parents=True, exist_ok=True)
    
    # Calculate hydraulic gradient from Darcy's law: v = K * i / n
    # So: i = v * n / K
    # Convert K from m/d to m/s for consistency
    K_ms = K_hydraulic / 86400  # m/s
    v_ms = v_md / 86400         # m/s
    grad_h = v_md * porosity / K_hydraulic  # hydraulic gradient [-]
    
    print(f"  K = {K_hydraulic} m/d = {K_ms:.2e} m/s")
    print(f"  v = {v_md} m/d = {v_ms:.2e} m/s")
    print(f"  grad_h = {grad_h:.6f}")
    
    # === Build GWF Model ===
    print("Building GWF model...")
    sim_ws_gwf = workspace / "mf6gwf"
    sim_ws_gwf.mkdir(parents=True, exist_ok=True)
    
    sim_gwf = flopy.mf6.MFSimulation(sim_name=sim_name, sim_ws=str(sim_ws_gwf), exe_name=mf6_exe)
    flopy.mf6.ModflowTdis(sim_gwf, nper=1, perioddata=[(1.0, 1, 1.0)], time_units="SECONDS")
    flopy.mf6.ModflowIms(sim_gwf, complexity="SIMPLE", inner_dvclose=1e-6)
    
    gwf = flopy.mf6.ModflowGwf(sim_gwf, modelname=gwf_name, save_flows=True)
    
    flopy.mf6.ModflowGwfdis(
        gwf, length_units="METERS", nlay=nlay, nrow=nrow, ncol=ncol,
        delr=[dx]*ncol, delc=[dy]*nrow, top=top, botm=botm
    )
    
    # Use actual hydraulic conductivity (in m/s for MODFLOW with SECONDS time unit)
    flopy.mf6.ModflowGwfnpf(
        gwf, save_saturation=True, save_specific_discharge=True, icelltype=0, k=K_ms
    )
    
    # Set up head boundary conditions to create the desired gradient
    hL = 10.0
    hR = hL - (Lx - dx) * grad_h  # Head at right boundary
    
    flopy.mf6.ModflowGwfic(gwf, strt=hL)
    flopy.mf6.ModflowGwfsto(gwf, ss=0, sy=0, steady_state={0: True})
    
    chd_pname = "CHD_0"
    chdrec = []
    for j in [0, ncol - 1]:
        hchd = hL if j == 0 else hR
        for i in range(nrow):
            chdrec.append([(0, i, j), hchd, T0_eff])
    
    flopy.mf6.ModflowGwfchd(gwf, auxiliary=["TEMPERATURE"], stress_period_data=chdrec, pname=chd_pname)
    flopy.mf6.ModflowGwfoc(gwf, head_filerecord=f"{gwf_name}.hds", budget_filerecord=f"{gwf_name}.cbc",
                          saverecord=[("HEAD", "LAST"), ("BUDGET", "LAST")])
    
    # === Build GWE Model ===
    print("Building GWE model...")
    sim_ws_gwe = workspace / "mf6gwe"
    sim_ws_gwe.mkdir(parents=True, exist_ok=True)
    
    sim_gwe = flopy.mf6.MFSimulation(sim_name=sim_name, sim_ws=str(sim_ws_gwe), exe_name=mf6_exe)
    gwe = flopy.mf6.ModflowGwe(sim_gwe, modelname=gwe_name, save_flows=True)
    flopy.mf6.ModflowIms(sim_gwe, linear_acceleration="BICGSTAB", complexity="SIMPLE", inner_dvclose=0.001)
    
    tdis_rc = [(sec_per_mo, 1, 1.0) for _ in range(n_mo)]
    flopy.mf6.ModflowTdis(sim_gwe, nper=n_mo, perioddata=tdis_rc, time_units="SECONDS")
    
    flopy.mf6.ModflowGwedis(
        gwe, length_units="METERS", nlay=nlay, nrow=nrow, ncol=ncol,
        delr=[dx]*ncol, delc=[dy]*nrow, top=top, botm=botm
    )
    
    flopy.mf6.ModflowGweic(gwe, strt=T0_eff)
    flopy.mf6.ModflowGweadv(gwe, scheme="TVD")
    
    alh = 1.0 if v_md > 0.01 else 0.0
    ath1 = 0.1 if v_md > 0.01 else 0.0
    flopy.mf6.ModflowGwecnd(gwe, alh=alh, ath1=ath1, ktw=k_w, kts=k_s)
    
    flopy.mf6.ModflowGweest(
        gwe, density_water=rho_w, heat_capacity_water=c_w,
        porosity=porosity, heat_capacity_solid=c_s, density_solid=rho_s
    )
    
    flopy.mf6.ModflowGwessm(gwe, sources=[(chd_pname, "AUX", "TEMPERATURE")])
    
    # ESL - Energy source loading
    # MODFLOW ESL convention: positive = add heat to ground
    # Building load: positive = need heating = extract from ground
    # So for ESL: use -q_building (which equals q_bhe)
    # But ESL already uses -q_cell in the tuple, so use q_building directly
    esl_data = {}
    for iper in range(n_mo):
        q_cell = q_Wm_all_building[iper] * layer_thickness  # W/m × 1m = W per cell
        esl_rec = [([(0, bhe_rows[i], bhe_cols[i]), -q_cell]) for i in range(n_bhe)]
        esl_data[iper] = esl_rec
    
    flopy.mf6.ModflowGweesl(gwe, stress_period_data=esl_data)
    
    flopy.mf6.ModflowGweoc(
        gwe, budget_filerecord=f"{gwe_name}.cbc", temperature_filerecord=f"{gwe_name}.ucn",
        saverecord=[("TEMPERATURE", "LAST"), ("BUDGET", "LAST")]
    )
    
    # FMI - Flow Model Interface (reference GWF output files by MODEL name, not sim_name)
    pd = [("GWFHEAD", "../mf6gwf/" + gwf_name + ".hds", None),
          ("GWFBUDGET", "../mf6gwf/" + gwf_name + ".cbc", None)]
    flopy.mf6.ModflowGwefmi(gwe, packagedata=pd)
    
    # === Run Models ===
    print("Running GWF model...")
    sim_gwf.write_simulation()
    success_gwf, _ = sim_gwf.run_simulation(silent=True)
    print(f"  GWF completed, success={success_gwf}")
    
    print("Running GWE model...")
    sim_gwe.write_simulation()
    success_gwe, _ = sim_gwe.run_simulation(silent=True)
    print(f"  GWE completed, success={success_gwe}")
    
    if not (success_gwf and success_gwe):
        print(f"ERROR: Simulation failed!")
        return None
    
    # === Extract Results ===
    print("Extracting results...")
    ucn_file = sim_ws_gwe / f"{gwe_name}.ucn"
    ucn = flopy.utils.HeadFile(str(ucn_file), text="TEMPERATURE")
    
    T_ground_monthly = []
    for t in ucn.get_times():
        temp = ucn.get_data(totim=t)
        T_bhe = [temp[0, bhe_rows[i], bhe_cols[i]] for i in range(n_bhe)]
        T_ground_monthly.append(np.mean(T_bhe))
    
    T_ground = np.array(T_ground_monthly)
    
    # Convert ground temperature to fluid temperature
    # Following POINT2 approach: T_fluid = T_borewall + q_bhe * R_b
    # where q_bhe uses BHE sign convention:
    #   - Injection (summer): q_bhe > 0, fluid hotter than ground
    #   - Extraction (winter): q_bhe < 0, fluid colder than ground
    # Also add R_grid for numerical correction
    R_total = R_b + R_grid
    dT_bhe = q_Wm_all_bhe * R_total  # dT = q_bhe [W/m] × R [(m·K)/W] = K
    T_fluid = T_ground + dT_bhe
    
    # Reorder SEP-AUG to JAN-DEC
    idx_jan = [yr * 12 + (mo + 4) % 12 for yr in range(n_yr) for mo in range(12)]
    T_fluid_jan = T_fluid[idx_jan]
    
    mae = np.mean(np.abs(T_fluid_jan - eed_25yr))
    _, _, r_value, _, _ = stats.linregress(eed_25yr, T_fluid_jan)
    r2 = r_value ** 2
    amplitude = T_fluid_jan.max() - T_fluid_jan.min()
    
    print(f"\n{scenario_name.upper()} Results:")
    print(f"  Tf range: {T_fluid_jan.min():.2f} to {T_fluid_jan.max():.2f} °C")
    print(f"  Amplitude: {amplitude:.2f} °C")
    print(f"  MAE vs EED: {mae:.3f} °C")
    print(f"  R² vs EED: {r2:.4f}")
    
    results = {
        "scenario": scenario_name, "velocity_md": v_md, "porosity": porosity,
        "n_years": n_yr, "Tf_jan": T_fluid_jan.tolist(),
        "mae_vs_eed": mae, "r2_vs_eed": r2, "amplitude": amplitude
    }
    
    results_file = workspace_base / f"modflow_2d_{scenario_name}_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {results_file}")
    
    return results


def load_3d_results():
    """Load existing 3D MODFLOW results."""
    results_3d = {}
    for scenario in ['low', 'medium', 'high']:
        filepath = workspace_base / f"modflow_gwflow_{scenario}_results.json"
        if filepath.exists():
            with open(filepath, 'r') as f:
                results_3d[scenario] = json.load(f)
            print(f"  Loaded 3D {scenario}: MAE calculation needed")
    return results_3d


def create_comparison_plots(results_2d, results_3d):
    """Create comparison plots: 2D vs 3D vs EED for all scenarios."""
    
    fig, axes = plt.subplots(3, 2, figsize=(16, 15))
    
    months = np.arange(1, n_mo + 1)
    years = months / 12
    
    for idx, scenario in enumerate(['low', 'medium', 'high']):
        ax1, ax2 = axes[idx, 0], axes[idx, 1]
        
        eed = eed_25yr
        tf_2d = np.array(results_2d[scenario]['Tf_jan']) if results_2d.get(scenario) else None
        tf_3d = np.array(results_3d[scenario]['Tf_jan']) if results_3d.get(scenario) else None
        v_md = scenarios[scenario]['v_md']
        
        # Time series
        ax1.plot(years, eed, 'k-', lw=2, label='EED', alpha=0.8)
        if tf_2d is not None:
            ax1.plot(years, tf_2d, 'b--', lw=1.5, label='MODFLOW 2D', alpha=0.8)
        if tf_3d is not None:
            ax1.plot(years, tf_3d, 'r:', lw=1.5, label='MODFLOW 3D', alpha=0.8)
        
        ax1.set_xlabel('Time [years]', fontsize=11)
        ax1.set_ylabel('Fluid Temperature [°C]', fontsize=11)
        ax1.set_title(f'{scenario.upper()} (v = {v_md} m/d)', fontsize=12, fontweight='bold')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(0, 25)
        
        # Scatter plot
        if tf_2d is not None:
            mae_2d = results_2d[scenario]['mae_vs_eed']
            ax2.scatter(eed, tf_2d, c='blue', alpha=0.4, s=15, label=f'2D (MAE={mae_2d:.2f}°C)')
        if tf_3d is not None:
            mae_3d = np.mean(np.abs(tf_3d - eed))
            ax2.scatter(eed, tf_3d, c='red', alpha=0.4, s=15, label=f'3D (MAE={mae_3d:.2f}°C)')
        
        t_range = [8, 20]
        ax2.plot(t_range, t_range, 'k--', lw=1, label='1:1 line')
        ax2.set_xlabel('EED Temperature [°C]', fontsize=11)
        ax2.set_ylabel('MODFLOW Temperature [°C]', fontsize=11)
        ax2.set_title(f'{scenario.upper()}: MODFLOW vs EED', fontsize=12, fontweight='bold')
        ax2.legend(loc='upper left')
        ax2.grid(True, alpha=0.3)
        ax2.set_aspect('equal', adjustable='box')
    
    plt.tight_layout()
    fig_path = figures_path / "modflow_2D_vs_3D_vs_EED_comparison.png"
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    print(f"\nFigure saved to {fig_path}")
    plt.close()
    
    # Summary table
    print("\n" + "="*85)
    print("SUMMARY: 2D vs 3D MODFLOW Comparison with EED (25 years)")
    print("="*85)
    print(f"{'Scenario':<10} {'v [m/d]':<10} {'Method':<15} {'MAE [°C]':<12} {'Amplitude [°C]':<15} {'R²':<10}")
    print("-"*85)
    
    for scenario in ['low', 'medium', 'high']:
        v_md = scenarios[scenario]['v_md']
        eed_amp = eed_base.max() - eed_base.min()
        
        print(f"{scenario.upper():<10} {v_md:<10} {'EED':<15} {'-':<12} {eed_amp:<15.2f} {'-':<10}")
        
        if results_2d.get(scenario):
            r = results_2d[scenario]
            print(f"{'':<10} {'':<10} {'MODFLOW 2D':<15} {r['mae_vs_eed']:<12.3f} {r['amplitude']:<15.2f} {r['r2_vs_eed']:<10.4f}")
        
        if results_3d.get(scenario):
            tf_3d = np.array(results_3d[scenario]['Tf_jan'])
            mae_3d = np.mean(np.abs(tf_3d - eed_25yr))
            amp_3d = tf_3d.max() - tf_3d.min()
            _, _, r_3d, _, _ = stats.linregress(eed_25yr, tf_3d)
            print(f"{'':<10} {'':<10} {'MODFLOW 3D':<15} {mae_3d:<12.3f} {amp_3d:<15.2f} {r_3d**2:<10.4f}")
        
        print("-"*85)


if __name__ == "__main__":
    
    # Run all scenarios
    results_2d = {}
    for scenario, params in scenarios.items():
        result = run_scenario(scenario, params['v_md'], params['n'])
        if result:
            results_2d[scenario] = result
    
    # Load 3D results
    print("\n" + "="*70)
    print("Loading 3D MODFLOW results...")
    print("="*70)
    results_3d = load_3d_results()
    
    # Create comparison
    print("\n" + "="*70)
    print("Creating comparison plots...")
    print("="*70)
    create_comparison_plots(results_2d, results_3d)
    
    print("\n" + "="*70)
    print("DONE!")
    print("="*70)
