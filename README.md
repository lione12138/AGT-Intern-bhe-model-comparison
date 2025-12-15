# BHE Groundwater Flow Sensitivity Analysis

## POINT2 Analytical vs MODFLOW Numerical vs EED Comparison

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A comprehensive comparison study of BHE (Borehole Heat Exchanger) thermal response calculation methods under various groundwater flow conditions.

[中文版](#中文版) | [English Version](#english-version)

---

# English Version

## 🎯 Project Overview

This project systematically compares **four** BHE field thermal response calculation methods:

| Method | Type | Groundwater Flow | Accuracy (MAE) | Speed |
|--------|------|------------------|----------------|-------|
| **EED** | Commercial (g-function) | ❌ No | Benchmark | <1 sec |
| **pygfunction** | Open-source (g-function) | ❌ No | 0.15°C vs EED | <1 sec |
| **POINT2** | Analytical (Wexler 1992) | ✅ Yes | 0.00-0.32°C | ~1 min |
| **MODFLOW-GWE** | Numerical (FDM) | ✅ Yes | 0.19-1.28°C | ~35-47 min |

### Key Findings

1. ✅ **Velocity Effect Validated**: Both POINT2 and MODFLOW show amplitude decrease with increasing velocity
2. ✅ **Method Consistency**: All methods agree at low velocity (v < 0.01 m/d)
3. ✅ **Physical Insight**: High velocity (1.0 m/d) reduces temperature amplitude by ~27-32%
4. ✅ **Practical Guidance**: Clear velocity thresholds for method selection
5. ✅ **Open-Source Alternative**: pygfunction provides scripted alternative to EED (MAE = 0.15°C)

### Velocity Scenarios

| Scenario | Darcy Velocity | Physical Meaning | Recommended Method |
|----------|---------------|------------------|-------------------|
| **LOW** | 0.001 m/d | Conduction-dominated | EED sufficient |
| **MEDIUM** | 0.1 m/d | Mixed transport | POINT2 validation |
| **HIGH** | 1.0 m/d | Advection-dominated | MODFLOW analysis |

## 📁 Project Structure

```
├── README.md                    # This file
├── LICENSE                      # MIT License
├── docs/                        # Documentation (Chinese & English)
│   ├── COMPREHENSIVE_COMPARISON_CN.md    # Full comparison report
│   └── COMPREHENSIVE_COMPARISON_EN.md    # Full comparison report
├── code/                        # Source code
│   ├── point2_bhe.py                     # POINT2 analytical module
│   ├── point2_groundwater_flow.ipynb     # POINT2 sensitivity analysis
│   ├── modflow_gwflow_comparison.ipynb   # MODFLOW groundwater flow analysis
│   ├── modflow_localrefined.ipynb        # MODFLOW local refined grid
│   ├── gfunction_pygfunction.py          # pygfunction wrapper (no flow)
│   ├── pygfunction_final.ipynb           # pygfunction analysis (no flow)
│   └── plot_gfunction_curve.py           # g-function plotting
├── figures/                     # Result figures
│   ├── point2_gwflow_*.png              # POINT2 results
│   └── modflow_gwflow_*.png             # MODFLOW results
├── data/eed_output/             # EED software output
└── reference/                   # Literature references
```

## 🔧 BHE System Parameters

| Parameter | Value | Unit |
|-----------|-------|------|
| Borehole array | 5 × 8 = 40 | - |
| Borehole depth H | 147 | m |
| Borehole spacing B | 7.0 | m |
| Borehole radius r_b | 0.07 | m |
| Borehole thermal resistance R_b | 0.1271 | (m·K)/W |
| Ground thermal conductivity k | 1.4 | W/(m·K) |
| Volumetric heat capacity ρc | 2.83 | MJ/(m³·K) |
| Porosity n | 0.2 | - |
| Effective ground temperature T₀_eff | 13.28 | °C |
| Simulation period | 25 | years |

## 📊 Results

### Temperature Time Series Comparison

The following figures show the 3-method comparison (EED, POINT2, MODFLOW) for each velocity scenario:

**LOW Scenario (v = 0.001 m/d):**

![3-Method LOW](figures/comparison_3methods_low.png)

**MEDIUM Scenario (v = 0.1 m/d):**

![3-Method MEDIUM](figures/comparison_3methods_medium.png)

**HIGH Scenario (v = 1.0 m/d):**

![3-Method HIGH](figures/comparison_3methods_high.png)

### Error Analysis vs EED

| Method | LOW (0.001 m/d) | MEDIUM (0.1 m/d) | HIGH (1.0 m/d) |
|--------|-----------------|------------------|----------------|
| **POINT2** | MAE=0.14°C | MAE=0.23°C | MAE=1.13°C |
| **MODFLOW** | MAE=0.19°C | MAE=0.44°C | MAE=1.28°C |

### Temperature Amplitude Comparison (Stabilized, Last 5 Years)

| Method | LOW (0.001 m/d) | MEDIUM (0.1 m/d) | HIGH (1.0 m/d) |
|--------|-----------------|------------------|----------------|
| **EED** | 7.70°C | N/A | N/A |
| **POINT2** | 8.19°C | 7.14°C | **4.93°C** |
| **MODFLOW** | 8.55°C | 6.33°C | **3.07°C** |

### pygfunction vs EED Validation

![pygfunction vs EED](figures/final_comparison_line_chart.png)

| Metric | Value |
|--------|-------|
| MAE | **0.15°C** |
| R² | **0.999** |
| Max Error | 0.32°C |

**Conclusion**: pygfunction can serve as an open-source, scripted alternative to EED for research purposes.

### Key Physical Findings

1. **Amplitude Reduction**: Both methods confirm 27-32% amplitude reduction at high velocity
2. **Phase Shift**: Temperature extremes shift from JAN/AUG to DEC/JUL at high velocity
3. **Method Divergence**: POINT2 (2D) and MODFLOW (3D) diverge at high velocity due to dimensional differences

## 🚀 Quick Start

### Prerequisites

```bash
pip install numpy scipy matplotlib pandas flopy
```

### Running POINT2 Analysis

```python
# See point2_groundwater_flow.ipynb for complete example

from point2_bhe import bhe, ground_to_fluid_temperature

# Calculate temperature at observation point
dT_ground = bhe(Finj, obs_x, obs_y, t_out, bhe_x, bhe_y, 
                v_pore, n, rho_s, c_s, k_s, T0=0.0)

# Convert to fluid temperature
T_fluid = T0_eff + dT_ground + q * R_b
```

### Running MODFLOW Analysis

```python
# See modflow_gwflow_comparison.ipynb for complete example

import flopy

# Create MODFLOW 6 GWE model with ESL (Energy Source Loading)
gwe = flopy.mf6.ModflowGwe(sim, modelname=gwe_name)
flopy.mf6.ModflowGweesl(gwe, stress_period_data=eslrec)  # BHE loads
```

## 📝 Method Comparison

### When to Use Each Method

| Velocity | Recommended Method | Reason |
|----------|-------------------|--------|
| v < 0.01 m/d | **EED** | Advection negligible, fast |
| 0.01-0.5 m/d | **POINT2** | Quick sensitivity analysis |
| v > 0.5 m/d | **MODFLOW** | 3D effects important |

### Method Characteristics

| Feature | EED | pygfunction | POINT2 | MODFLOW |
|---------|-----|-------------|--------|---------|
| **Dimension** | 3D (FLS) | 3D (FLS) | 2D | 3D (33 layers) |
| **Groundwater Flow** | ❌ | ❌ | ✅ | ✅ |
| **License** | Commercial | Open-source | Open-source | Open-source |
| **Spatial Output** | Single value | Single value | Single point | Full field |
| **Computation** | <1 sec | <1 sec | ~1 min | ~35-47 min |

### pygfunction: Open-Source Alternative to EED

pygfunction provides a scripted, open-source alternative to EED for g-function based calculations:

```python
# See pygfunction_final.ipynb for complete example
import pygfunction as gt

# Create borehole field
boreholes = gt.boreholes.rectangle_field(N_1=5, N_2=8, B_1=7, B_2=7, H=147, D=0, r_b=0.07)

# Calculate g-function
gfunc = gt.gfunction.gFunction(boreholes, alpha, time)

# Temperature calculation
T_fluid = T0_eff + sum(dq * g) / (2*pi*k*H) + q * R_b
```

**Key advantage**: Full access to g-function values and intermediate calculations for research purposes.

## 📚 References

1. Wexler, E.J. (1992). Analytical solutions for solute transport. USGS TWRI 03-B7.
2. Eskilson, P. (1987). Thermal Analysis of Heat Extraction Boreholes.
3. Langevin, C.D., et al. (2022). MODFLOW 6 GWE Module.
4. Cimmino, M. (2018). pygfunction: An open-source toolbox for g-function evaluation.

## 👤 Author

**Liuhuang Luo** | AGT Intern Project, December 2025

---

# 中文版

## 🎯 项目概述

本项目对**四种**BHE（地埋管换热器）场热响应计算方法进行了系统对比：

| 方法 | 类型 | 地下水流动 | 精度 (MAE) | 速度 |
|------|------|-----------|------------|------|
| **EED** | 商业软件 (g-function) | ❌ 不考虑 | 基准 | <1秒 |
| **pygfunction** | 开源 (g-function) | ❌ 不考虑 | 0.15°C vs EED | <1秒 |
| **POINT2** | 解析解 (Wexler 1992) | ✅ 考虑 | 0.00-0.32°C | ~1分钟 |
| **MODFLOW-GWE** | 数值模拟 (FDM) | ✅ 考虑 | 0.19-1.28°C | ~35-47分钟 |

### 主要发现

1. ✅ **流速效应验证**：POINT2和MODFLOW都显示流速增加→振幅减小
2. ✅ **方法一致性**：低流速下所有方法结果一致
3. ✅ **物理规律**：高流速(1.0 m/d)使温度振幅减少约27-32%
4. ✅ **实用指导**：明确的流速阈值用于方法选择
5. ✅ **开源替代方案**：pygfunction提供EED的脚本化替代方案 (MAE = 0.15°C)

### 流速场景

| 场景 | Darcy流速 | 物理意义 | 推荐方法 |
|------|-----------|----------|----------|
| **LOW** | 0.001 m/d | 传导主导 | EED足够 |
| **MEDIUM** | 0.1 m/d | 混合传热 | POINT2验证 |
| **HIGH** | 1.0 m/d | 对流主导 | MODFLOW分析 |

## 📁 项目结构

```
├── README.md                    # 本文件
├── LICENSE                      # MIT许可证
├── docs/                        # 文档（中英文）
│   ├── COMPREHENSIVE_COMPARISON_CN.md    # 完整对比报告
│   └── COMPREHENSIVE_COMPARISON_EN.md    # 完整对比报告
├── code/                        # 源代码
│   ├── point2_bhe.py                     # POINT2解析解模块
│   ├── point2_groundwater_flow.ipynb     # POINT2敏感性分析
│   ├── modflow_gwflow_comparison.ipynb   # MODFLOW地下水流分析
│   ├── modflow_localrefined.ipynb        # MODFLOW局部加密网格
│   ├── gfunction_pygfunction.py          # pygfunction封装（无流动）
│   ├── pygfunction_final.ipynb           # pygfunction分析（无流动）
│   └── plot_gfunction_curve.py           # g-function曲线绘制
├── figures/                     # 结果图片
├── data/eed_output/             # EED软件输出
└── reference/                   # 参考文献
```

## 📊 结果

### 温度时序对比

以下图形展示了三种方法（EED、POINT2、MODFLOW）在各流速场景下的对比：

**LOW场景 (v = 0.001 m/d):**

![3方法对比 LOW](figures/comparison_3methods_low.png)

**MEDIUM场景 (v = 0.1 m/d):**

![3方法对比 MEDIUM](figures/comparison_3methods_medium.png)

**HIGH场景 (v = 1.0 m/d):**

![3方法对比 HIGH](figures/comparison_3methods_high.png)

### 与EED的误差分析

| 方法 | LOW (0.001 m/d) | MEDIUM (0.1 m/d) | HIGH (1.0 m/d) |
|------|-----------------|------------------|----------------|
| **POINT2** | MAE=0.14°C | MAE=0.23°C | MAE=1.13°C |
| **MODFLOW** | MAE=0.19°C | MAE=0.44°C | MAE=1.28°C |

### 温度振幅对比（稳定后，最后5年）

| 方法 | LOW (0.001 m/d) | MEDIUM (0.1 m/d) | HIGH (1.0 m/d) |
|------|-----------------|------------------|----------------|
| **EED** | 7.70°C | N/A | N/A |
| **POINT2** | 8.19°C | 7.14°C | **4.93°C** |
| **MODFLOW** | 8.55°C | 6.33°C | **3.07°C** |

### pygfunction与EED验证

![pygfunction与EED对比](figures/final_comparison_line_chart.png)

| 指标 | 数值 |
|------|------|
| MAE | **0.15°C** |
| R² | **0.999** |
| 最大误差 | 0.32°C |

**结论**：pygfunction可作为EED的开源脚本化替代方案用于研究目的。

## 🔧 BHE系统参数

| 参数 | 数值 | 单位 |
|------|------|------|
| 钻孔阵列 | 5 × 8 = 40 | - |
| 钻孔深度 H | 147 | m |
| 钻孔间距 B | 7.0 | m |
| 钻孔热阻 R_b | 0.1271 | (m·K)/W |
| 地层导热系数 k | 1.4 | W/(m·K) |
| 容积热容 ρc | 2.83 | MJ/(m³·K) |
| 孔隙度 n | 0.2 | - |
| 有效地温 T₀_eff | 13.28 | °C |
| 模拟周期 | 25 | 年 |

## 📝 方法选择指南

| 流速范围 | 推荐方法 | 原因 |
|----------|----------|------|
| v < 0.01 m/d | **EED** | 对流可忽略，快速 |
| 0.01-0.5 m/d | **POINT2** | 快速敏感性分析 |
| v > 0.5 m/d | **MODFLOW** | 3D效应重要 |

## 📚 参考文献

1. Wexler, E.J. (1992). USGS TWRI 03-B7 溶质运移解析解
2. Eskilson, P. (1987). 地埋管热分析
3. Langevin, C.D., et al. (2022). MODFLOW 6 GWE模块
4. Cimmino, M. (2018). pygfunction开源工具箱

## 👤 作者

**雒鎏煌** | AGT实习项目，2025年12月

---

*详细技术分析请参见 [docs/COMPREHENSIVE_COMPARISON_CN.md](docs/COMPREHENSIVE_COMPARISON_CN.md)*
