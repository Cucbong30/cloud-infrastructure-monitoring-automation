# Runbook 01 - Remediation Success

## 1. Mục tiêu

Hướng dẫn xử lý khi service bị down nhưng hệ thống auto-remediation có thể khôi phục thành công.

## 2. Detection

Incident được tạo khi monitoring phát hiện service không còn hoạt động.

Ví dụ:

```text
WEB01    → Nginx :80 DOWN
APP01    → Application :8080 DOWN
WIN01    → Windows Exporter :9182 DOWN
AZURE01  → Nginx :80 DOWN
```

Management channel vẫn hoạt động:

```text
Linux   → SSH available
Windows → WinRM available
```

## 3. Automatic Action

Hệ thống kiểm tra policy và chạy remediation tương ứng:

```text
WEB01   → restart_nginx
APP01   → restart_container
WIN01   → restart_windows_exporter
AZURE01 → restart_nginx
```

## 4. Verification

Sau khi action chạy thành công, hệ thống thực hiện post-check:

```text
WEB01   → HTTP :80
APP01   → HTTP :8080
WIN01   → /metrics :9182
AZURE01 → HTTP :80
```

## 5. Expected Result

```text
Execution: SUCCESS
Verification: SUCCESS
Final Status: SUCCESS
```

Incident được xem là đã recovery thành công.

## 6. Operator Action

Không cần can thiệp thủ công.

Operator chỉ cần:

1. Kiểm tra service đã hoạt động.
2. Kiểm tra monitoring target đã trở lại trạng thái healthy.
3. Kiểm tra Audit Trail và notification.
4. Xác nhận incident đã được resolve.

## 7. Closure

Incident có thể đóng khi:

```text
Service Healthy
Monitoring Healthy
Verification Passed
Audit Recorded
Notification Sent
```
