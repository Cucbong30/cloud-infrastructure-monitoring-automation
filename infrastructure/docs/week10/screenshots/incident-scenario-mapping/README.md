# Incident Scenario Mapping – Evidence

## 1. Mục đích

Lưu minh chứng kiểm tra Alert Rule hiện tại để
xác định nguồn phát hiện sự cố và xây dựng
Incident Scenario Mapping trong Tuần 10.

## 2. Danh sách minh chứng

| STT | Screenshot | Nội dung |
|---|---|---|
| 08 | 08-incident-scenario-mapping.png | Kiểm tra Alert Name, Expression và Severity |

## 3. Kết quả

- Alert Rule: InstanceDown
- Expression: up == 0
- Severity: critical
- Total Alert Rules: 1
- Prometheus Targets: 6/6 UP

Không thay đổi hoặc bổ sung Alert Rule mới.

Incident Scenario Mapping phía Infrastructure
đã được chuẩn bị, chờ đối chiếu với Application.

## 4. Tài liệu liên quan

[Incident Scenario Mapping](../../configs/incident-scenario-mapping.md)
