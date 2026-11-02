# Week 6 - Auto-remediation Rules

## Mục tiêu

Tài liệu này định nghĩa các rule điều khiển controlled auto-remediation trong Week 6.

Mục tiêu là chỉ tự động xử lý các sự cố có mức rủi ro thấp, đã được kiểm thử và có phương pháp verification rõ ràng.

## Supported Auto-remediation Actions

| Target | Failure Condition | Management Requirement | Action | Verification | Risk |
|---|---|---|---|---|---|
| WEB01 | Nginx :80 DOWN | SSH :22 UP | restart_nginx | HTTP :80 | LOW |
| APP01 | App :8080 DOWN | SSH :22 UP | restart_container | HTTP :8080 | LOW |
| WIN01 | Windows Exporter :9182 DOWN | WinRM :5985 UP | restart_windows_exporter | /metrics :9182 | LOW |

## Auto-remediation Rule

Auto-remediation chỉ được thực hiện khi tất cả điều kiện sau đều đúng:

- Failure condition được xác nhận.
- Management channel đang hoạt động.
- Action nằm trong allow-list.
- Action có risk level LOW.
- Target không ở Maintenance Mode.
- Cooldown đã hết.
- Không có cùng target/action đang Queued hoặc Running.
- Retry limit chưa bị vượt.

```
Failure Confirmed
+ Management UP
+ Allow-listed
+ Risk LOW
+ Maintenance OFF
+ Cooldown OK
+ No Duplicate
+ Retry Available
→ AUTO
```

## Blocked Rule

Remediation bị Blocked khi không thể sử dụng management channel.

```
Failure Confirmed
+
Management Channel DOWN
→ BLOCKED
```

Ví dụ:

- WEB01 Nginx DOWN + SSH DOWN.
- APP01 container DOWN + SSH DOWN.
- WIN01 Windows Exporter DOWN + WinRM DOWN.

Trong trường hợp này không được gọi Ansible playbook.

## Diagnostic Rule

Diagnostic được sử dụng để thu thập thêm thông tin nhưng không thay đổi trạng thái hệ thống.

Các diagnostic action có thể bao gồm:

- Service status.
- Port status.
- Nginx configuration validation.
- Docker container status.
- CPU usage.
- Memory usage.
- Disk usage.
- SSH / WinRM availability.

```
Alert
→ Collect Diagnostic Information
→ No State Change
```

## Manual Intervention Rule

Manual intervention được yêu cầu trong các trường hợp:

- Server hoặc VM unreachable.
- Action có mức risk MEDIUM hoặc HIGH.
- Action không nằm trong allow-list.
- Execution fail sau retry limit.
- Verification fail.
- Disk cleanup hoặc delete file.
- Restart network.
- Firewall change.
- Reboot hoặc shutdown server.
- Start/stop VM.

## Execution Failure Rule

Nếu lần chạy đầu tiên bị execution failure:

```
Attempt 1
→ Execution Failed
→ Retry 1 time
```

Nếu lần retry vẫn thất bại:

```
Retry Failed
→ STOP AUTO
→ Manual Intervention Required
```

## Verification Failure Rule

Sau khi execution hoàn tất, hệ thống phải thực hiện post-check.

Nếu command chạy thành công nhưng verification không pass:

```
Execution Success
+
Verification Failed
→ STOP AUTO
→ Manual Intervention Required
```

Verification Failed không được auto retry.

## Cooldown Rule

Giá trị cooldown ban đầu:

```
5 minutes
```

Trong thời gian cooldown:

```
Same Target
+
Same Action
+
Cooldown Active
→ SKIP
```

Mục tiêu là tránh remediation loop.

## Duplicate Prevention Rule

Không tạo thêm job nếu đã có cùng target/action ở trạng thái:

- Queued.
- Running.

```
Same Target
+
Same Action
+
Queued / Running
→ SKIP DUPLICATE
```

## Maintenance Rule

Khi:

```
Maintenance Mode = ON
```

thì auto-remediation bị tắt.

Monitoring và diagnostic vẫn có thể tiếp tục hoạt động.

```
Alert
+
Maintenance ON
→ SKIP AUTO
```

## Resource Threshold Rules

### Disk

```
Disk > 80%
→ Warning
→ Diagnostic
```

```
Disk > 90%
→ Critical
→ Diagnostic
→ Manual Intervention
```

Không auto cleanup hoặc delete file.

### CPU

```
CPU > 85% for 5 minutes
→ Warning
→ Diagnostic
```

Không auto kill process hoặc restart server.

### Memory

```
Memory > 90% for 5 minutes
→ Warning
→ Diagnostic
```

Không auto kill process hoặc restart server.

## Final Decision

| Condition | Decision |
|---|---|
| Safe service failure + management UP | AUTO |
| Service failure + management DOWN | BLOCKED |
| Management DOWN but service still UP | DEGRADED |
| Diagnostic threshold alert | DIAGNOSTIC |
| Execution failed first attempt | RETRY |
| Retry failed | MANUAL |
| Verification failed | MANUAL |
| Cooldown active | SKIP |
| Duplicate job | SKIP |
| Maintenance Mode | SKIP |
| High-risk action | MANUAL |
| Server unreachable | MANUAL |
