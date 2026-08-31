# 债券调换变量定义

## 核心变量

- `old_bond_restrictions` (boolean): 旧债券是否包含过多限制性条款。
- `admin_cost_reduction_needed` (boolean): 是否需要通过合并减少管理费用。
- `cash_shortage_at_maturity` (boolean): 到期时是否面临现金不足。
- `new_bond_terms` (object): 新债券的利率、期限、契约条款。

## 执行结果

完成旧债券的替换或合并，新债券生效，旧债券注销。