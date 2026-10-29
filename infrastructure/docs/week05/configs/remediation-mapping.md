# Remediation Mapping - Week 5

## Mục tiêu

Week 5 giữ nguyên ba remediation action đã chạy được từ Week 4, nhưng bổ sung điều kiện kiểm tra trước khi cho phép execution.

Mỗi action chỉ được chạy đúng target đã định nghĩa sẵn.

## Mapping hiện tại

| Server | IP | Service | Management Channel | Remediation Action | Playbook |
|---|---|---|---|---|---|
| WEB01 | 192.168.10.11 | Nginx :80 | SSH :22 | `restart_nginx` | `restart-nginx.yml` |
| APP01 | 192.168.10.12 | app01-web :8080 | SSH :22 | `restart_container` | `restart-app-container.yml` |
| WIN01 | 192.168.10.13 | windows_exporter :9182 | WinRM :5985 | `restart_windows_exporter` | `restart-windows-exporter.yml` |

## Rule trước khi chạy remediation

### WEB01

```
Target: WEB01
Service: Nginx :80
Management: SSH :22
Action: restart_nginx
```

Nếu SSH port 22 UP:

```
Remediation allowed
→ run restart-nginx.yml
```

Nếu SSH port 22 DOWN:

```
Remediation blocked
→ do not start playbook
```

WEB01 vẫn có thể Healthy nếu Node Exporter và Nginx còn UP. SSH down chỉ có nghĩa là management channel hiện không khả dụng.

## APP01

```
Target: APP01
Service: app01-web :8080
Management: SSH :22
Action: restart_container
```

Nếu SSH port 22 UP:

```
Remediation allowed
→ run restart-app-container.yml
```

Nếu SSH port 22 DOWN:

```
Remediation blocked
→ do not start playbook
```

Trong Week 5 đã test trường hợp APP01 vẫn Healthy, App :8080 vẫn UP nhưng SSH :22 DOWN.

Trước khi có pre-check, Portal vẫn tạo job và Ansible trả về:

```
UNREACHABLE
No route to host
```

Sau khi bổ sung pre-check, remediation được block trước execution.

## WIN01

```
Target: WIN01
Service: windows_exporter :9182
Management: WinRM :5985
Action: restart_windows_exporter
```

Nếu WinRM port 5985 UP:

```
Remediation allowed
→ run restart-windows-exporter.yml
```

Nếu WinRM port 5985 DOWN:

```
Remediation blocked
→ do not start playbook
```

WIN01 vẫn có thể còn Windows Exporter :9182 UP trong khi WinRM down.

Trong trường hợp đó server chưa chết hoàn toàn nhưng Ansible không còn management channel để thực hiện remediation.

## Rule sau khi chạy remediation

Playbook chạy thành công chưa được xem là recovery thành công ngay.

Sau execution phải có post-check.

### WEB01

```
restart_nginx
→ verify port 80
→ verify HTTP 200
```

### APP01

```
restart_container
→ verify port 8080
→ verify HTTP 200
```

### WIN01

```
restart_windows_exporter
→ verify port 9182
→ verify /metrics endpoint
```

## Phân loại kết quả

### Success

```
Management channel UP
+
Playbook execution successful
+
Post-check successful
```

### Blocked

```
Management channel DOWN
→ playbook not started
```

### Execution Failed

```
Management channel UP
+
Ansible reached target
+
Task failed
```

Ví dụ:

```
unreachable=0
failed=1
```

### Verification Failed

```
Recovery task executed
+
Post-check failed
```

Ví dụ:

```
restart service → changed
verification port → timeout
```

## Nguyên tắc

Không cho phép user gửi trực tiếp:

```
command
shell command
playbook path
service name
container name
```

Remediation chỉ sử dụng các action đã map sẵn:

```text
restart_nginx
restart_container
restart_windows_exporter
```

Điều này giữ workflow giống Week 4 nhưng bổ sung thêm pre-check và post-check để tránh chạy sai target hoặc báo Success không đúng.
