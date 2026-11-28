# Cấu hình tuần 10

| Mục | Lab 28/11 |
| --- | --- |
| Trạng thái | OPEN, ACKNOWLEDGED, IN_PROGRESS, RESOLVED, CLOSED |
| Auto | Bỏ qua acknowledge, vào IN_PROGRESS khi playbook bắt đầu |
| Close | Chỉ từ RESOLVED |
| Risk | Lấy từ runbook. Container LOW. Docker service MEDIUM |
| Recovery | HTTP 200. HTTP 403 không tính là đã phục hồi |
| Timeout approval | Request 11 đã APPROVAL_EXPIRED lúc 20:25 ngày 20/11. Không đổi trạng thái đó |
