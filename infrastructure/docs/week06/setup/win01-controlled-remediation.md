# WIN01 - Controlled Remediation Setup

## Target

- Server: WIN01
- IP: 192.168.10.13
- Service: Windows Exporter
- Exporter Port: 9182
- Management Channel: WinRM :5985
- Production Playbook: `/home/bong/ansible/playbooks/restart-windows-exporter.yml`

## Case 1 - Auto-remediation thành công

Điều kiện:

```
Windows Exporter DOWN
WinRM UP
```

Tạo lỗi trên WIN01:

```
Stop-Service windows_exporter
```

Kiểm tra từ MON01:

```
ansible WIN01 -m win_ping
curl http://192.168.10.13:9182/metrics
```

Production playbook start lại Windows Exporter và verify port 9182.

Kết quả:

```
Windows Exporter started
/metrics :9182 available
SUCCESS
```

## Case 2 - Execution Failed

Service path được thay đổi tạm sang executable không tồn tại:

```
"C:\Program Files\windows_exporter\windows_exporter-invalid.exe"
```

Sau khi Windows Exporter bị stop, production remediation không thể start service.

Kết quả:

```
Execution Failed
→ Retry 1 lần
→ Retry Failed
→ MANUAL_REQUIRED
```

Sau khi kiểm thử, service path được restore về:

```
"C:\Program Files\windows_exporter\windows_exporter.exe"
```

## Case 3 - Management Channel Blocked

Điều kiện:

```
Windows Exporter DOWN
WinRM DOWN
```

Tạo trạng thái:

```
Stop-Service windows_exporter
Stop-Service WinRM
```

Kiểm tra từ MON01:

```
ansible WIN01 -m win_ping
curl http://192.168.10.13:9182/metrics
```

Kết quả:

```
Exporter unavailable
WinRM unavailable
BLOCKED
MANUAL_REQUIRED
```

Khi WinRM không hoạt động, remediation không được phép chạy.

## Case 4 - Verification Failed

Windows Exporter được cấu hình tạm thời listen trên port 9183:

```
--web.listen-address=:9183
```

Production playbook vẫn start service thành công nhưng verification trên port 9182 bị fail.

Kết quả:

```
Execution SUCCESS
Verification FAILED
MANUAL_REQUIRED
```

Sau khi kiểm thử, service được restore về port mặc định 9182.

## Kết quả

WIN01 đã kiểm thử các trạng thái:

- SUCCESS
- EXECUTION FAILED
- BLOCKED
- VERIFICATION FAILED
- MANUAL REQUIRED

Các case sử dụng production playbook và thay đổi trạng thái thật trên WIN01 để kiểm tra luồng remediation.
