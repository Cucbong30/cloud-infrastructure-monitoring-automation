# Approval Policy

## 1. Objective

Xác định quy tắc approval cho remediation action dựa trên mức độ rủi ro đã được định nghĩa trong Action Risk Matrix.

Approval chỉ quyết định action có được phép tiếp tục thực thi hay không. Các bước Management Pre-check và Verification vẫn được giữ nguyên sau khi action được approve.

## 2. Approval Rules

### LOW Risk

LOW-risk action không yêu cầu approval.

Flow:

```text
Request
→ Risk = LOW
→ Management Pre-check
→ Execute
→ Verification
→ Final Status
```

Ví dụ:

```text
restart_nginx
restart_container
restart_windows_exporter
```

---

### MEDIUM Risk

MEDIUM-risk action yêu cầu approval trước khi thực thi.

Flow:

```text
Request
→ Risk = MEDIUM
→ PENDING_APPROVAL
→ APPROVED
→ Management Pre-check
→ Execute
→ Verification
```

Nếu bị reject:

```text
PENDING_APPROVAL
→ REJECTED
→ NO EXECUTION
```

Action dự kiến:

```text
APP01
→ restart_docker_service
```

---

### HIGH Risk

HIGH-risk action bắt buộc phải được Admin approve.

Flow:

```text
Request
→ Risk = HIGH
→ PENDING_APPROVAL
→ Admin Approval
→ APPROVED
→ Management Pre-check
→ Execute
→ Recovery Check
→ Verification
```

Action dự kiến:

```text
AZURE01
→ reboot_server
```

Nếu Admin reject:

```text
REJECTED
→ NO EXECUTION
```

Nếu user không đủ quyền:

```text
UNAUTHORIZED
→ DENIED
→ NO EXECUTION
```

## 3. Approval States

Các trạng thái approval được sử dụng:

```text
PENDING_APPROVAL
APPROVED
REJECTED
APPROVAL_EXPIRED
```

`APPROVAL_EXPIRED` được sử dụng khi request không được xử lý trong thời gian cho phép.

Flow:

```text
PENDING_APPROVAL
→ Timeout
→ APPROVAL_EXPIRED
→ NO EXECUTION
```

## 4. RBAC Rules

```text
Viewer
→ không được request remediation
→ không được approve

Operator
→ được request LOW / MEDIUM
→ không được approve HIGH

Admin
→ được request remediation
→ được approve hoặc reject HIGH-risk action
```

Application phải enforce quyền ở backend, không chỉ ẩn chức năng trên giao diện.

## 5. Execution Guardrail

Approval không được bypass các guardrail hiện tại.

Sau khi `APPROVED`:

```text
Management Pre-check
→ Execute
→ Verification
→ Audit
→ Notification
```

Nếu management pre-check thất bại:

```text
APPROVED
→ Management BLOCKED
→ NO EXECUTION
→ MANUAL_REQUIRED
```

## 6. No Execution Conditions

Playbook không được thực thi khi request ở một trong các trạng thái:

```text
PENDING_APPROVAL
REJECTED
APPROVAL_EXPIRED
UNAUTHORIZED
```

Chỉ request hợp lệ ở trạng thái `APPROVED` hoặc action `LOW` không yêu cầu approval mới được phép đi tiếp.

## 7. Result

Approval Policy tạo thêm lớp kiểm soát giữa request và remediation execution:

```text
Request
→ Risk Classification
→ Approval Decision
→ Management Pre-check
→ Execute
→ Verification
```

Mục tiêu là bảo đảm action có mức ảnh hưởng cao hơn không thể được thực thi trực tiếp mà chưa qua đúng quyền và approval policy.
