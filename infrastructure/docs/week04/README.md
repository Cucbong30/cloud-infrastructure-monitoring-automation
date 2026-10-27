# Week 4 - Infrastructure Automation

## Mục tiêu

Tuần 4 phần Infrastructure bắt đầu chuyển từ monitoring sang automation. Ansible được triển khai trên MON01 để điều khiển các máy Linux và Windows trong Lab, sau đó kết nối với Web Portal để thực hiện remediation khi service gặp lỗi.

Luồng chính được kiểm tra trong tuần:

Monitoring → Portal → Automation → Ansible → Recovery

## Hệ thống sử dụng

| Server | IP | Vai trò | Kết nối Automation |
|---|---|---|---|
| MGMT01 | 192.168.10.5 | Management / Tailscale Gateway | - |
| MON01 | 192.168.10.10 | Monitoring / Ansible Controller | Controller |
| WEB01 | 192.168.10.11 | Linux Web Server | SSH |
| APP01 | 192.168.10.12 | Linux Application Server | SSH |
| WIN01 | 192.168.10.13 | Windows Server | WinRM |

## Công việc đã thực hiện

Trong tuần đã triển khai Ansible trên MON01 và kiểm tra kết nối tới các server trong Lab.

Đối với WEB01 và APP01, MON01 sử dụng SSH key để kết nối.

Đối với WIN01, Ansible sử dụng WinRM trên port 5985 với NTLM authentication.

Sau khi kiểm tra kết nối thành công, ba automation scenario được xây dựng:

- Restart Nginx trên WEB01.
- Start lại container `app01-web` trên APP01.
- Start lại service `windows_exporter` trên WIN01.

Web Portal cũng được cấu hình để kết nối tới MON01 qua SSH và gọi các playbook đã được định nghĩa sẵn.

## Remediation Scenario

### WEB01 - Nginx Recovery

Nginx trên WEB01 được dừng để mô phỏng lỗi service.

Khi Nginx down:

- WEB01 vẫn còn hoạt động.
- Node Exporter vẫn UP.
- Port 80 DOWN.
- Portal hiển thị WEB01 ở trạng thái DEGRADED.

Từ Portal chạy automation `restart_nginx`.

MON01 nhận request và thực thi Ansible playbook trên WEB01.

Sau khi chạy:

- Nginx hoạt động lại.
- Port 80 UP.
- HTTP trả về status 200.
- WEB01 quay lại HEALTHY.

### APP01 - Docker Container Recovery

Container `app01-web` trên APP01 được stop để mô phỏng application failure.

Khi container down:

- APP01 vẫn còn hoạt động.
- Node Exporter vẫn UP.
- Port 8080 DOWN.
- Portal hiển thị APP01 ở trạng thái DEGRADED.

Từ Portal chạy automation restart container.

MON01 thực thi playbook để start lại `app01-web`.

Sau khi recovery:

- Container chạy lại.
- Port 8080 UP.
- HTTP trả về status 200.
- APP01 quay lại HEALTHY.

### WIN01 - Windows Exporter Recovery

Service `windows_exporter` trên WIN01 được stop để kiểm tra automation cho Windows Server.

WinRM vẫn được giữ hoạt động để MON01 còn management channel tới WIN01.

Từ Portal chạy automation restart Windows Exporter.

MON01 sử dụng Ansible qua WinRM để start lại service.

Sau khi recovery:

- `windows_exporter` chuyển về Running.
- Port 9182 UP.
- Endpoint `/metrics` trả dữ liệu.
- WIN01 quay lại HEALTHY.

## Kết quả

Ba remediation scenario đã chạy thành công:

1. Linux service recovery.
2. Docker container recovery.
3. Windows service recovery.

Luồng Portal → MON01 → Ansible → Target Server đã hoạt động với Lab thật.

## Giới hạn hiện tại

Automation hiện tại phụ thuộc vào management channel của target server.

Ví dụ:

- Nginx down nhưng SSH còn hoạt động → có thể recovery.
- Container down nhưng SSH còn hoạt động → có thể recovery.
- Windows Exporter down nhưng WinRM còn hoạt động → có thể recovery.
- SSH hoặc WinRM down → không thể recovery bằng chính connection đó.
- VM down hoàn toàn → cần recovery từ hypervisor hoặc cloud layer.
- MON01 down → Ansible Controller không thể thực hiện automation.

Các trường hợp này sẽ được xem xét ở các tuần tiếp theo khi mở rộng phần resilience và cloud recovery.
