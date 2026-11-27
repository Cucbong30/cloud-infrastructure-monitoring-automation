# TUẦN 07 – Hybrid Cloud, SSO & Notification

## 1. Mục tiêu trong tuần

Mở rộng hệ thống từ Local Lab sang Hybrid Cloud bằng Microsoft Azure. Tích hợp máy chủ Cloud vào hệ thống Monitoring và Auto-remediation hiện tại, đồng thời bổ sung đăng nhập SSO, phân quyền qua Microsoft Entra ID và gửi thông báo qua Email.

## 2. Phân công công việc

### 2.1. Đỗ Đặng Thái Bảo – Infrastructure / System / Cloud

| STT | Công việc được phân công | Kết quả thực hiện |
|---|---|---|
| 1 | Triển khai AZURE01 trên Microsoft Azure. | Tạo Ubuntu Server 24.04 tại Japan East, cấu hình Resource Group, Virtual Network, NSG và Public IP. |
| 2 | Thiết lập kết nối quản trị từ MON01 đến AZURE01. | Tạo SSH Key riêng trên MON01, cấu hình Ansible Inventory và kiểm tra kết nối thành công. |
| 3 | Triển khai dịch vụ và Monitoring Exporter trên AZURE01. | Cài đặt Nginx, Node Exporter và giới hạn quyền truy cập metrics thông qua NSG. |
| 4 | Tích hợp AZURE01 vào hệ thống Monitoring. | Prometheus thu thập được metrics từ Azure VM cùng với các máy chủ Local. |
| 5 | Xây dựng playbook remediation cho AZURE01. | Triển khai playbook restart Nginx và kiểm tra HTTP port 80 sau khi thực thi. |
| 6 | Kiểm thử Auto-remediation trên Cloud. | Kiểm tra thành công các trường hợp Success, Execution Failed, Management Blocked và Verification Failed. |
| 7 | Cấu hình Microsoft Entra ID. | Tạo App Registration, Redirect URI, App Roles Admin, Operator, Viewer và tài khoản kiểm thử. |
| 8 | Chuẩn bị Microsoft Graph và Email Notification. | Cấp quyền Mail.Send, thực hiện Admin Consent và tạo Distribution Group theo mức Critical, Warning và Info. |
| 9 | Cập nhật tài liệu triển khai. | Ghi lại cấu hình Azure, SSH, Ansible, Entra ID và kết quả kiểm thử. |

**Trạng thái: Hoàn thành.**

### 2.2. Nguyễn Thế Gia Bảo – Application / Integration

| STT | Công việc được phân công | Kết quả thực hiện |
|---|---|---|
| 1 | Tích hợp Microsoft Entra SSO vào Portal. | Portal hỗ trợ đăng nhập bằng tài khoản Microsoft Entra ID. |
| 2 | Tích hợp RBAC với Entra App Roles. | Phân quyền Admin, Operator và Viewer dựa trên role nhận được từ token đăng nhập. |
| 3 | Bổ sung AZURE01 vào Server Inventory và Dashboard. | Hiển thị thông tin, metrics và trạng thái dịch vụ của Azure VM trên Portal. |
| 4 | Tích hợp Auto-remediation cho AZURE01. | Sử dụng lại policy Tuần 6, bao gồm Pre-check, Cooldown, Retry và Verification. |
| 5 | Tích hợp Microsoft Graph API. | Portal gửi được yêu cầu gửi Email thông qua Graph API, nhận phản hồi HTTP 202. |
| 6 | Xây dựng Email Notification theo severity. | Phân loại thông báo Critical, Warning và Info, gửi đến Distribution Group tương ứng. |
| 7 | Cập nhật nội dung Email và Audit Log. | Email hiển thị thông tin sự cố, action và kết quả xử lý. Audit phân biệt thao tác AUTO, MANUAL và SYSTEM. |
| 8 | Đóng gói Application bằng Docker. | Chuẩn bị môi trường chạy Portal bằng Docker, không đưa file .env chứa thông tin cấu hình nhạy cảm vào image. |

**Trạng thái: Hoàn thành.**

## 3. Công việc phối hợp giữa hai thành viên

| Công việc | Infrastructure | Application |
|---|---|---|
| Hybrid Cloud Integration | Triển khai Azure VM, cấu hình SSH, Ansible và Prometheus. | Tích hợp AZURE01 vào Inventory và Dashboard. |
| Cloud Remediation | Chuẩn bị playbook và tạo các tình huống lỗi trên AZURE01. | Kiểm tra luồng Auto-remediation và kết quả job trên Portal. |
| SSO và RBAC | Cấu hình Entra App Registration và App Roles. | Tích hợp đăng nhập SSO và xử lý phân quyền. |
| Email Notification | Cấu hình Graph API Permission và Distribution Group. | Xây dựng nội dung Email và cơ chế gửi theo severity. |
| Kiểm thử tích hợp | Kiểm tra dịch vụ, kết nối và trạng thái thực tế trên Cloud VM. | Đối chiếu kết quả Monitoring, Remediation, Job và Audit trên Portal. |

## 4. Kết quả cuối tuần

Hệ thống đã được mở rộng sang mô hình Hybrid Cloud, quản lý đồng thời các máy chủ Local và AZURE01. Monitoring và Auto-remediation trên Azure sử dụng cùng cơ chế kiểm soát với các máy chủ Local.

Portal đã tích hợp Microsoft Entra SSO, RBAC và Email Notification thông qua Microsoft Graph.

Tuần 8 sẽ tập trung xây dựng Runbook, kiểm thử Manual Remediation, RBAC, Audit Log và chuẩn hóa quy trình xử lý sự cố.
