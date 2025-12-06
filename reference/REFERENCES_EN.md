# Reference Documentation

---

## Methods Overview

This project compares three BHE (Borehole Heat Exchanger) temperature simulation methods:

| Method | Type | Theoretical Basis | Developer/Source |
|--------|------|-------------------|------------------|
| **EED** | Commercial software | g-function (Eskilson 1987) | BLOCON (Sweden) |
| **pygfunction** | Open-source Python library | g-function (Eskilson 1987) | Massimo Cimmino (Canada) |
| **MODFLOW 6 GWE** | Open-source numerical simulation | Finite Difference Method (3D) | USGS (USA) |

### Relationship Between EED and pygfunction

**Important Notes**:
- **EED** is commercial software requiring a license purchase
- **pygfunction** is an independently developed open-source alternative (MIT License)
- Both are based on the **same physical theory** (Eskilson's g-function method)
- pygfunction is **NOT** released by BLOCON (the EED company)
- Using pygfunction to implement g-function calculations is completely legal — the g-function theory is publicly available academic work

This project achieved nearly identical accuracy to EED using pygfunction (MAE = 0.15°C), validating the viability of the open-source approach.

---

## Online Resources

### pygfunction
- **GitHub Repository**: https://github.com/MassimoCimmino/pygfunction
- **Documentation**: https://pygfunction.readthedocs.io/
- **PyPI**: https://pypi.org/project/pygfunction/
- **DOI**: https://zenodo.org/badge/latestdoi/100305705
- **Author**: Massimo Cimmino, Polytechnique Montréal, Canada

### MODFLOW 6 GWE (Groundwater Energy Transport)
- **USGS Official Documentation**: https://www.usgs.gov/software/modflow-6-usgs-modular-hydrologic-model
- **GWE Module Guide**: https://modflow6.readthedocs.io/en/latest/
- **FloPy (Python interface)**: https://github.com/modflowpy/flopy

### EED (Earth Energy Designer)
- **BLOCON Official Website**: https://buildingphysics.com/eed-2/
- **Software Manual**: Available from BLOCON website with license
- **Note**: Commercial software requiring license purchase

---

## 1. Theoretical Basis of g-function Method

### 1.1 Core Concept

The g-function is a dimensionless response function describing the long-term thermal response of borehole heat exchangers.

**Basic Formula**:
$$T_b(t) = T_0 + \frac{q}{2\pi k H} \cdot g\left(\frac{t}{t_s}, \frac{r_b}{H}, \frac{B}{H}\right)$$

Where:
- $T_b$ = Borehole wall temperature [°C]
- $T_0$ = Undisturbed ground temperature [°C]
- $q$ = Heat transfer rate per unit length [W/m]
- $k$ = Ground thermal conductivity [W/(m·K)]
- $H$ = Borehole depth [m]
- $g$ = g-function value [-]
- $t_s = H^2/(9\alpha)$ = Characteristic time [s]
- $\alpha$ = Thermal diffusivity [m²/s]

**Fluid Temperature**:
$$T_f(t) = T_b(t) + q \cdot R_b$$

Where $R_b$ = Borehole thermal resistance [(m·K)/W]

### 1.2 Physical Significance of g-function

The g-function accounts for:
1. **Finite Line Source Effect** - Finite borehole depth
2. **Constant Surface Boundary** - Image source method
3. **Multi-borehole Thermal Interference** - Superposition between boreholes
4. **Temporal Evolution** - Response from short-term to long-term (decades)

### 1.3 Implementation Differences: EED vs pygfunction

| Feature | EED | pygfunction |
|---------|-----|-------------|
| g-function calculation | Pre-computed tables + interpolation | Real-time numerical integration |
| Borehole configuration | Predefined templates | Fully customizable |
| Speed | Very fast (table lookup) | Slower (requires calculation) |
| Flexibility | Limited | Highly flexible |
| Accuracy | High | High (verifiable) |

---

## 2. Key References

### 2.1 Foundational Works on g-function Method

1. **Eskilson, P. (1987)** ⭐ Core Reference
   - "Thermal Analysis of Heat Extraction Boreholes"
   - *PhD Thesis, Lund University, Sweden*
   - **Contribution**: Established the g-function method, theoretical foundation for both EED and pygfunction
   - **Note**: One of the most important works in BHE field

2. **Claesson, J. & Eskilson, P. (1988)**
   - "Conductive Heat Extraction to a Deep Borehole: Thermal Analyses and Dimensioning Rules"
   - *Energy, Vol. 13, No. 6, pp. 509-527*
   - **Contribution**: Refined analytical solution for single borehole

3. **Hellström, G. (1991)**
   - "Ground Heat Storage: Thermal Analyses of Duct Storage Systems"
   - *PhD Thesis, Lund University, Sweden*
   - **Contribution**: Developed multi-borehole system analysis and borehole thermal resistance theory

### 2.2 pygfunction Related Publications

4. **Cimmino, M. & Bernier, M. (2014)**
   - "A semi-analytical method to generate g-functions for geothermal bore fields"
   - *International Journal of Heat and Mass Transfer, Vol. 70, pp. 641-650*
   - **Contribution**: Semi-analytical method used in pygfunction

5. **Cimmino, M. (2018)**
   - "Fast calculation of the g-functions of geothermal borehole fields using similarities in the evaluation of the finite line source solution"
   - *Journal of Building Performance Simulation, Vol. 11, No. 6, pp. 655-668*
   - **Contribution**: Fast g-function calculation algorithm

6. **Cimmino, M. (2019)**
   - "pygfunction 2.1: An open-source toolbox for the evaluation of thermal response factors for geothermal borehole fields"
   - *MethodsX, Vol. 8, 101249*
   - **Contribution**: Official documentation paper for pygfunction library

### 2.3 Borehole Thermal Resistance Theory

7. **Mogensen, P. (1983)**
   - "Fluid to Duct Wall Heat Transfer in Duct System Heat Storages"
   - *Proceedings of the International Conference on Subsurface Heat Storage*
   - Stockholm, Sweden, pp. 652-657
   - **Contribution**: First proposed borehole thermal resistance concept

8. **Gehlin, S. (2002)**
   - "Thermal Response Test: Method Development and Evaluation"
   - *PhD Thesis, Luleå University of Technology, Sweden*
   - **Online**: http://urn.kb.se/resolve?urn=urn:nbn:se:ltu:diva-18295
   - **Contribution**: Systematic summary of TRT methods

### 2.4 MODFLOW Related Publications

9. **Langevin, C.D., et al. (2022)**
   - "MODFLOW 6 Modular Hydrologic Model version 6.4.1"
   - *U.S. Geological Survey Software Release*
   - https://doi.org/10.5066/P9FL1JCC

10. **Hughes, J.D., et al. (2022)**
    - "MODFLOW 6 Groundwater Energy Transport (GWE) Module"
    - *U.S. Geological Survey Techniques and Methods, Book 6, Chapter A61*
    - **Contribution**: Official documentation for GWE module

### 2.5 POINT2 Analytical Solution (Early Attempt)

11. **Wexler, E.J. (1992)**
    - "Analytical Solutions for One-, Two-, and Three-Dimensional Solute Transport in Ground-Water Systems with Uniform Flow"
    - *U.S. Geological Survey, Techniques of Water-Resources Investigations, Book 3, Chapter B7*
    - https://pubs.usgs.gov/twri/twri3-b7/
    - **Note**: Early attempt in this project, abandoned due to 2D limitations

---

## 3. Methodology Notes

### 3.1 Why Was POINT2 Analytical Solution Abandoned?

We initially attempted using POINT2 (2D point source solute transport solution) for BHE simulation, but abandoned it:

| Issue | Explanation |
|-------|-------------|
| **2D Limitation** | Cannot handle vertical effects of 147m deep boreholes |
| **No Boundary Effects** | Ignores "image effect" from constant surface temperature |
| **Insufficient Accuracy** | Deviation from EED > 3°C |

**Attempted Correction**: Geothermal gradient correction
- Conclusion: Can only adjust temperature baseline, cannot correct response curve shape
- Long-term (25 years) error remains > 30%

See: `docs/POINT2_ANALYSIS_EN.md`

### 3.2 Why Does g-function Method Work?

The g-function method (used by both EED and pygfunction) accounts for:
1. ✓ Finite borehole depth (Finite Line Source, not point source)
2. ✓ Constant surface temperature boundary (Image source method)
3. ✓ Multi-borehole thermal interference (Response superposition)
4. ✓ Long-term thermal evolution (Characteristic time scale)

These are exactly the 3D effects that POINT2 lacks.

### 3.3 Advantages of MODFLOW Numerical Method

Compared to analytical methods, MODFLOW 6 GWE provides:
1. ✓ Full 3D simulation
2. ✓ Arbitrary boundary conditions
3. ✓ Extensible to groundwater flow scenarios
4. ✓ Local grid refinement technique

---

## 4. Project Contributions

### 4.1 Validation Results

| Method | MAE vs EED | Conclusion |
|--------|------------|------------|
| pygfunction | 0.15°C | ✓ Can replace EED commercial software |
| MODFLOW (local refinement) | 0.084°C | ✓ Accuracy exceeds analytical methods |
| POINT2 + correction | > 3°C | ✗ Not suitable for BHE |

### 4.2 Practical Significance

1. **Open-source Alternative**: pygfunction can replace EED for g-function calculations
2. **Numerical Validation**: MODFLOW provides independent numerical verification
3. **Methodology**: Clarified limitations of 2D analytical solutions

---

## 5. Recommended Reading Order

For readers wanting to deeply understand BHE modeling:

1. **Introduction**: Gehlin (2002) - TRT method overview
2. **Core Theory**: Eskilson (1987) - g-function principles
3. **Implementation Details**: Cimmino (2018, 2019) - pygfunction algorithms
4. **Numerical Methods**: Hughes et al. (2022) - MODFLOW GWE

---

*Last Updated: December 2025*
*Author: AGT Intern Project*
