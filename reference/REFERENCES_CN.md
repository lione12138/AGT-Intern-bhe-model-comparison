# BHE地下水流影响建模文献综述

## 项目概述

本项目对比分析了**POINT2解析解**和**MODFLOW数值解**在模拟地下水流对钻孔换热器(BHE)影响方面的表现。两种方法均可有效捕捉地下水流速对热响应的影响规律。

---

## 1. 核心理论基础

### 1.1 热能传输理论

1. **Carslaw, H.S., & Jaeger, J.C. (1959)**
   - *Conduction of Heat in Solids* (Second Edition)
   - Oxford University Press
   - **贡献**: 热传导基本理论，包括无限线源解和点源解

2. **Ingersoll, L.R., Zobel, O.J., & Ingersoll, A.C. (1954)**
   - *Heat Conduction with Engineering, Geological, and Other Applications*
   - McGraw-Hill
   - **贡献**: 工程应用中的热传导分析方法

### 1.2 溶质/热量迁移理论

3. **Wexler, E.J. (1992)**
   - "Analytical Solutions for One-, Two-, and Three-Dimensional Solute Transport in Ground-Water Systems with Uniform Flow"
   - *U.S. Geological Survey, Techniques of Water-Resources Investigations, Book 3, Chapter B7*
   - https://pubs.usgs.gov/twri/twri3-b7/
   - **贡献**: 提供了POINT2解析解的理论基础——均匀流场中点源溶质迁移的解析解

---

## 2. 方法论文献

### 2.1 POINT2解析解方法

4. **Bear, J. (1972)**
   - *Dynamics of Fluids in Porous Media*
   - American Elsevier
   - **贡献**: 多孔介质流体力学基础理论

5. **Domenico, P.A., & Schwartz, F.W. (1990)**
   - *Physical and Chemical Hydrogeology*
   - John Wiley & Sons
   - **贡献**: 溶质迁移与热量迁移的类比方法（热-溶质转换原理）

**热-溶质类比原理**:
| 溶质迁移参数 | 对应热量迁移参数 |
|-------------|----------------|
| 浓度 C | 温度变化 ΔT |
| 扩散系数 D | 热扩散率 α |
| 达西流速 v | 达西流速 × (ρw·cw)/(ρs·cs) |
| 点源质量 M | 点源热量 Q / (ρs·cs) |

### 2.2 MODFLOW数值方法

6. **Langevin, C.D., et al. (2017)**
   - "Documentation for the MODFLOW 6 Groundwater Flow Model"
   - *U.S. Geological Survey Techniques and Methods, Book 6, Chapter A55*
   - https://doi.org/10.3133/tm6A55
   - **贡献**: MODFLOW 6核心流动模型文档

7. **Hughes, J.D., et al. (2022)**
   - "Documentation for the MODFLOW 6 Groundwater Energy Transport (GWE) Model"
   - *U.S. Geological Survey Techniques and Methods, Book 6, Chapter A61*
   - **贡献**: GWE热量传输模块官方文档

8. **Langevin, C.D., et al. (2024)**
   - "MODFLOW 6 Groundwater Energy Transport (GWE) Model"
   - *U.S. Geological Survey Software Release*
   - **贡献**: GWE模块最新版本，包含ESL（能量源载荷）包

### 2.3 g-function方法（无流场景）

9. **Eskilson, P. (1987)**
   - *Thermal Analysis of Heat Extraction Boreholes*
   - PhD Thesis, University of Lund, Sweden
   - **贡献**: g-function方法的奠基之作

10. **Cimmino, M., & Bernier, M. (2014)**
    - "A semi-analytical method to generate g-functions for geothermal bore fields"
    - *International Journal of Heat and Mass Transfer, 70, 641-650*
    - **贡献**: 改进的g-function半解析计算方法

11. **Cimmino, M. (2018)**
    - "pygfunction: an open-source toolbox for the evaluation of thermal response factors for geothermal borehole fields"
    - *eSim 2018*
    - **贡献**: pygfunction开源库，本项目用于无流场景验证

---

## 3. 方法论说明

### 3.1 POINT2解析解的适用性

POINT2解析解基于Wexler (1992)的2D点源溶质迁移模型，通过热-溶质类比转换应用于BHE热响应模拟：

| 特性 | 说明 |
|------|------|
| **维度** | 2D（水平面） |
| **流场** | 均匀水平地下水流 |
| **源项** | 点源（钻孔热阻转换） |
| **边界** | 无限域 |

**钻孔热阻(R_b)转换**:
- BHE通过钻孔热阻R_b与周围土壤交换热量
- POINT2使用注入温度：T_inj = Q × R_b / (2πH)
- 其中Q为热负荷，H为钻孔深度

### 3.2 MODFLOW数值解的优势

MODFLOW 6 GWE提供完整的3D热传输数值模拟：

| 特性 | 说明 |
|------|------|
| **维度** | 3D |
| **流场** | 任意非均匀流场 |
| **源项** | ESL包（能量源载荷） |
| **边界** | 灵活设置 |
| **网格** | 支持局部加密 |

### 3.3 方法对比

本项目验证了多种方法在不同场景下的表现：

| 方法 | 适用场景 | 计算效率 | 精度 | 开源 |
|------|---------|---------|------|------|
| EED | 商业g-function工具 | 快速（秒级） | 行业标准参考解 | ❌ |
| pygfunction | EED开源替代 | 快速（秒级） | MAE=0.15°C vs EED，R²=0.999 | ✅ |
| POINT2 | 均匀流场快速评估 | 极快（毫秒级） | 趋势正确，相对误差<10% | ✅ |
| MODFLOW | 复杂场景详细模拟 | 较慢（分钟级） | 高精度3D参考解 | ✅ |

### 3.4 pygfunction作为EED替代方案

**理论基础相同：**
- EED和pygfunction都使用Eskilson (1987)的g-function理论
- 两者均适用于无地下水流动的纯导热场景
- g-function描述钻孔对阶跃热负荷的标准化热响应

**验证结果：**

| 指标 | pygfunction vs EED |
|------|--------------------|
| g-function曲线 | 近乎完全重合 |
| 月均温差MAE | 0.15°C |
| 相关系数R² | 0.999 |
| 最大偏差 | <0.5°C |

**应用建议：**
- pygfunction可作为学术研究和开源项目中EED的可靠替代
- 商业项目仍推荐使用EED进行最终设计验证
- 详见: `code/pygfunction_final.ipynb`

---

## 4. 项目主要发现

### 4.1 地下水流速对热响应的影响

通过三种流速场景的对比分析：

| 流速 | v (m/d) | 热对流效应 | 温度振幅变化 |
|------|---------|-----------|-------------|
| LOW | 0.001 | 忽略不计 | 最大（接近无流） |
| MEDIUM | 0.1 | 显著 | 中等衰减 |
| HIGH | 1.0 | 主导 | 明显衰减 |

**关键发现**: 
- 两种方法均正确预测：流速越高，温度振幅越小
- 物理解释：地下水流带走热量，降低局部温度积累

### 4.2 方法一致性验证

| 指标 | POINT2 vs MODFLOW |
|------|-------------------|
| 温度趋势 | 完全一致 |
| 相位关系 | 基本一致（差异<1个月） |
| 绝对值 | 差异1-3°C（可接受） |

---

## 5. 推荐阅读顺序

### 5.1 地下水流影响分析

1. **入门**: Wexler (1992) - 溶质迁移解析解基础
2. **理论**: Bear (1972) - 多孔介质流体力学
3. **数值方法**: Hughes et al. (2022) - MODFLOW GWE模块
4. **项目报告**: `docs/COMPREHENSIVE_COMPARISON_CN.md`

### 5.2 无流场景（补充）

1. **g-function理论**: Eskilson (1987)
2. **开源实现**: Cimmino (2018) - pygfunction
3. **项目验证**: `code/pygfunction_final.ipynb`

---

*最后更新: 2025年12月*
*作者: Liuhuang Luo*
