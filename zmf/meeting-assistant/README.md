# 会议助手数字员工

> 版本：2026-05-26  
> 部署建议：电脑9，飞书入口“会议助手”，Hermes Agent 员工 ID：`meeting_assistant`

## 1. 员工定位

通过飞书接收会议主题、背景材料、录音转写和聊天记录，调用 Hermes Agent skills 完成会前准备、会中记录、会议纪要、行动项、会后督办、会议复盘和知识归档。

## 2. 场景包与子角色

| 场景包 | 子角色/责任位 | 目标 | 关键 skills |
| --- | --- | --- | --- |
| 会前准备 | 会议秘书 | 生成议程、参会人、资料包、通知和讨论问题。 | MT01_agenda_generate, MT02_material_pack, MT03_meeting_notice |
| 会中记录 | 记录员 | 接收录音或转写，整理关键讨论、分歧和待确认问题。 | MT04_transcript_clean, MT05_minutes_generate |
| 会议纪要 | 纪要员 | 生成结构化纪要、决议、问题清单和附件索引。 | MT05_minutes_generate, MT06_action_item_extract |
| 行动项提取 | 督办员 | 提取责任人、事项、截止时间、依赖和完成标准。 | MT06_action_item_extract, MT07_action_followup |
| 会后督办 | 执行跟踪员 | 发送飞书提醒、收集进展、更新状态和提示延期。 | MT07_action_followup |
| 会议复盘 | 复盘员 | 复盘会议质量、未闭环事项和改进建议。 | MT08_meeting_retro_archive |
| 知识归档 | 档案员 | 将纪要、决议、行动项和资料归档到项目或客户库。 | MT08_meeting_retro_archive, MT05_minutes_generate |

## 3. 领域 skills

| Skill ID | 名称 | 用途 | 主要输出 |
| --- | --- | --- | --- |
| MT01_agenda_generate | 会前议程生成 | 根据会议主题、目标、背景和参会人生成议程和讨论问题。 | agenda, discussion_questions, time_plan |
| MT02_material_pack | 会议资料包生成 | 汇总背景资料、项目状态、客户信息和需要预读的材料。 | material_pack, reading_list, missing_materials |
| MT03_meeting_notice | 参会通知生成 | 生成会议通知、参会人提醒、资料链接和会前准备要求。 | notice_text, feishu_reminder_payload |
| MT04_transcript_clean | 录音转写整理 | 整理录音转写、去噪、分段并识别发言人和议题。 | clean_transcript, topic_segments, speaker_notes |
| MT05_minutes_generate | 会议纪要生成 | 生成背景、议题、讨论过程、决议、问题和附件索引。 | minutes_draft, decisions, issue_list, attachment_index |
| MT06_action_item_extract | 行动项提取 | 提取责任人、任务、截止时间、依赖关系和验收标准。 | action_items, owner_table, due_dates |
| MT07_action_followup | 行动项督办 | 生成飞书待办、提醒节奏、延期提示和状态汇总。 | reminder_payload, status_summary, overdue_list |
| MT08_meeting_retro_archive | 会议复盘与归档 | 生成会议复盘、未闭环事项、知识标签和归档记录。 | retro_summary, archive_record, knowledge_tags |

## 4. 关键边界

- 可以生成草稿、建议、清单、摘要、风险提示和归档记录。
- 涉及正式会议纪要、决议发布、对外发送纪要、责任人和截止时间调整时必须人工确认。
- 演示样例必须使用脱敏或虚拟数据，不使用真实客户、员工、财务、合同或技术敏感信息。
- 所有 Hermes Agent skill 调用需要记录输入、输出、确认人和归档位置。

## 5. 文件结构

```text
meeting-assistant/
  README.md
  employee.yaml
  system_prompt.md
  workflows.md
  runbook.md
  skills/
  knowledge/
  templates/
  test_cases/
  demo/
```
