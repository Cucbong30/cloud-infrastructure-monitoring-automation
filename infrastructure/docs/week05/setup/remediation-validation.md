# Remediation Validation Setup - Week 5

## Mục tiêu

Week 5 bổ sung kiểm tra trước và sau remediation.

Mục tiêu là tránh hai trường hợp:

- Chạy playbook khi management channel đã down.
- Playbook chạy xong nhưng service thực tế vẫn chưa recovery.

Workflow mới:

```
Pre-check
→ Execute
→ Post-check
→ Success / Failed / Blocked
```

## 1. Pre-check management channel

### WEB01

Management channel:

```
SSH :22
```

Kiểm tra từ MON01:

```
nc -zvw 3 192.168.10.11 22
```

Nếu thành công:

```
Connection to 192.168.10.11 22 port [tcp/ssh] succeeded!
```

Remediation có thể tiếp tục.

Nếu SSH down:

```
Connection refused
```

hoặc timeout.

Khi đó remediation phải bị block trước khi gọi Ansible.

---

### APP01

Management channel:

```
SSH :22
```

Kiểm tra từ MON01:

```
nc -zvw 3 192.168.10.12 22
```

Nếu port 22 UP thì remediation được phép chạy.

Nếu port 22 DOWN thì action `restart_container` không được gọi.

Trong quá trình test đã có trường hợp APP01 vẫn Healthy vì:

```
Node Exporter :9100 UP
App :8080 UP
```

nhưng SSH :22 DOWN.

Trường hợp này target vẫn sống nhưng MON01 không còn đường quản trị.

---

### WIN01

Management channel:

```
WinRM :5985
```

Kiểm tra từ MON01:

```
nc -zvw 3 192.168.10.13 5985
```

Nếu WinRM UP thì remediation được phép chạy.

Nếu WinRM DOWN thì action `restart_windows_exporter` phải bị block.

WIN01 vẫn có thể còn Windows Exporter :9182 hoạt động dù WinRM đã down.

## 2. Tạo management channel failure

### WEB01

Trên WEB01:

```
sudo systemctl stop ssh
sudo systemctl stop ssh.socket
```

Lúc đầu chỉ dừng `ssh.service` nhưng phát hiện `ssh.socket` vẫn active.

Khi đó SSH vẫn có thể được kích hoạt lại bằng socket activation.

Vì vậy để test management channel down thật sự phải dừng cả:

```
ssh.service
ssh.socket
```

Khôi phục:

```
sudo systemctl start ssh.socket
sudo systemctl start ssh
```

---

### APP01

Trên APP01:

```
sudo systemctl stop ssh
sudo systemctl stop ssh.socket
```

Khôi phục:

```
sudo systemctl start ssh.socket
sudo systemctl start ssh
```

---

### WIN01

Trên WIN01 PowerShell:

```
Stop-Service WinRM
```

Khôi phục:

```
Start-Service WinRM
```

Kiểm tra:

```
Get-Service WinRM
```

## 3. Execution failure

Execution failure là trường hợp management channel vẫn hoạt động nhưng task bên trong playbook bị lỗi.

### WEB01

Một test playbook được tạo để kiểm tra execution failure.

Trong quá trình test gặp lỗi:

```
sudo: a password is required
```

Ansible vẫn kết nối được target nhưng task không thực thi được.

Kết quả:

```
unreachable=0
failed=1
```

### APP01

Test sử dụng Docker command không thực thi thành công.

Output có lỗi từ Docker API và Ansible trả:

```
rc=1
unreachable=0
failed=1
```

Trường hợp này khác với target unreachable vì SSH vẫn hoạt động.

### WIN01

Test sử dụng một Windows service không tồn tại:

```
windows_exporter_invalid
```

WinRM vẫn hoạt động nhưng task `win_service` thất bại.

Kết quả được phân loại là execution failure.

## 4. Post-check sau remediation

### WEB01

Sau khi chạy `restart-nginx.yml`:

```
curl -I http://192.168.10.11
```

Kết quả mong đợi:

```
HTTP/1.1 200 OK
```

Điều kiện Success:

```
Ansible execution successful
+
port 80 UP
+
HTTP 200
```

---

### APP01

Sau khi chạy `restart-app-container.yml`:

```
curl -I http://192.168.10.12:8080
```

Kết quả mong đợi:

```
HTTP/1.1 200 OK
```

Có thể kiểm tra thêm trên APP01:

```
sudo docker ps
```

Container:

```
app01-web
```

phải ở trạng thái Up.

---

### WIN01

Sau khi chạy `restart-windows-exporter.yml`:

```
curl http://192.168.10.13:9182/metrics | head
```

Kết quả phải trả lại metrics của Windows Exporter.

Điều kiện Success:

```
Playbook successful
+
port 9182 UP
+
/metrics trả dữ liệu
```

## 5. Verification failure

Verification failure được test bằng cách giữ recovery task đúng nhưng cố tình kiểm tra sai port.

### WEB01

Recovery vẫn restart Nginx bình thường nhưng verification sử dụng:

```
port 81
```

Kết quả:

```
Restart nginx → changed
Wait for 192.168.10.11:81 → timeout
unreachable=0
failed=1
```

### APP01

Container vẫn được start nhưng verification sử dụng:

```
port 8081
```

Kết quả:

```
Start app01-web → changed
Wait for 192.168.10.12:8081 → timeout
unreachable=0
failed=1
```

### WIN01

Windows Exporter vẫn được start nhưng verification sử dụng:

```
port 9183
```

Kết quả:

```
Start windows_exporter → successful
Wait for 192.168.10.13:9183 → timeout
unreachable=0
failed=1
```

Các port sai chỉ được sử dụng trong playbook test riêng.

Playbook production vẫn giữ đúng các port:

```
WEB01 :80
APP01 :8080
WIN01 :9182
```

## 6. Portal integration

Sau khi Application bổ sung management-channel pre-check, các test được chạy lại trên Portal.

### WEB01

```
Nginx :80 UP
Node Exporter :9100 UP
SSH :22 DOWN
```

Portal vẫn xác định WEB01 còn hoạt động nhưng ghi:

```
remediation.blocked
```

Playbook không được chạy.

### APP01

```
App :8080 UP
Node Exporter :9100 UP
SSH :22 DOWN
```

Trước khi có pre-check:

```
restart_container
→ Ansible
→ UNREACHABLE
→ No route to host
```

Sau khi có pre-check:

```
SSH down
→ remediation blocked
→ playbook not started
```

### WIN01

```
Windows Exporter :9182 UP
WinRM :5985 DOWN
```

Portal hiển thị WIN01 Degraded và block remediation vì management channel không khả dụng.

## Kết luận

Week 5 bổ sung hai lớp kiểm tra quanh automation:

```
Pre-check
→ kiểm tra target có thể quản lý được không

Post-check
→ kiểm tra service có thực sự recovery không
```

Nhờ đó hệ thống không còn phụ thuộc hoàn toàn vào việc playbook có chạy hay không.

Một remediation chỉ được xem là thành công khi:

```
Management channel available
+
Execution successful
+
Service verification successful
```
