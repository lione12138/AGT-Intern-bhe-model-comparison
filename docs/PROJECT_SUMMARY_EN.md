# Borehole Heat Exchanger (BHE) Temperature Simulation Method Comparison Study

## Comprehensive Project Report

---

## 1. Project Background

### 1.1 Research Objectives

This project aims to compare three different Borehole Heat Exchanger (BHE) temperature simulation methods:
1. **EED (Earth Energy Designer)** - Commercial analytical solution software
2. **pygfunction** - Open-source g-function based analytical solution
3. **MODFLOW 6 GWE** - Finite difference numerical simulation

The goal is to verify whether open-source tools can achieve accuracy comparable to commercial software and provide reliable alternatives for BHE system design.

### 1.2 Study Subject

| Parameter | Value | Unit |
|-----------|-------|------|
| Number of boreholes | 40 (5×8) | - |
| Borehole depth | 147 | m |
| Borehole spacing | 7.0 | m |
| Borehole diameter | 140 | mm |
| U-tube type | Double-U | 32mm |
| Simulation period | 25 | years |

### 1.3 Thermal Properties

| Parameter | Value | Unit |
|-----------|-------|------|
| Ground thermal conductivity k | 1.4 | W/(m·K) |
| Ground volumetric heat capacity ρc | 2.83 | MJ/(m³·K) |
| Surface temperature | 9.6 | °C |
| Geothermal heat flux | 0.07 | W/m² |
| Effective initial ground temperature | 13.28 | °C |
| Borehole thermal resistance R_b | 0.1271 | (m·K)/W |

---

## 2. Methodology Overview

### 2.1 EED (Earth Energy Designer)

**Principle**: Based on Eskilson's g-function theory, using pre-computed response factors for temperature calculation.

**Advantages**:
- Commercial software, extensively validated
- User-friendly interface
- Fast computation

**Disadvantages**:
- Closed source, not customizable
- Requires license purchase

### 2.2 Early Attempt: POINT2 Analytical Solution

**Principle**: POINT2 is a 2D point source analytical solution in MODFLOW for solute transport, which can be analogously applied to heat transport problems.

**Initial Approach**:
```
Heat transport ↔ Solute transport
Temperature ↔ Concentration
Thermal diffusion ↔ Dispersion
T_fluid = T_ground + q × R_b
```

**Why This Method Was Abandoned**:

1. **Dimensional limitation**: POINT2 is a 2D solution, while BHE is a 3D problem (borehole depth 147m)
2. **Cannot capture g-function effects**: Thermal interference in multi-borehole fields requires complete g-functions
3. **Large deviation**: Systematic deviation >3°C compared to EED results
4. **Calibration difficulty**: Requires empirical correction factors without physical meaning

**Lessons Learned**:
- Heat transport problems cannot be simply analogized to solute transport
- BHE temperature calculations require purpose-built methods (g-function or numerical simulation)
- Parameter consistency (thermal conductivity, initial temperature) is more important than method selection

### 2.3 pygfunction

**Principle**: Open-source Python library using Finite Line Source (FLS) model to calculate g-functions and temporal superposition for temperature response.

$$T_{fluid} = T_0^{eff} + \frac{1}{2\pi k_s H} \sum_{i} \Delta q_i \cdot g(t-t_i) + q \cdot R_b$$

**Advantages**:
- Open-source and free
- Highly customizable
- Same theoretical basis as EED

**Key Findings**:
- Must use correct thermal properties (k=1.4 W/(m·K))
- Must consider geothermal gradient (T0_eff=13.28°C)

### 2.4 MODFLOW 6 GWE

**Principle**: Three-dimensional finite difference numerical simulation solving the heat conduction equation.

**Advantages**:
- Can simulate complex boundary conditions
- Can couple with groundwater flow
- Can handle heterogeneous formations

**Challenges**:
- Grid discretization causes temperature measurement offset from borehole wall
- Requires appropriate grid strategy

---

## 3. Results Comparison

### 3.1 Accuracy Comparison of Three Methods

| Method | MAE [°C] | R² | Computation Time | Notes |
|--------|----------|-----|------------------|-------|
| **EED** | Benchmark | Benchmark | <1 sec | Commercial reference |
| **pygfunction** | 0.15 | 0.999 | ~10 sec | Analytical, high accuracy |
| **MODFLOW (1m grid)** | 0.67 | 0.988 | ~21 min | Coarse grid, low accuracy |
| **MODFLOW (local refined)** | 0.084 | 0.999 | ~24 min | Best accuracy |

### 3.2 Year 25 Monthly Temperature Comparison

![Three Methods Temperature Comparison](../figures/grid_comparison_comprehensive.png)
*Figure 1: Temperature simulation results comparison of three methods*

| Month | EED [°C] | pygfunction [°C] | MODFLOW [°C] |
|-------|----------|------------------|--------------|
| JAN | 10.5 | 10.66 | 10.5 |
| FEB | 10.6 | 10.85 | 10.6 |
| MAR | 11.3 | 11.62 | 11.4 |
| APR | 12.3 | 12.43 | 12.2 |
| MAY | 13.0 | 12.98 | 12.9 |
| JUN | 15.4 | 15.36 | 15.2 |
| JUL | 17.9 | 17.76 | 17.8 |
| AUG | 18.2 | 17.90 | 18.2 |
| SEP | 13.9 | 13.86 | 14.0 |
| OCT | 12.7 | 12.70 | 12.8 |
| NOV | 12.0 | 12.03 | 12.0 |
| DEC | 10.9 | 11.06 | 11.0 |

### 3.3 25-Year Time Series Comparison

![pygfunction vs EED Comparison](../figures/eed_comparison_25years.png)
*Figure 2: pygfunction vs EED 25-year temperature time series comparison*

![MODFLOW Local Refined vs EED Comparison](../figures/modflow_localref_eed_comparison.png)
*Figure 3: MODFLOW locally refined grid vs EED 25-year temperature time series comparison*

---

## 4. Key Technical Findings

### 4.1 pygfunction Key Points

1. **Parameter Consistency**: Must use thermal properties identical to EED
2. **Geothermal Gradient**: For deep boreholes (>100m), geothermal gradient must be considered
   $$T_0^{eff} = T_{surface} + \frac{q_{geo}}{k} \times \frac{H}{2}$$
3. **Load Sign Convention**: EED load signs need to be inverted when using g-function

### 4.2 MODFLOW Grid Strategy

![Grid Comparison Results](../figures/grid_comparison_comprehensive.png)
*Figure 4: Accuracy and efficiency comparison of different grid strategies*

1. **Uniform Coarse Grid (1.0m)**
   - MAE = 0.67°C
   - Fast but low accuracy
   - Grid thermal resistance R_grid = 0.24 (m·K)/W

2. **Uniform Fine Grid (0.5m)**
   - MAE = 0.35°C
   - 4× cell count, 48% accuracy improvement
   - Not efficient

3. **Locally Refined Grid**
   - MAE = 0.084°C
   - Only 1.15× cell count, 87% accuracy improvement
   - **Optimal solution**

---

## 5. Conclusions and Recommendations

### 5.1 Method Selection Guidelines

| Application Scenario | Recommended Method | Rationale |
|---------------------|-------------------|-----------|
| Quick design assessment | EED | Fast, user-friendly |
| Academic research/Customization | pygfunction | Open-source, customizable |
| Complex geological conditions | MODFLOW | Handles heterogeneity, groundwater flow |
| High accuracy requirements | MODFLOW local refined | MAE < 0.1°C |

### 5.2 MODFLOW Grid Recommendations

For BHE field MODFLOW simulation:
- BHE location: ≤0.25m
- Transition zone (1-3m): 0.5m
- Intermediate zone (3-10m): 1.0m
- Boundary zone (>10m): 2.0m

### 5.3 Main Contributions

1. **Verified pygfunction equivalence with EED** (MAE=0.15°C)
2. **Proposed MODFLOW locally refined grid strategy** (87% accuracy improvement)
3. **Established complete comparison framework for three methods**

---

## 6. Project Structure

```
Base case for comparision/
├── Analytic solution for EED/
│   ├── code/
│   │   ├── pygfunction_final.ipynb      # pygfunction analysis
│   │   ├── modflow_bhe.ipynb            # Original MODFLOW model
│   │   ├── modflow_localrefined.ipynb   # MODFLOW locally refined
│   │   ├── gfunction_pygfunction.py     # pygfunction wrapper
│   │   └── figures/                     # Result figures
│   ├── PYGFUNCTION_ANALYSIS_CN.md       # pygfunction analysis (Chinese)
│   ├── PYGFUNCTION_ANALYSIS_EN.md       # pygfunction analysis (English)
│   ├── GRID_COMPARISON_ANALYSIS_CN.md   # Grid comparison (Chinese)
│   ├── GRID_COMPARISON_ANALYSIS_EN.md   # Grid comparison (English)
│   ├── PROJECT_SUMMARY_CN.md            # This document (Chinese)
│   ├── PROJECT_SUMMARY_EN.md            # This document (English)
│   └── reference/                       # References
└── EED Output Files/
    └── 6443_SCENARIO 1_*.txt            # EED raw output
```

---

## 7. References

1. Eskilson, P. (1987). Thermal Analysis of Heat Extraction Boreholes. Doctoral Thesis, Lund University.
2. Cimmino, M. (2018). pygfunction 2.1: An open-source toolbox for the evaluation of thermal response factors for geothermal borehole fields.
3. Langevin, C.D., et al. (2022). MODFLOW 6 - Groundwater Energy Transport Module.
4. Hellström, G. (1991). Ground Heat Storage: Thermal Analyses of Duct Storage Systems.
5. BLOCON. Earth Energy Designer (EED) Software Manual.

---

*Document Version: 1.0*  
*Created: December 2025*  
*Author: Liuhuang Luo*  
*Project: AGT Intern - BHE Model Comparison*


