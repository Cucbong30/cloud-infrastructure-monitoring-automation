# Runbook 02 - Execution Failed

## 1. Mục tiêu

Hướng dẫn xử lý khi remediation command không thể thực thi thành công.

## 2. Detection

Service bị down và management channel vẫn hoạt động, nhưng remediation action trả về lỗi.

Ví dụ:

```text
Nginx configuration invalid
Docker container không tồn tại hoặc không thể start
Windows service không thể start
```

## 3. Automatic Action

Hệ thống chạy remediation action lần đầu.

Nếu execution failed:

```text
Execution Failed
→ Retry đúng 1 lần
```

Nếu lần retry tiếp tục thất bại:

```text
Retry Failed
→ MANUAL_REQUIRED
```

## 4. Expected Result

```text
Execution: FAILED
Retry Count: 1
Verification: NOT REACHED
Final Status: MANUAL_REQUIRED
```

## 5. Operator Action

### Linux / Nginx

Kiểm tra:

```text
systemctl status nginx
nginx -t
journalctl -u nginx
```

Nếu configuration lỗi:

1. Xác định file config gây lỗi.
2. Restore configuration đúng.
3. Chạy lại:

```text
nginx -t
systemctl restart nginx
```

### Docker

Kiểm tra:

```text
docker ps -a
docker logs <container>
```

Sau đó xác định container có tồn tại và có thể start hay không.

### Windows

Kiểm tra:

```text
Get-Service
```

và xác định nguyên nhân service không thể start.

## 6. Recovery Verification

Sau khi xử lý thủ công:

```text
Service Active
Expected Port Available
Application/Metric Endpoint Accessible
```

## 7. Closure

Chỉ đóng incident khi:

```text
Service Recovered
Verification Passed
Audit Updated
Final Status = RESOLVED
```
