# Runbook 04 - Verification Failed

## 1. Mục tiêu

Hướng dẫn xử lý khi remediation command chạy thành công nhưng service không đạt post-check sau remediation.

## 2. Detection

Remediation execution trả về thành công:

```text
Execution: SUCCESS
```

nhưng verification không đạt.

Ví dụ:

```text
Nginx restart thành công
nhưng HTTP :80 không truy cập được
```

Trường hợp đã kiểm thử trên AZURE01:

```text
Nginx listen :8081
→ restart thành công
→ port :80 verification failed
```

## 3. System Response

Theo policy hiện tại:

```text
Execution SUCCESS
→ Verification FAILED
→ NO RETRY
→ MANUAL_REQUIRED
```

Không retry vì remediation command đã chạy thành công. Vấn đề nằm ở trạng thái service sau execution.

## 4. Expected Result

```text
Execution: SUCCESS
Verification: FAILED
Retry Count: 0
Final Status: MANUAL_REQUIRED
```

## 5. Operator Action

Kiểm tra service:

```text
systemctl status nginx
nginx -t
```

Kiểm tra port:

```text
ss -lntp
```

Kiểm tra endpoint:

```text
curl -I http://localhost
```

Nếu service listen sai port:

1. Kiểm tra configuration.
2. Restore port đúng.
3. Validate config.
4. Restart service.

Ví dụ:

```text
nginx -t
systemctl restart nginx
curl -I http://localhost
```

## 6. Recovery Verification

Kết quả phải đạt:

```text
Expected Port Available
HTTP / Metric Endpoint Accessible
Monitoring Healthy
```

## 7. Closure

Incident được đóng khi:

```text
Verification Passed
Service Healthy
Audit Updated
Manual Recovery Recorded
```
