# ZMF Digital Employees

This folder contains Zhuomufeng (ZMF) digital employee packages. These are kept separate from the general-purpose skills in this repository because they are business-specific employee/workflow definitions intended for Feishu + Hermes Agent deployment.

## Current Packages

| Package | Description |
| --- | --- |
| `finance-assistant/` | 财务助手数字员工，覆盖报销申请受理、报销单审核、审批流转、财务制度问答、台账与费用分析。 |
| `bid-assistant/` | 标书助手数字员工，覆盖招标机会识别、招标文件解析、投标可行性评估、任务拆解、标书撰写、合规审查和投标复盘。 |

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
