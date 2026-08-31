# Changelog 更新日志

## [0.3.0] — 2026-08-31
### Added 新增
- 新增「知识领域（Knowledge-domain）」分类，收录 3 个教材知识卡聚合 skill：
  - `accounting-basics` — 会计专业技能知识卡聚合（166 卡，源自会计学教材）
  - `cpa-financial-management` — 注会《财务成本管理》知识卡聚合（442 卡）
  - `cpa-financial-management-expert` — 注会《财务成本管理》专家团版
    （113 SKU：mapping.md 路由表 + skills.json 注册表 + eureka.md 知识图谱 + skus/）
- 三包均来自 `D:\出厂自带\桌面备份\AI\AI配置\Agent Skills\`（pdf2skill 产物）。
- README 索引扩充为「发布工程 / 通用技能 / 知识领域」三大板块并增版权提示。

### Security 安全
- 审计确认三包无真实敏感标识（用户名/主机名/密钥/路径 0 命中）。
- 三包为受版权教材的 AI 学习摘录，已在 README 标注「仅供个人学习，版权归原作者/出版社」。

## [0.2.0] — 2026-08-31
### Added 新增
- 新增 15 个通用技能（来自 WorkBuddy 自建备份，均为 AI 原创 `agent_created=true`，脱敏后入库）：
  - `deepseek-image-ocr` — 无视觉模型时经 DeepSeek 网页识读图片内容
  - `github-mirror` — 经公共镜像加速 GitHub 下载
  - `agnes-multimodal` — Agnes AI 多模态生成客户端（密钥改走 `AGNES_API_KEY` 环境变量）
  - `bilinote-skill` — B 站/笔记处理
  - `cli-skill-calibrator` — CLI 技能校准
  - `darwin-skill` — 达尔文式循证研究流水线
  - `Exam2Knowledge` — 考试资料转知识库
  - `opencode-compose-max` / `opencode-compose-next` / `opencode-max` — 三档工作模式
  - `ponytail` / `ponytail-toolkit` — 懒人极简哲学与按需工具箱
  - `retail-investors` — 散户投资研究框架
  - `scientific-learning-loop` — 科学学习循环
  - `xiaohongshu-ops-framework` — 小红书运营框架
- README 技能索引扩充为「发布工程 / 通用技能」两大板块。

### Security 安全
- `agnes-multimodal` 原有 `keys.conf` 含真实 `sk-` 密钥，**不入库**；`agnes_client.py` 改为仅从环境变量读取，杜绝密钥公开。

## [0.1.0] — 2026-08-31
### Added 新增
- 初建 skills 集合，沉淀自 `github-publish-playbook`（蛟龙15K / Acer A615-51G 公开发布经验）。
- 收录 6 个可用 skill：
  - `github-publish-redact` — 发布前脱敏与保密
  - `github-publish-compliance` — 社区文件与合规
  - `github-publish-readme` — README 双语工程
  - `github-publish-git-safe` — 本地 git 安全初始化与提交
  - `github-publish-push-scan` — 建仓推送与安全扫描
  - `github-publish-ops` — 发布后运营与迭代升级
- 配套：双语 README、LICENSE（署名 段雪健）、THIRDPARTY、SECURITY、CONTRIBUTING、FUNDING、打赏二维码 assets。