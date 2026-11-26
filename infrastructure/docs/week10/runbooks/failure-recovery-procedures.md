# Week 10 – Failure and Recovery Procedures

## 1. Mục đích

Cung cấp các thao tác kỹ thuật để tạo sự cố,
kiểm tra và khôi phục dịch vụ trên target thật
trong quá trình Incident Management Integration Testing.

Tài liệu này là hướng dẫn thực hiện, không phải
báo cáo kết quả kiểm thử.

## 2. Failure and Recovery Mapping

| Target | Service | Failure | Recovery |
|---|---|---|---|
| WEB01 | Nginx | Stop service | Start service |
| APP01 | app01-web | Stop container | Start container |
| WIN01 | Windows Exporter | Stop service | Start service |
| AZURE01 | Nginx | Stop service | Start service |

## 3. WEB01 – Nginx

Thực hiện trên WEB01.

### Pre-check

```bash
systemctl is-active nginx
```

### Failure

```bash
sudo systemctl stop nginx
systemctl is-active nginx
```

### Manual Recovery

```bash
sudo systemctl start nginx
systemctl is-active nginx
```

### Verification from MON01

```bash
curl -sS --max-time 5 -o /dev/null \
    -w "HTTP %{http_code}\n" \
    http://192.168.10.11:80
```

Expected Recovery: HTTP 200.

## 4. APP01 – Application Container

Thực hiện trên APP01.

### Pre-check

```bash
sudo docker ps -a --filter "name=app01-web"
```

### Failure

```bash
sudo docker stop app01-web
```

### Manual Recovery

```bash
sudo docker start app01-web
sudo docker ps --filter "name=app01-web"
```

### Verification from MON01

```bash
curl -sS --max-time 5 -o /dev/null \
    -w "HTTP %{http_code}\n" \
    http://192.168.10.12:8080
```

Expected Recovery: HTTP 200.

## 5. WIN01 – Windows Exporter

Thực hiện bằng PowerShell Administrator trên WIN01.

### Pre-check

```powershell
Get-Service *exporter*
```

Xác nhận tên service trước khi sử dụng
các lệnh bên dưới.

### Failure

```powershell
Stop-Service -Name windows_exporter
Get-Service -Name windows_exporter
```

### Manual Recovery

```powershell
Start-Service -Name windows_exporter
Get-Service -Name windows_exporter
```

### Verification from MON01

```bash
curl -sS --max-time 5 -o /dev/null \
    -w "HTTP %{http_code}\n" \
    http://192.168.10.13:9182/metrics
```

Expected Recovery:

- Windows Exporter Running.
- HTTP 200.
- Prometheus Target UP.

## 6. AZURE01 – Nginx

Thực hiện trên AZURE01.

### Pre-check

```bash
systemctl is-active nginx
```

### Failure

```bash
sudo systemctl stop nginx
```

### Manual Recovery

```bash
sudo systemctl start nginx
systemctl is-active nginx
```

### Verification from MON01

```bash
curl -sS --max-time 5 -o /dev/null \
    -w "HTTP %{http_code}\n" \
    http://20.243.24.91:80
```

Expected Recovery: HTTP 200.

Public IP cần được kiểm tra trước khi thực hiện.

## 7. Advanced Failure Scenarios

| Scenario | Required Condition | Status |
|---|---|---|
| Execution Failed | Management available, Ansible execution fails | Pending Validation |
| Verification Failed | Execution succeeds, service verification fails | Pending Validation |
| Management Blocked | Management channel unavailable | Pending Validation |
| Recurring Incident | Service fails again after recovery | Pending Validation |

Phương án tạo lỗi cụ thể phải được xác nhận
trên môi trường thực tế trước khi kiểm thử.

Không thay đổi Production Playbook, Credential
hoặc chính sách kiểm soát chỉ để tạo kết quả test.

## 8. Recovery Checklist

Sau mỗi Test Case:

- Xác nhận dịch vụ hoạt động bình thường.
- Xác nhận HTTP endpoint trả về HTTP 200.
- Xác nhận Prometheus Targets trở lại 6/6 UP.
- Xác nhận SSH và WinRM khả dụng.
- Xác nhận Ansible Connectivity.
- Gỡ bỏ các điều kiện tạo lỗi tạm thời.

Manual Recovery chỉ được thực hiện khi cần thiết,
không thực hiện trước khi thu thập đủ kết quả
của remediation job đang kiểm thử.

Nếu phải khôi phục thủ công, cần ghi nhận rõ
để không nhầm với kết quả Auto Remediation.

## 9. Evidence and Responsibility

Infrastructure:

- Tạo sự cố trên target thật.
- Xác minh trạng thái trước và sau remediation.
- Hỗ trợ phân tích Ansible Execution.
- Khôi phục môi trường kiểm thử.

Application:

- Thu thập Incident Lifecycle Evidence.
- Ghi nhận Incident ID, Job ID và Approval ID nếu có.
- Đối chiếu Database và Audit Trail.
- Thu thập Screenshot Integration.

Hai bên thống nhất kết quả thực tế trước khi
hoàn thành báo cáo Tuần 10.

## 10. Status

- Basic Failure and Recovery Commands: Prepared.
- Advanced Failure Scenarios: Pending Validation.
- Integration Testing: Pending.
- Test Results: Not Executed.

Tài liệu sẽ được cập nhật khi các thao tác
được kiểm chứng trên môi trường thực tế.
