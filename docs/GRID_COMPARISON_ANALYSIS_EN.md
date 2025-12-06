# MODFLOW Grid Discretization Strategy Comparison Analysis

## 1. Background

When simulating Borehole Heat Exchangers (BHE) using MODFLOW 6 GWE module, grid discretization is a critical factor affecting simulation accuracy. Since MODFLOW uses the finite difference method, temperature is calculated at cell centers rather than at the borehole wall, leading to systematic deviations between simulated and actual borehole wall temperatures.

### 1.1 Problem Description

The core issue in BHE simulation is the difference between **grid equivalent radius** and **actual borehole radius**:

- For a square grid cell (side length $\Delta x$), the equivalent radius is:
  $$r_{eq} = \sqrt{\frac{\Delta x^2}{\pi}}$$

- Actual borehole radius: $r_b = 0.07$ m

- When $r_{eq} >> r_b$, simulated temperatures deviate from actual values

### 1.2 Research Objectives

Compare the accuracy and computational efficiency of three grid strategies:
1. Uniform coarse grid (1.0m × 1.0m)
2. Uniform fine grid (0.5m × 0.5m)
3. Locally refined grid (0.25m at BHE, 2.0m at boundaries)

## 2. Model Configuration

### 2.1 BHE Field Parameters

| Parameter | Value | Unit |
|-----------|-------|------|
| Number of boreholes | 40 (5×8) | - |
| Borehole depth H | 147 | m |
| Borehole spacing B | 7.0 | m |
| Borehole radius r_b | 0.07 | m |
| Borehole thermal resistance R_b | 0.1271 | (m·K)/W |

### 2.2 Thermal Properties

| Parameter | Value | Unit |
|-----------|-------|------|
| Thermal conductivity k | 1.4 | W/(m·K) |
| Volumetric heat capacity ρc | 2.83 | MJ/(m³·K) |
| Effective ground temperature T₀ | 13.28 | °C |

### 2.3 Simulation Period

- Simulation period: 25 years (300 stress periods)
- Time step: 1 month

## 3. Grid Strategy Comparison

### 3.1 Three Grid Schemes

#### Scheme 1: Uniform 1.0m Grid

```
Grid size: 1.0m × 1.0m × 5.0m
Total cells: 629,376
Equivalent radius: r_eq = 0.564 m
r_eq/r_b = 8.1
```

#### Scheme 2: Uniform 0.5m Grid

```
Grid size: 0.5m × 0.5m × 5.0m
Total cells: 2,517,504
Equivalent radius: r_eq = 0.282 m
r_eq/r_b = 4.0
```

#### Scheme 3: Locally Refined Grid

```
Grid at BHE: 0.25m × 0.25m
Transition zone: 0.5m (1-3m from BHE)
Intermediate zone: 1.0m (3-10m from BHE)
Boundary zone: 2.0m (>10m from BHE)
Total cells: 720,852
Equivalent radius at BHE: r_eq = 0.141 m
r_eq/r_b = 2.0
```

### 3.2 Grid Thermal Resistance Analysis

The additional thermal resistance introduced by grid discretization:

$$R_{grid} = \frac{\ln(r_{eq}/r_b)}{2\pi k}$$

| Grid Scheme | r_eq [m] | R_grid [(m·K)/W] |
|-------------|----------|------------------|
| Uniform 1.0m | 0.564 | 0.2372 |
| Uniform 0.5m | 0.282 | 0.1584 |
| Local refined | 0.141 | 0.0796 |

## 4. Results Comparison

### 4.1 Accuracy Comparison

Comparison with EED analytical solution:

| Metric | Uniform 1.0m | Uniform 0.5m | Local Refined |
|--------|--------------|--------------|---------------|
| **MAE [°C]** | 0.670 | 0.349 | **0.084** |
| **R²** | 0.9884 | 0.9965 | **0.9987** |
| Improvement | Baseline | 48% | **87%** |

![Grid Comparison Results](../figures/grid_comparison_comprehensive.png)
*Figure 1: Comprehensive comparison of three grid strategies*

### 4.2 Computational Efficiency Comparison

| Metric | Uniform 1.0m | Uniform 0.5m | Local Refined |
|--------|--------------|--------------|---------------|
| Cell count | 629,376 | 2,517,504 | 720,852 |
| Cell ratio | 1.0x | 4.0x | 1.15x |
| Computation time [min] | ~21 | ~77 | ~24 |
| Time ratio | 1.0x | 3.7x | 1.1x |

### 4.3 Efficiency Metric

Efficiency metric definition: accuracy improvement / computational cost increase

$$\eta = \frac{1/MAE}{N_{cells}/10^6}$$

| Grid Scheme | Efficiency η |
|-------------|--------------|
| Uniform 1.0m | 2.37 |
| Uniform 0.5m | 1.14 |
| **Local Refined** | **16.52** |

**The local refined grid is 7× more efficient than uniform coarse grid and 14× more efficient than uniform fine grid!**

## 5. Year 25 Monthly Temperature Comparison

| Month | EED [°C] | Uniform 1.0m | Local Refined | Local Refined Deviation |
|-------|----------|--------------|---------------|------------------------|
| JAN | 10.5 | 11.3 | 10.5 | -0.03 |
| FEB | 10.6 | 11.4 | 10.6 | -0.01 |
| MAR | 11.3 | 12.0 | 11.4 | +0.05 |
| APR | 12.3 | 12.8 | 12.2 | -0.07 |
| MAY | 13.0 | 13.3 | 12.9 | -0.13 |
| JUN | 15.4 | 15.3 | 15.2 | -0.17 |
| JUL | 17.9 | 17.0 | 17.8 | -0.09 |
| AUG | 18.2 | 16.7 | 18.2 | +0.05 |
| SEP | 13.9 | 13.3 | 14.0 | +0.06 |
| OCT | 12.7 | 12.4 | 12.8 | +0.06 |
| NOV | 12.0 | 12.0 | 12.0 | -0.02 |
| DEC | 10.9 | 11.7 | 11.0 | +0.06 |

## 6. Peak Load Temperatures

### 6.1 Peak Load Conditions
- Peak power: 160 kW
- Peak linear heat flux: 27.2 W/m

### 6.2 Year 25 Peak Temperatures

| Condition | EED | Local Refined MODFLOW | Deviation |
|-----------|-----|----------------------|-----------|
| Winter peak (January) | 6.91°C | 7.01°C | +0.10°C |
| Summer peak (August) | 22.40°C | 21.71°C | -0.69°C |

![Local Refined Model Results](../figures/modflow_localref_eed_comparison.png)
*Figure 2: 25-year temperature time series comparison between MODFLOW local refined grid and EED*

## 7. Conclusions and Recommendations

### 7.1 Main Conclusions

1. **Uniform 1.0m grid**: Low accuracy (MAE=0.67°C), but computationally efficient, suitable for preliminary design and quick assessment.

2. **Uniform 0.5m grid**: 48% accuracy improvement, but 4× computational cost increase, poor cost-effectiveness.

3. **Locally refined grid**:
   - Highest accuracy (MAE=0.084°C, 87% improvement)
   - Only 15% increase in computational cost
   - No numerical correction needed, uses actual borehole thermal resistance
   - **Best cost-effective solution**

### 7.2 Physical Explanation

Reasons for local refined grid effectiveness:

1. Fine grid near BHE (maximum temperature gradient region) accurately captures heat transfer
2. Coarse grid far from BHE (lower temperature gradient) saves computational resources
3. Reduced equivalent radius $r_{eq}$ closer to actual borehole radius $r_b$
4. Reduced additional thermal resistance $R_{grid}$ introduced by discretization

### 7.3 Recommendations

For MODFLOW simulation of BHE fields:

1. **Recommend using local grid refinement strategy**
2. Grid size at BHE location: ≤0.25m
3. Transition zone grid size: 0.5-1.0m
4. Boundary zone grid size: 1.0-2.0m
5. Use actual borehole thermal resistance $R_b$, no additional correction needed

## 8. File Description

### 8.1 Related Files

| File | Description |
|------|-------------|
| `modflow_bhe.ipynb` | Original 1.0m uniform grid model |
| `modflow_finegrid.ipynb` | 0.5m uniform fine grid model |
| `modflow_localrefined.ipynb` | Local refined grid model |
| `figures/grid_comparison_comprehensive.png` | Comprehensive comparison chart |
| `figures/modflow_localref_eed_comparison.png` | Local refined model time series |

## 9. References

1. Langevin, C.D., et al. (2022). MODFLOW 6 Modular Hydrologic Model - Groundwater Energy Transport (GWE) Module Documentation
2. Hellström, G. (1991). Ground Heat Storage: Thermal Analyses of Duct Storage Systems. Lund University, Sweden.
3. BLOCON. Earth Energy Designer (EED) Software Manual

---

*Document generated: December 2025*
*Author: Liuhuang Luo*


