# Báo cáo Application — Tuần 5

Nguyễn Thế Gia Bảo – Application / Integration

Trạng thái: Portal chặn remediation khi SSH hoặc WinRM down, và chỉ nhận Success khi post-check thấy service lên. Evidence nằm ở `application/docs/week05/`.

## Công việc được phân công

- Gợi ý remediation theo server và service.
- Pre-check management channel trước khi tạo job.
- Verification sau Ansible, Job Detail, Alert gắn Job, Retry.
- Audit `remediation.blocked`, `remediation.verified`, `remediation.failed`.

## Kết quả thực hiện

1. **Management channel.** WEB01 và APP01 dùng SSH `:22`. WIN01 dùng WinRM `:5985`. SSH down không làm WEB01 hay APP01 thành Unreachable.
2. **Blocked.** Cổng down thì không gọi playbook và không tạo job mới. Reason ghi rõ kênh nào down.
3. **Lỗi giữ lại.** 21:20 ngày 23/10, APP01 vẫn Healthy nhưng `restart_container` đã chạy và `No route to host`. Job không xóa.
4. **Sau khi sửa.** Tối 30/10, APP01 Healthy và SSH DOWN thì remediation bị chặn. SSH lên lại thì job 20 Success, verification Passed.
5. **WIN01.** WinRM down trong khi exporter còn UP thì host Degraded, remediation unavailable.
6. **Retry.** Job 19 là job mới, retry của job 18. Job 18 không bị sửa.

Báo cáo: [week-05-application.md](week-05-application.md). Bản Word: [week-05-application.docx](week-05-application.docx). Khai báo AI: [ai-usage.md](ai-usage.md).

## Kết quả trên GitHub

| Kết quả | Link | Commit |
| --- | --- | --- |
| Code tuần 5 | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/a7a65e96e9265517fad7cac7c136f9e1f0825bf4/application | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/a7a65e96e9265517fad7cac7c136f9e1f0825bf4 |
| Pre-check | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/a7a65e96e9265517fad7cac7c136f9e1f0825bf4/application/app/services/checks.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/a7a65e96e9265517fad7cac7c136f9e1f0825bf4 |
| Job và verification | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/a7a65e96e9265517fad7cac7c136f9e1f0825bf4/application/app/services/automation.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/a7a65e96e9265517fad7cac7c136f9e1f0825bf4 |
| Allow-list tuần 4 | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/aecb279c07407ae612b4b9476fec702ddeaa1eaf/application | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/aecb279c07407ae612b4b9476fec702ddeaa1eaf |
| Ảnh ba job tuần 4 | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/64b6de060eb31a7b09230cf36afa0e88b6673969/application/docs/week04/screenshots/02-three-playbooks-success.png | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/64b6de060eb31a7b09230cf36afa0e88b6673969 |

Bảng đủ file và ảnh nằm trong [week-05-application.md](week-05-application.md).

## Ảnh

Xem [screenshots/README.md](screenshots/README.md).
