# Week 6 - Phân loại mức độ rủi ro của action

## Mục tiêu

Các remediation action được phân loại theo mức độ rủi ro để xác định action nào được phép chạy tự động và action nào phải chuyển sang manual intervention.

## Mức LOW

Các action có phạm vi ảnh hưởng nhỏ, đã được kiểm thử và có cách verification rõ ràng.

Action LOW có thể được phép chạy Auto-remediation.

## Mức MEDIUM

Các action có thể ảnh hưởng đến availability của hệ thống, dữ liệu hoặc nhiều thành phần cùng lúc.

Trong Week 6, các action MEDIUM không chạy tự động.

## Mức HIGH

Các action có khả năng gây gián đoạn server, network hoặc làm thay đổi dữ liệu.

Các action HIGH bắt buộc xử lý thủ công.

## Phân loại action

| Target | Action | Risk | Mode | Verification |
|---|---|---|---|---|
| WEB01 | restart_nginx | LOW | AUTO | HTTP :80 |
| APP01 | restart_container | LOW | AUTO | HTTP :8080 |
| WIN01 | restart_windows_exporter | LOW | AUTO | /metrics :9182 |
| All | check_service_status | LOW | DIAGNOSTIC | Service state |
| All | check_management_channel | LOW | DIAGNOSTIC | SSH / WinRM |
| All | check_port | LOW | DIAGNOSTIC | TCP state |
| All | check_cpu | LOW | DIAGNOSTIC | Metric |
| All | check_memory | LOW | DIAGNOSTIC | Metric |
| All | check_disk | LOW | DIAGNOSTIC | Metric |
| All | disk_cleanup | MEDIUM | MANUAL | Operator validation |
| All | reboot_server | HIGH | MANUAL | Operator validation |
| All | shutdown_server | HIGH | MANUAL | Operator validation |
| All | restart_network | HIGH | MANUAL | Operator validation |
| All | change_firewall | HIGH | MANUAL | Operator validation |
| All | delete_files | HIGH | MANUAL | Operator validation |

## Điều kiện để một action được chạy Auto

Một action chỉ được phép chạy tự động khi:

- Risk = LOW.
- Action đã được kiểm thử trước.
- Failure condition đã được xác nhận.
- Management channel vẫn hoạt động.
- Có bước verification sau remediation.

Ví dụ:

```
Nginx DOWN
+ SSH UP
+ restart_nginx nằm trong allow-list
+ có HTTP :80 để verify
→ AUTO
```

## Khi nào phải chuyển sang Manual

```
Management channel unavailable
OR
Execution Failed sau retry
OR
Verification Failed
OR
Action có Risk MEDIUM/HIGH
→ MANUAL_REQUIRED
```

## Nguyên tắc

Quyết định Auto hay Manual không chỉ dựa trên việc action có chạy được hay không.

Cần dựa trên:

```
Loại sự cố
+ Management Availability
+ Risk của action
+ Kết quả Verification
→ Final Decision
```

Chỉ những action có mức rủi ro thấp, đã được kiểm thử và có thể xác nhận kết quả rõ ràng mới được phép chạy tự động.
