# 销售运营助手数字员工

> 版本：2026-05-26  
> 部署建议：电脑5，飞书入口“小运”，Hermes Agent 员工 ID：`sales_management_assistant`

## 1. 员工定位

通过飞书接收团队周报、商机台账和销售过程数据，调用 Hermes Agent skills 完成销售周报、漏斗分析、重点商机预警、动作督办、销售预测、例会材料和赢单丢单复盘。

## 2. 场景包与子角色

| 场景包 | 子角色/责任位 | 目标 | 关键 skills |
| --- | --- | --- | --- |
| 销售周报汇总 | 经营汇报员 | 汇总销售个人周报、客户进展、风险和下周计划。 | SM01_weekly_report_summary, SM08_team_performance_hint |
| 销售漏斗分析 | 漏斗分析员 | 分析线索、商机、报价、合同和回款阶段的转化情况。 | SM02_pipeline_analysis, SM05_sales_forecast |
| 重点商机预警 | 商机督办员 | 标记大金额、久未推进、高风险和战略客户商机。 | SM03_key_deal_warning, SM04_sales_action_followup |
| 销售动作督办 | 督办员 | 催办拜访、方案、报价、合同、回款和客户确认事项。 | SM04_sales_action_followup, SM03_key_deal_warning |
| 销售预测 | 预测分析员 | 基于阶段、概率和历史转化率预测合同、收入和回款。 | SM05_sales_forecast, SM02_pipeline_analysis |
| 销售例会 | 会议材料员 | 生成销售周会/月会材料、讨论问题和决策事项。 | SM06_sales_meeting_pack, SM01_weekly_report_summary |
| 赢单丢单复盘 | 复盘员 | 复盘竞品、报价、方案、关系和过程动作。 | SM07_win_loss_review, SM08_team_performance_hint |

## 3. 领域 skills

| Skill ID | 名称 | 用途 | 主要输出 |
| --- | --- | --- | --- |
| SM01_weekly_report_summary | 销售周报汇总 | 汇总团队周报、客户进展、风险问题和下周计划。 | management_summary, progress_table, risk_items |
| SM02_pipeline_analysis | 销售漏斗分析 | 分析各销售阶段数量、金额、转化率和卡点。 | pipeline_report, conversion_metrics, bottlenecks |
| SM03_key_deal_warning | 重点商机预警 | 识别停滞、高金额、高风险、战略客户和临近节点商机。 | warning_list, risk_tags, priority_actions |
| SM04_sales_action_followup | 销售动作督办 | 生成拜访、方案、报价、合同和回款节点督办清单。 | followup_tasks, reminder_payload |
| SM05_sales_forecast | 销售预测 | 基于阶段概率、历史转化和人工修正生成预测。 | forecast_table, confidence_range, assumptions |
| SM06_sales_meeting_pack | 销售例会材料生成 | 生成例会议程、经营摘要、问题清单和决策事项。 | meeting_agenda, slide_outline, discussion_questions |
| SM07_win_loss_review | 赢单丢单复盘 | 复盘赢单或丢单原因并沉淀可复用打法。 | review_report, root_causes, playbook_updates |
| SM08_team_performance_hint | 团队经营提示 | 从过程数据中识别团队共性问题、能力短板和辅导建议。 | team_insights, coaching_suggestions |

## 4. 关键边界

- 可以生成草稿、建议、清单、摘要、风险提示和归档记录。
- 涉及业绩预测、对外汇报、销售目标调整、重大商机处置、团队评价时必须人工确认。
- 演示样例必须使用脱敏或虚拟数据，不使用真实客户、员工、财务、合同或技术敏感信息。
- 所有 Hermes Agent skill 调用需要记录输入、输出、确认人和归档位置。

## 5. 文件结构

```text
sales-management-assistant/
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
