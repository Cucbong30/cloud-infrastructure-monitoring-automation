# Action Risk Matrix

## 1. Objective

Mở rộng cơ chế phân loại remediation action theo mức độ ảnh hưởng để làm cơ sở cho Approval Workflow trong Week 9.

Mỗi action được phân loại theo:

```text
Target
→ Action
→ Scope of Impact
→ Risk
→ Approval Requirement
```

Hệ thống sử dụng ba mức:

```text
LOW
MEDIUM
HIGH
```

---

## 2. Risk Classification

### LOW

Action chỉ tác động đến một service hoặc application cụ thể và có thể verification ngay sau khi thực thi.

Ví dụ:

```text
restart_nginx
restart_container
restart_windows_exporter
```

Policy:

```text
LOW
→ No Approval
→ Management Pre-check
→ Execute
→ Verification
```

---

### MEDIUM

Action có phạm vi ảnh hưởng lớn hơn một service đơn lẻ và có thể làm gián đoạn nhiều thành phần trên cùng target.

Action được chọn cho Week 9:

```text
restart_docker_service
```

Target:

```text
APP01
```

Việc restart Docker service có thể ảnh hưởng đến toàn bộ container đang chạy trên APP01, do đó mức độ ảnh hưởng cao hơn việc chỉ restart `app01-web`.

Policy:

```text
MEDIUM
→ Approval Required
→ Approved
→ Management Pre-check
→ Execute
→ Verification
```

Nếu bị reject:

```text
MEDIUM
→ REJECTED
→ NO EXECUTION
```

---

### HIGH

Action ảnh hưởng đến toàn bộ máy chủ và gây downtime cho tất cả service đang chạy trên target.

Action được chọn cho Week 9:

```text
reboot_server
```

Target test dự kiến:

```text
AZURE01
```

Reboot server sẽ làm gián đoạn:

```text
SSH
Nginx
Node Exporter
Monitoring connectivity
```

do đó action này được phân loại `HIGH`.

Policy:

```text
HIGH
→ Admin Approval Required
→ Approved
→ Execute
→ Wait for Host Recovery
→ Management Verification
→ Service Verification
```

Nếu bị reject hoặc user không đủ quyền:

```text
HIGH
→ NO EXECUTION
```

---

## 3. Action Risk Matrix

| Action | Target | Impact Scope | Risk | Approval |
|---|---|---|---|---|
| `restart_nginx` | WEB01 | Single service | LOW | No |
| `restart_container` | APP01 | Single container | LOW | No |
| `restart_windows_exporter` | WIN01 | Single service | LOW | No |
| `restart_nginx` | AZURE01 | Single service | LOW | No |
| `restart_docker_service` | APP01 | Multiple containers / Docker runtime | MEDIUM | Required |
| `reboot_server` | AZURE01 | Entire host | HIGH | Admin required |

---

## 4. Execution Rules

### LOW

```text
Request
→ Risk = LOW
→ Execute directly
→ Verify
```

### MEDIUM

```text
Request
→ Risk = MEDIUM
→ PENDING_APPROVAL
→ APPROVED
→ Execute
→ Verify
```

### HIGH

```text
Request
→ Risk = HIGH
→ PENDING_APPROVAL
→ Admin Approval
→ Execute
→ Host Recovery
→ Verify
```

---

## 5. Guardrail

Approval không thay thế các guardrail đã có.

Sau khi được approve, action vẫn phải đi qua:

```text
Management Pre-check
→ Execute
→ Verification
→ Audit
→ Notification
```

Nếu management channel unavailable:

```text
BLOCKED
→ NO EXECUTION
```

Nếu approval bị reject:

```text
REJECTED
→ NO EXECUTION
```

Nếu approval hết hạn:

```text
APPROVAL_EXPIRED
→ NO EXECUTION
```

## 6. Result

Risk Matrix của Week 9 tạo nền tảng cho Approval Workflow:

```text
LOW
→ Direct Execution

MEDIUM
→ Approval Required

HIGH
→ Admin Approval Required
```

Các action MEDIUM và HIGH sẽ được triển khai và kiểm thử bằng trạng thái thật của Infrastructure trong các bước tiếp theo.
