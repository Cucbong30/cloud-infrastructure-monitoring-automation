# Week 07 - Hybrid Cloud Integration

Tuần 7 tập trung mở rộng hệ thống từ local lab sang mô hình Hybrid Cloud.

Phần Infrastructure thực hiện:

- Đưa `AZURE01` trên Azure vào hệ thống monitoring.
- Kết nối `AZURE01` với Prometheus và Ansible trên MON01.
- Test Nginx remediation trên Cloud target theo policy Week 6.
- Chuẩn bị Microsoft Entra ID cho SSO và RBAC.
- Chuẩn bị generic mailbox và Microsoft Graph cho Alert Notification.
- Bổ sung evidence còn thiếu theo góp ý của giảng viên.
- Cập nhật tài liệu và commit theo từng phần trên branch `infra`.

Mục tiêu cuối tuần là hệ thống có thể monitor và remediation cả local server lẫn Azure Cloud target.
