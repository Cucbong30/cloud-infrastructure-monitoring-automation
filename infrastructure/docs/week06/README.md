# Week 6 - Controlled Auto-remediation

## Mục tiêu

Week 6 tiếp tục phát triển từ nền tảng remediation của Week 4 và Week 5, nhưng mở rộng từ manual remediation sang controlled auto-remediation.

Mục tiêu chính của tuần này là xây dựng cơ chế tự động xử lý sự cố theo policy thay vì tự động restart mọi service khi có alert.

Hệ thống cần phân biệt:

- Khi nào được phép Auto-remediation.
- Khi nào chỉ chạy Diagnostic.
- Khi nào phải Blocked.
- Khi nào cần Manual intervention.
- Khi nào phải bỏ qua remediation do Maintenance, Cooldown hoặc Duplicate job.

## Scope

Week 6 tập trung vào các thành phần sau:

- Auto-remediation policy.
- Risk classification.
- Management pre-check.
- Diagnostic actions.
- Maintenance Mode.
- Cooldown.
- Retry limit.
- Duplicate prevention.
- Post-remediation verification.
- Manual fallback.
- Audit result.

## Auto-remediation Targets

Các action được phép chạy tự động trong Week 6 chỉ bao gồm những action có mức rủi ro thấp và đã được kiểm thử từ các tuần trước.

| Server | Failure | Management Channel | Action | Verification |
|---|---|---|---|---|
| WEB01 | Nginx :80 DOWN | SSH :22 UP | restart_nginx | HTTP :80 |
| APP01 | App :8080 DOWN | SSH :22 UP | restart_container | HTTP :8080 |
| WIN01 | Windows Exporter :9182 DOWN | WinRM :5985 UP | restart_windows_exporter | /metrics :9182 |

## Action Classification

Các action được chia thành ba nhóm chính.

### AUTO

Dùng cho các thao tác có mức rủi ro thấp và đã có verification rõ ràng.

Ví dụ:

- Restart Nginx.
- Restart APP01 container.
- Restart Windows Exporter.

### DIAGNOSTIC

Chỉ thu thập trạng thái hệ thống, không thay đổi cấu hình hoặc dữ liệu.

Ví dụ:

- Check service status.
- Check port status.
- Validate Nginx configuration.
- Check Docker container status.
- Check CPU, RAM và Disk usage.
- Check SSH hoặc WinRM availability.

### MANUAL

Dùng cho các thao tác có mức rủi ro cao hơn hoặc chưa đủ điều kiện để tự động hóa.

Ví dụ:

- Reboot hoặc shutdown server.
- Restart network.
- Firewall change.
- Disk cleanup hoặc delete file.
- Start/stop VM.
- System configuration change.

## Auto-remediation Conditions

Auto-remediation chỉ được phép chạy khi tất cả các điều kiện sau đều đúng:

- Service thực sự DOWN.
- Management channel đang UP.
- Action nằm trong allow-list.
- Server không ở Maintenance Mode.
- Không nằm trong cooldown.
- Không có remediation job cùng target/action đang chạy.
- Chưa vượt retry limit.

Flow tổng quát:

```
Service DOWN
→ Check Maintenance
→ Check Management Channel
→ Check Risk / Allow-list
→ Check Cooldown
→ Check Duplicate Job
→ Auto-remediation
→ Verification
→ Final Result
```

## Management Channel Rules

### WEB01

```
SSH :22 UP
→ remediation available
```

### APP01

```
SSH :22 UP
→ remediation available
```

### WIN01

```
WinRM :5985 UP
→ remediation available
```

Nếu service DOWN nhưng management channel cũng DOWN:

```
Service DOWN
+
Management Channel DOWN
→ BLOCKED
```

Nếu service vẫn UP nhưng management channel DOWN:

```
Service UP
+
Management Channel DOWN
→ DEGRADED
→ Auto-remediation unavailable
```

## Execution Failure

Nếu remediation execution fail ở lần đầu:

```
Attempt 1
→ Execution Failed
→ Retry 1 lần
```

Nếu lần retry vẫn thất bại:

```
Retry Failed
→ STOP AUTO
→ Manual intervention required
```

## Verification Failure

Execution success không đồng nghĩa với service đã recovery thành công.

Sau mỗi remediation phải thực hiện post-check.

Nếu:

```
Execution Success
+
Verification Failed
```

thì:

```
STOP AUTO
→ Manual intervention required
```

Không tự động retry thêm khi verification đã fail.

## Cooldown

Mỗi auto-remediation action sử dụng cooldown để tránh restart loop.

Giá trị ban đầu:

```
Cooldown = 5 phút
```

Ví dụ:

```
10:00 restart_nginx Success
10:02 alert tiếp tục firing
→ Skip Auto-remediation
```

Chỉ sau khi cooldown kết thúc mới cho phép tạo auto-remediation mới.

## Duplicate Prevention

Nếu đã tồn tại remediation job cùng target và action ở trạng thái:

- Queued.
- Running.

thì alert mới không được tạo thêm job.

Rule:

```
Same Target
+
Same Action
+
Queued / Running
→ Skip Duplicate
```

## Maintenance Mode

Khi server được đặt vào Maintenance Mode:

```
Maintenance Mode = ON
```

hệ thống vẫn có thể tiếp tục monitor trạng thái nhưng không thực hiện auto-remediation.

Rule:

```
Alert
+
Maintenance Mode ON
→ Skip Auto-remediation
```

Mục đích là tránh tạo remediation không cần thiết khi administrator đang chủ động bảo trì hệ thống.

## Resource Threshold Rules

### Disk Usage

```
Disk > 80%
→ Warning
→ Diagnostic
```

```
Disk > 90%
→ Critical
→ Diagnostic
→ Manual cleanup required
```

Hệ thống chỉ thu thập thông tin sử dụng disk.

Không tự động:

- Delete file.
- Remove log.
- Cleanup dữ liệu.

### CPU Usage

```
CPU > 85% trong 5 phút
→ Warning
→ Diagnostic
```

Không tự động kill process hoặc restart server.

### Memory Usage

```
RAM > 90% trong 5 phút
→ Warning
→ Diagnostic
```

Không tự động kill process hoặc restart server.

## Health Status

Trạng thái server được phân loại:

### HEALTHY

- Service hoạt động bình thường.
- Management channel hoạt động bình thường.

### DEGRADED

- Service hoặc management channel có vấn đề nhưng host vẫn reachable.

### UNREACHABLE

- Không thể xác nhận trạng thái host hoặc các health check chính đều thất bại.

### MAINTENANCE

- Server đang trong chế độ bảo trì.
- Monitoring vẫn hoạt động nhưng auto-remediation bị tắt.

## Decision Matrix

| Condition | Result |
|---|---|
| Safe service DOWN + management UP | AUTO |
| Service DOWN + management DOWN | BLOCKED |
| Service UP + management DOWN | DEGRADED / BLOCKED |
| Execution fail lần đầu | RETRY 1 |
| Retry execution fail | MANUAL |
| Verification fail | MANUAL |
| Cooldown active | SKIP |
| Duplicate running job | SKIP |
| Maintenance Mode | SKIP |
| Disk high | DIAGNOSTIC + MANUAL |
| CPU/RAM high | DIAGNOSTIC |
| Server unreachable | MANUAL |
| High-risk action | MANUAL |

## Week 6 Validation Targets

Các case cần được kiểm thử trong Week 6:

### WEB01

- Nginx DOWN + SSH UP.
- Auto restart Nginx.
- Verify HTTP :80.
- Nginx DOWN + SSH DOWN.
- Verification failure.

### APP01

- Container DOWN + SSH UP.
- Auto restart container.
- Verify HTTP :8080.
- Container DOWN + SSH DOWN.
- Verification failure.

### WIN01

- Windows Exporter DOWN + WinRM UP.
- Auto restart Windows Exporter.
- Verify /metrics :9182.
- Windows Exporter DOWN + WinRM DOWN.
- Verification failure.

### Control Cases

- Cooldown.
- Duplicate job.
- Retry limit.
- Maintenance Mode.
- Manual fallback.

## Responsibility

### Infrastructure / System / Cloud

- Validate actual service state.
- Validate SSH / WinRM.
- Execute Ansible playbook.
- Perform technical pre-check and post-check.
- Test failure scenarios.
- Validate auto-remediation on real lab targets.
- Collect technical evidence.

### Application / Integration

- Trigger remediation from alert.
- Auto / Manual decision logic.
- Cooldown.
- Retry tracking.
- Duplicate prevention.
- Maintenance Mode state.
- Job history.
- Audit log.
- Portal UI.

## Expected Result

Week 6 should demonstrate that the platform does not automatically remediate every alert.

The system must:

```
Detect
→ Classify
→ Evaluate Policy
→ AUTO / DIAGNOSTIC / BLOCKED / MANUAL
→ Execute
→ Verify
→ Audit
```

Mục tiêu là tạo một controlled auto-remediation workflow có guardrail, thay vì chỉ thực hiện restart service đơn giản.
