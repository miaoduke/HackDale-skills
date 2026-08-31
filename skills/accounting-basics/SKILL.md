---
name: accounting-basics
description: >
  Aggregated accounting knowledge-card collection distilled from professional
  accounting textbook(s) via the pdf2skill methodology. Covers bookkeeping
  (double-entry, vouchers, ledgers), account classification, financial statement
  preparation, ratio/solvency/profitability analysis, fraud detection, and
  accounting workflow. Use when asked to help with practical accounting tasks:
  recording business transactions, classifying accounts, preparing vouchers or
  ledgers, reconciling bank deposits, computing financial ratios, assessing
  solvency/profitability, or detecting financial misstatement patterns. Provides
  166 per-topic SKILL cards in `_cards/`. Does NOT provide tax/legal advice or
  definitive accounting-standards rulings.
whenToUse: >
  Dispatch inside an AI agent when a concrete accounting or financial-analysis
  task arrives: journal entry, voucher, account classification, ledger, bank
  reconciliation, financial statements, ratio analysis, solvency/profitability
  assessment. Each card under `_cards/<topic>/SKILL.md` has its own frontmatter
  and body; load the specific card that matches the sub-task, or the index for
  browsing.
argument-hint: "accounting sub-task (e.g. double-entry bookkeeping, solvency ratio)"
license: MIT
---

# Accounting Basics — 会计专业技能集合（聚合知识卡）

An **aggregated** knowledge-card collection (166 cards) distilled from
professional accounting textbook content via the pdf2skill methodology. It is a
browseable knowledge layer, not a single executable tool.

> 这是一个**聚合型**会计知识卡集合（166 张知识卡），由专业会计教材内容经
> pdf2skill 方法论提炼而来。它是可浏览的知识层，而非单一可执行工具。

## How to use / 如何使用

1. **Browse first**：read `_cards/index.md` for the full skill table (topic /
   description / use case).
2. **Load the matching card**：`_cards/<topic>/SKILL.md` for the concrete
   procedure (frontmatter `name` usually bilingual, body in Chinese).
3. **Apply**：follow the card's steps; fill in the user's real numbers.

## Scope & coverage / 覆盖范围

- Bookkeeping：double-entry, vouchers, ledgers, accounting workflow
- Account classification & accounting subjects
- Financial statements：balance sheet, income statement, cash-flow statement
- Analysis：ratio, solvency, profitability, cash-flow, turnover
- Fraud detection：revenue/receivables/inventory misstatement patterns
- Cost & ownership-equity basics

See `_cards/index.md` for the authoritative 166-topic table.

## Source / 深挖参考

- 提炼方法：pdf2skill（github.com/dayuer/pdf2skill），AI 转写学习摘录
- 原始参考：《一看就懂的会计学全图解（升级版）》图书内容（版权归原作者）
- Disclaimer：本卡为 AI 学习摘录，仅供个人学习；不保证完整性，不构成专业会计意见。