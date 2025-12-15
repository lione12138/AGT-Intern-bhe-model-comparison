# BHE Modeling Methods Comprehensive Comparison

## Point2 Analytical vs 2D/3D MODFLOW Numerical vs pygfunction vs EED

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A comprehensive comparison study of **five** BHE (Borehole Heat Exchanger) thermal response calculation methods under various groundwater flow conditions.

[中文版](#中文版) | [English Version](#english-version)

---

# English Version

## 🎯 Project Overview

This project systematically compares **five** BHE field thermal response calculation methods:

| Method | Type | Groundwater Flow | Dimension | Accuracy (MAE vs EED) | Speed |
|--------|------|------------------|-----------|----------------------|-------|
| **EED** | Commercial (g-function) | ❌ No | 2D axisymmetric | Benchmark | <1 min |
| **pygfunction** | Open-source (g-function) | ❌ No | 2D axisymmetric | 0.15°C | 2-5 min |
| **Point2** | Analytical (Wexler 1992) | ✅ Yes | 2D planar | 0.00-0.32°C | <1 min |
| **2D MODFLOW** | Numerical (FDM) | ✅ Yes | 2D planar | 0.07-0.41°C | 1-3 min |
| **3D MODFLOW** | Numerical (FDM) | ✅ Yes | 3D (33 layers) | 0.19-1.28°C | 20-40 hrs |

### Key Findings

1. ✅ **Point2** matches EED perfectly at low velocity (MAE=0.002°C)
2. ✅ **2D MODFLOW** performs best at medium velocity (MAE=0.069°C)
3. ✅ **3D MODFLOW** shows significant deviation at high velocity due to 3D advection effects
4. ✅ **pygfunction** can serve as open-source alternative to EED (MAE=0.15°C, R²=0.995)
5. ✅ **Velocity Effect**: Higher groundwater velocity → smaller temperature amplitude

### Velocity Scenarios

| Scenario | Darcy Velocity | Physical Meaning | Best Method |
|----------|---------------|------------------|-------------|
| **LOW** | 0.001 m/d | Conduction-dominated | Point2 / pygfunction |
| **MEDIUM** | 0.1 m/d | Mixed transport | 2D MODFLOW |
| **HIGH** | 1.0 m/d | Advection-dominated | 2D MODFLOW |

## 📁 Project Structure

```
├── README.md                              # This file
├── LICENSE                                # MIT License
├── docs/                                  # Documentation
│   ├── BHE_MODELING_COMPARISON_REPORT_CN.md   # Full comparison report (Chinese)
│   ├── BHE_MODELING_COMPARISON_REPORT_EN.md   # Full comparison report (English)
│   └── ...
├── code/                                  # Source code
│   ├── point2_bhe.py                      # Point2 analytical solution module
│   ├── point2_groundwater_flow.ipynb      # Point2 groundwater flow analysis
│   ├── modflow_2D.py                      # 2D MODFLOW single-layer model
│   ├── modflow_3D_localrefined.ipynb      # 3D MODFLOW with local grid refinement
│   ├── modflow_3D_gwflow_comparison.ipynb # 3D MODFLOW results visualization
│   ├── gfunction_pygfunction.py           # pygfunction BHE model class
│   ├── pygfunction_final.ipynb            # pygfunction analysis notebook
│   ├── plot_comparison_figures.py         # Generate comparison figures
│   └── plot_gfunction_curve.py            # Plot g-function curve
├── figures/                               # Result figures
│   ├── comparison_point2_2Dmodflow_eed.png
│   ├── comparison_2Dmodflow_3Dmodflow_eed.png
│   ├── comparison_pygfunction_eed.png
│   ├── gfunction_curve.png
│   └── ...
├── workspace/                             # Simulation results (JSON)
│   ├── point2_gwflow_*_results.json
│   ├── modflow_2d_*_results.json
│   ├── modflow_gwflow_*_results.json
│   └── ...
├── data/eed_output/                       # EED software reference output
└── reference/                             # Literature references
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
| Hydraulic conductivity K | 10.0 | m/d |
| Surface temperature T₀ | 9.6 | °C |
| Geothermal heat flux | 0.07 | W/m² |
| Simulation period | 25 | years |

## 📊 Results

### Figure 1: Point2 vs 2D MODFLOW vs EED

![Point2 vs 2D MODFLOW vs EED](figures/comparison_point2_2Dmodflow_eed.png)

| Scenario | Point2 MAE | 2D MODFLOW MAE | Point2 Amp | 2D MODFLOW Amp | EED Amp |
|:--------:|:----------:|:--------------:|:----------:|:--------------:|:-------:|
| LOW | 0.002°C | 0.365°C | 7.70°C | 9.09°C | 7.70°C |
| MEDIUM | 0.319°C | 0.069°C | 6.62°C | 7.98°C | 7.70°C |
| HIGH | 0.314°C | 0.406°C | 8.84°C | 6.37°C | 7.70°C |

### Figure 2: 2D MODFLOW vs 3D MODFLOW vs EED

![2D vs 3D MODFLOW vs EED](figures/comparison_2Dmodflow_3Dmodflow_eed.png)

| Scenario | 2D MODFLOW MAE | 3D MODFLOW MAE | 2D Amp | 3D Amp | EED Amp |
|:--------:|:--------------:|:--------------:|:------:|:------:|:-------:|
| LOW | 0.365°C | 0.187°C | 9.09°C | 8.39°C | 7.70°C |
| MEDIUM | 0.069°C | 0.440°C | 7.98°C | 6.23°C | 7.70°C |
| HIGH | 0.406°C | 1.279°C | 6.37°C | 3.08°C | 7.70°C |

**Key Finding**: 2D MODFLOW outperforms 3D at medium/high velocity by avoiding excessive 3D advection effects.

### Figure 3: pygfunction vs EED (No Groundwater Flow)

![pygfunction vs EED](figures/comparison_pygfunction_eed.png)

| Metric | pygfunction | EED | Deviation |
|:------:|:-----------:|:---:|:---------:|
| MAE | - | - | 0.147°C |
| R² | 0.995 | - | - |
| Amplitude | 7.33°C | 7.70°C | -0.37°C |

**Conclusion**: pygfunction is a valid open-source alternative to EED.

### Figure 4: g-function Curve

![g-function Curve](figures/gfunction_curve.png)

## 📝 Method Selection Guide

| Flow Velocity | Recommended Method | Reason |
|---------------|-------------------|--------|
| No flow | **pygfunction** / EED | g-function method, fast and accurate |
| v < 0.01 m/d | **Point2** | Analytical solution, highly accurate |
| 0.01-0.1 m/d | **2D MODFLOW** | Best accuracy, moderate computation |
| v > 0.1 m/d | **2D MODFLOW** | Avoids 3D advection overestimation |
| Complex geology | **3D MODFLOW** | Flexible material zoning |

## 🚀 Quick Start

### Prerequisites

```bash
pip install numpy scipy matplotlib flopy pygfunction
```

### Running Point2 Analysis

```python
from point2_bhe import point2, bhe

# Calculate temperature field for BHE array
dT_ground = bhe(Finj, obs_x, obs_y, t_out, bhe_x, bhe_y, 
                v_pore, n, rho_s, c_s, k_s, T0=0.0)

# Convert to fluid temperature
T_fluid = T0_eff + dT_ground + q * R_b
```

### Running 2D MODFLOW

```bash
cd code
python modflow_2D.py
```

### Running pygfunction

```python
import pygfunction as gt

# Create borehole field
boreholes = gt.boreholes.rectangle_field(5, 8, 7, 7, 147, 0, 0.07)

# Calculate g-function
gfunc = gt.gfunction.gFunction(boreholes, alpha, time)
```

## 📚 References

1. Eskilson, P. (1987). *Thermal Analysis of Heat Extraction Boreholes*. Lund University.
2. Cimmino, M. (2018). pygfunction: An open-source toolbox for g-function evaluation. *MethodsX*, 5, 1199-1213.
3. Wexler, E.J. (1992). Analytical solutions for solute transport. *USGS TWRI 03-B7*.
4. Hughes, J.D., et al. (2023). MODFLOW 6 GWE Module Documentation.

## 👤 Author

**Liuhuang Luo** | AGT Intern Project, December 2025

---

# 中文版

## 🎯 项目概述

本项目系统对比了**五种**BHE（地埋管换热器）场热响应计算方法：

| 方法 | 类型 | 地下水流动 | 维度 | 精度 (MAE vs EED) | 速度 |
|------|------|-----------|------|------------------|------|
| **EED** | 商业软件 (g-function) | ❌ 不考虑 | 2D轴对称 | 基准 | <1分钟 |
| **pygfunction** | 开源 (g-function) | ❌ 不考虑 | 2D轴对称 | 0.15°C | 2-5分钟 |
| **Point2** | 解析解 (Wexler 1992) | ✅ 考虑 | 2D平面 | 0.00-0.32°C | <1分钟 |
| **2D MODFLOW** | 数值模拟 (FDM) | ✅ 考虑 | 2D平面 | 0.07-0.41°C | 1-3分钟 |
| **3D MODFLOW** | 数值模拟 (FDM) | ✅ 考虑 | 3D (33层) | 0.19-1.28°C | 20-40小时 |

### 主要发现

1. ✅ **Point2** 在低流速下与EED完全一致 (MAE=0.002°C)
2. ✅ **2D MODFLOW** 在中等流速下表现最佳 (MAE=0.069°C)
3. ✅ **3D MODFLOW** 在高流速下偏差显著（3D对流效应过度）
4. ✅ **pygfunction** 可作为EED的开源替代 (MAE=0.15°C, R²=0.995)
5. ✅ **流速效应**: 地下水流速越高→温度振幅越小

### 流速场景

| 场景 | Darcy流速 | 物理意义 | 最佳方法 |
|------|-----------|----------|----------|
| **LOW** | 0.001 m/d | 传导主导 | Point2 / pygfunction |
| **MEDIUM** | 0.1 m/d | 混合传热 | 2D MODFLOW |
| **HIGH** | 1.0 m/d | 对流主导 | 2D MODFLOW |

## 📁 项目结构

```
├── README.md                              # 本文件
├── LICENSE                                # MIT许可证
├── docs/                                  # 文档
│   ├── BHE_MODELING_COMPARISON_REPORT_CN.md   # 完整对比报告（中文）
│   ├── BHE_MODELING_COMPARISON_REPORT_EN.md   # 完整对比报告（英文）
│   └── ...
├── code/                                  # 源代码
│   ├── point2_bhe.py                      # Point2解析解模块
│   ├── point2_groundwater_flow.ipynb      # Point2地下水流分析
│   ├── modflow_2D.py                      # 2D MODFLOW单层模型
│   ├── modflow_3D_localrefined.ipynb      # 3D MODFLOW局部细化网格
│   ├── modflow_3D_gwflow_comparison.ipynb # 3D MODFLOW结果可视化
│   ├── gfunction_pygfunction.py           # pygfunction BHE模型类
│   ├── pygfunction_final.ipynb            # pygfunction分析笔记本
│   ├── plot_comparison_figures.py         # 生成对比图
│   └── plot_gfunction_curve.py            # 绘制g-function曲线
├── figures/                               # 结果图片
├── workspace/                             # 模拟结果（JSON）
├── data/eed_output/                       # EED软件参考输出
└── reference/                             # 参考文献
```

## 📊 结果

### 图1: Point2 vs 2D MODFLOW vs EED

![Point2 vs 2D MODFLOW vs EED](figures/comparison_point2_2Dmodflow_eed.png)

### 图2: 2D MODFLOW vs 3D MODFLOW vs EED

![2D vs 3D MODFLOW vs EED](figures/comparison_2Dmodflow_3Dmodflow_eed.png)

**关键发现**: 2D MODFLOW在中/高流速下优于3D，因为避免了过度的3D对流效应。

### 图3: pygfunction vs EED（无地下水流动）

![pygfunction vs EED](figures/comparison_pygfunction_eed.png)

**结论**: pygfunction可作为EED的有效开源替代方案。

## 📝 方法选择指南

| 流速范围 | 推荐方法 | 原因 |
|----------|----------|------|
| 无流动 | **pygfunction** / EED | g-function方法，快速准确 |
| v < 0.01 m/d | **Point2** | 解析解，精度极高 |
| 0.01-0.1 m/d | **2D MODFLOW** | 精度最高，计算适中 |
| v > 0.1 m/d | **2D MODFLOW** | 避免3D对流过估 |
| 复杂地质 | **3D MODFLOW** | 灵活的材料分区 |

## 📚 参考文献

1. Eskilson, P. (1987). 地埋管热分析. 隆德大学.
2. Cimmino, M. (2018). pygfunction开源工具箱. *MethodsX*, 5, 1199-1213.
3. Wexler, E.J. (1992). 溶质运移解析解. *USGS TWRI 03-B7*.
4. Hughes, J.D., et al. (2023). MODFLOW 6 GWE模块文档.

## 👤 作者

**雒鎏煌** | AGT实习项目，2025年12月

---

*详细技术分析请参见 [docs/BHE_MODELING_COMPARISON_REPORT_CN.md](docs/BHE_MODELING_COMPARISON_REPORT_CN.md)*
