# Requirements Traceability Matrix

**Đề tài:** Xây dựng hệ thống giám sát và tự động hóa vận hành hạ tầng trong môi trường Hybrid Cloud  
**Phụ trách Application:** Nguyễn Thế Gia Bảo  
**Nguồn yêu cầu:** [SRS.md](SRS.md)  
**Nguồn thiết kế:** [SDD.md](SDD.md)

Mức độ:

- **Đã triển khai:** có trong Portal hiện tại và được mô tả đúng với code.
- **Một phần:** có dữ liệu hoặc luồng nền, chưa đủ màn hình hoặc trạng thái yêu cầu.
- **Tuần 10:** nằm trong phân công đang thực hiện, chưa nghiệm thu.

## 1. Functional Requirements

| ID | Yêu cầu | Thiết kế | Sơ đồ | Mức độ |
|---|---|---|---|---|
| FR-AUTH-01 | Đăng nhập Entra ID | SDD 13.1, 13.2 | DG-03, DG-08 | Đã triển khai |
| FR-AUTH-02 | Gán Admin, Operator, Viewer | SDD 13.3 | DG-03, DG-06 | Đã triển khai |
| FR-AUTH-03 | Chặn ở giao diện và backend | SDD 13.4 | DG-03, DG-06 | Đã triển khai |
| FR-AUTH-04 | Đăng xuất | SDD 13.2 | DG-03 | Đã triển khai |
| FR-INV-01 | Danh sách máy lab | SDD 4, 7 | DG-01, DG-08 | Đã triển khai |
| FR-INV-02 | Hostname, địa chỉ, OS, môi trường | SDD 8 | DG-04 | Đã triển khai |
| FR-INV-03 | Admin quản lý inventory | SDD 7 | DG-03 | Đã triển khai |
| FR-INV-04 | Kiểm tra dữ liệu đầu vào | SDD 7 | DG-04 | Đã triển khai |
| FR-MON-01 | CPU, RAM, Disk, Uptime từ exporter | SDD 9.2 | DG-01, DG-02 | Đã triển khai |
| FR-MON-02 | Dashboard lấy số liệu thật | SDD 9.1 | DG-08 | Đã triển khai |
| FR-MON-03 | Healthy, Degraded, Unreachable | SDD 9.3 | DG-01 | Đã triển khai |
| FR-MON-04 | Giám sát dịch vụ | SDD 9.2 | DG-02, DG-05 | Đã triển khai |
| FR-MON-05 | Không báo Healthy khi mất metrics | SDD 9.3 | DG-08 | Đã triển khai |
| FR-MON-06 | Biểu đồ Grafana | SDD 9.1 | DG-08 | Đã triển khai trên MON01 |
| FR-ALT-01 | Nhận webhook Alertmanager | SDD 9.4 | DG-05 | Đã triển khai |
| FR-ALT-02 | Firing và Resolved | SDD 9.5 | DG-04, DG-07 | Đã triển khai. Thêm `acknowledged`. |
| FR-ALT-03 | Severity | SDD 9.4, 14.2 | DG-04 | Đã triển khai |
| FR-ALT-04 | Chống trùng theo fingerprint và cửa sổ `starts_at` | SDD 9.4 | DG-04, DG-07 | Đã triển khai |
| FR-ALT-05 | Gợi ý action | SDD 10.3 | DG-05 | Đã triển khai |
| FR-ALT-06 | Acknowledge | SDD 9.5 | DG-04 | Đã triển khai trên Alert, chưa phải trạng thái Incident |
| FR-MAN-01 | Manual theo quyền và risk | SDD 10, 11 | DG-05, DG-06 | Đã triển khai |
| FR-MAN-02 | Chặn khi mất SSH hoặc WinRM | SDD 10.2 | DG-05 | Đã triển khai |
| FR-MAN-03 | Chỉ action allow-list | SDD 10.1 | DG-05 | Đã triển khai |
| FR-MAN-04 | SUCCESS chỉ sau verification | SDD 10.9 | DG-05, DG-07 | Đã triển khai |
| FR-MAN-05 | Retry tạo job mới | SDD 10.6 | DG-04, DG-07 | Đã triển khai. Manual không tự retry. |
| FR-AUTO-01 | Auto chỉ khi đủ policy | SDD 10.4 | DG-05 | Đã triển khai |
| FR-AUTO-02 | Pre-check | SDD 10.4 | DG-05 | Đã triển khai |
| FR-AUTO-03 | Một lần retry mỗi incident | SDD 10.6 | DG-07 | Đã triển khai |
| FR-AUTO-04 | Cooldown 120 giây | SDD 10.7 | DG-05 | Đã triển khai |
| FR-AUTO-05 | Không chạy trùng queued hoặc running | SDD 10.8 | DG-05 | Đã triển khai |
| FR-AUTO-06 | Verification failed không retry | SDD 10.6 | DG-07 | Đã triển khai |
| FR-AUTO-07 | Manual required | SDD 10.5 | DG-07 | Đã triển khai bằng cờ, chưa bằng trạng thái riêng |
| FR-AUTO-08 | Chỉ LOW được auto | SDD 11.1 | DG-06 | Đã triển khai |
| FR-JOB-01 | Danh sách job | SDD 10 | DG-03 | Đã triển khai |
| FR-JOB-02 | Job Detail đủ trường | SDD 10.5, 11 | DG-04, DG-06 | Đã triển khai |
| FR-JOB-03 | AUTO và MANUAL | SDD 10 | DG-04 | Đã triển khai |
| FR-JOB-04 | Sáu kết quả nghiệp vụ | SDD 10.5 | DG-05, DG-07 | Đã triển khai |
| FR-JOB-05 | Không ghi đè lịch sử | SDD 8 | DG-04 | Đã triển khai |
| FR-APR-01 | LOW, MEDIUM, HIGH | SDD 10.3 | DG-06 | Đã triển khai |
| FR-APR-02 | LOW chạy trực tiếp | SDD 11.1 | DG-06 | Đã triển khai |
| FR-APR-03 | MEDIUM và HIGH chưa có job khi chưa duyệt | SDD 11 | DG-04, DG-06 | Đã triển khai |
| FR-APR-04 | Operator không request HIGH | SDD 11.1 | DG-03, DG-06 | Đã triển khai |
| FR-APR-05 | Chỉ Admin approve hoặc reject | SDD 11.4 | DG-06 | Đã triển khai |
| FR-APR-06 | Hết hạn sau 5 phút | SDD 11.4 | DG-06 | Đã triển khai |
| FR-APR-07 | Rejected không gọi Ansible | SDD 11.3 | DG-06 | Đã triển khai |
| FR-APR-08 | Lưu requester, approver, decision, thời gian, action | SDD 15 | DG-04, DG-06 | Đã triển khai |
| FR-INC-01 | Tạo incident từ alert và target | SDD 12.4 | DG-04, DG-07 | Đã triển khai |
| FR-INC-02 | Vòng đời đầy đủ | SDD 12.2 | DG-07 | Một phần. DB chỉ có `open` và `resolved`. |
| FR-INC-03 | Một incident nhiều job | SDD 12.4 | DG-04, DG-07 | Đã triển khai |
| FR-INC-04 | Resolve khi verification đạt | SDD 12.3 | DG-07 | Đã triển khai |
| FR-INC-05 | Không resolve khi chưa phục hồi | SDD 12.3 | DG-07 | Đã triển khai |
| FR-INC-06 | Cập nhật incident thủ công | SDD 12 | DG-07 | Tuần 10. Hiện chỉ đổi qua kết quả remediation. |
| FR-INC-07 | Sự cố tái diễn tạo incident mới | SDD 12.5 | DG-07 | Đã triển khai |
| FR-INC-08 | Màn hình lịch sử incident | SDD 12.6 | DG-07 | Một phần. Có ID trên Job Detail và audit, chưa có màn hình incident. |
| FR-NOT-01 | Gửi mail qua Microsoft Graph | SDD 14.1 | DG-08 | Đã triển khai |
| FR-NOT-02 | Nhóm Critical, Warning, Info | SDD 14.2 | DG-06 | Đã triển khai cho kết quả chạy. Mail duyệt đi tới Admin hoặc requester. |
| FR-NOT-03 | Email có target, service, thời gian, action, trạng thái | SDD 14.3 | DG-06 | Đã triển khai. Mail duyệt thêm Request ID và risk. |
| FR-NOT-04 | Lỗi mail không dừng remediation | SDD 14.4 | DG-05 | Đã triển khai |
| FR-AUD-01 | Actor, role, action, target, thời gian, kết quả | SDD 15 | DG-04 | Đã triển khai |
| FR-AUD-02 | Auto ghi SYSTEM | SDD 15.2 | DG-03, DG-05 | Đã triển khai |
| FR-AUD-03 | Audit approval | SDD 15.2 | DG-06 | Đã triển khai |
| FR-AUD-04 | Audit đổi incident | SDD 15.2 | DG-07 | Đã triển khai cho created và resolved |
| FR-AUD-05 | Không sửa hoặc xóa audit trên UI | SDD 15.3 | DG-04 | Đã triển khai |

## 2. Business Rules

| ID | Quy tắc | Sơ đồ | Mức độ |
|---|---|---|---|
| RULE-01 | Viewer không đổi hệ thống | DG-03 | Đã triển khai |
| RULE-02 | Operator chạy LOW và request MEDIUM | DG-06 | Đã triển khai |
| RULE-03 | Operator không request HIGH và không duyệt | DG-06 | Đã triển khai |
| RULE-04 | Chỉ Admin duyệt MEDIUM và HIGH | DG-06 | Đã triển khai |
| RULE-05 | Ngoài allow-list không chạy | DG-05 | Đã triển khai |
| RULE-06 | Auto không chạy MEDIUM và HIGH | DG-06 | Đã triển khai |
| RULE-07 | Mất management channel thì không gọi playbook | DG-05 | Đã triển khai |
| RULE-08 | Auto retry một lần khi execution failed | DG-07 | Đã triển khai |
| RULE-09 | Manual không tự retry | DG-05 | Đã triển khai |
| RULE-10 | Verification failed không retry | DG-07 | Đã triển khai |
| RULE-11 | Cooldown 120 giây | DG-05 | Đã triển khai |
| RULE-12 | Không chạy trùng queued hoặc running | DG-05 | Đã triển khai |
| RULE-13 | Pending hết hạn sau 5 phút | DG-06 | Đã triển khai |
| RULE-14 | Rejected và expired không gọi Ansible | DG-06 | Đã triển khai |
| RULE-15 | SUCCESS chỉ sau verification | DG-05, DG-07 | Đã triển khai |
| RULE-16 | Không resolve khi dịch vụ chưa lên | DG-07 | Đã triển khai |
| RULE-17 | Job mới không ghi đè job cũ | DG-04 | Đã triển khai |
| RULE-18 | Lỗi notification không dừng remediation | DG-05 | Đã triển khai |

## 3. Use case

| ID trong SRS | Nội dung | Sơ đồ đối chiếu | Mức độ |
|---|---|---|---|
| UC-01 | Đăng nhập | DG-03 UC-01 | Đã triển khai |
| UC-02 | Dashboard | DG-03 UC-02 | Đã triển khai |
| UC-03 | Inventory | DG-03 | Đã triển khai |
| UC-04 | Alert | DG-03 UC-03 | Đã triển khai |
| UC-05 | Manual remediation | DG-03 UC-05, DG-05 | Đã triển khai |
| UC-06 | Auto-remediation | DG-03 UC-12, DG-05 | Đã triển khai |
| UC-07 | Xem job | DG-03 UC-04 | Đã triển khai |
| UC-08 | Request MEDIUM hoặc HIGH | DG-03 UC-06, UC-07 | Đã triển khai |
| UC-09 | Approve hoặc reject | DG-03 UC-08, DG-06 | Đã triển khai |
| UC-10 | Quản lý incident | DG-07 | Tuần 10 đối với acknowledge và close |
| UC-11 | SYSTEM cập nhật incident | DG-07 | Đã triển khai cho resolve và cờ lỗi |
| UC-12 | Email | DG-03 UC-14, DG-06 | Đã triển khai |
| UC-13 | Audit | DG-03 UC-09 | Đã triển khai |
| UC-14 | Đăng xuất | DG-03 | Đã triển khai |

DG-03 đánh số use case theo actor và quyền. SRS đánh số theo nghiệp vụ. Hai bộ ID cùng mô tả một Portal; RTM này là chỗ đối chiếu, không đổi mã đã dùng trong từng file.

## 4. Non-functional Requirements

| ID | Thiết kế liên quan | Ghi chú |
|---|---|---|
| NFR-PER-01 đến NFR-PER-03 | SDD 18 | Ngưỡng đo khi nghiệm thu, không suy ra từ sơ đồ. |
| NFR-REL-01 đến NFR-REL-05 | SDD 9, 14, 18 | Cần số liệu vận hành riêng. |
| NFR-SEC-01 đến NFR-SEC-07 | SDD 13, 10, 11 | Đối chiếu test RBAC, approval và verification. |
| NFR-MNT-01, NFR-MNT-02 | Runbook và bộ tài liệu này | Runbook nằm ở tài liệu vận hành, không thay SRS. |
| NFR-TRC-01 | SDD 15, DG-04, DG-06 | Audit approval và remediation đã có trường truy vết. |
| NFR-TRC-02 | DG-04, DG-07 | Incident kiểm thử đã nối alert, server và job. Màn hình lịch sử đầy đủ thuộc Tuần 10. |

## 5. Sơ đồ

| Sơ đồ | Yêu cầu chính |
|---|---|
| DG-01 System Architecture | FR-MON, FR-ALT, FR-AUTO |
| DG-02 Network Topology | FR-MON, NFR-SEC-06 |
| DG-03 Use Case | FR-AUTH, RULE-01 đến RULE-04 |
| DG-04 Database ERD | FR-JOB, FR-APR, FR-INC, FR-AUD |
| DG-05 Remediation Sequence | FR-MAN, FR-AUTO, RULE-07 đến RULE-12 |
| DG-06 Approval Workflow | FR-APR, RULE-13, RULE-14 |
| DG-07 Incident State | FR-INC, RULE-15, RULE-16 |
| DG-08 Deployment | FR-MON-06, FR-NOT-01, vị trí Flask và SQLite |
