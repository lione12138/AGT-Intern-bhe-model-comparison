# pygfunction vs EED Comparison Analysis Report

## 1. Project Overview

This project uses the open-source library **pygfunction** to reproduce the BHE (Borehole Heat Exchanger) temperature calculations from commercial software **EED (Earth Energy Designer)**.

### System Configuration

| Parameter | Value |
|-----------|-------|
| Number of boreholes | 40 (5×8 rectangular layout) |
| Borehole depth | 147 m |
| Borehole spacing | 7 m |
| Borehole diameter | 140 mm |
| U-tube type | Double-U, 32mm |

## 2. Methodology Evolution

### 2.1 Early Attempt: POINT2 Analytical Solution

Before using pygfunction, we initially attempted to simulate BHE temperatures using MODFLOW's POINT2 analytical solution. POINT2 is a 2D point source solution for solute transport that can theoretically be analogized to heat transport:

```
Heat transport ↔ Solute transport
Temperature ↔ Concentration  
Thermal diffusion ↔ Dispersion
```

**Limitations of POINT2 Method**:
1. **Dimensional constraint**: POINT2 is a 2D solution, unable to accurately describe 3D heat conduction in 147m deep boreholes
2. **Cannot capture thermal interference**: Complex thermal interference in multi-borehole fields requires g-functions
3. **Large deviation**: >3°C deviation from EED results

**Key Insight**: BHE temperature calculations require purpose-designed g-function methods, not simple point source models.

### 2.2 Transition to pygfunction

Based on the above experience, we transitioned to using **pygfunction**, a library specifically designed for BHE calculations.

## 3. Problem Discovery and Resolution

### 3.1 Initial Problem

Initial pygfunction calculations showed a **systematic deviation of approximately 3.5°C** from EED results:

```
Original results:
  pygfunction temperature range: 7.0 ~ 14.3 °C
  EED temperature range:         10.5 ~ 18.2 °C
  MAE (Mean Absolute Error):     3.5 °C
```

### 3.2 Root Cause Analysis

After detailed investigation, **two key errors** were identified:

#### Error 1: Incorrect Thermal Properties

| Parameter | Wrong Value | Correct EED Value | Source |
|-----------|-------------|-------------------|--------|
| Thermal conductivity k | 2.5 W/(m·K) | **1.4 W/(m·K)** | EED input file |
| Volumetric heat capacity ρc | 2.5 MJ/(m³·K) | **2.83 MJ/(m³·K)** | EED input file |

#### Error 2: Ignoring Geothermal Gradient

EED input includes **geothermal heat flux of 0.07 W/m²**, meaning underground temperature increases with depth:

```
Geothermal gradient = Heat flux / Thermal conductivity
                    = 0.07 / 1.4 
                    = 0.05 °C/m 
                    = 50 °C/km

Average borehole temperature = Surface temperature + Gradient × Depth/2
                             = 9.6 + 0.05 × 73.5 
                             = 13.28 °C
```

**Key insight**: Cannot simply use surface temperature 9.6°C as initial ground temperature; must use **average temperature within borehole depth range: 13.28°C**.

## 3. Correct Calculation Parameters

### 3.1 EED Input Parameters (Correct Values)

```python
# Ground thermal properties
k_ground = 1.4        # Thermal conductivity [W/(m·K)]
rho_c = 2.83e6        # Volumetric heat capacity [J/(m³·K)]
alpha = k / rho_c     # Thermal diffusivity = 4.95×10⁻⁷ m²/s

# Borehole thermal resistance (EED calculated)
R_b = 0.1271          # Effective borehole resistance [(m·K)/W]

# Temperature parameters
T_surface = 9.6       # Surface temperature [°C]
q_geo = 0.07          # Geothermal heat flux [W/m²]
T_gradient = q_geo / k_ground  # Geothermal gradient = 0.05 °C/m

# Effective initial ground temperature (considering geothermal gradient)
T0_effective = T_surface + T_gradient * H/2  # = 13.28 °C
```

### 3.2 g-function Characteristics

```
Characteristic time ts = H²/(9α) = 153.8 years

Key g-values:
  g(1 month)  = 3.12
  g(1 year)   = 5.04
  g(5 years)  = 10.21
  g(10 years) = 14.48
  g(25 years) = 23.61
```

![g-function curve](../figures/gfunction_curve.png)
*Figure: g-function curve for 40-borehole BHE field*

## 4. Final Results

### 4.1 Load Sign Convention

When using g-function, note the difference in sign conventions:

| Convention | EED | g-function |
|------------|-----|------------|
| Positive value | Heat extraction (heating) | Heat injection (temperature rise) |
| Negative value | Heat injection (cooling) | Heat extraction (temperature drop) |

**Key**: When using g-function, **invert the sign of EED's ground load**!

### 4.2 Temperature Comparison (Year 25)

| Month | EED [°C] | pygfunction [°C] | Error [°C] |
|-------|----------|------------------|------------|
| JAN | 10.5 | 10.66 | +0.16 |
| FEB | 10.6 | 10.85 | +0.25 |
| MAR | 11.3 | 11.62 | +0.32 |
| APR | 12.3 | 12.43 | +0.13 |
| MAY | 13.0 | 12.98 | -0.02 |
| JUN | 15.4 | 15.36 | -0.04 |
| JUL | 17.9 | 17.76 | -0.14 |
| AUG | 18.2 | 17.90 | -0.30 |
| SEP | 13.9 | 13.86 | -0.04 |
| OCT | 12.7 | 12.70 | 0.00 |
| NOV | 12.0 | 12.03 | +0.03 |
| DEC | 10.9 | 11.06 | +0.16 |

### 4.3 Error Statistics

| Metric | Value |
|--------|-------|
| MAE (Mean Absolute Error) | **0.15°C** |
| R² (Coefficient of Determination) | **0.999** |
| Maximum Error | **0.32°C** |

![pygfunction vs EED Comparison](../figures/eed_comparison_25years.png)
*Figure 1: pygfunction vs EED temperature comparison (25 years)*

## 5. Core Solution Approach

### 5.1 Methodology

```
┌─────────────────────────────────────────────────────────────┐
│  Correct pygfunction Calculation Workflow                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Use correct thermal properties (from EED input file)    │
│     k = 1.4 W/(m·K), ρc = 2.83 MJ/(m³·K)                   │
│                                                             │
│  2. Calculate effective initial temperature with gradient   │
│     T0_eff = T_surface + (q_geo/k) × H/2                   │
│            = 9.6 + 0.05 × 73.5 = 13.28°C                   │
│                                                             │
│  3. Use pygfunction to calculate g-function                 │
│     - 40-borehole rectangular field                         │
│     - UBWT boundary condition                               │
│                                                             │
│  4. Temporal superposition for temperature response         │
│     T_fluid = T0_eff + ΔT_ground + q × R_b                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Key Equations

**Mean fluid temperature calculation**:

$$T_{fluid} = T_0^{eff} + \frac{1}{2\pi k_s H} \sum_{i} \Delta q_i \cdot g(t-t_i) + q \cdot R_b$$

Where:
- $T_0^{eff} = T_{surface} + \frac{q_{geo}}{k_s} \cdot \frac{H}{2}$ (effective initial ground temperature)
- $g(t)$ is the g-function calculated by pygfunction
- $R_b = 0.1271$ (m·K)/W is the effective borehole thermal resistance from EED

## 6. Key Conclusions

### 6.1 Technical Findings

1. **Thermal properties must be consistent**
   - Must use the same k and ρc values as EED
   - Different thermal conductivity leads to completely different g-function shapes

2. **Geothermal gradient cannot be ignored**
   - For deep boreholes (>100m), geothermal gradient causes 3-4°C temperature offset
   - Must use average temperature within borehole depth as reference

3. **Directly use EED's borehole thermal resistance**
   - EED-calculated $R_b = 0.1271$ (m·K)/W already accounts for all factors
   - Includes: fluid-pipe thermal resistance, pipe material resistance, grout resistance

### 6.2 Final Accuracy

```
┌────────────────────────────────────────┐
│  Final Results                         │
│                                        │
│  MAE = 0.15°C                          │
│  R² = 0.999                            │
│  No empirical calibration needed       │
│                                        │
│  This is a physically correct solution!│
└────────────────────────────────────────┘
```

## 7. File Description

### 7.1 Code Files

| File | Description |
|------|-------------|
| `gfunction_pygfunction.py` | pygfunction wrapper module |
| `pygfunction_final.ipynb` | Final analysis notebook |

### 7.2 Result Figures

| Figure | Description |
|--------|-------------|
| `final_comparison_pygfunction_eed.png` | pygfunction vs EED comparison |
| `pygfunction_optimization_results.png` | Parameter optimization process |

## 8. References

1. Cimmino, M. (2018). pygfunction 2.1: An open-source toolbox for the evaluation of thermal response factors for geothermal borehole fields. SoftwareX.
2. Eskilson, P. (1987). Thermal Analysis of Heat Extraction Boreholes. Doctoral Thesis, Lund University.
3. BLOCON. Earth Energy Designer (EED) Software Manual.

---

*Document Version: 2.0*  
*Created: December 2025*  
*Author: Liuhuang Luo*


