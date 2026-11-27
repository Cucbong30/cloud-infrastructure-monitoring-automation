# DG-06 – Approval Workflow

**Đề tài:** Xây dựng hệ thống giám sát và tự động hóa vận hành hạ tầng trong môi trường Hybrid Cloud  
**Phụ trách:** Nguyễn Thế Gia Bảo – Application / Integration  
**Baseline:** Approval service, RBAC và hàng đợi trên Operations Portal, Tuần 9  
**Timeout hiện hành:** `APPROVAL_TIMEOUT_MINUTES = 5`

## 1. Mục đích

Activity Diagram mô tả điều kiện một remediation action được chạy Ansible. Request và Job là hai đối tượng riêng. Trạng thái chờ duyệt, bị từ chối hoặc hết hạn không có job thực thi.

Email dùng Microsoft Graph đã cấu hình từ Tuần 7. Email có Request ID, target, action, risk và trạng thái, có thể có link mở request trên Portal. Email không có nút Approve.

## 2. Phân quyền

| Thao tác | Viewer | Operator | Admin |
|---|---|---|---|
| Xem request | Có | Có | Có |
| Request LOW | Không | Có | Có |
| Request MEDIUM | Không | Có | Có |
| Request HIGH | Không | Không | Có |
| Approve hoặc Reject MEDIUM | Không | Không | Có |
| Approve hoặc Reject HIGH | Không | Không | Có |

Operator không tự duyệt request của mình hay của người khác. Admin trong lab được duyệt cả request do chính Admin tạo, vì môi trường có một tài khoản quản trị. Viewer bị từ chối ở backend bằng HTTP 403, không chỉ bằng việc ẩn nút.

## 3. Phân loại rủi ro

| Target | Action | Risk | Cách xử lý |
|---|---|---|---|
| WEB01 | `restart_nginx` | LOW | Chạy sau pre-check. Không tạo approval request. |
| APP01 | `restart_container` | LOW | Auto và manual đều được chạy khi đủ policy. |
| WIN01 | `restart_windows_exporter` | LOW | Auto và manual đều được chạy khi đủ policy. |
| AZURE01 | `restart_nginx` | LOW | Dùng playbook `restart-azure-nginx.yml`. |
| APP01 | `restart_docker_service` | MEDIUM | Tạo request. Ansible chỉ chạy sau khi Admin approve. |
| AZURE01 | `reboot_server` | HIGH | Chỉ Admin được request. Ansible chỉ chạy sau khi Admin approve. |

Auto-remediation chỉ thực thi action LOW. Nếu một action medium hoặc high được gắn vào cảnh báo tự động, Portal tạo request với actor SYSTEM và không chạy playbook. SYSTEM không có quyền duyệt.

Nút Retry, cảnh báo AUTO và lời gọi dispatch trực tiếp đều đi qua cùng cổng này. Chúng không được tạo job khi action còn cần duyệt.

## 4. Activity Diagram

```mermaid
flowchart TD
    start([Có yêu cầu remediation])
    role{Role của người yêu cầu}
    deny[Ghi permission.denied<br/>HTTP 403<br/>Không tạo request và không tạo job]
    risk{Risk của action}
    lowGate{LOW đã đủ quyền<br/>và không trùng policy chặn}
    open[Tạo Approval Request<br/>status = PENDING_APPROVAL<br/>job_id = null<br/>expires_at = requested_at + 5 phút]
    mailReq[Email Approval Requested<br/>tới Admin có email]
    auditReq[Audit approval.requested]
    wait{Admin mở Portal<br/>trước khi hết hạn}
    expire[status = APPROVAL_EXPIRED<br/>execution = NOT_RUN<br/>Không gọi Ansible]
    mailExp[Email Approval Expired<br/>tới requester]
    auditExp[Audit approval.expired]
    decide{Quyết định của Admin}
    reject[status = REJECTED<br/>lưu decision_reason<br/>job_id = null]
    mailRej[Email Approval Rejected<br/>tới requester]
    auditRej[Audit approval.rejected]
    approve[status = APPROVED<br/>lưu approver và decision_at]
    mailOk[Email Approval Approved<br/>tới requester]
    auditOk[Audit approval.approved]
    pre{Pre-check Week 6<br/>management, cooldown, duplicate}
    blocked[Tạo job MANAGEMENT_BLOCKED<br/>hoặc DUPLICATE_SKIPPED<br/>playbook_executed = false]
    run[SSH tới MON01<br/>ansible-playbook đúng file allow-list]
    verify{Verification}
    success[Job SUCCESS<br/>ghi execution và verification]
    failed[Job EXECUTION_FAILED<br/>hoặc VERIFICATION_FAILED<br/>Manual không tự retry]
    mailExec[Email Success hoặc Failed<br/>theo nhóm severity]
    auditDone[Audit kết quả execution<br/>và approval.completed]
    stop([Kết thúc<br/>Request và Job vẫn là hai bản ghi])

    start --> role
    role -->|Viewer| deny
    role -->|Operator và action HIGH| deny
    role -->|Operator hoặc Admin| risk
    deny --> stop
    risk -->|LOW| lowGate
    risk -->|MEDIUM và Operator hoặc Admin| open
    risk -->|HIGH và chỉ Admin| open
    lowGate -->|Không đủ điều kiện| blocked
    lowGate -->|Đủ điều kiện| run
    open --> auditReq --> mailReq --> wait
    wait -->|expires_at đã qua| expire
    expire --> auditExp --> mailExp --> stop
    wait -->|Còn PENDING_APPROVAL| decide
    decide -->|Reject| reject
    reject --> auditRej --> mailRej --> stop
    decide -->|Approve| approve
    approve --> auditOk --> mailOk --> pre
    pre -->|Management down hoặc job đang chạy| blocked
    pre -->|Đạt| run
    blocked --> mailExec --> stop
    run --> verify
    verify -->|Đạt| success
    verify -->|Không đạt| failed
    success --> auditDone --> mailExec --> stop
    failed --> auditDone
```

Cổng thực thi sau khi đã có quyết định:

| Điều kiện | Ansible |
|---|---|
| LOW và người dùng có quyền | Được chạy, sau pre-check, cooldown, duplicate và verification. |
| MEDIUM hoặc HIGH đang `PENDING_APPROVAL` | Không chạy. |
| MEDIUM hoặc HIGH đã `APPROVED` | Được chạy, rồi áp dụng lại policy Tuần 6. |
| `REJECTED`, `APPROVAL_EXPIRED` hoặc không đủ quyền | Không chạy. |

Với `reboot_server`, verification của Portal chỉ đạt khi SSH cổng 22 và Nginx đều trả lời sau khi máy khởi động lại. Thời gian chờ Ansible của riêng reboot là 420 giây để playbook `reboot-azure01.yml` có thể chờ tối đa 300 giây.

## 5. Vòng đời request

```mermaid
stateDiagram-v2
    [*] --> PENDING_APPROVAL: MEDIUM hoặc HIGH hợp lệ
    PENDING_APPROVAL --> APPROVED: Admin approve
    PENDING_APPROVAL --> REJECTED: Admin reject kèm lý do
    PENDING_APPROVAL --> APPROVAL_EXPIRED: Quá 5 phút
    APPROVED --> [*]: Job được tạo sau pre-check
    REJECTED --> [*]: Không có job
    APPROVAL_EXPIRED --> [*]: Không có job và không approve lại
```

Hết hạn được kiểm tra khi mở hàng đợi, mở chi tiết và trước lúc ghi quyết định. Request đã hết hạn không được approve thành công.

Nếu đã có request pending cùng server và cùng action, Portal trả lại request đó và không gửi thêm email request mới.

## 6. Giao diện

Menu **Operations → Approvals** có hai phần:

- **Pending:** request còn `PENDING_APPROVAL`, gồm requester, role, target, service, action, risk, thời điểm yêu cầu và thời điểm hết hạn.
- **History:** request đã approved, rejected hoặc expired, gồm approver, thời điểm quyết định và job nếu có.

Nút **Review** và việc bấm vào dòng mở chi tiết. Nút **Approve** và **Reject** chỉ render khi user là Admin và request còn pending. Reject bắt buộc có lý do.

## 7. Audit và email

| Sự kiện | Audit | Người nhận email |
|---|---|---|
| Tạo request | `approval.requested` | Admin đang active và có email |
| Approve | `approval.approved`, sau khi chạy xong có `approval.completed` | Requester khi approve; kết quả chạy gửi theo severity |
| Reject | `approval.rejected` | Requester |
| Hết hạn | `approval.expired` | Requester |
| Từ chối quyền | `permission.denied` | Không gửi mail duyệt |
| Chạy xong | audit remediation kèm job ID | Nhóm Critical, Warning hoặc Info đã cấu hình |

Mỗi dòng audit của approval lưu được request ID, requester, requester role, approver, risk, decision, thời điểm, job ID, execution result và verification result. Màn Audit lọc theo ngày ICT và theo đúng tên action.

`approval.completed` được ghi để nối request với kết quả job. Sự kiện này không gửi thêm một email riêng; email kết quả vẫn là email remediation.

## 8. Trường bắt buộc của request

`request_id`, `requester`, `requester_role`, `target`, `action`, `risk`, `mode`, `status`, `requested_at`, `expires_at`, `approver`, `decision_at`, `decision_reason`, `job_id`.

Trước khi approve, approver, decision time, decision reason và job ID để trống. Execution và verification của request chưa chạy là `NOT_RUN`.

## 9. Tài liệu liên quan

- [SRS – FR-APR và RULE-13, RULE-14](../SRS.md)
- [SDD – Approval Workflow Design](../SDD.md)
- [DG-03 Use Case](use-case-diagram.md)
- [DG-04 Database ERD](database-erd.md)
- [DG-05 Remediation Sequence](remediation-sequence.md)
