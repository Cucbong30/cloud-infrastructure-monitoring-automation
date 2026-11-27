# TUẦN 04 – Service Monitoring & Ansible Automation

## 1. Mục tiêu trong tuần

Tiếp nối phần Monitoring của Tuần 3, nhóm triển khai Ansible và kết nối với Operations Portal. Thay vì chỉ phát hiện và hiển thị cảnh báo, hệ thống bắt đầu hỗ trợ người vận hành thực hiện các remediation action để khôi phục dịch vụ.

## 2. Phân công công việc

### 2.1. Đỗ Đặng Thái Bảo – Infrastructure / System / Cloud

| STT | Công việc được phân công | Kết quả thực hiện |
|---|---|---|
| 1 | Hoàn thiện service-level monitoring. | Tiếp tục giám sát trạng thái các dịch vụ trên WEB01, APP01, WIN01 và MON01. |
| 2 | Hoàn thiện luồng cảnh báo từ Alertmanager đến Portal. | Duy trì luồng cảnh báo đã tích hợp ở Tuần 3 để phục vụ remediation. |
| 3 | Triển khai Ansible Control Node trên MON01. | MON01 được sử dụng để thực thi automation trên các target server. |
| 4 | Xây dựng Ansible Inventory cho Linux và Windows. | Khai báo các target server và phương thức kết nối tương ứng. |
| 5 | Kiểm tra kết nối SSH và WinRM. | Ansible có thể thực hiện các remediation action trên WEB01, APP01 và WIN01. |
| 6 | Xây dựng các remediation playbook cơ bản. | Triển khai các action restart Nginx, restart application container và restart Windows service. |
| 7 | Kiểm thử remediation trên môi trường lab. | Chạy thành công các remediation cơ bản trên ba target server. |

**Trạng thái: Hoàn thành các nội dung chính.**

### 2.2. Nguyễn Thế Gia Bảo – Application / Integration

| STT | Công việc được phân công | Kết quả thực hiện |
|---|---|---|
| 1 | Kết nối Operations Portal với Ansible. | Portal đã có thể gọi Ansible để thực hiện remediation trên máy chủ thật. |
| 2 | Xây dựng cơ chế kiểm soát automation action. | Kết nối Portal với danh sách playbook được phép thực thi trên MON01. |
| 3 | Hoàn thiện Automation Jobs. | Kiểm thử thành công ba job remediation trên WEB01, APP01 và WIN01. |
| 4 | Lưu execution history và hiển thị kết quả automation. | Đã có kết quả kiểm thử ba job thành công; cần đối chiếu thêm chi tiết execution history. |
| 5 | Kết nối cảnh báo với remediation action tương ứng. | Chuẩn bị luồng xử lý từ cảnh báo đến automation action. |
| 6 | Hoàn thiện Audit Log cho automation. | Tiếp tục phát triển chức năng ghi nhận thao tác và kết quả thực thi job. |

**Trạng thái: Hoàn thành các nội dung chính.**

## 3. Công việc phối hợp giữa hai thành viên

| Công việc | Infrastructure | Application |
|---|---|---|
| Tích hợp Ansible | Chuẩn bị Control Node, Inventory và Playbook. | Kết nối Portal với Ansible execution. |
| Remediation WEB01 | Chuẩn bị playbook restart Nginx. | Thực hiện remediation từ Portal. |
| Remediation APP01 | Chuẩn bị playbook restart container. | Thực hiện remediation từ Portal. |
| Remediation WIN01 | Chuẩn bị playbook restart Windows service. | Thực hiện remediation từ Portal. |
| Kiểm thử tích hợp | Kiểm tra kết quả thực thi trên target server. | Kiểm tra job và kết quả hiển thị trên Portal. |

## 4. Kết quả cuối tuần

Portal đã kết nối được với Ansible và thực hiện thành công các remediation cơ bản trên WEB01, APP01 và WIN01.

Hệ thống chuyển từ giai đoạn chỉ giám sát và cảnh báo sang hỗ trợ xử lý sự cố thông qua Manual Remediation.

Tuần 5 sẽ tập trung kiểm tra các trường hợp playbook chạy thất bại, mất kết nối quản trị và dịch vụ chưa phục hồi sau khi thực thi automation.
