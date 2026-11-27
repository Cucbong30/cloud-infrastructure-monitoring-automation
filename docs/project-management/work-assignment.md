# BẢNG PHÂN CÔNG CÔNG VIỆC

## 1. Thông tin đề tài

**Đề tài:** Xây dựng hệ thống giám sát và tự động hóa vận hành hạ tầng trong môi trường Hybrid Cloud.

## 2. Phân công theo vai trò

| Thành viên | Vai trò | Công việc phụ trách |
|---|---|---|
| Đỗ Đặng Thái Bảo | Infrastructure / System / Cloud | Thiết kế và triển khai hạ tầng, Linux, Windows Server, Networking, Monitoring, Ansible, Microsoft Azure, Entra ID và kiểm thử Infrastructure. |
| Nguyễn Thế Gia Bảo | Application / Integration | Phát triển Operations Portal, Database, API Integration, Automation Workflow, SSO, RBAC, Approval, Incident Management, Audit Log và Notification. |

Hai thành viên cùng thống nhất kiến trúc, tích hợp hệ thống, kiểm thử các tình huống sự cố và xây dựng tài liệu đề tài.

## 3. Bảng phân công theo từng tuần

| Tuần | Nội dung | Đỗ Đặng Thái Bảo | Nguyễn Thế Gia Bảo | Trạng thái | Chi tiết |
|---|---|---|---|---|---|
| 01 | System Design | Thiết kế kiến trúc hạ tầng, VM, Network, IP và Port Plan. | Thiết kế Application Architecture, Database, Wireframe và các module Portal. | Hoàn thành | [Tuần 01](weekly-progress/week01.md) |
| 02 | System Deployment | Triển khai các VM, dịch vụ, SSH, WinRM và Monitoring Exporter. | Phát triển Portal, Database, Login, RBAC và các module cơ bản. | Hoàn thành | [Tuần 02](weekly-progress/week02.md) |
| 03 | Monitoring & Alerting | Triển khai Prometheus, Grafana, Alertmanager và Remote Access. | Tích hợp Prometheus API, Dashboard và Alertmanager Webhook. | Hoàn thành | [Tuần 03](weekly-progress/week03.md) |
| 04 | Ansible Automation | Triển khai Ansible Control Node, Inventory và Remediation Playbook. | Tích hợp Portal với Ansible và Automation Jobs. | Hoàn thành nội dung chính | [Tuần 04](weekly-progress/week04.md) |
| 05 | Failure Handling | Kiểm thử Execution Failed, Management Channel Down và Verification Failed. | Xây dựng Pre-check, Verification, Retry, Job Detail và Audit Log. | Hoàn thành | [Tuần 05](weekly-progress/week05.md) |
| 06 | Controlled Auto-remediation | Xác định action an toàn và phối hợp kiểm thử Auto-remediation. | Xây dựng Cooldown, Retry Policy, Duplicate Handling và Auto-remediation. | Hoàn thành nội dung chính | [Tuần 06](weekly-progress/week06.md) |
| 07 | Hybrid Cloud Integration | Triển khai Azure VM, Entra ID, Graph Permission và Distribution Group. | Tích hợp Azure Monitoring, SSO, RBAC và Email Notification. | Hoàn thành | [Tuần 07](weekly-progress/week07.md) |
| 08 | Runbook & Manual Remediation | Xây dựng Runbook, Action Matrix, Ansible Vault và kiểm thử Manual Remediation. | Kiểm thử RBAC, Audit Trail, Duplicate Handling và Notification. | Hoàn thành nội dung chính | [Tuần 08](weekly-progress/week08.md) |
| 09 | Approval & Risk Control | Xây dựng Risk Matrix, Approval Policy, MEDIUM/HIGH Playbook và kiểm thử. | Phát triển Approval Workflow, Approval Queue, RBAC, Audit và Notification. | Hoàn thành nội dung chính | [Tuần 09](weekly-progress/week09.md) |
| 10 | Incident Management Workflow | Kiểm thử Incident Lifecycle, Service Recovery, Failure Handling và Recurring Incident. | Phát triển Incident Management, liên kết Alert/Job, Lifecycle, giao diện và Audit. | Đang thực hiện | Cập nhật sau |
| 11 | Theo roadmap | Cập nhật phân công theo kế hoạch. | Cập nhật phân công theo kế hoạch. | Kế hoạch | — |
| 12 | Theo roadmap | Cập nhật phân công theo kế hoạch. | Cập nhật phân công theo kế hoạch. | Kế hoạch | — |
| 13 | Theo roadmap | Cập nhật phân công theo kế hoạch. | Cập nhật phân công theo kế hoạch. | Kế hoạch | — |
| 14 | Theo roadmap | Cập nhật phân công theo kế hoạch. | Cập nhật phân công theo kế hoạch. | Kế hoạch | — |
| 15 | Theo roadmap | Cập nhật phân công theo kế hoạch. | Cập nhật phân công theo kế hoạch. | Kế hoạch | — |

## 4. Công việc chung

| Công việc | Thành viên thực hiện |
|---|---|
| Thống nhất kiến trúc và phạm vi hệ thống | Cả hai |
| Tích hợp Infrastructure và Application | Cả hai |
| Kiểm thử Monitoring và Remediation | Cả hai |
| Kiểm thử các tình huống sự cố thực tế | Cả hai |
| Rà soát kết quả và phản hồi của GVHD | Cả hai |
| Cập nhật GitHub và tài liệu | Cả hai |
| Chuẩn bị báo cáo và bảo vệ đề tài | Cả hai |

## 5. Theo dõi kết quả thực hiện

Kết quả công việc của từng thành viên được cập nhật trong thư mục [Weekly Progress](weekly-progress/).

Các nội dung chưa thực hiện được ghi nhận ở trạng thái kế hoạch hoặc đang thực hiện. Kết quả và minh chứng sẽ được bổ sung theo tiến độ thực tế của từng tuần.
