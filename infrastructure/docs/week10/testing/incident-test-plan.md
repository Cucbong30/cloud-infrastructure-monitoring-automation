# Week 10 – Incident Integration Test Plan

## 1. Mục đích

Xây dựng kế hoạch kiểm thử tích hợp Incident Management Workflow giữa Infrastructure và Application.

Đảm bảo hệ thống có khả năng phát hiện, ghi nhận, xử lý, xác minh và quản lý Incident trong môi trường Hybrid Cloud.

## 2. Phạm vi kiểm thử

- Incident Detection.
- Incident Creation.
- Incident Lifecycle.
- Alert and Incident Mapping.
- Remediation Job Mapping.
- Auto Remediation.
- Manual Remediation.
- Execution Failure Handling.
- Verification Failure Handling.
- Management Pre-check.
- Recurring Incident.
- RBAC and Audit Trail.

## 3. Điều kiện trước khi kiểm thử

| Requirement | Status |
|---|---|
| Infrastructure Baseline | PASS |
| Monitoring Services | PASS |
| Prometheus Targets | 6/6 UP |
| Ansible Connectivity | PASS |
| Service Verification Baseline | PASS |
| Management Pre-check | PASS |
| Incident Handling Runbook | Prepared |
| Application Incident Management | Pending Validation |
| Incident and Job Integration | Pending Validation |

Không thực hiện Integration Testing khi các thành phần bắt buộc chưa sẵn sàng.

## 4. Test Environment

| Target | Environment | Service |
|---|---|---|
| MON01 | On-premises Linux | Monitoring and Ansible |
| WEB01 | On-premises Linux | Nginx |
| APP01 | On-premises Linux | Docker Container |
| WIN01 | On-premises Windows | Windows Exporter |
| AZURE01 | Microsoft Azure | Nginx |

## 5. Test Case Summary

| Test ID | Test Scenario | Priority | Status |
|---|---|---|---|
| TC01 | Incident Creation | High | Not Tested |
| TC02 | Remediation Success | High | Not Tested |
| TC03 | Execution Failed | High | Not Tested |
| TC04 | Verification Failed | High | Not Tested |
| TC05 | Manual Handling | High | Not Tested |
| TC06 | Recurring Incident | Medium | Not Tested |
| TC07 | RBAC and Audit Trail | High | Not Tested |
| TC08 | Management Blocked | High | Not Tested |

TC08 được đề xuất bổ sung để kiểm chứng Management Pre-check trong Incident Workflow.

## 6. Detailed Test Cases

### TC01 – Incident Creation

**Objective:** Kiểm tra khả năng tạo Incident khi phát hiện sự cố.

**Proposed Target:** WIN01.

**Test Steps:**

1. Xác nhận Windows Exporter đang hoạt động.
2. Dừng Windows Exporter.
3. Kiểm tra Prometheus Target và InstanceDown Alert.
4. Kiểm tra Incident được tạo trên Portal.
5. Kiểm tra thông tin Incident và Detection Source.

**Expected Results:**

- Prometheus phát hiện target không thể scrape metrics.
- Incident được tạo với trạng thái OPEN.
- Target, Severity và Timestamp được ghi nhận.
- Incident được liên kết với Alert tương ứng.
- Không tạo Incident trùng lặp cho cùng một sự cố đang hoạt động.

**Status:** Not Tested.

### TC02 – Remediation Success

**Objective:** Kiểm tra toàn bộ quy trình remediation thành công và xác minh dịch vụ phục hồi.

**Proposed Target:** WEB01.

**Remediation Action:** restart_nginx.

**Test Steps:**

1. Kiểm tra Nginx đang hoạt động.
2. Dừng Nginx.
3. Xác nhận endpoint HTTP không khả dụng.
4. Kiểm tra cơ chế phát hiện sự cố.
5. Thực hiện Auto Remediation nếu đủ điều kiện.
6. Kiểm tra Ansible Execution Result.
7. Kiểm tra HTTP endpoint sau remediation.
8. Kiểm tra Incident Status và Job Mapping.

**Expected Results:**

- Management Pre-check thành công.
- Remediation Job được liên kết với Incident.
- Ansible thực thi thành công.
- HTTP endpoint trả về HTTP 200.
- Remediation Result là SUCCESS.
- Incident được chuyển sang RESOLVED sau khi verification thành công.
- Audit Trail ghi nhận actor SYSTEM nếu sử dụng Auto Remediation.

**Note:**

InstanceDown không trực tiếp phát hiện Nginx bị dừng khi Node Exporter vẫn hoạt động.

Cần xác nhận Service Probe phía Application trước khi thực hiện test case này.

**Status:** Not Tested.

### TC03 – Execution Failed

**Objective:** Kiểm tra Incident Handling khi Ansible Execution thất bại.

**Proposed Target:** WEB01 hoặc APP01.

**Test Steps:**

1. Chuẩn bị tình huống execution failure có kiểm soát.
2. Đảm bảo Management Pre-check thành công.
3. Thực hiện Auto Remediation.
4. Kiểm tra Ansible Execution Result.
5. Kiểm tra cơ chế Auto Retry.
6. Kiểm tra Incident Status và Audit Trail.
7. Khôi phục môi trường kiểm thử.

**Expected Results:**

- Execution Failure được ghi nhận.
- Auto Retry tối đa một lần nếu đủ điều kiện.
- Không thực thi vô hạn.
- Nếu execution cuối cùng vẫn thất bại, Incident không được chuyển sang RESOLVED.
- Failure Reason được lưu trong Audit Trail.
- Người vận hành có thể tiếp tục Manual Handling.

Không sửa đổi Production Playbook để tạo lỗi.

**Status:** Not Tested.

### TC04 – Verification Failed

**Objective:** Kiểm tra trường hợp Ansible Execution thành công nhưng dịch vụ chưa được xác minh phục hồi.

**Proposed Target:** WEB01 hoặc APP01.

**Test Steps:**

1. Chuẩn bị tình huống verification failure có kiểm soát.
2. Thực hiện remediation.
3. Xác nhận Ansible Execution thành công.
4. Kiểm tra Service Verification.
5. Kiểm tra Remediation Result.
6. Kiểm tra Incident Status.
7. Khôi phục điều kiện verification bình thường.

**Expected Results:**

- Execution Result thành công.
- Verification Result thất bại.
- Remediation Result là VERIFICATION_FAILED.
- Không tự động retry.
- Không tự động chuyển Incident sang RESOLVED.
- Failure Reason được ghi nhận.

**Status:** Not Tested.

### TC05 – Manual Handling

**Objective:** Kiểm tra khả năng xử lý Incident thủ công theo quyền của người vận hành.

**Proposed Target:** APP01.

**Remediation Action:** restart_container.

**Test Steps:**

1. Dừng Application Container.
2. Xác nhận dịch vụ không khả dụng.
3. Tạo hoặc tiếp nhận Incident.
4. Đăng nhập bằng tài khoản Operator.
5. Acknowledge Incident.
6. Thực hiện Manual Remediation.
7. Kiểm tra Service Verification.
8. Kiểm tra Incident Lifecycle và Audit Trail.
9. Đóng Incident bằng tài khoản có quyền phù hợp.

**Expected Results:**

- Người vận hành có thể tiếp nhận Incident.
- Manual Remediation tuân thủ RBAC.
- Remediation Job được liên kết với Incident.
- Actor là tài khoản người thực hiện.
- HTTP endpoint phục hồi.
- Incident được Resolve và Close theo quyền được cấp.

**Status:** Not Tested.

### TC06 – Recurring Incident

**Objective:** Kiểm tra khả năng quản lý sự cố tái diễn sau khi Incident trước đã được xử lý.

**Proposed Target:** WIN01.

**Test Steps:**

1. Tạo sự cố Windows Exporter.
2. Thực hiện remediation và xác minh phục hồi.
3. Kiểm tra Incident đã được Resolve hoặc Close.
4. Tạo lại sự cố trong thời gian cooldown.
5. Kiểm tra Incident và Remediation History.
6. Kiểm tra hành vi hệ thống sau khi cooldown kết thúc.

**Expected Results:**

- Hệ thống nhận diện sự cố tái diễn.
- Không ghi nhận trùng lặp cho cùng một sự cố đang hoạt động.
- Auto Remediation tuân thủ cooldown 120 giây.
- Không thực thi remediation ngoài điều kiện cho phép.
- Lịch sử Incident trước đó vẫn được lưu giữ.
- Sự cố tái diễn được quản lý theo Incident Lifecycle.

Cơ chế tạo Incident mới hoặc liên kết với Incident cũ cần được thống nhất với Application.

**Status:** Not Tested.

### TC07 – RBAC and Audit Trail

**Objective:** Kiểm tra quyền xử lý Incident và khả năng truy vết thao tác.

**Test Accounts:**

- Admin.
- Operator.
- Viewer.

**Test Steps:**

1. Đăng nhập bằng từng Role.
2. Kiểm tra quyền xem Incident.
3. Kiểm tra quyền tiếp nhận và cập nhật Incident.
4. Kiểm tra quyền thực hiện LOW Remediation.
5. Kiểm tra MEDIUM Approval Workflow.
6. Kiểm tra giới hạn quyền đối với HIGH Remediation.
7. Kiểm tra Audit Trail cho các thao tác.

**Expected Results:**

- Viewer chỉ có quyền xem.
- Operator được thực hiện LOW Action theo quyền.
- Operator có thể gửi yêu cầu MEDIUM Action.
- MEDIUM Action yêu cầu Admin Approval.
- HIGH Action chỉ dành cho Admin và tuân thủ Approval Workflow.
- Các thao tác không có quyền bị từ chối.
- Audit Trail ghi nhận Actor, Action, Timestamp và Result.

Không bắt buộc thực thi HIGH Action thực tế chỉ để kiểm tra quyền.

**Status:** Not Tested.

### TC08 – Management Blocked

**Objective:** Kiểm tra khả năng ngăn chặn remediation khi Management Channel không khả dụng.

**Proposed Target:** WEB01.

**Test Steps:**

1. Kiểm tra SSH Port 22 đang khả dụng.
2. Đảm bảo có phương thức truy cập khôi phục ngoài SSH.
3. Tạo tình huống SSH bị chặn có kiểm soát.
4. Thực hiện yêu cầu remediation.
5. Kiểm tra Management Pre-check.
6. Kiểm tra Remediation Result.
7. Kiểm tra Incident Status và Audit Trail.
8. Khôi phục SSH Connectivity.
9. Kiểm tra lại Ansible Connectivity.

**Expected Results:**

- Management Pre-check phát hiện kết nối không khả dụng.
- Remediation Result là MANAGEMENT_BLOCKED.
- Không thực thi Ansible Playbook.
- Không sử dụng ngân sách retry.
- Incident không được chuyển sang RESOLVED.
- Failure Reason được ghi nhận.
- Management Channel hoạt động bình thường sau khi khôi phục.

**Status:** Not Tested.

## 7. Evidence Requirements

Mỗi test case cần lưu các minh chứng phù hợp:

- Trạng thái dịch vụ trước khi tạo lỗi.
- Trạng thái dịch vụ khi xảy ra sự cố.
- Alert hoặc Detection Source.
- Incident Status.
- Remediation Job Result.
- Verification Result.
- Audit Trail.
- Trạng thái sau khi khôi phục.

Chỉ lưu minh chứng cần thiết để chứng minh kết quả kiểm thử.

Screenshot bắt đầu từ số 11 và được phân loại theo từng Test Case.

Tên file và đường dẫn ảnh sẽ được xác định khi thực hiện kiểm thử thực tế.

## 8. Test Execution Rules

- Kiểm thử từng Test Case theo thứ tự.
- Không tạo đồng thời nhiều sự cố ngoài phạm vi kiểm thử.
- Khôi phục dịch vụ về trạng thái bình thường sau mỗi Test Case.
- Không thay đổi Production Playbook để tạo lỗi.
- Không vô hiệu hóa RBAC hoặc Approval Policy.
- Không thay đổi thông số Retry, Cooldown hoặc Timeout để ép Test Case thành công.
- Không ghi nhận PASS khi chưa có kết quả kiểm thử.
- Ghi nhận nguyên nhân và hướng xử lý nếu Test Case thất bại.

## 9. Acceptance Criteria

Incident Management Integration được đánh giá thành công khi:

- Incident được tạo từ nguồn phát hiện hợp lệ.
- Incident và Remediation Job được liên kết chính xác.
- Incident Lifecycle hoạt động đúng quy trình.
- Auto và Manual Remediation tuân thủ chính sách.
- Service Verification xác nhận trạng thái phục hồi.
- Không tự động Resolve Incident khi remediation thất bại.
- Management Blocked ngăn chặn việc thực thi playbook.
- RBAC và Audit Trail hoạt động đúng yêu cầu.
- Không ảnh hưởng đến các chức năng đã triển khai từ Tuần 1 đến Tuần 9.

## 10. Test Execution Status

| Metric | Result |
|---|---|
| Total Planned Test Cases | 8 |
| Executed | 0 |
| Passed | 0 |
| Failed | 0 |
| Not Tested | 8 |

## 11. Kết luận

Incident Integration Test Plan đã được chuẩn bị cho quá trình kiểm thử phối hợp giữa Infrastructure và Application.

Các Test Case được xây dựng dựa trên Infrastructure Baseline, Incident Scenario Mapping, Service Verification Baseline, Management Pre-check và Incident Handling Runbook.

Kết quả kiểm thử thực tế sẽ được ghi nhận riêng sau khi Application sẵn sàng.

**Test Plan Status: Prepared**

**Integration Testing: Pending**

**Next Step: Failure and Recovery Preparation.**
