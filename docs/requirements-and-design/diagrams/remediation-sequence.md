# DG-05 – Remediation Sequence Diagram

**Đề tài:** Cloud Infrastructure Monitoring and Automation   
**Phụ trách:** Infrastructure / System / Cloud và Application / Integration

## 1. Mục đích

Sơ đồ mô tả quá trình từ phát hiện sự cố đến thực thi remediation, kiểm tra kết quả và ghi nhận lịch sử. Hệ thống không thực thi lệnh trực tiếp từ nội dung cảnh báo mà sử dụng action và playbook đã được cho phép.

## 2. Thành phần tham gia

| Thành phần | Trách nhiệm |
|---|---|
| Prometheus | Thu thập metrics và đánh giá alert rules. |
| Alertmanager | Gửi sự kiện cảnh báo đến Portal qua webhook. |
| Flask Portal | Xử lý cảnh báo, RBAC, policy, approval, job và kết quả. |
| SQLite | Lưu trạng thái cảnh báo, incident, approval, job và audit. |
| MON01 | Ansible control node; nhận yêu cầu thực thi qua SSH từ Portal. |
| Target Server | WEB01, APP01, WIN01 hoặc AZURE01. |
| Email Notification | Thông báo theo sự kiện và severity. |

## 3. Controlled Auto-remediation

```mermaid
sequenceDiagram
    autonumber
    participant T as Target Server
    participant P as Prometheus
    participant A as Alertmanager
    participant W as Flask Portal
    participant D as SQLite
    participant M as MON01 / Ansible
    participant N as Email Notification

    P->>T: Scrape metrics / evaluate service health
    T-->>P: Metrics or unavailable endpoint
    P->>A: Firing alert
    A->>W: POST alert webhook
    W->>D: Upsert alert and identify incident
    W->>W: Check auto enabled, allow-list and LOW risk
    W->>W: Check duplicate and cooldown
    alt Not eligible or duplicate or cooldown
        W->>D: Record skip decision and audit
        Note over W,M: No playbook execution
    else Eligible
        W->>T: Management pre-check (SSH / WinRM)
        alt Management unavailable
            W->>D: BLOCKED / management_channel_unavailable
            W->>N: Blocked notification
        else Management available
            W->>D: Record execution attempt
            W->>M: SSH and invoke allowed playbook
            M->>T: Execute remediation via SSH / WinRM
            T-->>M: Execution result
            M-->>W: Execution status and output
            alt Execution failed
                W->>D: Record EXECUTION_FAILED
                W->>N: Failure notification
                opt Retry budget available
                    W->>N: Retry notification
                    W->>T: Recheck management availability
                    alt Management available
                        W->>M: Execute one retry
                        M->>T: Run allowed playbook
                        T-->>M: Result
                        M-->>W: Retry result
                    else Management unavailable
                        W->>D: Record BLOCKED; no retry execution
                    end
                end
            end
            alt Latest execution successful
                W->>T: Verify service / endpoint
                T-->>W: Verification result
                alt Verification passed
                    W->>D: SUCCESS and incident resolved
                    W->>N: Success notification
                else Verification failed
                    W->>D: VERIFICATION_FAILED / MANUAL_REQUIRED
                    Note over W,M: No automatic retry
                end
            else Execution failed and retry exhausted
                W->>D: MANUAL_REQUIRED
            end
        end
    end
    Note over W,D: Persist outcomes and audit for traceability
```

Sơ đồ thể hiện luồng logic; thứ tự ghi database, gửi mail và tên hàm nội bộ cần đối chiếu source code khi nghiệm thu. Nếu pre-check của lần retry thất bại thì kết thúc theo nhánh BLOCKED, không chạy verification hay playbook. Khi cảnh báo chuyển resolved, Portal cập nhật trạng thái cảnh báo tương ứng; không đồng nhất alert resolved với job SUCCESS.

## 4. Manual Remediation và Approval

```mermaid
sequenceDiagram
    autonumber
    actor U as Admin / Operator / Viewer
    actor B as Admin approver
    participant W as Flask Portal
    participant D as SQLite
    participant M as MON01 / Ansible
    participant T as Target Server
    U->>W: Request action on target
    W->>W: Validate RBAC, action and risk
    alt Unauthorized or invalid action
        W->>D: Record denial audit
        W-->>U: Denied (403 for unauthorized)
    else Authorized
        alt MEDIUM or HIGH
            W->>D: Create PENDING_APPROVAL request
            W-->>B: Notify approval request
            alt Rejected or expired after 5 minutes
                W->>D: Record decision / expiry
                Note over W,M: No execution job or playbook
            else Approved by Admin
                B->>W: Approve request
                W->>D: Record approval decision
            end
        else LOW
            Note over W,D: No approval required
        end
        opt LOW or valid approved request
            W->>W: Check duplicate and execution eligibility
            alt Duplicate active job
                W->>D: DUPLICATE_SKIPPED / NOT_RUN
            else Eligible
                W->>T: Management pre-check
                alt Management unavailable
                    W->>D: BLOCKED; no playbook
                else Available
                    W->>M: Invoke allowed playbook via SSH
                    M->>T: Execute action
                    T-->>M: Execution result
                    M-->>W: Execution result
                    alt Execution successful
                        W->>T: Verify expected service state
                        T-->>W: Verification result
                        W->>D: Record SUCCESS or VERIFICATION_FAILED
                    else Execution failed
                        W->>D: Record EXECUTION_FAILED
                    end
                    Note over W,M: Manual execution has no automatic retry
                end
            end
        end
    end
    W-->>U: Display request / job status
```

Chi tiết trạng thái approval được trình bày riêng trong [DG-06](approval-workflow.md). Incident lifecycle đầy đủ thuộc [DG-07](incident-state-diagram.md), dự kiến hoàn thiện trong Tuần 10.

## 5. Action, risk và verification

| Target | Action | Risk | Management | Verification |
|---|---|---|---|---|
| WEB01 | `restart_nginx` | LOW | SSH 22 | HTTP 80 |
| APP01 | `restart_container` | LOW | SSH 22 | Application HTTP 8080 |
| WIN01 | `restart_windows_exporter` | LOW | WinRM 5985 | Exporter 9182 |
| AZURE01 | `restart_nginx` | LOW | SSH 22 | HTTP 80 |
| APP01 | `restart_docker_service` | MEDIUM | SSH 22 | Docker service / workload check |
| AZURE01 | `reboot_server` | HIGH | SSH 22 | SSH 22 và Nginx HTTP sau khi máy lên lại. Playbook còn kiểm tra Nginx, Node Exporter, cổng 80 và 9100. |

Các action LOW trong allow-list có thể chạy tự động nếu đủ điều kiện. MEDIUM chỉ Admin hoặc Operator được request, HIGH chỉ Admin được request; cả hai mức đều cần Admin approve. CPU, RAM hoặc Disk cao không tự động dẫn đến reboot, xóa file hoặc thay đổi network.

## 6. Quy tắc kiểm soát thực thi

| Quy tắc | Thiết kế |
|---|---|
| Allow-list | Chỉ thực thi action được ánh xạ đến playbook hợp lệ. |
| RBAC | Viewer không được trigger remediation; backend từ chối request trái quyền. |
| Duplicate | Không chạy trùng target + action đang queued hoặc running. |
| Cooldown | AUTO: 120 giây sau SUCCESS. |
| Retry | AUTO: tối đa một lần khi execution failed; ngân sách theo incident. |
| Manual | Không tự retry. |
| Management unavailable | Không thực thi playbook; ghi nhận BLOCKED. |
| Verification failed | Không retry; yêu cầu xử lý thủ công đối với AUTO. |
| Approval timeout | 5 phút; rejected hoặc expired không thực thi. |
| Credential | Portal gọi MON01; SSH key AZURE01 và credential WinRM được quản lý phía Ansible, không truyền từ Portal. |
| Audit | AUTO ghi SYSTEM; MANUAL ghi user, role, target, action, thời gian và kết quả; approval ghi requester, approver và decision. |

## 7. Đối chiếu kiểm thử

| Kịch bản | Kết quả mong đợi |
|---|---|
| LOW, management UP, execution và verification PASS | SUCCESS |
| AUTO execution fail hai lần | MANUAL_REQUIRED, không có lần chạy thứ ba |
| Management DOWN | BLOCKED, playbook NOT_RUN |
| Execution PASS nhưng verification FAIL | VERIFICATION_FAILED; không retry |
| Duplicate active job | Skip, không thực thi thêm |
| AUTO trong cooldown | Skip, không thực thi |
| MEDIUM/HIGH chưa approve, rejected hoặc expired | Không thực thi |
| Viewer trigger hoặc Operator request HIGH | Denied, không gọi executor |
| MEDIUM/HIGH được approve hợp lệ | Tiếp tục pre-check, execution và verification |

Đây là tiêu chí thiết kế, không phải tuyên bố mọi test đều đã có đầy đủ minh chứng. Báo cáo Tuần 9 còn thiếu ảnh HTTP 403, drawer Job 71/72 và đối chiếu timeout phía Infrastructure.

## 8. Tài liệu tham chiếu

- [DG-01 – System Architecture](system-architecture.md)
- [DG-02 – Network Topology](network-topology.md)
- [DG-03 – Use Case Diagram](use-case-diagram.md)
- [Application – Controlled Auto-remediation, Tuần 6](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517)
- [Application – Manual Remediation và RBAC, Tuần 8](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/4960f041ed12294b595016e993720ba209fd6bf8)
- [Application – Approval Workflow, Tuần 9](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/b95ad447b07e58401e4296b4bd67a15852064998)
- [Infrastructure – Risk Matrix](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/infra/infrastructure/docs/week09/configs/action-risk-matrix.md)
- [Infrastructure – Approval Policy](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/infra/infrastructure/docs/week09/configs/approval-policy.md)

## 9. Giới hạn thiết kế

Không bổ sung orchestration platform, AI tự quyết định action hoặc cơ chế HA mới. Maintenance Mode không được coi là chức năng đã nghiệm thu. Sơ đồ mô tả thiết kế logic đến Tuần 9 dựa trên báo cáo triển khai; cần review chung với Application để xác nhận thứ tự xử lý nội bộ, đặc biệt ở nhánh retry và approval. Không thay đổi production playbook hay policy hiện hành.
