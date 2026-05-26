# 报销审核意见

## 处理结论

{{ audit_result }}

## 审核明细

| 审核项 | 结果 | 说明 |
| --- | --- | --- |
| 发票识别 | {{ invoice_ocr_status }} | {{ invoice_ocr_message }} |
| 发票验真 | {{ invoice_verify_status }} | {{ invoice_verify_message }} |
| 重复报销 | {{ duplicate_status }} | {{ duplicate_message }} |
| 附件完整性 | {{ attachment_status }} | {{ attachment_message }} |
| 费用标准 | {{ policy_status }} | {{ policy_message }} |
| 项目/部门归属 | {{ cost_center_status }} | {{ cost_center_message }} |
| 审批路径 | {{ approval_route_status }} | {{ approval_route_message }} |

## 需要补充

{{ missing_materials }}

## 下一步建议

{{ next_action }}

