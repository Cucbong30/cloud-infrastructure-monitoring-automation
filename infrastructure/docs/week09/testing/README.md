# Week 9 Approval Workflow Testing

Thư mục này được sử dụng để lưu các test case và kết quả kiểm thử cho Approval & High-risk Action Control trong Week 9.

## Planned Test Cases

Các case  kiểm thử:

```text
TC01 - LOW Risk Direct Execution
TC02 - MEDIUM Risk Approved
TC03 - MEDIUM Risk Rejected
TC04 - HIGH Risk Approved
TC05 - HIGH Risk Rejected
TC06 - Unauthorized Approval
TC07 - Approval Timeout
```

## Test Scope

Các bài test sẽ kiểm tra toàn bộ flow:

```text
Remediation Request
→ Risk Classification
→ Approval Decision
→ RBAC Validation
→ Infrastructure Execution
→ Verification
→ Audit
→ Notification
```

## Infrastructure Validation

Phía Infrastructure sẽ chịu trách nhiệm xác nhận:

- Playbook có được thực thi hay không.
- Target thực tế có thay đổi đúng theo action hay không.
- Service, container hoặc host có phục hồi đúng trạng thái mong đợi hay không.
- Các request bị Reject, Unauthorized hoặc Expired không được thực thi trên Infrastructure.

## Application Validation

Phía Application sẽ xác nhận:

- Risk classification.
- Approval state.
- Approver và requester.
- RBAC enforcement.
- Job execution status.
- Audit Trail.
- Notification.

## Evidence

Evidence sẽ được bổ sung sau khi thực hiện kiểm thử chung giữa Infrastructure và Application.

Mỗi test case sẽ được ghi nhận với:

```text
Test condition
Expected result
Actual result
Infrastructure verification
Application verification
Screenshot evidence
Final status
```

Các screenshot sẽ được lưu theo từng test case sau khi quá trình kiểm thử thực tế hoàn tất.
