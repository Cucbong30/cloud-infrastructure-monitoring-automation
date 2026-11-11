# Runbook 03 - Management Blocked

## 1. Mục tiêu

Hướng dẫn xử lý khi service gặp sự cố nhưng hệ thống không thể kết nối management channel để thực hiện remediation.

## 2. Detection

Service đang down và management pre-check thất bại.

Ví dụ:

```text
Linux   → SSH unavailable
Windows → WinRM unavailable
```

## 3. System Response

Hệ thống phải dừng trước bước execution.

```text
Management Pre-check Failed
→ BLOCKED
→ No Playbook Execution
→ MANUAL_REQUIRED
```

Không retry remediation vì management channel chưa hoạt động.

## 4. Expected Result

```text
Execution: NOT STARTED
Management: BLOCKED
Final Status: MANUAL_REQUIRED
```

## 5. Operator Action

### Linux / Azure

Nếu SSH không hoạt động:

1. Kiểm tra VM/server có đang running hay không.
2. Kiểm tra network và firewall/NSG.
3. Sử dụng console hoặc Azure management tool nếu không thể SSH.
4. Kiểm tra:

```text
systemctl status ssh
```

5. Khởi động lại SSH nếu cần:

```text
sudo systemctl start ssh
```

### Windows

Kiểm tra WinRM:

```text
Get-Service WinRM
```

Khởi động lại nếu cần:

```text
Start-Service WinRM
```

## 6. Recovery

Sau khi management channel hoạt động trở lại:

```text
SSH / WinRM Available
→ Re-check Target
→ Run remediation if service still down
```

## 7. Closure

Incident chỉ được đóng khi:

```text
Management Channel Healthy
Service Healthy
Verification Passed
Audit Updated
```
