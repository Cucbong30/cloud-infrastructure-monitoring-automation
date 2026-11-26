# TUẦN 09 – Approval Workflow & Risk-based Remediation

## 1. Mục tiêu trong tuần

Mở rộng hệ thống remediation theo mức độ rủi ro của từng action. Các action LOW được thực thi trực tiếp, trong khi MEDIUM và HIGH phải được Admin phê duyệt trước khi chạy Ansible. Kiểm thử các trường hợp Approved, Rejected, Unauthorized và Timeout.

## 2. Phân công công việc

### 2.1. Đỗ Đăng Thái Bảo – Infrastructure / System / Cloud

| STT | Công việc được phân công | Kết quả thực hiện |
|---|---|---|
| 1 | Xây dựng Action Risk Matrix. | Phân loại các remediation action theo ba mức LOW, MEDIUM và HIGH. |
| 2 | Xây dựng Approval Policy và Action Mapping. | Xác định điều kiện thực thi, quyền phê duyệt và verification tương ứng với từng action. |
| 3 | Xây dựng playbook cho action MEDIUM và HIGH. | Hoàn thành playbook restart Docker Service trên APP01 và reboot AZURE01. |
| 4 | Kiểm thử LOW Risk. | Restart Nginx trên WEB01 thành công mà không cần approval. |
| 5 | Kiểm thử MEDIUM Risk. | Restart Docker Service thành công khi được duyệt. Request bị từ chối không thực thi Ansible. |
| 6 | Kiểm thử HIGH Risk. | Reboot AZURE01 thành công khi được duyệt, xác nhận Boot ID thay đổi, SSH và HTTP hoạt động trở lại. Request bị từ chối không thực hiện reboot. |
| 7 | Kiểm thử Unauthorized và Timeout. | Xác nhận action không được thực thi khi người dùng không đủ quyền. Timeout đã được kiểm thử phía Application, cần bổ sung đối chiếu Infrastructure. |
| 8 | Cập nhật tài liệu và kết quả kiểm thử. | Hoàn thành tài liệu Risk Matrix, Approval Policy, Playbook và các kịch bản kiểm thử. |

**Trạng thái: Hoàn thành các nội dung chính.**

### 2.2. Nguyễn Thế Gia Bảo – Application / Integration

| STT | Công việc được phân công | Kết quả thực hiện |
|---|---|---|
| 1 | Tích hợp Risk Level vào remediation action. | LOW thực thi trực tiếp, MEDIUM và HIGH yêu cầu approval. |
| 2 | Xây dựng Approval Workflow. | Portal hỗ trợ tạo yêu cầu, phê duyệt, từ chối và tự động hết hạn sau 5 phút. |
| 3 | Kiểm soát quyền theo RBAC. | Operator được yêu cầu action MEDIUM. Chỉ Admin được yêu cầu action HIGH và phê duyệt các request. |
| 4 | Kiểm soát thực thi Ansible theo Approval. | Chỉ tạo execution job khi request được duyệt. Rejected và Expired không gọi playbook. |
| 5 | Xây dựng Approval Queue và History. | Hiển thị các yêu cầu đang chờ, đã duyệt, bị từ chối và hết hạn. |
| 6 | Tích hợp Audit Trail và Email Notification. | Ghi nhận người yêu cầu, người phê duyệt, quyết định, thời gian và kết quả thực thi. |
| 7 | Kiểm thử Approval Workflow. | Kiểm tra LOW, MEDIUM, HIGH và các trường hợp Approved, Rejected, Unauthorized, Timeout. |
| 8 | Rà soát kết quả còn thiếu từ Tuần 8. | Xác nhận Incident 46 đã Resolved, job 71 và job 72 có trạng thái SUCCESS trong database. |

**Trạng thái: Hoàn thành các chức năng chính, còn một số hình ảnh minh chứng cần bổ sung.**

## 3. Công việc phối hợp giữa hai thành viên

| Công việc | Infrastructure | Application |
|---|---|---|
| Action Risk Matrix | Xác định mức rủi ro và điều kiện thực thi từng action. | Áp dụng Risk Level và Approval Policy trên Portal. |
| LOW Risk | Kiểm tra restart Nginx trên WEB01. | Thực thi trực tiếp không qua approval. |
| MEDIUM Risk | Kiểm tra Docker Service và Container trên APP01. | Kiểm thử luồng yêu cầu, phê duyệt và từ chối. |
| HIGH Risk | Kiểm tra reboot, Boot ID, SSH và HTTP trên AZURE01. | Kiểm soát quyền và thực thi sau khi được duyệt. |
| Unauthorized và Timeout | Kiểm tra action không được thực thi trái phép. | Kiểm tra RBAC, thời hạn approval và trạng thái NOT_RUN. |

## 4. Kết quả cuối tuần

Hệ thống đã hỗ trợ Approval Workflow theo ba mức rủi ro LOW, MEDIUM và HIGH. Các action MEDIUM và HIGH chỉ được thực thi sau khi có phê duyệt từ Admin, đồng thời vẫn tuân thủ Pre-check và Verification.

Incident 46 đã được xác nhận Resolved. Còn thiếu hình ảnh Job Detail của job 71, job 72, hình ảnh backend trả 403 và minh chứng Timeout riêng phía Infrastructure.

Tuần 10 sẽ mở rộng sang Incident Management Workflow, tập trung quản lý vòng đời sự cố và liên kết Incident với Alert, Automation Job và kết quả remediation.
``
