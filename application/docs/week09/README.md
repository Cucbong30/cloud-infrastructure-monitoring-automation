# Báo cáo Application — Tuần 9

Nguyễn Thế Gia Bảo – Application / Integration

Trạng thái: LOW vẫn chạy ngay. MEDIUM và HIGH tạo approval request, hết hạn sau 5 phút, chỉ Admin approve. Rejected và expired không gọi playbook. Evidence tối 20/11 ở `application/docs/week09/`.

## Công việc được phân công

- Approval workflow. Pending, Approved, Rejected, Expired.
- Operator không approve. Operator không request HIGH.
- Audit requester, approver, role, decision, timestamp, action, final status.
- Mail approval requested, approved, rejected.
- Chốt incident 46. Bộ ảnh này không có drawer job 71, job 72 và không có trang 403.

## Kết quả thực hiện

1. **LOW.** Job 79 WEB01 AUTO SUCCESS, approval required No.
2. **MEDIUM.** Request 7 approved, job 91 SUCCESS. Request 6 rejected, không có job. Request 2 và request 11 hết hạn.
3. **HIGH.** Request 8 approved, job 92 reboot AZURE01 SUCCESS. Request 9 rejected. Request 10 hết hạn. Operator không thấy nút Approve.
4. **Incident 46.** Đã resolved lúc 22:23 ngày 13/11, reason service restored, retry_count 0.

Báo cáo: [week-09-application.md](week-09-application.md). Bản Word: [week-09-application.docx](week-09-application.docx). Khai báo AI: [ai-usage.md](ai-usage.md).

## Kết quả trên GitHub

| Kết quả | Link | Commit |
| --- | --- | --- |
| Code tuần 9 | [b95ad44](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/b95ad447b07e58401e4296b4bd67a15852064998) | cùng link |
| Code tuần 8 | [4960f04](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/4960f041ed12294b595016e993720ba209fd6bf8) | cùng link |
| Báo cáo tuần 8 | [week08](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/e3ad3935a71b701b96f455ffb83121fc7e619497/application/docs/week08) | [e3ad393](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e3ad3935a71b701b96f455ffb83121fc7e619497) |
| Ảnh và báo cáo tuần 9 | [week09](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/__DOCS_SHA__/application/docs/week09) | [__DOCS_SHA__](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/__DOCS_SHA__) |

## Ảnh

Xem [screenshots/README.md](screenshots/README.md).
