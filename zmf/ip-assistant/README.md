# 知识产权助手数字员工

> 版本：2026-05-26  
> 部署建议：电脑10，飞书入口“小知”，Hermes Agent 员工 ID：`ip_assistant`

## 1. 员工定位

通过飞书接收技术方案、产品说明、研发记录、软件材料和商标信息，调用 Hermes Agent skills 完成创新点挖掘、专利交底、专利检索、软著材料、商标材料、期限管理、IP 台账和成果归档。

## 2. 场景包与子角色

| 场景包 | 子角色/责任位 | 目标 | 关键 skills |
| --- | --- | --- | --- |
| 创新点挖掘 | 技术挖掘员 | 从项目、产品和方案中提炼可申报 IP 点。 | IP01_innovation_mining, IP08_tech_result_archive |
| 专利交底 | 专利撰写助理 | 生成交底书初稿、技术效果和实施例。 | IP02_patent_disclosure_generate, IP01_innovation_mining |
| 专利检索 | 检索分析员 | 根据关键词和检索结果生成相似技术摘要。 | IP03_patent_search_summary |
| 软著材料 | 软著助理 | 生成软著说明书、功能说明、材料清单和代码说明。 | IP05_software_copyright_material |
| 商标材料 | 商标助理 | 生成商标申请材料清单、类别建议和使用说明。 | IP04_trademark_material_checklist |
| 期限管理 | 期限管理员 | 管理补正、答复、缴费、续展等期限并飞书提醒。 | IP06_ip_deadline_reminder, IP07_ip_ledger_update |
| IP 台账 | 台账管理员 | 维护专利、商标、软著状态和风险标签。 | IP07_ip_ledger_update |
| 成果归档 | 成果管理员 | 将研发成果沉淀为可检索、可复用、可申报材料。 | IP08_tech_result_archive, IP01_innovation_mining |

## 3. 领域 skills

| Skill ID | 名称 | 用途 | 主要输出 |
| --- | --- | --- | --- |
| IP01_innovation_mining | 创新点挖掘 | 从技术方案、项目材料和产品说明中提炼创新点、差异点和技术效果。 | innovation_points, technical_effects, disclosure_questions |
| IP02_patent_disclosure_generate | 专利交底书生成 | 生成技术领域、背景问题、方案、效果、附图说明和实施例初稿。 | disclosure_draft, missing_details, inventor_questions |
| IP03_patent_search_summary | 专利检索摘要 | 基于关键词和检索结果生成相似技术、差异方向和风险提示。 | search_summary, similar_tech, differentiation_notes |
| IP04_trademark_material_checklist | 商标材料清单 | 生成商标名称、类别、申请主体、使用证据和材料清单。 | trademark_checklist, class_suggestion, risk_notes |
| IP05_software_copyright_material | 软著材料生成 | 生成软件说明书、功能模块、运行环境、材料清单和代码说明。 | copyright_materials, manual_outline, missing_items |
| IP06_ip_deadline_reminder | IP 期限提醒 | 管理答复、缴费、补正、续展和年费等期限提醒。 | deadline_list, reminder_payload, overdue_alerts |
| IP07_ip_ledger_update | IP 台账更新 | 生成专利、商标、软著状态、费用、负责人和风险标签。 | ledger_row, status_summary, risk_tags |
| IP08_tech_result_archive | 研发成果归档 | 将项目成果、技术点、材料和后续申请建议归档。 | archive_record, knowledge_tags, reuse_suggestions |

## 4. 关键边界

- 可以生成草稿、建议、清单、摘要、风险提示和归档记录。
- 涉及是否申请、专利权利要求、商标类别、最终提交、答复口径、费用缴纳时必须人工确认。
- 演示样例必须使用脱敏或虚拟数据，不使用真实客户、员工、财务、合同或技术敏感信息。
- 所有 Hermes Agent skill 调用需要记录输入、输出、确认人和归档位置。

## 5. 文件结构

```text
ip-assistant/
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
