"""
Plot g-function curve for the BHE field
Generate g-function visualization for documentation
"""

import numpy as np
import matplotlib.pyplot as plt
import pygfunction as gt

# Set matplotlib style
plt.rcParams['font.size'] = 12
plt.rcParams['figure.figsize'] = (10, 6)

# BHE field parameters
H = 147.0       # Borehole depth [m]
D = 2.0         # Buried depth [m]
r_b = 0.07      # Borehole radius [m]
B = 7.0         # Borehole spacing [m]
N_x = 5         # Number of boreholes in x direction
N_y = 8         # Number of boreholes in y direction

# Ground thermal properties
k_s = 1.4       # Ground thermal conductivity [W/(m·K)]
rho_c_s = 2.83e6  # Ground volumetric heat capacity [J/(m³·K)]
alpha_s = k_s / rho_c_s  # Thermal diffusivity [m²/s]

# Characteristic time
ts = H**2 / (9 * alpha_s)  # [s]

print("=" * 60)
print("BHE Field g-function Calculation")
print("=" * 60)
print(f"Borehole field: {N_x} × {N_y} = {N_x * N_y} boreholes")
print(f"Borehole depth: H = {H} m")
print(f"Borehole spacing: B = {B} m")
print(f"Borehole radius: r_b = {r_b * 1000} mm")
print(f"Thermal conductivity: k = {k_s} W/(m·K)")
print(f"Thermal diffusivity: α = {alpha_s:.2e} m²/s")
print(f"Characteristic time: ts = {ts / (365.25 * 24 * 3600):.1f} years")
print("=" * 60)

# Create borehole field
boreholes = gt.boreholes.rectangle_field(N_x, N_y, B, B, H, D, r_b)
print(f"\nCreated borehole field with {len(boreholes)} boreholes")

# Time vector for g-function calculation
# From 100 seconds to 25 years, log-distributed
t_min = 100  # seconds
t_max = 25 * 365.25 * 24 * 3600  # 25 years in seconds
n_points = 50
time = np.logspace(np.log10(t_min), np.log10(t_max), n_points)

# Calculate g-function
print("\nCalculating g-function (this may take a moment)...")
try:
    # Try newer pygfunction API
    gFunc = gt.gfunction.gFunction(
        boreholes, alpha_s, time,
        boundary_condition='MIFT',
        options={'nSegments': 8, 'disp': True}
    )
    gfunc_values = gFunc.gFunc
except (AttributeError, TypeError):
    # Fallback to older API or use uniform heat extraction rate
    gfunc_values = gt.gfunction.uniform_heat_extraction(
        boreholes, time, alpha_s, 
        nSegments=8, disp=True
    )
print("g-function calculation complete!")

# Convert time to ln(t/ts) for standard g-function representation
ln_t_ts = np.log(time / ts)

# Create figure with two subplots
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: g-function vs ln(t/ts)
ax1 = axes[0]
ax1.plot(ln_t_ts, gfunc_values, 'b-', linewidth=2, label=f'{N_x}×{N_y} BHE field')
ax1.set_xlabel('ln(t/ts)', fontsize=12)
ax1.set_ylabel('g-function', fontsize=12)
ax1.set_title('g-function vs Normalized Time', fontsize=14)
ax1.grid(True, alpha=0.3)
ax1.legend(loc='upper left')

# Add characteristic time annotation
ax1.axvline(x=0, color='r', linestyle='--', alpha=0.5, label='t = ts')
ax1.annotate(f't = ts\n({ts/(365.25*24*3600):.1f} years)', 
             xy=(0, gfunc_values[np.argmin(np.abs(ln_t_ts))]),
             xytext=(1, gfunc_values[np.argmin(np.abs(ln_t_ts))] - 5),
             fontsize=10, color='red',
             arrowprops=dict(arrowstyle='->', color='red', alpha=0.5))

# Plot 2: g-function vs time (years)
ax2 = axes[1]
time_years = time / (365.25 * 24 * 3600)
ax2.semilogx(time_years, gfunc_values, 'b-', linewidth=2)
ax2.set_xlabel('Time [years]', fontsize=12)
ax2.set_ylabel('g-function', fontsize=12)
ax2.set_title('g-function vs Time', fontsize=14)
ax2.grid(True, alpha=0.3)

# Add key time points
key_times = [1/12, 1, 5, 10, 25]  # 1 month, 1 year, 5, 10, 25 years
for t in key_times:
    idx = np.argmin(np.abs(time_years - t))
    ax2.plot(time_years[idx], gfunc_values[idx], 'ro', markersize=6)
    label = f'{int(t)} yr' if t >= 1 else '1 mo'
    ax2.annotate(f'{label}\ng={gfunc_values[idx]:.1f}', 
                 xy=(time_years[idx], gfunc_values[idx]),
                 xytext=(time_years[idx] * 1.5, gfunc_values[idx] + 1),
                 fontsize=9, ha='left')

plt.tight_layout()

# Save figure
output_path = 'figures/gfunction_curve.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"\nFigure saved to: {output_path}")

plt.show()

# Print g-function values at key times
print("\n" + "=" * 60)
print("g-function values at key time points:")
print("=" * 60)
print(f"{'Time':<15} {'ln(t/ts)':<12} {'g-function':<12}")
print("-" * 40)
for t in [1/12, 1, 5, 10, 25]:
    idx = np.argmin(np.abs(time_years - t))
    label = f'{int(t)} year' if t >= 1 else '1 month'
    print(f"{label:<15} {ln_t_ts[idx]:<12.2f} {gfunc_values[idx]:<12.2f}")
print("=" * 60)
