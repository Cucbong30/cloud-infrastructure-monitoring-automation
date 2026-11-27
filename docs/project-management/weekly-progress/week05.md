# TUẦN 05 – Failure Handling & Verification

## 1. Mục tiêu trong tuần

Theo góp ý của GVHD ở Tuần 4, nhóm tập trung kiểm tra các trường hợp remediation thất bại, mất kết nối quản trị hoặc playbook chạy xong nhưng dịch vụ chưa phục hồi. Bổ sung pre-check và post-check để đánh giá đúng kết quả thực thi.

## 2. Phân công công việc

### 2.1. Đỗ Đặng Thái Bảo – Infrastructure / System / Cloud

| STT | Công việc được phân công | Kết quả thực hiện |
|---|---|---|
| 1 | Kiểm tra các trường hợp Ansible thực thi thất bại. | Phân biệt được Execution Failed và Target Unreachable dựa trên kết quả Ansible. |
| 2 | Kiểm tra management channel trên Linux và Windows. | Kiểm thử SSH port 22 trên WEB01, APP01 và WinRM port 5985 trên WIN01. |
| 3 | Kiểm thử failure handling trên WEB01. | Kiểm tra lỗi execution, SSH down, restart Nginx và xác nhận HTTP 200 OK sau khi khôi phục. |
| 4 | Kiểm thử failure handling trên APP01. | Tạo lỗi Docker task, kiểm tra SSH down và xác nhận container hoạt động trở lại trên port 8080. |
| 5 | Kiểm thử failure handling trên WIN01. | Tạo lỗi Windows service, kiểm tra WinRM down và khôi phục Windows Exporter trên port 9182. |
| 6 | Kiểm thử Verification Failed. | Tạo các trường hợp playbook chạy được nhưng post-check thất bại trên cả ba target server. |
| 7 | Kiểm tra cơ chế chặn remediation. | Xác nhận Portal không gọi playbook khi SSH hoặc WinRM không khả dụng. |
| 8 | Cập nhật tài liệu và kết quả kiểm thử. | Ghi lại remediation mapping, pre-check, execution failure và verification failure. |

**Trạng thái: Hoàn thành.**

### 2.2. Nguyễn Thế Gia Bảo – Application / Integration

| STT | Công việc được phân công | Kết quả thực hiện |
|---|---|---|
| 1 | Ánh xạ cảnh báo với remediation action. | Portal gợi ý đúng action theo server và dịch vụ gặp lỗi. |
| 2 | Xây dựng management pre-check. | Kiểm tra SSH và WinRM từ MON01 trước khi cho phép chạy playbook. |
| 3 | Chặn remediation khi management channel down. | Hiển thị Remediation unavailable, ghi rõ nguyên nhân và không gọi Ansible. |
| 4 | Bổ sung verification sau khi thực thi. | Chỉ ghi nhận Success khi dịch vụ hoạt động trở lại, không chỉ dựa vào exit code của Ansible. |
| 5 | Hoàn thiện Job Detail. | Hiển thị server, action, trigger, thời gian thực thi, exit code, output và kết quả verification. |
| 6 | Liên kết Alert với Automation Job. | Theo dõi được các job phát sinh từ từng cảnh báo. |
| 7 | Bổ sung chức năng Retry. | Khi chạy lại remediation, Portal tạo job mới và giữ nguyên lịch sử job cũ. |
| 8 | Cập nhật Audit Log. | Ghi nhận các sự kiện remediation.blocked, remediation.verified và remediation.failed. |

**Trạng thái: Hoàn thành.**

## 3. Công việc phối hợp giữa hai thành viên

| Công việc | Infrastructure | Application |
|---|---|---|
| Execution Failed | Tạo lỗi bên trong Ansible playbook. | Xử lý và hiển thị kết quả Failed. |
| Management Channel Down | Tắt và khôi phục SSH, WinRM trên target server. | Kiểm tra kết nối, chặn remediation và hiển thị nguyên nhân. |
| Verification Failed | Tạo tình huống post-check thất bại sau khi playbook thực thi. | Ghi nhận Verification Failed thay vì Success. |
| Service Recovery | Khôi phục dịch vụ và kiểm tra endpoint thực tế. | Hiển thị kết quả verification và cập nhật Audit Log. |
| Kiểm thử tích hợp | Kiểm tra trạng thái thực tế trên WEB01, APP01 và WIN01. | Đối chiếu trạng thái máy chủ, dịch vụ và automation job trên Portal. |

## 4. Kết quả cuối tuần

Hệ thống đã phân biệt được lỗi thực thi playbook, lỗi kết nối quản trị và lỗi verification. Remediation chỉ được ghi nhận thành công khi dịch vụ thực sự hoạt động trở lại.

Phần remediation vẫn do Admin hoặc Operator chủ động thực hiện. Tuần 6 sẽ mở rộng sang Controlled Auto-remediation với các cơ chế Retry, Cooldown và chống thực thi trùng lặp.
