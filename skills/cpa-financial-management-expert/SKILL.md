---
name: cpa-financial-management-expert
description: >
  Expert-team (专家团) edition of the 2026 CPA Financial Cost Management
  knowledge base, produced by the pdf2skill methodology as a structured expert
  pack: 113 knowledge units (SKUs) organized in `_src/skus/{factual,
  procedural, relational}/<unit>/` (each with header.md + content.md), plus a
  routing table (`_src/mapping.md`), a machine-readable registry
  (`_src/skills.json`), and a cross-domain insight document
  (`_src/eureka.md`). Use when you need a query-able, unit-addressable
  encyclopedia of financial cost management: look up a concept by SKU id, dump
  the routing table to find units by trigger/domain/confidence, or load eureka.md
  for the subject's knowledge graph. Complements (not replaces) the flat
  `cpa-financial-management` card collection. Does NOT constitute professional
  financial/investment advice.
whenToUse: >
  Dispatch for precise knowledge lookups in financial cost management: given a
  financial concept/question, find the relevant SKU via mapping.md or
  skills.json (filter by domain / trigger / confidence), then read that unit's
  content.md. For cross-topic/narrative guidance, read eureka.md's knowledge
  graph. Use alone or alongside the flat `cpa-financial-management` cards.
argument-hint: "financial cost management concept to look up (e.g. WACC, EOQ, EVA)"
license: MIT
---

# CPA Financial Cost Management — Expert Team（专家团版知识库）

Structured **expert-team** knowledge base (113 SKUs / 26 domains) distilled from
the 2026 CPA《财务成本管理》textbook via the pdf2skill methodology.

> 结构化**专家团**知识库（113 个知识单元 / 26 个领域），源自 2026 注册会计师
> 《财务成本管理》教材，经 pdf2skill 方法论提炼（AI 转写学习摘录）。

## Layout / 结构

```
cpa-financial-management-expert/
├── SKILL.md          ← this entry
└── _src/
    ├── eureka.md     跨领域洞察与核心知识图谱
    ├── mapping.md    知识库路由表（SKU → 触发条件 / 领域 / 置信度）
    ├── skills.json   SKU 机器可读注册表（name/name_cn/trigger/domain/sku_type/...）
    └── skus/
        ├── factual/      事实型知识单元（单位 header.md + content.md）
        ├── procedural/   程序型知识单元
        └── relational/   关系型知识单元
```

## How to use / 如何使用

1. **Query by routing**：read `_src/mapping.md` or query `_src/skills.json`
   (filter by `domain` / `trigger` / `confidence` / `sku_type`) to locate units.
2. **Read a unit**：`_src/skus/<type>/<sku_id>/content.md`（+ header.md 元数据）。
3. **Cross-topic insight**：`_src/eureka.md` for the knowledge graph and the
   logical links between domains.

## Source / 深挖参考

- 提炼方法：pdf2skill（github.com/dayuer/pdf2skill），AI 转写学习摘录
- 原始参考：《2026年注册会计师·财务成本管理》教材（版权归官方/出版社）
- Disclaimer：本卡为 AI 学习摘录，仅供个人学习，不构成专业财务/投资意见；不保证完整性及考试权威性。