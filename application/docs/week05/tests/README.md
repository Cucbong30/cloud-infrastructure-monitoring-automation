# Test tuần 5

Các case đã đối chiếu trên lab và bằng test tự động:

- SSH `:22` của WEB01 hoặc APP01 down thì không tạo job và không gọi playbook. Audit `remediation.blocked`.
- Exporter và service còn UP thì host vẫn Healthy.
- WinRM down trong khi Windows Exporter UP thì WIN01 Degraded, remediation bị chặn.
- Exit code 0 mà post-check fail thì Verification Failed, không phải Success.
- Retry tạo job mới.
