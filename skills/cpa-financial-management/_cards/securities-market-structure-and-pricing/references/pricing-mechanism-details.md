# 一级市场与二级市场定价机制详解

## 价格传导的数学表达

### 基础定价公式

一级市场发行价格（Primary Issue Price）与二级市场价格（Secondary Market Price）的关系：

```
Primary Issue Price = Secondary Market Price × (1 - Discount Rate)
```

其中：
- **Discount Rate（折扣率）**：通常为 5%-20%，取决于市场流动性、发行规模、行业特性
- 当 Secondary Market Price 波动时，Primary Issue Price 需相应调整

### 筹资规模计算

发行总筹资额（Total Proceeds）计算公式：

```
Total Proceeds = Primary Issue Price × Issuance Quantity
               = Secondary Market Price × (1 - Discount Rate) × Issuance Quantity
```

### 价格弹性系数

衡量二级市场价格变动对一级市场筹资额的影响：

```
价格弹性 = (ΔPrimary Proceeds / Primary Proceeds) / (ΔSecondary Price / Secondary Price)
```

在完全传导情况下，价格弹性接近 1。

## 流动性影响机制

二级市场流动性水平（Liquidity Level）对一级市场的影响：

1. **高流动性市场**：
   - 买卖价差（Bid-Ask Spread）小
   - 一级市场发行折扣率可降低
   - 投资者参与意愿强

2. **低流动性市场**：
   - 需要更高折扣率吸引投资者
   - 发行难度增加
   - 可能需要引入做市商机制

## 市场间资本流动

### 正向循环
```
二级市场活跃 → 流动性溢价上升 → 一级市场发行价格提升 → 企业融资增加 → 投资扩张 → 基本面改善 → 二级市场价格上升
```

### 负向循环（风险）
```
二级市场低迷 → 流动性枯竭 → 一级市场发行困难 → 企业融资受限 → 投资收缩 → 基本面恶化 → 二级市场价格下跌
```

## 实际应用示例

### 示例 1：IPO定价
某公司计划在主板IPO：
- 同行业可比公司二级市场平均市盈率：20倍
- 该公司预期每股收益：2元
- 二级市场隐含价格：40元/股
- 考虑流动性折扣（15%）：IPO定价 = 40 × (1-0.15) = 34元/股
- 发行数量：1亿股
- 预计筹资额：34亿元

### 示例 2：增发定价
已上市公司增发新股：
- 当前二级市场股价：50元/股
- 20日均价：48元/股
- 增发折扣率（通常10%）：定价约 43-45元/股
- 若二级市场股价跌至40元，需重新评估增发可行性或调整发行规模

## 关键变量说明

| 变量名 | 类型 | 说明 |
|--------|------|------|
| `issuance_status` | boolean | 是否初次发行：true（首次发行）或 false（已发行） |
| `market_type` | categorical | 市场类型：primary（一级）或 secondary（二级） |
| `secondary_market_price` | currency | 二级市场上同类证券价格 |
| `primary_issue_price` | currency | 一级市场发行价格 |
| `issuance_quantity` | integer | 发行数量 |
| `total_proceeds` | currency | 发行总筹资额 |
| `liquidity_level` | index | 二级市场流动性水平 |