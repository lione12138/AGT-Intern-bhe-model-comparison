# BHE Model Comparison: EED vs pygfunction vs MODFLOW

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A comprehensive comparison study of three Borehole Heat Exchanger (BHE) temperature simulation methods for ground-source heat pump systems.

[中文版](#中文版) | [English Version](#english-version)

---

# English Version

## 🎯 Project Overview

This project compares three different approaches for simulating BHE fluid temperatures:

| Method | Type | Accuracy (MAE) | Speed |
|--------|------|----------------|-------|
| **EED** | Commercial analytical | Benchmark | <1 sec |
| **pygfunction** | Open-source analytical | 0.15°C | ~10 sec |
| **MODFLOW 6 GWE** | Numerical (FDM) | 0.084°C | ~24 min |

### Key Findings

1. ✅ **pygfunction achieves EED-equivalent accuracy** (MAE = 0.15°C) when using correct thermal properties
2. ✅ **MODFLOW with local grid refinement outperforms analytical solutions** (MAE = 0.084°C)
3. ✅ **87% accuracy improvement** achieved through optimized grid strategy

### Current Status

⚠️ **Note**: Current results are for **pure heat conduction** (no groundwater flow). Future work will incorporate groundwater flow effects to study their impact on BHE performance.

## 📁 Project Structure

```
├── README.md                    # This file
├── LICENSE                      # MIT License
├── docs/                        # Documentation (Chinese & English)
│   ├── PROJECT_SUMMARY_CN.md / EN.md
│   ├── PYGFUNCTION_ANALYSIS_CN.md / EN.md
│   ├── GRID_COMPARISON_ANALYSIS_CN.md / EN.md
│   └── POINT2_ANALYSIS_CN.md / EN.md
├── code/                        # Source code
│   ├── gfunction_pygfunction.py     # pygfunction wrapper module
│   ├── pygfunction_final.ipynb      # pygfunction analysis
│   ├── modflow_localrefined.ipynb   # MODFLOW local refined grid
│   ├── modflow_baseline.ipynb       # MODFLOW baseline (1m grid)
│   ├── plot_gfunction_curve.py      # g-function plotting
│   └── point2_correction_analysis.py # POINT2 correction analysis
├── figures/                     # Result figures
├── data/eed_output/             # EED software output
└── reference/                   # Literature references
    ├── REFERENCES_CN.md         # 参考文献 (中文)
    └── REFERENCES_EN.md         # References (English)
```

## 🔧 BHE System Parameters

| Parameter | Value | Unit |
|-----------|-------|------|
| Number of boreholes | 40 (5×8) | - |
| Borehole depth | 147 | m |
| Borehole spacing | 7.0 | m |
| Borehole diameter | 140 | mm |
| Ground thermal conductivity | 1.4 | W/(m·K) |
| Ground volumetric heat capacity | 2.83 | MJ/(m³·K) |
| Borehole thermal resistance | 0.1271 | (m·K)/W |
| Simulation period | 25 | years |

## 📊 Results

### g-function Curve

![g-function curve](figures/gfunction_curve.png)

### pygfunction vs EED (25-year comparison)

![pygfunction vs EED](figures/eed_comparison_25years.png)

### MODFLOW Grid Comparison

![Grid Comparison](figures/grid_comparison_comprehensive.png)

### MODFLOW Local Refined vs EED

![MODFLOW vs EED](figures/modflow_localref_eed_comparison.png)

### POINT2 Correction Analysis

![POINT2 Analysis](figures/point2_correction_analysis.png)

## 🚀 Quick Start

### Prerequisites

```bash
pip install numpy scipy matplotlib pandas flopy pygfunction
```

### Running pygfunction Analysis

```python
from gfunction_pygfunction import PygfunctionBHEModel

model = PygfunctionBHEModel(
    H=147.0, D=2.0, r_b=0.07, k_s=1.4, 
    rho_c_s=2.83e6, R_b=0.1271, T0=13.28
)
model.create_borehole_field(5, 8, 7.0)
model.precompute_gfunction()
T_b, T_f, time = model.calculate_monthly_temperatures(q_monthly, n_years=25)
```

## 📝 Key Technical Points

### Why Not Use POINT2 Analytical Solution?

We initially attempted using MODFLOW's POINT2 (2D point source for solute transport) for BHE simulation, but abandoned it because:
- POINT2 is 2D, cannot handle 147m deep boreholes properly
- Cannot capture thermal interference between multiple boreholes
- Systematic deviation >3°C from EED results

**Can geothermal gradient correction fix this?** No - while correction can adjust the temperature baseline, it cannot fix the response curve shape. See [POINT2 Analysis (EN)](docs/POINT2_ANALYSIS_EN.md) for detailed analysis.

**Lesson**: BHE calculations require purpose-built g-function methods that account for 3D effects.

### pygfunction Optimization

1. Use correct thermal properties: k = 1.4 W/(m·K)
2. Consider geothermal gradient: T₀_eff = 13.28°C
3. Invert EED load signs for g-function

### MODFLOW Grid Strategy

| Zone | Distance | Grid Size |
|------|----------|-----------|
| BHE | 0 m | 0.25 m |
| Transition | 1-3 m | 0.5 m |
| Intermediate | 3-10 m | 1.0 m |
| Boundary | >10 m | 2.0 m |

## 📚 References

1. Eskilson, P. (1987). Thermal Analysis of Heat Extraction Boreholes.
2. Cimmino, M. (2018). pygfunction: An open-source toolbox for g-function evaluation.
3. Langevin, C.D., et al. (2022). MODFLOW 6 GWE Module.
4. Hellström, G. (1991). Ground Heat Storage.

## 🔮 Future Work

- [ ] Incorporate groundwater flow into MODFLOW simulations
- [ ] Study groundwater flow impact on BHE performance
- [ ] Compare advection vs conduction-dominated scenarios

## 👤 Author

**Liuhuang Luo** | AGT Intern Project, December 2025

---

# 中文版

## 🎯 项目概述

本项目对比研究三种地埋管换热器(BHE)温度模拟方法：

| 方法 | 类型 | 精度 (MAE) | 速度 |
|------|------|------------|------|
| **EED** | 商业解析解 | 基准 | <1秒 |
| **pygfunction** | 开源解析解 | 0.15°C | ~10秒 |
| **MODFLOW 6 GWE** | 数值模拟(FDM) | 0.084°C | ~24分钟 |

### 主要发现

1. ✅ **pygfunction达到EED同等精度** (MAE = 0.15°C)
2. ✅ **MODFLOW局部加密网格精度超越解析解** (MAE = 0.084°C)
3. ✅ **优化网格策略实现87%精度提升**

### 当前状态

⚠️ **注意**：当前结果为**纯热传导**模拟（无地下水流动）。后续工作将加入地下水流动，研究其对BHE性能的影响。

## 📁 项目结构

```
├── README.md                    # 本文件
├── LICENSE                      # MIT许可证
├── docs/                        # 文档（中英文）
│   ├── PROJECT_SUMMARY_CN.md / EN.md      # 项目综述
│   ├── PYGFUNCTION_ANALYSIS_CN.md / EN.md # pygfunction分析
│   ├── GRID_COMPARISON_ANALYSIS_CN.md / EN.md # 网格对比
│   └── POINT2_ANALYSIS_CN.md / EN.md      # POINT2补正分析
├── code/                        # 源代码
│   ├── gfunction_pygfunction.py     # pygfunction封装模块
│   ├── pygfunction_final.ipynb      # pygfunction分析
│   ├── modflow_localrefined.ipynb   # MODFLOW局部加密网格
│   ├── modflow_baseline.ipynb       # MODFLOW基准(1m网格)
│   ├── plot_gfunction_curve.py      # g-function曲线绘制
│   └── point2_correction_analysis.py # POINT2补正分析
├── figures/                     # 结果图表
├── data/eed_output/             # EED软件输出
└── reference/                   # 参考文献
    ├── REFERENCES_CN.md         # 参考文献 (中文)
    └── REFERENCES_EN.md         # References (English)
```

## 🔧 BHE系统参数

| 参数 | 数值 | 单位 |
|------|------|------|
| 钻孔数量 | 40 (5×8) | - |
| 钻孔深度 | 147 | m |
| 钻孔间距 | 7.0 | m |
| 钻孔直径 | 140 | mm |
| 地层热导率 | 1.4 | W/(m·K) |
| 地层体积热容 | 2.83 | MJ/(m³·K) |
| 钻孔热阻 | 0.1271 | (m·K)/W |
| 模拟周期 | 25 | 年 |

## 📊 结果展示

### g-function曲线

![g-function曲线](figures/gfunction_curve.png)

### pygfunction与EED对比（25年）

![pygfunction与EED对比](figures/eed_comparison_25years.png)

### MODFLOW网格策略对比

![网格对比](figures/grid_comparison_comprehensive.png)

### MODFLOW局部加密与EED对比

![MODFLOW与EED对比](figures/modflow_localref_eed_comparison.png)

### POINT2补正方法分析

![POINT2分析](figures/point2_correction_analysis.png)

## 🚀 快速开始

### 依赖安装

```bash
pip install numpy scipy matplotlib pandas flopy pygfunction
```

### pygfunction使用示例

```python
from gfunction_pygfunction import PygfunctionBHEModel

model = PygfunctionBHEModel(
    H=147.0, D=2.0, r_b=0.07, k_s=1.4, 
    rho_c_s=2.83e6, R_b=0.1271, T0=13.28
)
model.create_borehole_field(5, 8, 7.0)
model.precompute_gfunction()
T_b, T_f, time = model.calculate_monthly_temperatures(q_monthly, n_years=25)
```

## 📝 关键技术要点

### 为什么不使用POINT2解析解？

最初尝试使用MODFLOW的POINT2（2D溶质运移点源解）模拟BHE，但放弃了：
- POINT2是2D解，无法正确处理147m深钻孔
- 无法捕捉多钻孔之间的热干扰
- 与EED系统偏差>3°C

**地热梯度补正能解决吗？** 不能——虽然补正可以调整温度基准值，但无法修正响应曲线的形状。详见 [POINT2分析文档 (CN)](docs/POINT2_ANALYSIS_CN.md)。

**启示**：BHE计算需要考虑3D效应的专用g-function方法。

### pygfunction优化要点

1. 使用正确的热物性参数：k = 1.4 W/(m·K)
2. 考虑地热梯度：T₀_eff = 13.28°C
3. g-function使用时需反转EED负荷符号

### MODFLOW网格策略

| 区域 | 距离 | 网格尺寸 |
|------|------|----------|
| BHE位置 | 0 m | 0.25 m |
| 过渡区 | 1-3 m | 0.5 m |
| 中间区 | 3-10 m | 1.0 m |
| 边界区 | >10 m | 2.0 m |

## 📚 参考文献

1. Eskilson, P. (1987). 地热钻孔热分析.
2. Cimmino, M. (2018). pygfunction: g-function开源工具箱.
3. Langevin, C.D., et al. (2022). MODFLOW 6 GWE模块.
4. Hellström, G. (1991). 地下储热系统热分析.

## 🔮 后续工作

- [ ] 在MODFLOW中加入地下水流动
- [ ] 研究地下水流动对BHE温度演化的影响
- [ ] 对比对流主导与传导主导情景

## 👤 作者

**雒鎏煌** | AGT实习项目，2025年12月

---

## 🙏 致谢

- AGT nv提供 EED 软件
- Massimo Cimmino 开发 pygfunction
- USGS 开发 MODFLOW 6 GWE
