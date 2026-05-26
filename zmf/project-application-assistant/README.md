# 项目申报数字员工数字员工

> 版本：2026-05-26  
> 部署建议：电脑7，飞书入口“小申”，Hermes Agent 员工 ID：`project_application_assistant`

## 1. 员工定位

通过飞书接收政策通知、申报指南、企业资料和项目材料，调用 Hermes Agent skills 完成政策机会、指南解析、匹配评估、材料清单、申报书框架、预算辅助、附件检查和答辩准备。

## 2. 场景包与子角色

| 场景包 | 子角色/责任位 | 目标 | 关键 skills |
| --- | --- | --- | --- |
| 政策机会 | 政策情报员 | 抓取和整理项目申报通知，生成机会摘要和提醒。 | A01_policy_opportunity_monitor, A02_guideline_parse |
| 指南解析 | 申报分析员 | 提取申报方向、条件、时间、材料、评分点和限制条件。 | A02_guideline_parse, A04_material_checklist |
| 匹配评估 | 申报顾问 | 判断企业和项目是否符合申报条件并提示风险。 | A03_match_evaluation, A02_guideline_parse |
| 材料清单 | 申报秘书 | 生成附件清单、责任人、截止时间和补充材料提醒。 | A04_material_checklist, A08_attachment_review |
| 申报书撰写 | 申报写作员 | 生成申报书目录、章节框架、亮点和正文初稿。 | A05_application_outline, A06_application_draft |
| 预算辅助 | 预算助理 | 生成预算科目、费用说明和合规提示。 | A07_budget_draft |
| 附件检查 | 材料质检员 | 检查附件完整性、格式、盖章、时间和一致性。 | A08_attachment_review, A04_material_checklist |
| 答辩准备 | 答辩教练 | 预测评审问题并生成答辩口径和 PPT 大纲。 | A09_review_question_predict, A06_application_draft |

## 3. 领域 skills

| Skill ID | 名称 | 用途 | 主要输出 |
| --- | --- | --- | --- |
| A01_policy_opportunity_monitor | 政策机会监测 | 整理政策通知、申报公告、截止时间和适配方向。 | opportunity_list, deadline_alert, source_links |
| A02_guideline_parse | 申报指南解析 | 提取申报方向、条件、材料、流程、时间和评分关注点。 | parsed_guideline, requirements, timeline, scoring_focus |
| A03_match_evaluation | 申报匹配度评估 | 判断企业、项目、团队、财务和知识产权是否满足条件。 | match_score, matched_items, gaps, risk_items |
| A04_material_checklist | 材料清单生成 | 生成附件、证明、责任人、截止时间和补充材料清单。 | material_checklist, owner_table, missing_items |
| A05_application_outline | 申报书框架生成 | 根据指南生成申报书目录、章节重点和写作素材需求。 | application_outline, section_requirements, material_needs |
| A06_application_draft | 申报书初稿生成 | 生成项目背景、技术路线、创新点、应用价值和实施计划初稿。 | draft_sections, highlights, need_human_input |
| A07_budget_draft | 预算测算辅助 | 生成预算科目、费用说明、测算依据和合规风险提示。 | budget_table, budget_notes, risk_notes |
| A08_attachment_review | 附件完整性检查 | 检查附件、格式、盖章、日期、主体一致性和缺项。 | review_result, missing_items, correction_notice |
| A09_review_question_predict | 评审问题预判 | 预测评审关注问题、答辩口径和 PPT 大纲。 | question_list, answer_points, ppt_outline |

## 4. 关键边界

- 可以生成草稿、建议、清单、摘要、风险提示和归档记录。
- 涉及是否申报、申报承诺、预算金额、财务数据、盖章材料、最终提交时必须人工确认。
- 演示样例必须使用脱敏或虚拟数据，不使用真实客户、员工、财务、合同或技术敏感信息。
- 所有 Hermes Agent skill 调用需要记录输入、输出、确认人和归档位置。

## 5. 文件结构

```text
project-application-assistant/
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
