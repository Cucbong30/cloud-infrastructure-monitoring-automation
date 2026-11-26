# TUẦN 01 – System Architecture & Design

## 1. Mục tiêu theo roadmap

Thiết kế kiến trúc hạ tầng và ứng dụng, xác định các thành phần và chuẩn bị nền tảng triển khai.

## 2. Phân công và kết quả thực hiện

### 2.1. Đỗ Đăng Thái Bảo

**Vai trò:** Infrastructure / System / Cloud

| STT | Công việc được phân công | Kết quả thực hiện | Trạng thái | Tài liệu / Minh chứng |
|---|---|---|---|---|
| 1 | Thiết kế kiến trúc hạ tầng và VM Specification | Xác định MON01, WEB01, APP01, WIN01 và vai trò từng máy. | Đã thực hiện | [Tài liệu](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/main/infrastructure/vm-specification.md) |
| 2 | Network/IP Plan | Xác định subnet, IP và gateway. | Đã thực hiện | [Tài liệu](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/main/infrastructure/network-plan.md) |
| 3 | Port Plan | Xác định port SSH, WinRM, monitoring, exporter và Flask. | Đã thực hiện | [Tài liệu](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/main/infrastructure/ports.md) |
| 4 | Infrastructure & Network Diagram; Monitoring & Automation Diagram | Hoàn thành hai sơ đồ và tài liệu chuẩn bị Tuần 2. | Đã thực hiện | Chờ bổ sung link |

### 2.2. Nguyễn Thế Gia Bảo

**Vai trò:** Application / Integration

| STT | Công việc được phân công | Kết quả thực hiện | Trạng thái | Tài liệu / Minh chứng |
|---|---|---|---|---|
| 1 | Xác định module Portal và kiến trúc ứng dụng | Chốt Login, Dashboard, Inventory, Alerts, Jobs, Audit; thiết kế Flask, SQLite và adapter tích hợp. | Đã thực hiện | Chờ bổ sung link |
| 2 | Thiết kế ERD | Xác định users, servers, alerts, automation_jobs, audit_logs, PK/FK và quan hệ. | Đã thực hiện | Chờ bổ sung link |
| 3 | Thiết kế wireframe | Hoàn thành Login, Dashboard, Inventory, Server Detail, Alerts, Jobs, Audit. | Đã thực hiện | Chờ bổ sung link |
| 4 | Flask skeleton, SQLite schema và mock data | Portal chạy được; metrics N/A khi Prometheus chưa sẵn sàng. | Đã thực hiện | Chờ bổ sung link |
| 5 | Thiết kế tích hợp Prometheus và Ansible | Chốt phương thức tích hợp; chưa thực thi trên máy thật. | Đã thực hiện | Chờ bổ sung link |

## 3. Công việc phối hợp

Thống nhất kiến trúc, danh sách máy chủ, module Portal và ranh giới tích hợp.

## 4. Tổng kết và nội dung cần theo dõi

Hoàn thành thiết kế theo tài liệu phân công. Bổ sung link sơ đồ, ERD, wireframe và commit Application khi có.
