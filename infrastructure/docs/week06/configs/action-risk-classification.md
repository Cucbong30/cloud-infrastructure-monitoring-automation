# Week 6 - Action Risk Classification

## Purpose

Tài liệu này phân loại các remediation action theo mức độ rủi ro để xác định action nào được phép chạy tự động và action nào phải yêu cầu manual intervention.

## Risk Levels

### LOW

Action có phạm vi ảnh hưởng nhỏ, đã được kiểm thử và có verification rõ ràng.

Các action LOW có thể được phép chạy AUTO nếu các điều kiện guardrail đều đạt.

### MEDIUM

Action có thể ảnh hưởng đến service hoặc một phần hệ thống nhưng chưa đến mức thay đổi hạ tầng lớn.

Các action MEDIUM mặc định không auto trong Week 6.

### HIGH

Action có thể gây gián đoạn hệ thống, thay đổi network, dữ liệu hoặc trạng thái server.

Các action HIGH bắt buộc MANUAL.

## Action Classification

| Target | Action | Type | Risk | Mode | Verification |
|---|---|---|---|---|---|
| WEB01 | restart_nginx | Remediation | LOW | AUTO | HTTP :80 |
| WEB01 | check_nginx_status | Diagnostic | LOW | DIAGNOSTIC | Service state |
| WEB01 | nginx -t | Diagnostic | LOW | DIAGNOSTIC | Config validation |
| WEB01 | check_port_80 | Diagnostic | LOW | DIAGNOSTIC | TCP :80 |
| APP01 | restart_container | Remediation | LOW | AUTO | HTTP :8080 |
| APP01 | check_container_status | Diagnostic | LOW | DIAGNOSTIC | Container state |
| APP01 | docker ps | Diagnostic | LOW | DIAGNOSTIC | Container listing |
| APP01 | check_port_8080 | Diagnostic | LOW | DIAGNOSTIC | TCP :8080 |
| WIN01 | restart_windows_exporter | Remediation | LOW | AUTO | /metrics :9182 |
| WIN01 | check_windows_exporter_status | Diagnostic | LOW | DIAGNOSTIC | Service state |
| WIN01 | check_port_9182 | Diagnostic | LOW | DIAGNOSTIC | TCP :9182 |
| All | check_cpu | Diagnostic | LOW | DIAGNOSTIC | Metric result |
| All | check_memory | Diagnostic | LOW | DIAGNOSTIC | Metric result |
| All | check_disk | Diagnostic | LOW | DIAGNOSTIC | Metric result |
| All | check_management_channel | Diagnostic | LOW | DIAGNOSTIC | SSH / WinRM |
| All | reboot_server | Infrastructure | HIGH | MANUAL | Manual validation |
| All | shutdown_server | Infrastructure | HIGH | MANUAL | Manual validation |
| All | restart_network | Infrastructure | HIGH | MANUAL | Manual validation |
| All | change_firewall | Infrastructure | HIGH | MANUAL | Manual validation |
| All | disk_cleanup | Remediation | MEDIUM | MANUAL | Manual validation |
| All | delete_files | Remediation | HIGH | MANUAL | Manual validation |
| Cloud VM | start_vm | Infrastructure | MEDIUM | MANUAL | VM state |
| Cloud VM | stop_vm | Infrastructure | MEDIUM | MANUAL | VM state |

## AUTO Rule

Chỉ action có tất cả điều kiện sau mới được chạy AUTO:

- Risk = LOW.
- Action đã được kiểm thử trước.
- Có verification rõ ràng.
- Có management channel hoạt động.
- Có guardrail đầy đủ.
- Không nằm ngoài allow-list.

## DIAGNOSTIC Rule

Diagnostic action chỉ đọc trạng thái hệ thống.

Diagnostic không được:

- Delete dữ liệu.
- Restart server.
- Thay đổi firewall.
- Thay đổi network.
- Kill process.
- Thay đổi cấu hình hệ thống.

## MANUAL Rule

Action MEDIUM hoặc HIGH phải chuyển sang manual intervention.

Ví dụ:

```
Disk > 90%
→ Diagnostic
→ Manual cleanup
```

```
Server requires reboot
→ Manual approval
```

```
Network issue
→ Manual investigation
```

## Design Principle

Hệ thống không đánh giá AUTO chỉ dựa trên việc action có thể chạy được hay không.

Decision phải dựa trên:

```
Risk
+ Impact
+ Verification
+ Management Availability
+ Previous Validation
→ Execution Mode
```

Mục tiêu là giảm rủi ro khi auto-remediation và tránh biến platform thành hệ thống tự động thực hiện các thao tác nguy hiểm.
