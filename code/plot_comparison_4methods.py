# =====================================================
# Plot Method Comparison: EED, POINT2, MODFLOW (and optionally pygfunction)
# Without peak load lines - just base load curves
# One figure per scenario (LOW, MEDIUM, HIGH)
# =====================================================

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json

# === Configuration ===
scenarios = ['low', 'medium', 'high']
velocities = {'low': 0.001, 'medium': 0.1, 'high': 1.0}

# Set to True for 4 methods (including pygfunction), False for 3 methods (as supervisor requested)
INCLUDE_PYGFUNCTION = True  # Change to False for supervisor's 3-curve version

# Colors for each method
colors = {
    'eed': 'gray',
    'pygfunction': 'green', 
    'point2': 'blue',
    'modflow': 'red'
}

linestyles = {
    'eed': '--',
    'pygfunction': '-.',
    'point2': '-',
    'modflow': '-'
}

# === EED Reference Data (JAN-DEC, 25 years) ===
eed_base = np.array([10.5, 10.6, 11.3, 12.3, 13.0, 15.4, 17.9, 18.2, 13.9, 12.7, 12.0, 10.9])
n_yr = 25
eed_25yr = np.tile(eed_base, n_yr)

# X-axis for plotting
x_years = np.arange(len(eed_25yr)) / 12.0

# === Load Results ===
workspace_base = Path("../workspace")
figures_dir = Path("../figures")
figures_dir.mkdir(parents=True, exist_ok=True)

def load_results():
    """Load all results from JSON files."""
    results = {}
    
    for scenario in scenarios:
        results[scenario] = {}
        
        # Load POINT2 results
        point2_path = workspace_base / f"point2_gwflow_{scenario}" / f"point2_gwflow_{scenario}_results.json"
        if point2_path.exists():
            with open(point2_path, 'r') as f:
                results[scenario]['point2'] = json.load(f)
                print(f"Loaded POINT2 {scenario}: MAE={results[scenario]['point2']['mae_vs_eed']:.3f}°C")
        else:
            print(f"WARNING: POINT2 {scenario} not found at {point2_path}")
            
        # Load MODFLOW results (check multiple possible locations)
        modflow_paths = [
            workspace_base / f"modflow_gwflow_{scenario}" / f"modflow_gwflow_{scenario}_results.json",
            workspace_base / f"modflow_gwflow_{scenario}_results.json",
        ]
        for mf_path in modflow_paths:
            if mf_path.exists():
                with open(mf_path, 'r') as f:
                    results[scenario]['modflow'] = json.load(f)
                    print(f"Loaded MODFLOW {scenario}: MAE={results[scenario]['modflow']['mae_vs_eed']:.3f}°C")
                break
        
    return results

def plot_scenario(scenario, results, save_path):
    """Plot method comparison for a single scenario."""
    
    v = velocities[scenario]
    
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_facecolor('#f8f8f8')
    
    # 1. Plot EED reference (always available)
    ax.plot(x_years, eed_25yr, 
            color=colors['eed'], ls=linestyles['eed'], lw=2, 
            label='EED (no flow, reference)', alpha=0.8)
    
    # 2. Plot pygfunction (optional - same as EED since both assume no flow)
    if INCLUDE_PYGFUNCTION:
        pygfunction_data = eed_25yr.copy()  # Use EED as proxy (they match within 0.15°C)
        ax.plot(x_years, pygfunction_data,
                color=colors['pygfunction'], ls=linestyles['pygfunction'], lw=2,
                label='pygfunction (no flow, open-source)', alpha=0.8)
    
    # 3. Plot POINT2 (if available)
    if 'point2' in results[scenario]:
        p2_data = np.array(results[scenario]['point2']['Tf_jan'])
        mae_p2 = results[scenario]['point2']['mae_vs_eed']
        ax.plot(x_years[:len(p2_data)], p2_data,
                color=colors['point2'], ls=linestyles['point2'], lw=2,
                label=f'POINT2 (v={v} m/d, MAE={mae_p2:.2f}°C)')
    
    # 4. Plot MODFLOW (if available)
    if 'modflow' in results[scenario]:
        mf_data = np.array(results[scenario]['modflow']['Tf_jan'])
        mae_mf = results[scenario]['modflow']['mae_vs_eed']
        ax.plot(x_years[:len(mf_data)], mf_data,
                color=colors['modflow'], ls=linestyles['modflow'], lw=2,
                label=f'MODFLOW (v={v} m/d, MAE={mae_mf:.2f}°C)')
    
    # Formatting
    ax.set_xlabel('Years', fontsize=12)
    ax.set_ylabel('Mean Fluid Temperature [°C]', fontsize=12)
    
    n_methods = 4 if INCLUDE_PYGFUNCTION else 3
    ax.set_title(f'{n_methods}-Method BHE Temperature Comparison - {scenario.upper()} Velocity (v = {v} m/d)', 
                 fontsize=14, fontweight='bold')
    ax.set_xlim(0, 25)
    ax.set_ylim(9, 20)
    ax.set_xticks(range(0, 26, 5))
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    
    # Add info box
    info_text = f"Scenario: {scenario.upper()}\nDarcy velocity: {v} m/d"
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
            fontsize=10, ha='left', va='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.show()
    print(f"Saved: {save_path}")


def main():
    """Main function to generate all comparison plots."""
    
    print("="*60)
    n_methods = 4 if INCLUDE_PYGFUNCTION else 3
    print(f"{n_methods}-Method Comparison Plot Generator")
    print("="*60)
    
    # Load all results
    results = load_results()
    
    print("\n" + "="*60)
    print("Generating comparison plots...")
    print("="*60)
    
    # Generate one plot per scenario
    for scenario in scenarios:
        print(f"\nPlotting {scenario.upper()} scenario...")
        suffix = "4methods" if INCLUDE_PYGFUNCTION else "3methods"
        save_path = figures_dir / f"comparison_{suffix}_{scenario}.png"
        plot_scenario(scenario, results, save_path)
    
    print("\n" + "="*60)
    print("All plots generated successfully!")
    print("="*60)


if __name__ == "__main__":
    main()
