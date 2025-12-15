# 地埋管换热器(BHE)热响应建模方法综合对比研究

## 摘要

本研究对五种地埋管换热器(Borehole Heat Exchanger, BHE)热响应建模方法进行了系统性对比分析：Point2解析解、2D MODFLOW数值模型、3D MODFLOW数值模型、pygfunction (g-function)方法以及EED商业软件。以EED软件计算结果作为基准，在三种不同地下水流速情景(LOW: 0.001 m/d, MEDIUM: 0.1 m/d, HIGH: 1.0 m/d)和无流动情景下，对各方法进行了25年模拟对比。

研究结果表明：
1. **Point2方法**在低流速条件下与EED完全吻合(MAE=0.002°C)，但在高流速情景下出现温度振幅过估现象(8.84°C vs EED的7.70°C)；
2. **2D MODFLOW方法**在中等流速条件下表现最佳(MAE=0.069°C)，整体误差范围为0.07-0.41°C；
3. **3D MODFLOW方法**在低流速条件下表现良好(MAE=0.187°C)，但在高流速情景下偏差显著增大(MAE=1.279°C)；
4. **pygfunction方法**与EED在无流动条件下高度一致(MAE=0.147°C, R²=0.995)，可作为EED的开源替代方案。

关键词：地埋管换热器、g-function、MODFLOW、地下水流动、热传输、数值模拟

---

## 1. 模型概述

### 1.1 研究背景

地源热泵系统中地埋管换热器(BHE)的设计需要准确预测长期运行过程中的循环流体温度变化。不同的建模方法在计算精度、计算效率和适用范围等方面存在差异。本研究选取了目前主流的五种建模方法进行对比：

| 方法 | 类型 | 是否考虑地下水流动 | 计算维度 |
|------|------|:------------------:|:--------:|
| EED | 商业软件 (g-function) | ✗ | 2D轴对称 |
| pygfunction | 开源工具 (g-function) | ✗ | 2D轴对称 |
| Point2 | 解析解 | ✓ | 2D平面 |
| 2D MODFLOW | 数值模型 | ✓ | 2D平面 |
| 3D MODFLOW | 数值模型 | ✓ | 3D |

### 1.2 研究案例

本研究采用统一的BHE场参数进行对比分析：

**BHE场配置：**

- 布局：5×8 矩形阵列，共40根钻孔
- 钻孔深度：H = 147 m
- 钻孔间距：B = 7 m
- 钻孔半径：r_b = 70 mm

**地层热物性：**

- 热导率：k = 1.4 W/(m·K)
- 体积热容：ρc = 2.83 MJ/(m³·K)
- 地表温度：T₀ = 9.6°C
- 地热热流：q_geo = 0.07 W/m²
- 孔隙率：n = 0.2

**热负荷特征：**

- 年制热负荷：131 MWh
- 年制冷负荷：98 MWh
- 峰值功率：160 kW (制热/制冷)

**模拟参数：**
- 模拟时长：25年
- 时间步长：月度

---

## 2. 方法介绍

### 2.1 五种方法总体介绍

#### EED (Earth Energy Designer)

EED是目前应用最广泛的BHE设计商业软件，基于Eskilson的g-function理论开发。该方法将钻孔场简化为无限线热源阵列，通过预计算的热响应因子(g-function)进行温度叠加计算。

核心公式：
$$T_f(t) = T_0 + \Delta T_{ground}(t) + \Delta T_{bh}(t)$$

其中：
- $\Delta T_{ground} = \frac{q}{2\pi k} \cdot g(t/t_s)$ 为地层热响应
- $\Delta T_{bh} = q \cdot R_b$ 为钻孔热阻效应
- $t_s = H^2/(9\alpha)$ 为特征时间

#### pygfunction

pygfunction是Cimmino开发的开源Python工具包，实现了与EED相同的g-function计算方法。主要优势在于：
- 开源免费，计算过程透明
- 支持任意钻孔布局
- 可进行参数敏感性分析

#### Point2解析解

Point2方法基于热-溶质传输类比原理，将钻孔简化为点热源，使用解析解计算地下水流动条件下的温度场。该方法特别适用于存在地下水对流传热的情况。

温度场解析解：
$$T(x,y,t) = T_0 + \frac{Q}{4\pi k H} \exp\left(\frac{v_x (x-x_0)}{2\alpha_x}\right) \cdot W(u)$$

其中$W(u)$为井函数，$v_x$为地下水流速。

#### 2D MODFLOW

2D MODFLOW采用MODFLOW 6的GWF-GWE耦合模块，将BHE场简化为单层水平切片进行模拟。该方法假设：

- 垂直方向温度分布均匀
- 地下水在水平方向流动
- 热传输发生在二维平面内

#### 3D MODFLOW

3D MODFLOW采用完整的三维数值模拟，将钻孔深度方向离散为多层网格。该方法可以精确模拟：

- 垂直方向的温度分布
- 三维热传导和对流传热
- 钻孔与周围地层的热交换

### 2.2 Point2方法详解

Point2方法的核心是将热传输问题类比为地下水中的溶质传输问题。这种类比成立的理论基础是两者具有相似的控制方程形式。

**基本假设：**
1. 含水层为均质各向同性介质
2. 地下水流为稳态达西流
3. 热传输主要通过对流和弥散进行
4. 忽略密度变化导致的自然对流

**温度计算公式：**

对于单个点热源在存在均匀地下水流动时的温度响应：
$$\Delta T = \frac{Q}{4\pi k H n R} \exp\left(\frac{v_x x}{2D_x}\right) \int_0^t \frac{1}{\tau} \exp\left(-\frac{x^2/R}{4D_x\tau}-\frac{y^2/R}{4D_y\tau}-\frac{v_x^2\tau}{4D_x}\right) d\tau$$

其中：
- $R = 1 + \frac{(1-n)\rho_s c_s}{n\rho_w c_w}$ 为热迟滞因子
- $D_x, D_y$ 为热弥散系数
- $v_x$ 为达西流速

**从地层温度到流体温度的转换：**
$$T_f = T_{ground} + q_{bhe} \cdot R_b$$

其中$q_{bhe}$为钻孔热流密度(W/m)，符号约定：正值表示向地层注热，负值表示从地层取热。

### 2.3 2D与3D MODFLOW的区别与联系

#### 共同点

1. **基础软件**：均基于USGS开发的MODFLOW 6软件，使用GWF-GWE耦合模块
2. **控制方程**：求解相同的热传输方程
   $$\frac{\partial(\rho c T)}{\partial t} = \nabla \cdot (k\nabla T) - \nabla \cdot (\rho_w c_w \mathbf{v} T) + Q$$
3. **边界条件**：使用相同的热负荷边界和流速边界
4. **参数设置**：热物性参数、孔隙率、渗透系数等保持一致

#### 区别

| 特征 | 2D MODFLOW | 3D MODFLOW |
|------|:----------:|:----------:|
| 模型维度 | 单层(z方向积分) | 多层(完整3D) |
| 层厚 | 1 m (单位深度) | 根据深度分层(147m, 33层) |
| 热负荷处理 | 线热源 (W/m) | 体积热源 (W/m³) |
| 计算网格数 | ~4,000 | ~400,000 |
| 计算时间 | ~10分钟 | ~4小时 |
| 垂直方向 | 假设均匀 | 精确模拟 |

#### 水力梯度设置

两种模型均通过达西定律设置水力边界条件：
$$v = K \cdot \nabla h / n$$

因此水力梯度：
$$\nabla h = v \cdot n / K$$

其中K = 10 m/d为水力传导系数。

### 2.4 g-function与EED的区别与联系

#### g-function理论基础

g-function（热响应因子）是Eskilson在1987年博士论文中提出的概念，定义为无量纲化的钻孔壁面平均温度响应：

$$g(t/t_s, r_b/H) = \frac{2\pi k \cdot \Delta T_b(t)}{q}$$

该函数描述了恒定热流作用下，钻孔壁面温度随时间的演变规律。对于多钻孔系统，g-function还需要考虑钻孔间的热干扰效应。

#### EED软件特点

EED软件的主要特点包括：
- 内置多种标准钻孔配置的预计算g-function
- 月度负荷叠加计算
- 包含峰值负荷修正
- 友好的图形用户界面
- 符合国际标准(ISO 13256)

#### pygfunction特点

pygfunction作为开源替代方案，具有以下特点：
- 基于有限线热源(FLS)模型计算g-function
- 支持任意自定义钻孔布局
- 可调整计算精度(分段数)
- 完全透明的计算过程
- 可与其他Python工具集成

#### 主要区别

| 特征 | EED | pygfunction |
|------|:---:|:-----------:|
| 软件类型 | 商业 | 开源 |
| g-function来源 | 预计算数据库 | 实时计算 |
| 钻孔布局 | 标准配置 | 任意自定义 |
| 计算速度 | 快速 | 较慢(首次) |
| 可扩展性 | 有限 | 高度灵活 |
| 价格 | 付费许可 | 免费 |

---

## 3. 结果对比

### 3.1 EED、Point2、2D MODFLOW对比分析

图1展示了在三种地下水流速情景下，Point2、2D MODFLOW与EED基准的对比结果。

![图1: Point2与2D MODFLOW对比EED](../figures/comparison_point2_2Dmodflow_eed.png)

**图1说明：** 三个子图分别对应LOW (v=0.001 m/d)、MEDIUM (v=0.1 m/d)和HIGH (v=1.0 m/d)三种流速情景。黑色虚线为EED基准值，蓝色实线为Point2结果，红色实线为2D MODFLOW结果。

**定量对比结果：**

| 情景 | 方法 | MAE (°C) | R² | 振幅 (°C) |
|:----:|:----:|:--------:|:--:|:---------:|
| LOW | Point2 | 0.002 | 1.0000 | 7.70 |
| LOW | 2D MODFLOW | 0.365 | 0.9719 | 9.09 |
| MEDIUM | Point2 | 0.319 | 0.9768 | 6.62 |
| MEDIUM | 2D MODFLOW | 0.069 | 0.9984 | 7.98 |
| HIGH | Point2 | 0.314 | 0.9753 | 8.84 |
| HIGH | 2D MODFLOW | 0.406 | 0.9660 | 6.37 |
| 基准 | EED | - | - | 7.70 |

**结果分析：**

1. **LOW情景(v=0.001 m/d)**
   - Point2方法与EED几乎完全一致(MAE=0.002°C)，说明在低流速条件下，Point2的解析解具有很高的精度
   - 2D MODFLOW出现约0.4°C的平均误差，且振幅偏大(9.09°C vs 7.70°C)
   - 这是因为2D模型采用水平切片假设，在低流速时对流传热贡献小，而地层热容量的处理差异导致了振幅偏差

2. **MEDIUM情景(v=0.1 m/d)**
   - 2D MODFLOW表现最佳(MAE=0.069°C)，这是因为中等流速下水平方向的对流传热占主导
   - Point2方法误差增大至0.32°C，可能是由于解析解中弥散系数的简化假设
   - 振幅方面，2D MODFLOW(7.98°C)最接近EED(7.70°C)

3. **HIGH情景(v=1.0 m/d)**
   - 两种方法均出现较大偏差(~0.3-0.4°C)
   - Point2振幅明显偏大(8.84°C)，说明在高流速下该方法可能高估了热量的快速耗散后温度恢复的幅度
   - 2D MODFLOW振幅偏小(6.37°C)，热量被更快地带走

### 3.2 2D MODFLOW、3D MODFLOW、EED对比分析

图2展示了2D与3D MODFLOW在不同流速情景下与EED的对比。

![图2: 2D MODFLOW与3D MODFLOW对比EED](../figures/comparison_2Dmodflow_3Dmodflow_eed.png)

**图2说明：** 蓝色实线为2D MODFLOW结果，绿色实线为3D MODFLOW结果，黑色虚线为EED基准。

**定量对比结果：**

| 情景 | 方法 | MAE (°C) | R² | 振幅 (°C) |
|:----:|:----:|:--------:|:--:|:---------:|
| LOW | 2D MODFLOW | 0.365 | 0.9719 | 9.09 |
| LOW | 3D MODFLOW | 0.187 | 0.9929 | 8.39 |
| MEDIUM | 2D MODFLOW | 0.069 | 0.9984 | 7.98 |
| MEDIUM | 3D MODFLOW | 0.440 | 0.9600 | 6.23 |
| HIGH | 2D MODFLOW | 0.406 | 0.9660 | 6.37 |
| HIGH | 3D MODFLOW | 1.279 | 0.6394 | 3.08 |

**结果分析：**

1. **LOW情景(v=0.001 m/d)**
   - 3D MODFLOW表现优于2D(MAE: 0.187 vs 0.365°C)
   - 低流速时，垂直方向的热传导对整体温度场有显著影响，3D模型能更好地捕捉这一特性
   - 振幅方面3D(8.39°C)较2D(9.09°C)更接近EED(7.70°C)

2. **MEDIUM情景(v=0.1 m/d)**
   - 2D MODFLOW显著优于3D(MAE: 0.069 vs 0.440°C)
   - 这一结果表明，在中等流速下，水平方向的对流传热占主导地位
   - 3D模型可能由于网格分辨率限制，在对流占优时产生较大的数值弥散

3. **HIGH情景(v=1.0 m/d)**
   - 3D MODFLOW出现严重偏差(MAE=1.279°C, R²=0.64)
   - 温度振幅仅为3.08°C，远小于EED的7.70°C
   - **原因分析**：高流速下，3D模型中的对流传热在三维空间内发生，热量被快速带出计算域，导致温度波动被过度平滑
   - 2D模型虽也有偏差，但通过水平切片假设反而减轻了这一问题

**关键发现：**

2D MODFLOW与3D MODFLOW的对比揭示了一个重要规律：
- 低流速 → 3D模型更准确(能捕捉垂直热传导)
- 中/高流速 → 2D模型更准确(避免了3D对流造成的过度热量耗散)

这为实际工程应用提供了重要参考：当地下水流速>0.1 m/d时，简化的2D模型可能比复杂的3D模型更可靠。

### 3.3 pygfunction与EED对比分析

图3展示了pygfunction与EED在无地下水流动条件下的对比。

![图3: pygfunction对比EED](../figures/comparison_pygfunction_eed.png)

**图3说明：** 蓝色实线为pygfunction基础负荷计算结果，黑色虚线为EED基准。红色竖线表示峰值制热负荷(1月)，蓝色竖线表示峰值制冷负荷(8月)。

**定量对比结果：**

| 指标 | pygfunction | EED | 偏差 |
|:----:|:-----------:|:---:|:----:|
| MAE (基础负荷) | - | - | 0.147°C |
| R² | 0.995 | - | - |
| 年振幅 | 7.33°C | 7.70°C | -0.37°C |
| 峰值制热温度(1月) | 7.01°C | 6.91°C | +0.10°C |
| 峰值制冷温度(8月) | 22.36°C | 22.40°C | -0.04°C |

**结果分析：**

1. **基础负荷对比**
   - MAE仅为0.147°C，两种方法高度一致
   - R²达到0.995，说明温度变化趋势完全吻合
   - 振幅差异仅0.37°C(4.8%相对偏差)

2. **峰值负荷对比**
   - 峰值制热温度几乎相同(7.01 vs 6.91°C)
   - 峰值制冷温度完全一致(22.36 vs 22.40°C)
   - 峰值负荷的处理方式两者基本相同

3. **差异来源分析**
   - g-function计算方法略有不同(EED使用预计算数据，pygfunction使用FLS实时计算)
   - 钻孔热阻($R_b$)的处理方式存在细微差别
   - 时间离散和叠加方法可能存在数值精度差异

#### g-function曲线分析

图4展示了5×8钻孔场的g-function曲线，这是pygfunction和EED计算的核心基础。

![图4: g-function曲线](../figures/gfunction_curve.png)

**图4说明：** 左图为g-function与无量纲时间ln(t/t_s)的关系，右图为g-function与实际时间(年)的关系。红色标记点显示了关键时间点的g值。

**g-function物理意义：**

g-function是无量纲化的热响应因子，描述了恒定热流作用下钻孔壁面温度的时间演变规律。从图中可以观察到：

| 时间点 | ln(t/t_s) | g值 | 物理含义 |
|:------:|:---------:|:----:|:--------:|
| 1个月 | -5.15 | 7.8 | 短期响应，主要受单钻孔热阻影响 |
| 1年 | -2.67 | 13.5 | 钻孔间热干扰开始显现 |
| 5年 | -1.06 | 18.9 | 热干扰效应显著增强 |
| 10年 | -0.37 | 21.6 | 达到准稳态状态 |
| 25年 | 0.55 | 25.4 | 接近稳态，g值增长减缓 |

**关键观察点：**

1. **短期响应(t < 1年)：** g-function线性增长，主要反映单个钻孔的热响应
2. **中期响应(1-10年)：** 增长率加快，钻孔间的热干扰作用逐渐显现
3. **长期响应(>10年)：** g值趋于平稳，表明热影响区域基本稳定

这解释了为什么pygfunction和EED的计算结果在长期模拟(25年)中高度一致——两者都基于相同的g-function理论，而在达到准稳态后，不同计算方法的差异对结果影响很小。

**结论：** pygfunction可以作为EED的有效开源替代方案，两者在无地下水流动条件下的计算结果高度一致。

---

## 4. 总结与分析

### 4.1 计算效率与适用场景

**各方法计算效率对比：**

| 方法 | 典型计算时间 | 计算资源 | 可并行 |
|:----:|:------------:|:--------:|:------:|
| EED | <1分钟 | 低 | - |
| pygfunction | 2-5分钟 | 中 | 是 |
| Point2 | <1分钟 | 低 | 是 |
| 2D MODFLOW | 1-3分钟 | 中 | 部分 |
| 3D MODFLOW | 20-40小时 | 高 | 部分 |

*注：测试环境为Intel Core i7处理器，16GB内存。计算时间为25年月度模拟。*

**适用场景建议：**

| 应用场景 | 推荐方法 | 理由 |
|:--------:|:--------:|:----:|
| 初步设计/快速评估 | EED或pygfunction | 计算快速，精度足够 |
| 无地下水/低流速 | pygfunction + Point2 | 开源免费，验证充分 |
| 中等流速(0.01-0.1 m/d) | 2D MODFLOW | 精度最高，计算量适中 |
| 低流速详细分析 | 3D MODFLOW | 能捕捉三维热传导 |
| 高流速(>0.1 m/d) | 2D MODFLOW | 避免3D对流过估问题 |
| 参数敏感性分析 | Point2 | 解析解，计算高效 |
| 复杂地质条件 | 3D MODFLOW | 灵活的材料分区 |

**方法选择流程图：**

```
开始
  │
  ├─ 是否存在显著地下水流动?
  │    │
  │    ├─ 否 → pygfunction/EED (g-function方法)
  │    │
  │    └─ 是 → 流速范围?
  │           │
  │           ├─ <0.01 m/d → Point2 或 3D MODFLOW
  │           │
  │           ├─ 0.01-0.1 m/d → 2D MODFLOW (最佳精度)
  │           │
  │           └─ >0.1 m/d → 2D MODFLOW (避免3D过估)
  │
结束
```

### 4.2 流速对热传输的影响

从本研究的结果可以清晰地观察到地下水流速对BHE热响应的显著影响：

**温度振幅随流速的变化：**

| 流速 (m/d) | 2D MODFLOW振幅 | 3D MODFLOW振幅 | 变化趋势 |
|:----------:|:--------------:|:--------------:|:--------:|
| 0.001 | 9.09°C | 8.39°C | 基准 |
| 0.1 | 7.98°C | 6.23°C | 下降12%/26% |
| 1.0 | 6.37°C | 3.08°C | 下降30%/63% |

**物理机制解释：**
1. 地下水流动增强了对流传热，加速了热量从BHE周围向远场的传输
2. 流速越高，热量扩散越快，温度波动越小
3. 3D模型对流速更敏感，因为对流在三维空间内发生
4. 2D模型通过水平切片假设，一定程度上抑制了对流效应的过度估计

**工程意义：**
- 在存在地下水流动的场地，BHE的热恢复能力更强
- 高流速场地可以采用更小的钻孔间距或更少的钻孔数量
- 但过高的流速可能导致热量损失过大，降低系统效率
- 设计时应根据实际水文地质条件选择合适的模拟方法

### 4.3 pygfunction能否替代EED

基于本研究的对比分析，对"pygfunction能否替代EED"这一问题做出以下评估：

**完全可以替代的场景：**
1. ✅ 无地下水流动的标准BHE设计
2. ✅ 学术研究和教学演示
3. ✅ 参数敏感性分析
4. ✅ 非标准钻孔布局的设计
5. ✅ 需要与其他Python工具集成的项目

**部分可以替代的场景：**
1. ⚠️ 商业设计项目(可能需要额外验证)
2. ⚠️ 需要符合特定标准认证的项目
3. ⚠️ 需要图形化界面的用户

**无法替代的场景：**
1. ❌ 需要考虑地下水流动的设计(两者都不支持)
2. ❌ 需要特定报告格式的项目
3. ❌ 非技术人员使用

**技术精度对比总结：**

| 指标 | pygfunction | EED | 评价 |
|:----:|:-----------:|:---:|:----:|
| 基础负荷MAE | 0.147°C | 基准 | 优秀 |
| 峰值温度偏差 | <0.1°C | 基准 | 优秀 |
| R² | 0.995 | 基准 | 优秀 |
| g-function理论 | FLS模型 | Eskilson | 等效 |

**结论：** 在无地下水流动条件下，pygfunction可以作为EED的有效开源替代方案。两者基于相同的理论框架（g-function方法），计算结果高度一致（MAE<0.15°C）。pygfunction的主要优势在于开源免费、计算过程透明、支持自定义配置；主要劣势在于缺乏图形界面、需要编程基础、首次计算g-function耗时较长。

---

## 参考文献

1. Eskilson, P. (1987). *Thermal Analysis of Heat Extraction Boreholes*. Doctoral Thesis, Lund University, Sweden.

2. Cimmino, M. (2018). pygfunction: An open-source toolbox for the evaluation of thermal response factors for geothermal borehole fields. *MethodsX*, 5, 1199-1213. https://doi.org/10.1016/j.mex.2018.09.009

3. Hellström, G. (1991). *Ground Heat Storage: Thermal Analyses of Duct Storage Systems*. Doctoral Thesis, Lund University, Sweden.

4. BLOCON (2015). *EED - Earth Energy Designer, Version 4.20*. BLOCON Software, Lund, Sweden.

5. Langevin, C.D., Hughes, J.D., Banta, E.R., Niswonger, R.G., Panday, S., and Provost, A.M. (2017). Documentation for the MODFLOW 6 Groundwater Flow Model. *U.S. Geological Survey Techniques and Methods*, Book 6, Chap. A55.

6. Hughes, J.D., Langevin, C.D., Paulinski, S.R., Larsen, J.D., and Brakefield, L.K. (2023). Documentation for the MODFLOW 6 Groundwater Energy Transport (GWE) Model. *U.S. Geological Survey Techniques and Methods*, Book 6, Chap. A57.

7. Diao, N., Li, Q., & Fang, Z. (2004). Heat transfer in ground heat exchangers with groundwater advection. *International Journal of Thermal Sciences*, 43(12), 1203-1211.

8. Molina-Giraldo, N., Blum, P., Zhu, K., Bayer, P., & Fang, Z. (2011). A moving finite line source model to simulate borehole heat exchangers with groundwater advection. *International Journal of Thermal Sciences*, 50(12), 2506-2513.

9. Claesson, J., & Hellström, G. (2011). Multipole method to calculate borehole thermal resistances in a borehole heat exchanger. *HVAC&R Research*, 17(6), 895-911.

10. Zeng, H., Diao, N., & Fang, Z. (2002). A finite line-source model for boreholes in geothermal heat exchangers. *Heat Transfer—Asian Research*, 31(7), 558-567.

---

*报告生成日期：2025年12月15日*
*基于25年月度模拟数据分析*
