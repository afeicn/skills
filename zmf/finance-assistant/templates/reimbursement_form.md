# 报销单草稿

| 字段 | 内容 |
| --- | --- |
| 报销编号 | {{ reimbursement_id }} |
| 报销人 | {{ applicant_name }} |
| 部门 | {{ department }} |
| 项目/成本中心 | {{ project_or_cost_center }} |
| 费用类型 | {{ expense_type }} |
| 报销金额 | {{ amount }} |
| 发票号码 | {{ invoice_number }} |
| 开票日期 | {{ invoice_date }} |
| 销售方 | {{ seller_name }} |
| 购买方 | {{ buyer_name }} |
| 报销说明 | {{ reimbursement_description }} |
| 附件清单 | {{ attachment_list }} |

## 系统识别提示

- OCR 置信度：{{ ocr_confidence }}
- 费用类型置信度：{{ expense_type_confidence }}
- 需员工确认字段：{{ fields_need_user_confirm }}

