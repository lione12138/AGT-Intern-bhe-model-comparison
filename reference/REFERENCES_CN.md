# 参考文献文档

---

## 方法对比概览

本项目对比了三种BHE（钻孔换热器）温度模拟方法：

| 方法 | 类型 | 理论基础 | 开发者/来源 |
|------|------|----------|-------------|
| **EED** | 商业软件 | g-function (Eskilson 1987) | BLOCON (瑞典) |
| **pygfunction** | 开源Python库 | g-function (Eskilson 1987) | Massimo Cimmino (加拿大) |
| **MODFLOW 6 GWE** | 开源数值模拟 | 有限差分法 (3D热传导) | USGS (美国) |

### 关于EED与pygfunction的关系

**重要说明**：
- **EED**是商业软件，需要购买许可证
- **pygfunction**是独立开发的开源替代方案（MIT许可证）
- 两者基于**相同的物理理论**（Eskilson的g-function方法）
- pygfunction**不是**EED公司（BLOCON）发布的
- 使用pygfunction实现g-function计算是完全合法的——g-function理论是公开的学术成果

本项目使用pygfunction达到了与EED几乎相同的精度（MAE=0.15°C），验证了开源方案的可行性。

---

## 在线资源

### pygfunction
- **GitHub仓库**: https://github.com/MassimoCimmino/pygfunction
- **文档**: https://pygfunction.readthedocs.io/
- **PyPI**: https://pypi.org/project/pygfunction/
- **DOI**: https://zenodo.org/badge/latestdoi/100305705
- **作者**: Massimo Cimmino, 蒙特利尔理工学院, 加拿大

### MODFLOW 6 GWE (地下水能量传输)
- **USGS官方文档**: https://www.usgs.gov/software/modflow-6-usgs-modular-hydrologic-model
- **GWE模块指南**: https://modflow6.readthedocs.io/en/latest/
- **FloPy (Python接口)**: https://github.com/modflowpy/flopy

### EED (Earth Energy Designer)
- **BLOCON官网**: https://buildingphysics.com/eed-2/
- **软件手册**: 需购买许可证后从BLOCON网站获取
- **备注**: 商业软件，需购买许可证

---

## 1. g-function方法的理论基础

### 1.1 核心概念

g-function是描述地埋管换热器（BHE）长期热响应的无量纲响应函数。

**基本公式**：
$$T_b(t) = T_0 + \frac{q}{2\pi k H} \cdot g\left(\frac{t}{t_s}, \frac{r_b}{H}, \frac{B}{H}\right)$$

其中：
- $T_b$ = 钻孔壁温度 [°C]
- $T_0$ = 未扰动地层温度 [°C]
- $q$ = 单位长度热流 [W/m]
- $k$ = 地层热导率 [W/(m·K)]
- $H$ = 钻孔深度 [m]
- $g$ = g-function值 [-]
- $t_s = H^2/(9\alpha)$ = 特征时间 [s]
- $\alpha$ = 热扩散率 [m²/s]

**流体温度**：
$$T_f(t) = T_b(t) + q \cdot R_b$$

其中 $R_b$ = 钻孔热阻 [(m·K)/W]

### 1.2 g-function的物理意义

g-function考虑了：
1. **有限线热源效应** - 钻孔有限深度
2. **地表恒温边界** - 镜像热源法
3. **多钻孔热干扰** - 钻孔间的热叠加
4. **时间演化** - 从短期到长期（数十年）的响应

### 1.3 EED vs pygfunction的实现差异

| 特征 | EED | pygfunction |
|------|-----|-------------|
| g-function计算 | 预计算表格+插值 | 实时数值积分 |
| 钻孔配置 | 预定义模板 | 任意自定义配置 |
| 速度 | 极快（查表） | 较慢（需计算） |
| 灵活性 | 有限 | 高度灵活 |
| 精度 | 高 | 高（可验证） |

---

## 2. 主要参考文献

### 2.1 g-function方法的奠基文献

1. **Eskilson, P. (1987)** ⭐ 核心文献
   - "Thermal Analysis of Heat Extraction Boreholes"
   - *博士论文, 瑞典隆德大学*
   - **贡献**: 创立g-function方法，是EED和pygfunction的共同理论基础
   - **备注**: 这是BHE领域最重要的文献之一

2. **Claesson, J. & Eskilson, P. (1988)**
   - "Conductive Heat Extraction to a Deep Borehole: Thermal Analyses and Dimensioning Rules"
   - *Energy, Vol. 13, No. 6, pp. 509-527*
   - **贡献**: 完善了单钻孔的解析解

3. **Hellström, G. (1991)**
   - "Ground Heat Storage: Thermal Analyses of Duct Storage Systems"
   - *博士论文, 瑞典隆德大学*
   - **贡献**: 完善了多钻孔系统和钻孔热阻理论

### 2.2 pygfunction相关文献

4. **Cimmino, M. & Bernier, M. (2014)**
   - "A semi-analytical method to generate g-functions for geothermal bore fields"
   - *International Journal of Heat and Mass Transfer, Vol. 70, pp. 641-650*
   - **贡献**: pygfunction使用的半解析计算方法

5. **Cimmino, M. (2018)**
   - "Fast calculation of the g-functions of geothermal borehole fields using similarities in the evaluation of the finite line source solution"
   - *Journal of Building Performance Simulation, Vol. 11, No. 6, pp. 655-668*
   - **贡献**: g-function快速计算算法

6. **Cimmino, M. (2019)**
   - "pygfunction 2.1: An open-source toolbox for the evaluation of thermal response factors for geothermal borehole fields"
   - *MethodsX, Vol. 8, 101249*
   - **贡献**: pygfunction库的官方文档论文

### 2.3 钻孔热阻理论

7. **Mogensen, P. (1983)**
   - "Fluid to Duct Wall Heat Transfer in Duct System Heat Storages"
   - *地下储热国际会议论文集*
   - 瑞典斯德哥尔摩, pp. 652-657
   - **贡献**: 首次提出钻孔热阻概念

8. **Gehlin, S. (2002)**
   - "Thermal Response Test: Method Development and Evaluation"
   - *博士论文, 瑞典吕勒奥理工大学*
   - **在线**: http://urn.kb.se/resolve?urn=urn:nbn:se:ltu:diva-18295
   - **贡献**: TRT方法的系统总结

### 2.4 MODFLOW相关文献

9. **Langevin, C.D., et al. (2022)**
   - "MODFLOW 6 Modular Hydrologic Model version 6.4.1"
   - *美国地质调查局软件发布*
   - https://doi.org/10.5066/P9FL1JCC

10. **Hughes, J.D., et al. (2022)**
    - "MODFLOW 6 Groundwater Energy Transport (GWE) Module"
    - *美国地质调查局技术与方法, Book 6, Chapter A61*
    - **贡献**: GWE模块的官方文档

### 2.5 POINT2解析解（早期尝试）

11. **Wexler, E.J. (1992)**
    - "Analytical Solutions for One-, Two-, and Three-Dimensional Solute Transport in Ground-Water Systems with Uniform Flow"
    - *美国地质调查局, 水资源调查技术, Book 3, Chapter B7*
    - https://pubs.usgs.gov/twri/twri3-b7/
    - **备注**: 本项目早期尝试使用此方法，后因2D限制放弃

---

## 3. 方法论说明

### 3.1 为什么放弃POINT2解析解？

我们最初尝试使用POINT2（2D点源溶质运移解析解）模拟BHE，但放弃了：

| 问题 | 说明 |
|------|------|
| **2D限制** | 无法处理147m深钻孔的垂向效应 |
| **无边界效应** | 忽略地表恒温边界的"镜像效应" |
| **精度不足** | 与EED偏差>3°C |

**尝试的补正方案**：地热梯度补正
- 结论：只能调整温度基准，无法修正响应曲线形状
- 长期（25年）误差仍>30%

详见：`docs/POINT2_ANALYSIS_CN.md`

### 3.2 g-function方法为什么有效？

g-function方法（EED和pygfunction都使用）考虑了：
1. ✓ 钻孔有限深度（有限线热源，非点源）
2. ✓ 地表恒温边界（镜像热源法）
3. ✓ 多钻孔热干扰（响应叠加）
4. ✓ 长期热演化（特征时间尺度）

这正是POINT2缺少的3D效应。

### 3.3 MODFLOW数值方法的优势

相比解析方法，MODFLOW 6 GWE提供：
1. ✓ 完全3D模拟
2. ✓ 任意边界条件
3. ✓ 可扩展到地下水流动情景
4. ✓ 局部网格加密技术

---

## 4. 本项目的贡献

### 4.1 验证结果

| 方法 | 对比EED的MAE | 结论 |
|------|--------------|------|
| pygfunction | 0.15°C | ✓ 可替代EED商业软件 |
| MODFLOW (局部加密) | 0.084°C | ✓ 精度超越解析方法 |
| POINT2 + 补正 | >3°C | ✗ 不适用于BHE |

### 4.2 实践意义

1. **开源替代**：pygfunction可替代EED商业软件进行g-function计算
2. **数值验证**：MODFLOW提供了独立的数值验证手段
3. **方法论**：明确了2D解析解的局限性

---

## 5. 推荐阅读顺序

对于想要深入理解BHE建模的读者：

1. **入门**：Gehlin (2002) - TRT方法综述
2. **核心理论**：Eskilson (1987) - g-function原理
3. **实现细节**：Cimmino (2018, 2019) - pygfunction算法
4. **数值方法**：Hughes et al. (2022) - MODFLOW GWE

---

*最后更新: 2025年12月*
*作者: AGT实习项目*
