---
name: agnes-multimodal
description: Agnes AI 多模态生成技能，支持文生图、图生图、文生视频、图生视频。基于 agnes-image-2.1-flash 和
  agnes-video-v2.0 模型。当用户需要 AI
  生成图片或视频、把文字描述转为视觉内容、或对现有图片做图生图变换时使用。触发词:生成图片,文生图,图生图,生成视频,文生视频,图生视频,AI绘画,AI视频,agnes。
version: 1.0.0
agent_created: true
disable-model-invocation: true
---

# Agnes AI Multimodal Generation

集成 Agnes AI API 进行图像和视频生成。API 兼容 OpenAI 格式，Base URL: `https://apihub.agnes-ai.com/v1`。

## 前置要求

- API Key 已预配置在 `scripts/keys.conf` 文件中（双 Key 自动轮换）
- 若需更换 Key，编辑 `scripts/keys.conf` 或在控制台创建新 Key

## 支持的模型

| 模型 | 用途 |
|---|---|
| `agnes-image-2.1-flash` | 文生图 / 图生图 |
| `agnes-video-v2.0` | 文生视频 / 图生视频 / 多图视频 / 关键帧动画 |

## 核心 API 端点

### 1. 图像生成 (`images/generations`)

**端点**: `POST https://apihub.agnes-ai.com/v1/images/generations`

**请求格式** (OpenAI-compatible):
```json
{
  "model": "agnes-image-2.1-flash",
  "prompt": "你的描述词",
  "size": "1024x768",
  "n": 1
}
```

**关键参数**:
- `model`: 固定 `agnes-image-2.1-flash`
- `prompt`: 英文提示词效果最佳，格式建议 `[主体] + [场景/环境] + [风格] + [光照] + [构图] + [质量要求]`
- `size`: 支持 `1024x1024`, `1024x768`, `768x1024` 等，默认 `1024x1024`
- `n`: 生成数量，默认 1

**图生图模式**: 添加 `"image": "https://..."` 参数。

### 2. 视频生成 (`videos`)

**创建任务**: `POST https://apihub.agnes-ai.com/v1/videos`

**轮询结果**: `GET https://apihub.agnes-ai.com/v1/videos/{task_id}`

**请求格式**:
```json
{
  "model": "agnes-video-v2.0",
  "prompt": "视频描述",
  "size": "1280x768",
  "duration_seconds": 5,
  "fps": 24
}
```

**关键参数**:
- `model`: 固定 `agnes-video-v2.0`
- `prompt`: 视频内容描述
- `size`: `1280x768`(16:9) 或 `768x1280`(9:16)
- `duration_seconds`: 3, 5, 10, 18 秒
- `fps`: 帧率

**异步流程**:
1. POST 创建任务 → 返回 `task_id`
2. 轮询 GET `/v1/videos/{task_id}` 直到 `status: "completed"` 或失败
3. 轮询间隔 3-5 秒

## 使用流程

1. **询问用户**需要生成什么（图片/视频/描述词）
2. **自动使用预配置的 API Key**（已在 `scripts/keys.conf` 中配置）
3. **调用 API**获取结果

> 🔴 **CHECKPOINT · 调用前确认**：发出请求前，先与用户确认「生成类型（图/视频）+ 尺寸 + 数量 + 风格描述」齐备。视频为异步计费任务（见 §注意事项），避免无谓消耗；若用户在初始请求中已明确给出全部参数，可跳过此确认直接调用。

### 脚本调用方式

```bash
# 生成图像（英文提示词效果最佳）
python scripts/agnes_client.py image "A futuristic city at sunset, cinematic lighting" 1024x1024 ./output

# 生成视频（异步轮询，最多等待 600 秒）
python scripts/agnes_client.py video "A cat walking on the beach at sunset" 1280x768 5 24 5
```

### 直接 HTTP 调用（OpenAI 兼容格式）

```bash
# 图像生成
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"agnes-image-2.1-flash","prompt":"你的描述","size":"1024x1024"}'

# 视频生成
curl https://apihub.agnes-ai.com/v1/videos \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"agnes-video-v2.0","prompt":"你的视频描述","size":"1280x768","duration_seconds":5}'
```

**视频轮询**: 创建任务后使用 `GET https://apihub.agnes-ai.com/v1/videos/{task_id}` 轮询状态直到 `completed`

## 失败模式与降级（dim3 · 必须显式处理）

| 触发条件 | 一线修复 | 仍失败兜底 |
|----------|----------|------------|
| API Key 缺失 / `keys.conf` 不存在 | 提示用户「请在 `scripts/keys.conf` 配置双 Key，或在控制台创建新 Key」 | 终止并说明无法调用，不编造输出 |
| 图像生成返回非 200 / 报错 | 检查 `size` 是否在允许集（1024x1024/1024x768/768x1024）内；重试 1 次 | 返回错误原文给用户，不静默降级 |
| 视频任务 `status` 长时间非 `completed` | 按 §异步流程 轮询（间隔 3-5s，上限 600s） | 超时即报「视频生成超时」，返回 `task_id` 供用户稍后查询 |
| 图生图但 `image` 参数 URL 不可达 | 提示用户提供可公网访问的图片链接 | 退化为文生图，明确告知已改变模式 |

## 反模式与黑名单（不要做什么 · dim9 合规必读）

| # | 反模式（不要做） | 为什么不要做 | 正确做法 |
|---|----------------|--------------|----------|
| 1 | **把 API Key 写进提示词 / 提交到仓库** | Key 泄露导致额度被盗用 | Key 仅存 `scripts/keys.conf`，调用走 Bearer Header，不进 prompt |
| 2 | **忽略 `size` 限制硬传非法分辨率** | 服务端拒绝，浪费一次请求 | 使用允许集，或按比例取最接近项 |
| 3 | **视频任务无上限轮询 / 无限重试** | 占用会话、额度空耗 | 轮询上限 600s，超时即报并交还 `task_id` |
| 4 | **中文提示词不转写直接发** | 非英文描述效果明显偏差 | 提示词默认英文；中文先内部转写为 `[主体]+[场景]+[风格]+[光照]+[构图]+[质量]` |

## 权限与依赖（运行时声明 · P0）

- **必需依赖**：`scripts/keys.conf`（双 Key，自动轮换）；Python 3 运行 `scripts/agnes_client.py`
- **调用工具**：`Bash`（执行 `python` / `curl` 调 Agnes API）
- **外部服务**：`https://apihub.agnes-ai.com/v1`（需联网；图像免费、视频可能计费，以控制台为准）
- **不依赖**任何宿主 agent 专属能力，可在任意 skills-compatible runtime 安装使用

## 注意事项

- 提示词建议使用英文，效果更准确
- 图像生成免费，视频生成可能收费（以控制台为准）
- 视频为异步任务，需耐心等待完成
- 超时设置：图像 60-360s，视频 300-1800s

## Changelog

### 1.0.0 — 2026-07-12（首版结构补全 · 借 skill-optimization-playbook 方法论）

- 补 `version` 字段 + 触发词（dim1）
- 新增 🔴 CHECKPOINT 调用前确认（dim4）
- 新增「失败模式与降级」if-then 表（dim3）
- 新增「反模式与黑名单」不要做表（dim9）
- 新增「权限与依赖」运行时声明（P0 perms）
- 新增 `test-prompts.json`（dim8 实测基线）
