# Runbook 05 - Manual Required

## 1. Mục tiêu

Hướng dẫn operator xử lý các incident mà hệ thống không thể tự động recovery hoàn toàn.

## 2. Trigger Conditions

Incident chuyển sang `MANUAL_REQUIRED` khi xảy ra một trong các trường hợp:

```text
Execution Failed after Retry
Verification Failed
Management Channel Blocked
Unsupported / Non-automatic Action
```

## 3. System Response

Khi `MANUAL_REQUIRED`:

```text
Automatic Remediation Stops
→ Final Status = MANUAL_REQUIRED
→ Audit Recorded
→ Critical Notification Sent
```

Hệ thống không tiếp tục tự động retry ngoài policy đã cấu hình.

## 4. Operator Investigation

Operator kiểm tra theo thứ tự:

```text
1. Target
2. Service
3. Incident ID
4. Job ID
5. Failure Stage
6. Execution Result
7. Verification Result
8. Audit Trail
```

Sau đó kiểm tra trực tiếp trên target.

### Linux

```text
systemctl status <service>
journalctl -u <service>
ss -lntp
```

### Docker

```text
docker ps -a
docker logs <container>
```

### Windows

```text
Get-Service
```

## 5. Manual Recovery

Operator thực hiện action phù hợp với nguyên nhân thực tế.

Ví dụ:

```text
Fix configuration
Restart service
Start container
Restore management channel
Restore correct listening port
```

## 6. Verification

Sau manual recovery phải kiểm tra lại:

```text
Service State
Expected Port
HTTP / Metrics Endpoint
Monitoring Status
```

Không xem incident là resolved nếu chỉ restart service nhưng post-check chưa đạt.

## 7. Audit

Manual recovery cần được ghi nhận:

```text
Actor
Target
Action
Mode = MANUAL
Timestamp
Result
Final Status
```

## 8. Closure

Incident được đóng khi:

```text
Manual Action Completed
Verification Passed
Monitoring Healthy
Audit Recorded
Final Status = RESOLVED
```
