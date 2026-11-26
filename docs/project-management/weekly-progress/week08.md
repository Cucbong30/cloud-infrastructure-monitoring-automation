# TUẦN 08 – Runbook & Manual Remediation

## 1. Mục tiêu trong tuần

Chuẩn hóa quy trình xử lý sự cố thông qua Runbook, kiểm thử Manual Remediation trên cả Local và Cloud. Đồng thời kiểm tra lại RBAC, Audit Trail, Duplicate Job và Email Notification theo góp ý của GVHD.

## 2. Phân công công việc

### 2.1. Đỗ Đăng Thái Bảo – Infrastructure / System / Cloud

| STT | Công việc được phân công | Kết quả thực hiện |
|---|---|---|
| 1 | Xây dựng Runbook vận hành. | Hoàn thành 5 Runbook tương ứng với Success, Execution Failed, Management Blocked, Verification Failed và Manual Required. |
| 2 | Kiểm thử Manual Remediation trên Local Lab. | Khôi phục thành công Nginx trên WEB01, Docker Container trên APP01 và Windows Exporter trên WIN01. |
| 3 | Kiểm thử Manual Remediation trên AZURE01. | Restart Nginx thành công và xác nhận dịch vụ hoạt động trên HTTP port 80. |
| 4 | Kiểm thử các trường hợp remediation thất bại. | Tạo lỗi thực tế trên AZURE01 để kiểm tra Execution Failed, Verification Failed và Management Blocked. |
| 5 | Xây dựng Manual Remediation Action Matrix. | Xác định target, action, điều kiện thực thi, verification và mức rủi ro LOW cho các action hiện tại. |
| 6 | Bảo mật thông tin quản trị Ansible. | Chuyển credential WinRM của WIN01 sang Ansible Vault và kiểm tra lại kết nối thành công. |
| 7 | Kiểm thử tích hợp với Application. | Phối hợp kiểm tra RBAC, Audit Trail, Duplicate Job và Email Notification. |
| 8 | Cập nhật tài liệu triển khai. | Hoàn thành tài liệu Runbook, Action Matrix, Ansible Vault và kết quả kiểm thử. |

**Trạng thái: Hoàn thành.**

### 2.2. Nguyễn Thế Gia Bảo – Application / Integration

| STT | Công việc được phân công | Kết quả thực hiện |
|---|---|---|
| 1 | Kiểm soát quyền Manual Remediation. | Admin và Operator được thực thi remediation, Viewer bị chặn trên giao diện và backend. |
| 2 | Hoàn thiện Audit Trail cho Manual Job. | Ghi nhận actor, role, mode, target, action, timestamp, result và final status. |
| 3 | Kiểm tra Audit Trail cho Auto Job. | Các job tự động được ghi nhận với actor SYSTEM và mode AUTO. |
| 4 | Hoàn thiện cơ chế chống Duplicate Job. | Job trùng được ghi nhận DUPLICATE_SKIPPED, trạng thái thực thi NOT_RUN. |
| 5 | Kiểm thử Email Notification. | Gửi thông báo Execution Failed đến nhóm Critical, Retry và Management Blocked đến nhóm Warning. |
| 6 | Chuẩn hóa cách gọi Ansible trên AZURE01. | Portal chỉ gọi playbook, SSH Key của AZURE01 được quản lý trực tiếp trên MON01. |
| 7 | Kiểm soát Retry theo chế độ thực thi. | Manual Job không tự retry. Verification Failed và Management Blocked không sử dụng lượt retry. |
| 8 | Kiểm thử và bổ sung minh chứng. | Kiểm tra các luồng RBAC, Manual/Auto Job, Duplicate Handling và Notification. |

**Trạng thái: Hoàn thành các chức năng chính, còn một số hình ảnh minh chứng cần bổ sung.**

## 3. Công việc phối hợp giữa hai thành viên

| Công việc | Infrastructure | Application |
|---|---|---|
| Manual Remediation | Chuẩn bị playbook và kiểm tra dịch vụ trên bốn target server. | Thực hiện remediation từ Portal và hiển thị kết quả. |
| RBAC | Kiểm tra việc thực thi thực tế trên Infrastructure. | Kiểm soát quyền Admin, Operator và Viewer. |
| Audit Trail | Đối chiếu action và kết quả thực thi. | Ghi nhận người thực hiện, chế độ và trạng thái job. |
| Duplicate Handling | Tạo tình huống remediation trùng lặp. | Chặn job trùng và ghi nhận DUPLICATE_SKIPPED. |
| Email Notification | Tạo các tình huống lỗi thực tế. | Kiểm tra nội dung và nhóm nhận Email theo severity. |

## 4. Kết quả cuối tuần

Hoàn thành bộ Runbook vận hành và kiểm thử Manual Remediation trên WEB01, APP01, WIN01 và AZURE01. Các action vẫn tuân thủ Pre-check và Verification, không bỏ qua cơ chế kiểm soát đã xây dựng ở các tuần trước.

RBAC, Audit Trail, Duplicate Handling và Email Notification đã được kiểm thử. Thông tin quản trị WIN01 được bảo mật bằng Ansible Vault.

Cần bổ sung hình ảnh Job Detail của job 71, job 72, minh chứng backend trả 403 và xác nhận trạng thái cuối của Incident 46.

Tuần 9 sẽ mở rộng sang Approval Workflow và phân loại remediation action theo ba mức rủi ro LOW, MEDIUM và HIGH.
