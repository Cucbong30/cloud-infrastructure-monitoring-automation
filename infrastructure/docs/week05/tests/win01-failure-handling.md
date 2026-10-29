# WIN01 Failure Handling Test

## Target

- Server: WIN01
- IP: `192.168.10.13`
- Service: Windows Exporter `:9182`
- Management Channel: WinRM `:5985`

## 1. WinRM Pre-check

Kiểm tra WinRM từ MON01:

```
nc -zvw 3 192.168.10.13 5985
```

Khi WinRM hoạt động:

```
Connection succeeded
```

## 2. Stop WinRM

Trên WIN01 PowerShell:

```
Stop-Service WinRM
Get-Service WinRM
```

Kiểm tra lại từ MON01:

```
nc -zvw 3 192.168.10.13 5985
```

Kết quả: WinRM port `5985` không còn reachable.

## 3. Restore WinRM

Trên WIN01:

```
Start-Service WinRM
Get-Service WinRM
```

Kiểm tra lại từ MON01:

```
nc -zvw 3 192.168.10.13 5985
```

WinRM port `5985` hoạt động lại bình thường.

## 4. Ansible Execution Failure

Chạy playbook test với Windows service không tồn tại:

```
ansible-playbook ~/ansible/playbooks/restart-windows-exporter-fail-test.yml
```

Service test:

```
windows_exporter_invalid
```

Kết quả:

```
unreachable=0
failed=1
```

Ansible vẫn kết nối được WIN01 qua WinRM nhưng task bị lỗi.

## 5. Windows Exporter Recovery Post-check

Chạy production playbook:

```
ansible-playbook ~/ansible/playbooks/restart-windows-exporter.yml
```

Kiểm tra Windows Exporter:

```
curl http://192.168.10.13:9182/metrics | head
```

Kết quả: endpoint `:9182/metrics` trả về metrics bình thường.

## 6. Verification Failure

Chạy playbook test với verification port sai `9183`:

```
ansible-playbook ~/ansible/playbooks/restart-windows-exporter-verification-fail.yml
```

Kết quả:

```
Start windows_exporter: successful
Wait for port 9183: timeout
unreachable=0
failed=1
```

## Result

Đã kiểm tra được:

- WinRM pre-check PASS/FAIL
- WinRM restore
- Ansible Execution Failed
- Windows Exporter recovery success
- Metrics post-check success
- Verification Failed
