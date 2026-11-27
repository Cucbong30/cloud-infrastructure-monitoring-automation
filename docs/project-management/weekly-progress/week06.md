# TUẦN 06 – Controlled Auto-remediation

## 1. Mục tiêu trong tuần

Mở rộng từ Manual Remediation sang Auto-remediation có kiểm soát. Hệ thống có thể tự xử lý một số lỗi dịch vụ, nhưng vẫn phải kiểm tra kết nối quản trị, giới hạn số lần retry và tránh chạy nhiều job cho cùng một sự cố.

## 2. Phân công công việc

### 2.1. Đỗ Đặng Thái Bảo – Infrastructure / System / Cloud

| STT | Công việc được phân công | Kết quả thực hiện |
|---|---|---|
| 1 | Xác định các remediation action có thể chạy tự động. | Sử dụng ba action: restart Nginx, restart container và restart Windows Exporter. |
| 2 | Duy trì management pre-check và post-check. | Tiếp tục kiểm tra SSH, WinRM và trạng thái dịch vụ trước và sau remediation. |
| 3 | Kiểm thử Auto-remediation thành công. | Kiểm tra khả năng khôi phục dịch vụ trên các target server trong môi trường lab. |
| 4 | Kiểm thử Auto-remediation thất bại. | Phối hợp kiểm tra các trường hợp Execution Failed, Management Blocked và Verification Failed. |
| 5 | Kiểm tra cơ chế Cooldown và Retry. | Phối hợp kiểm thử giới hạn thực thi để tránh remediation chạy liên tục. |
| 6 | Kiểm tra khả năng Manual Remediation. | Operator vẫn có thể thực hiện remediation thủ công khi đủ điều kiện quản trị. |

**Trạng thái: Đã thực hiện các nội dung chính, kết quả kiểm thử được ghi nhận chung với phần Application.**

### 2.2. Nguyễn Thế Gia Bảo – Application / Integration

| STT | Công việc được phân công | Kết quả thực hiện |
|---|---|---|
| 1 | Xây dựng luồng Auto-remediation từ cảnh báo. | Portal tự tạo remediation job đối với các action nằm trong allow-list. |
| 2 | Bổ sung cơ chế Cooldown. | Áp dụng thời gian chờ 120 giây sau khi remediation thành công, tránh chạy lại liên tục. |
| 3 | Giới hạn số lần Retry. | Cho phép retry tối đa một lần khi Execution Failed. Nếu vẫn thất bại, chuyển sang MANUAL_REQUIRED. |
| 4 | Xây dựng cơ chế chống Duplicate Job. | Không tạo thêm job khi cùng target và action đang ở trạng thái Queued hoặc Running. |
| 5 | Quản lý retry theo từng Incident. | Số lần retry được quản lý riêng cho từng sự cố và reset khi phát sinh incident mới. |
| 6 | Xử lý Management Blocked và Verification Failed. | Không chạy playbook khi mất kết nối quản trị. Verification Failed không tự retry mà chuyển sang xử lý thủ công. |
| 7 | Duy trì Manual Remediation. | Admin và Operator vẫn có thể chủ động chạy remediation khi cần. |
| 8 | Kiểm thử và ghi nhận kết quả. | Kiểm tra Auto-remediation, Cooldown, Retry, Duplicate Job và các trạng thái xử lý sự cố. |

**Trạng thái: Hoàn thành.**

## 3. Công việc phối hợp giữa hai thành viên

| Công việc | Infrastructure | Application |
|---|---|---|
| Auto-remediation | Tạo lỗi dịch vụ và kiểm tra khả năng khôi phục. | Tự động tạo job và gọi Ansible theo policy. |
| Cooldown và Retry | Tạo các tình huống lỗi lặp lại. | Kiểm soát thời gian chờ và số lần thực thi. |
| Failure Handling | Tạo lỗi playbook, mất kết nối quản trị và verification failure. | Xử lý các trạng thái Blocked, Failed và Manual Required. |
| Manual Remediation | Kiểm tra điều kiện kết nối và trạng thái dịch vụ. | Duy trì chức năng chạy remediation thủ công. |

## 4. Kết quả cuối tuần

Hệ thống đã hỗ trợ Auto-remediation có kiểm soát trên môi trường lab. Các cơ chế Pre-check, Verification, Cooldown, Retry và chống Duplicate Job được áp dụng để hạn chế việc automation chạy sai hoặc chạy lặp.

Manual Remediation vẫn được giữ lại để người vận hành can thiệp khi hệ thống không thể tự xử lý.

Tuần 7 sẽ mở rộng sang môi trường Hybrid Cloud trên Microsoft Azure, tích hợp SSO và Email Notification.
