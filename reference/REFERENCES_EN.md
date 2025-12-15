# BHE Groundwater Flow Impact Modeling Literature Review

## Project Overview

This project provides a comparative analysis of **POINT2 analytical solution** and **MODFLOW numerical solution** for simulating the impact of groundwater flow on Borehole Heat Exchangers (BHE). Both methods effectively capture the effect of groundwater velocity on thermal response.

---

## 1. Core Theoretical Foundations

### 1.1 Heat Transfer Theory

1. **Carslaw, H.S., & Jaeger, J.C. (1959)**
   - *Conduction of Heat in Solids* (Second Edition)
   - Oxford University Press
   - **Contribution**: Fundamental heat conduction theory, including infinite line source and point source solutions

2. **Ingersoll, L.R., Zobel, O.J., & Ingersoll, A.C. (1954)**
   - *Heat Conduction with Engineering, Geological, and Other Applications*
   - McGraw-Hill
   - **Contribution**: Heat conduction analysis methods for engineering applications

### 1.2 Solute/Heat Transport Theory

3. **Wexler, E.J. (1992)**
   - "Analytical Solutions for One-, Two-, and Three-Dimensional Solute Transport in Ground-Water Systems with Uniform Flow"
   - *U.S. Geological Survey, Techniques of Water-Resources Investigations, Book 3, Chapter B7*
   - https://pubs.usgs.gov/twri/twri3-b7/
   - **Contribution**: Theoretical foundation for POINT2 analytical solution—analytical solution for point source solute transport in uniform flow fields

---

## 2. Methodology Literature

### 2.1 POINT2 Analytical Solution Method

4. **Bear, J. (1972)**
   - *Dynamics of Fluids in Porous Media*
   - American Elsevier
   - **Contribution**: Fundamental theory of fluid dynamics in porous media

5. **Domenico, P.A., & Schwartz, F.W. (1990)**
   - *Physical and Chemical Hydrogeology*
   - John Wiley & Sons
   - **Contribution**: Analogy method between solute and heat transport (heat-solute conversion principle)

**Heat-Solute Analogy Principle**:
| Solute Transport Parameter | Corresponding Heat Transport Parameter |
|---------------------------|---------------------------------------|
| Concentration C | Temperature change ΔT |
| Diffusion coefficient D | Thermal diffusivity α |
| Darcy velocity v | Darcy velocity × (ρw·cw)/(ρs·cs) |
| Point source mass M | Point source heat Q / (ρs·cs) |

### 2.2 MODFLOW Numerical Method

6. **Langevin, C.D., et al. (2017)**
   - "Documentation for the MODFLOW 6 Groundwater Flow Model"
   - *U.S. Geological Survey Techniques and Methods, Book 6, Chapter A55*
   - https://doi.org/10.3133/tm6A55
   - **Contribution**: MODFLOW 6 core flow model documentation

7. **Hughes, J.D., et al. (2022)**
   - "Documentation for the MODFLOW 6 Groundwater Energy Transport (GWE) Model"
   - *U.S. Geological Survey Techniques and Methods, Book 6, Chapter A61*
   - **Contribution**: Official documentation for GWE heat transport module

8. **Langevin, C.D., et al. (2024)**
   - "MODFLOW 6 Groundwater Energy Transport (GWE) Model"
   - *U.S. Geological Survey Software Release*
   - **Contribution**: Latest GWE module version, including ESL (Energy Source Loading) package

### 2.3 g-function Method (No-Flow Scenarios)

9. **Eskilson, P. (1987)**
   - *Thermal Analysis of Heat Extraction Boreholes*
   - PhD Thesis, University of Lund, Sweden
   - **Contribution**: Foundational work on g-function method

10. **Cimmino, M., & Bernier, M. (2014)**
    - "A semi-analytical method to generate g-functions for geothermal bore fields"
    - *International Journal of Heat and Mass Transfer, 70, 641-650*
    - **Contribution**: Improved semi-analytical g-function calculation method

11. **Cimmino, M. (2018)**
    - "pygfunction: an open-source toolbox for the evaluation of thermal response factors for geothermal borehole fields"
    - *eSim 2018*
    - **Contribution**: pygfunction open-source library, used in this project for no-flow scenario validation

---

## 3. Methodology Notes

### 3.1 Applicability of POINT2 Analytical Solution

POINT2 analytical solution is based on Wexler (1992)'s 2D point source solute transport model, applied to BHE thermal response simulation through heat-solute analogy:

| Feature | Description |
|---------|-------------|
| **Dimension** | 2D (horizontal plane) |
| **Flow Field** | Uniform horizontal groundwater flow |
| **Source Term** | Point source (borehole resistance conversion) |
| **Boundary** | Infinite domain |

**Borehole Resistance (R_b) Conversion**:
- BHE exchanges heat with surrounding soil through borehole resistance R_b
- POINT2 uses injection temperature: T_inj = Q × R_b / (2πH)
- Where Q is heat load, H is borehole depth

### 3.2 Advantages of MODFLOW Numerical Solution

MODFLOW 6 GWE provides complete 3D heat transport numerical simulation:

| Feature | Description |
|---------|-------------|
| **Dimension** | 3D |
| **Flow Field** | Arbitrary non-uniform flow fields |
| **Source Term** | ESL package (Energy Source Loading) |
| **Boundary** | Flexible configuration |
| **Grid** | Supports local refinement |

### 3.3 Method Comparison

This project validated the performance of multiple methods:

| Method | Applicable Scenario | Computational Efficiency | Accuracy vs EED |
|--------|--------------------|-----------------------|-----------------|
| **pygfunction** | No-flow scenarios (EED alternative) | Fast (<1 sec) | MAE = 0.15°C, R² = 0.999 |
| **POINT2** | Uniform flow, quick assessment | Fast (~1 min) | MAE = 0.14-1.13°C |
| **MODFLOW** | Complex 3D scenarios with flow | Slower (~35-47 min) | MAE = 0.19-1.28°C |

### 3.4 pygfunction as EED Alternative

pygfunction provides an open-source alternative to commercial EED software:

| Feature | Comparison |
|---------|------------|
| **Theoretical basis** | Same g-function method as EED |
| **Accuracy** | MAE = 0.15°C compared to EED |
| **Advantages** | Open-source, scriptable, cross-platform |
| **Limitations** | No GUI, requires Python, no groundwater flow |
| **Use case** | Research, optimization workflows, reproducible analysis |

---

## 4. Key Project Findings

### 4.1 Effect of Groundwater Velocity on Thermal Response

Through comparative analysis of three velocity scenarios:

| Scenario | v (m/d) | Advection Effect | Temperature Amplitude Change |
|----------|---------|-----------------|----------------------------|
| LOW | 0.001 | Negligible | Maximum (close to no-flow) |
| MEDIUM | 0.1 | Significant | Moderate attenuation |
| HIGH | 1.0 | Dominant | Significant attenuation |

**Key Findings**: 
- Both methods correctly predict: higher velocity → smaller temperature amplitude
- Physical explanation: groundwater flow carries heat away, reducing local temperature accumulation

### 4.2 Method Consistency Validation

| Metric | POINT2 vs MODFLOW |
|--------|-------------------|
| Temperature trend | Fully consistent |
| Phase relationship | Basically consistent (difference <1 month) |
| Absolute values | Difference 1-3°C (acceptable) |

---

## 5. Recommended Reading Order

### 5.1 Groundwater Flow Impact Analysis

1. **Introduction**: Wexler (1992) - Solute transport analytical solution fundamentals
2. **Theory**: Bear (1972) - Fluid dynamics in porous media
3. **Numerical Methods**: Hughes et al. (2022) - MODFLOW GWE module
4. **Project Report**: `docs/COMPREHENSIVE_COMPARISON_EN.md`

### 5.2 No-Flow Scenarios (Supplementary)

1. **g-function Theory**: Eskilson (1987)
2. **Open-source Implementation**: Cimmino (2018) - pygfunction
3. **Project Validation**: `code/pygfunction_final.ipynb`

---

*Last Updated: December 2025*
*Author: Liuhuang Luo, AGT Intern Project*
