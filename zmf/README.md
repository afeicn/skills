# ZMF Digital Employees

ZMF 数字员工放在本目录下，区别于仓库中的通用 skills。每个数字员工都是一个可部署到飞书 + Hermes Agent 的岗位型能力包。

## Current Packages

| Package | Description |
| --- | --- |
| `finance-assistant/` | 财务助手数字员工，覆盖报销申请受理、报销单审核、审批流转、财务制度问答、台账与费用分析。 |
| `bid-assistant/` | 标书助手数字员工，覆盖招标机会识别、招标文件解析、评分模型建立、服务方案结构设计、章节撰写、表达净化、一致性审查和投标复盘。 |
| `marketing-assistant/` | 通过飞书接收主题、素材和传播需求，调用 Hermes Agent skills 完成选题策划、海报文案、公众号初稿、短视频脚本、活动方案、发布包和营销复盘。 |
| `sales-assistant/` | 通过飞书接收客户信息、拜访记录、聊天记录和需求材料，调用 Hermes Agent skills 完成商机卡、客户画像、拜访纪要、需求提炼、跟进建议、风险提示和客户归档。 |
| `sales-management-assistant/` | 通过飞书接收团队周报、商机台账和销售过程数据，调用 Hermes Agent skills 完成销售周报、漏斗分析、重点商机预警、动作督办、销售预测、例会材料和赢单丢单复盘。 |
| `hr-assistant/` | 通过飞书接收岗位需求、简历、面试记录、合同模板和培训资料，调用 Hermes Agent skills 完成岗位画像、JD、简历筛选、面试支持、录用入职、劳动合同、培训计划和制度问答。 |
| `project-application-assistant/` | 通过飞书接收政策通知、申报指南、企业资料和项目材料，调用 Hermes Agent skills 完成政策机会、指南解析、匹配评估、材料清单、申报书框架、预算辅助、附件检查和答辩准备。 |
| `project-management-assistant/` | 通过飞书接收合同、方案、会议纪要、日报周报和交付材料，调用 Hermes Agent skills 完成项目启动、WBS、进度跟进、风险预警、周报、客户沟通、验收归档和复盘。 |
| `meeting-assistant/` | 通过飞书接收会议主题、背景材料、录音转写和聊天记录，调用 Hermes Agent skills 完成会前准备、会中记录、会议纪要、行动项、会后督办、会议复盘和知识归档。 |
| `legal-assistant/` | 通过飞书接收合同、补充协议、合作方案和法律咨询问题，调用 Hermes Agent skills 完成合同接收、要素抽取、条款风险审查、模板对比、修改建议、法律问答、审批意见和合同台账。 |
| `ip-assistant/` | 通过飞书接收技术方案、产品说明、研发记录、软件材料和商标信息，调用 Hermes Agent skills 完成创新点挖掘、专利交底、专利检索、软著材料、商标材料、期限管理、IP 台账和成果归档。 |

## Package Structure

Each digital employee package should follow this structure:

```text
employee.yaml
system_prompt.md
workflows.md
skills/
knowledge/
templates/
test_cases/
demo/
runbook.md
```

## Completion Checklist

See `digital-employees-checklist.md` for the 11-package completion list, deployment mapping, scenario counts and skill counts.
