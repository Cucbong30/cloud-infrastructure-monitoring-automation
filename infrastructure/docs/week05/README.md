# Week 5 - Failure Handling and Validated Remediation

## Mục tiêu

Sau khi Week 4 đã kết nối Portal với Ansible và chạy được ba remediation case trên WEB01, APP01 và WIN01, Week 5 tập trung vào failure handling.

Mục tiêu của tuần này là kiểm tra hệ thống trong các trường hợp automation không chạy đúng như mong đợi, thay vì chỉ test các case thành công.

Luồng chính cần kiểm tra:

```
Failure detected
→ Management pre-check
→ Block hoặc Execute
→ Ansible execution
→ Post-check
→ Success / Failed / Verification Failed
```

Trong tuần này phần Infrastructure tập trung vào ba loại tình huống:

- Management channel bị mất.
- Playbook hoặc task thực thi thất bại.
- Playbook chạy được nhưng bước xác minh sau recovery không đạt.

## 

| Server | IP | Service | Management Channel |
|---|---|---|---|
| WEB01 | 192.168.10.11 | Nginx :80 | SSH :22 |
| APP01 | 192.168.10.12 | app01-web :8080 | SSH :22 |
| WIN01 | 192.168.10.13 | windows_exporter :9182 | WinRM :5985 |

## WEB01

WEB01 sử dụng SSH port 22 làm management channel.

Các case đã test:

- SSH port 22 UP.
- SSH port 22 DOWN.
- SSH được restore lại.
- Playbook execution failed.
- Nginx recovery thành công.
- HTTP port 80 trả về status 200 sau recovery.
- Verification failed khi cố tình kiểm tra sai port 81.
- Portal block remediation khi SSH port 22 DOWN.

Một điểm gặp trong lúc test là `ssh.service` có thể đã inactive nhưng `ssh.socket` vẫn active. Khi đó port 22 vẫn có thể được kích hoạt lại bởi socket activation. Vì vậy để tạo tình huống SSH management channel down thật sự, cả `ssh.service` và `ssh.socket` đều được dừng.

Khi SSH down nhưng Node Exporter và Nginx vẫn UP, WEB01 vẫn còn hoạt động. Tuy nhiên MON01 không thể dùng Ansible để điều khiển WEB01. Portal vì vậy phải block remediation thay vì cố chạy playbook.

## APP01

APP01 cũng sử dụng SSH port 22 làm management channel.

Các case đã test:

- SSH pre-check pass.
- SSH pre-check fail.
- SSH restore.
- Container recovery execution failed.
- Container `app01-web` hoạt động lại.
- HTTP port 8080 trả về status 200 sau recovery.
- Verification failed khi cố tình kiểm tra sai port 8081.
- Portal block remediation khi SSH port 22 DOWN.

Trong execution failure test, Ansible vẫn kết nối được tới APP01 nhưng Docker command trả lỗi. Điều này được phân biệt với trường hợp target unreachable.

Trước khi phần Application có management pre-check, khi SSH APP01 down Portal vẫn tạo job `restart_container`. Ansible sau đó trả về `UNREACHABLE / No route to host`.

Sau khi bổ sung pre-check, Portal phát hiện SSH port 22 down trước khi execution và block remediation. Playbook không còn được gọi trong trường hợp này.

## WIN01

WIN01 sử dụng WinRM port 5985 làm management channel.

Các case đã test:

- WinRM pre-check pass.
- WinRM pre-check fail.
- WinRM restore.
- Windows service execution failed.
- Windows Exporter recovery thành công.
- Endpoint `:9182/metrics` trả dữ liệu sau recovery.
- Verification failed khi cố tình kiểm tra sai port 9183.
- Portal block remediation khi WinRM port 5985 DOWN.

Khi WinRM down nhưng Windows Exporter vẫn UP, WIN01 vẫn còn hoạt động nhưng MON01 không thể quản lý máy bằng Ansible.

Portal hiển thị WIN01 ở trạng thái Degraded và block action `restart_windows_exporter` thay vì chạy playbook rồi mới nhận lỗi.

## Phân loại kết quả

Qua các test trong Week 5, automation được chia thành bốn trường hợp chính.

### Success

Management channel hoạt động, playbook chạy thành công và post-check xác nhận service thực sự hoạt động lại.

### Execution Failed

Ansible kết nối được target nhưng task bên trong playbook bị lỗi.

Ví dụ:

```
unreachable=0
failed=1
```

### Unreachable / Blocked

Management channel SSH hoặc WinRM không hoạt động.

Nếu chưa có pre-check, Ansible có thể trả về `UNREACHABLE`.

Sau khi có pre-check, Portal block remediation trước execution.

### Verification Failed

Task recovery chạy được nhưng post-check không đạt.

Ví dụ:

```
Restart service → changed
Verification port → timeout
unreachable=0
failed=1
```

Playbook execution thành công chưa đủ để kết luận recovery thành công.

## Kết quả Week 5

Sau Week 5, hệ thống không còn chỉ xử lý automation theo kiểu chạy playbook và nhận exit result.

Luồng đã được mở rộng thành:

```
Service Failure
→ Check Management Channel
→ Block hoặc Run Playbook
→ Check Execution Result
→ Verify Service
→ Success / Execution Failed / Blocked / Verification Failed
```

Ba management channel đã được kiểm tra:

```
WEB01 → SSH :22
APP01 → SSH :22
WIN01 → WinRM :5985
```

Ba service recovery được xác minh lại:

```
WEB01 → Nginx :80
APP01 → app01-web :8080
WIN01 → windows_exporter :9182
```

Week 5 tập trung vào failure handling để tránh trường hợp Portal cố chạy remediation khi target không thể được quản lý hoặc báo Success khi service thực tế chưa recovery.
