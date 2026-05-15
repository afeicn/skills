---
name: moji-daily
description: 墨记 — 每日任务追踪系统。通过聊天对话自动管理每日待办事项的创建、更新、跟进、总结和滚动。适用场景：(1) 每日09:00 cron触发早间Review，询问用户当天任务并写入 tasks/YYYY-MM-DD.md；(2) 每日12:00 cron触发午间跟进，检查进度；(3) 每日18:00 cron触发晚间总结，汇总完成情况并滚动未完成项到次日；(4) 用户随时在聊天中报告任务完成、添加新任务、修改或取消任务时，自动更新任务文件。适合需要精细记录每日工作的管理者、创业者、咨询顾问，数据以本地Markdown文件存储，零服务器依赖，可轻松复制迁移。
version: 1.0.1
author: afeicn
license: MIT-0
---

# 墨记 (moji-daily)

## 概述

墨记是一个完全基于聊天对话的每日任务追踪系统。用户不需要打开任何网页——早间安排任务、午间汇报进度、晚间确认总结，全部在聊天中完成。数据存储为本地文件，零服务器运维，复制文件夹即可迁移。

## 架构

```
moji-daily/
├── SKILL.md                    ← 本文件（skill 说明）
├── assets/daily-template.md   ← 每日任务文件模板
├── references/workflow.md     ← 详细工作流（Cron场景 + 用户交互场景）
└── scripts/setup-crons.sh     ← 参考：Cron 配置模板
```

任务文件存储在工作目录的 `tasks/YYYY-MM-DD.md`，每天独立文件。

## 快速开始

### 1. 设置 Cron 定时任务

使用 Hermes 的 `cronjob` 工具创建三个定时任务：

**早间 Review（每天 09:00）**
```
cronjob(action='create', name='moji-daily-morning', schedule='0 9 * * *', prompt='现在是早上9点，请执行早间Review流程：1) 检查今天tasks/目录下是否有任务文件；2) 询问用户今天要安排什么任务；3) 将任务写入tasks/YYYY-MM-DD.md（用今天日期）。参考 moji-daily skill 的workflow。', skills=['moji-daily'])
```

**午间跟进（每天 12:00）**
```
cronjob(action='create', name='moji-daily-noon', schedule='0 12 * * *', prompt='现在是中午12点，请执行午间跟进流程：1) 读取今天的tasks/YYYY-MM-DD.md；2) 询问用户各项任务进展；3) 更新已完成和未完成项。参考 moji-daily skill 的workflow。', skills=['moji-daily'])
```

**晚间总结（每天 18:00）**
```
cronjob(action='create', name='moji-daily-evening', schedule='0 18 * * *', prompt='现在是下午6点，请执行晚间总结流程：1) 读取今天的tasks/YYYY-MM-DD.md；2) 汇总完成情况；3) 让用户确认后将未完成任务滚动到明天的文件。参考 moji-daily skill 的workflow。', skills=['moji-daily'])
```

### 2. 创建任务目录

系统会在首次使用时自动创建 `tasks/` 目录，也可以手动：
```bash
mkdir -p tasks
```

### 3. 开始使用

Cron 定时任务会自动在设定时间触发。用户也可以在聊天中随时汇报：
- "XXX做完了"
- "加一个任务XXX"
- "取消XXX"
- "XXX改到明天"

## 核心工作流

详见 `references/workflow.md`，涵盖 4 种场景：

| 场景 | 触发方式 | 目标 |
|------|---------|------|
| 早间Review | 09:00 Cron | 创建/更新当天任务清单 |
| 午间跟进 | 12:00 Cron | 检查进度，适时提醒 |
| 晚间总结 | 18:00 Cron | 汇总完成，滚动未完成项 |
| 用户主动交互 | 聊天消息 | 实时更新任务状态 |

## 命名规范

- **文件命名**：`tasks/YYYY-MM-DD.md`
- **状态标识**：`- [ ]` 待办 → `- [x]` 已完成

## When to Use / 触发条件

Agent 在以下场景应主动加载此 skill：
- 用户提到「今日任务」「待办」「今天做什么」「日程安排」「打卡」
- Cron 定时触发（09:00 / 12:00 / 18:00）时
- 用户说「XXX做完了」「加一个任务」「取消XXX」「XXX改到明天」等任务状态变更时
- 用户问「今天还有什么没做」

## Pitfalls / 注意事项

- **任务文件路径**：使用 `${HOME}/tasks/` 而非相对路径，cron 任务无工作目录上下文时会找不到文件。
- **Cron 首次创建**：用户首次使用需手动运行三个 `cronjob create` 命令，skill 不会自动创建 cron job。
- **跨日滚动**：晚间总结必须等用户确认后才创建明天的文件，未确认则保持现状。
- **时区**：Cron 使用系统本地时区，确保 `hermes config` 中 `timezone` 设置正确。
- **已有文件**：早间 Review 若检测到当天文件已存在，应先询问用户是否继续沿用或调整，不要覆盖。

## 迁移指南

把 `moji-daily/` 文件夹整体复制到新环境的 `~/.hermes/skills/productivity/` 目录即可。
复制后重新设置 cron 定时任务、创建 `tasks/` 目录，即刻可用。