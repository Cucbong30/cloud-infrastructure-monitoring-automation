# Week 10 – Incident Handling Runbook

## 1. Mục đích

Chuẩn hóa quy trình tiếp nhận, phân tích, xử lý và xác minh sự cố trong môi trường Hybrid Cloud.

Đảm bảo Incident được xử lý có kiểm soát, đúng quyền hạn và có khả năng truy vết thông qua Audit Trail.

## 2. Phạm vi áp dụng

| Target | Environment | Service |
|---|---|---|
| WEB01 | On-premises Linux | Nginx |
| APP01 | On-premises Linux | Docker / Application Container |
| WIN01 | On-premises Windows | Windows Exporter |
| AZURE01 | Microsoft Azure | Nginx / Virtual Machine |

MON01 tiếp tục đóng vai trò Monitoring Server và Ansible Control Node.

## 3. Incident Detection

Incident có thể được phát hiện thông qua:

- Prometheus Alert.
- Service Probe phía Application.
- Manual Incident Reporting.

Alert Rule hiện tại của Prometheus:

| Attribute | Value |
|---|---|
| Alert Name | InstanceDown |
| Expression | up == 0 |
| Severity | critical |

InstanceDown chỉ phát hiện target không thể scrape metrics, không trực tiếp phát hiện tất cả sự cố ở cấp độ dịch vụ.

Khả năng tiếp nhận Incident từ Service Probe và Manual Reporting cần được xác nhận trong Integration Testing với Application.

## 4. Incident Lifecycle

| Status | Description |
|---|---|
| OPEN | Incident được tạo và ghi nhận |
| ACKNOWLEDGED | Người vận hành xác nhận đã tiếp nhận |
| IN_PROGRESS | Incident đang được xử lý |
| RESOLVED | Sự cố đã được xử lý và xác minh phục hồi |
| CLOSED | Incident được kiểm tra và đóng |

Luồng xử lý dự kiến:

```text
OPEN
  |
  v
ACKNOWLEDGED
  |
  v
IN_PROGRESS
  |
  v
RESOLVED
  |
  v
CLOSED
```

Incident không được tự động chuyển sang RESOLVED chỉ vì Ansible Playbook thực thi thành công.

## 5. Remediation Action Mapping

| Target | Action | Risk Level |
|---|---|---|
| WEB01 | restart_nginx | LOW |
| APP01 | restart_container | LOW |
| WIN01 | restart_windows_exporter | LOW |
| AZURE01 | restart_nginx | LOW |
| APP01 | restart_docker_service | MEDIUM |
| AZURE01 | reboot_server | HIGH |

Chỉ sử dụng các remediation action đã được định nghĩa từ những tuần trước.

Không bổ sung action hoặc playbook mới trong phạm vi Incident Management.

## 6. Incident Handling Procedure

### Step 1 – Detect Incident

- Xác định nguồn phát hiện sự cố.
- Ghi nhận target, service và thời điểm phát hiện.
- Liên kết Incident với Alert hoặc nguồn phát hiện tương ứng.
- Kiểm tra Incident đang tồn tại để tránh ghi nhận trùng lặp.

### Step 2 – Analyze Incident

- Kiểm tra trạng thái target trên Prometheus.
- Kiểm tra trạng thái dịch vụ bị ảnh hưởng.
- Xác định remediation action phù hợp.
- Xác định Risk Level của action.
- Kiểm tra quyền thực hiện remediation.

### Step 3 – Management Pre-check

Kiểm tra khả năng kết nối từ MON01 đến target.

| Target | Protocol | Port |
|---|---|---|
| WEB01 | SSH | 22 |
| APP01 | SSH | 22 |
| WIN01 | WinRM | 5985 |
| AZURE01 | SSH | 22 |

Nếu Management Channel không khả dụng:

- Ghi nhận MANAGEMENT_BLOCKED.
- Không thực thi Ansible Playbook.
- Không sử dụng ngân sách retry.
- Giữ Incident ở trạng thái chưa được giải quyết.
- Chuyển sang quy trình kiểm tra thủ công.

### Step 4 – Select Remediation Mode

| Risk Level | Auto Remediation | Approval |
|---|---|---|
| LOW | Allowed for approved actions | Not required |
| MEDIUM | Not allowed | Admin approval required |
| HIGH | Not allowed | Admin approval required |

Auto Remediation chỉ được áp dụng cho các action LOW nằm trong Allow-list và đáp ứng các điều kiện kiểm soát.

Manual Remediation phải tuân thủ RBAC và Approval Workflow.

### Step 5 – Execute Remediation

- Kiểm tra Management Pre-check.
- Kiểm tra Risk Level và Approval Status.
- Kiểm tra remediation job đang thực thi.
- Kiểm tra cooldown đối với Auto Remediation.
- Thực thi Ansible Playbook tương ứng.
- Ghi nhận thời gian, actor và execution result.
- Liên kết Remediation Job với Incident.

Các điều kiện kiểm soát được tái sử dụng:

| Control | Policy |
|---|---|
| Execution Timeout | 5 minutes |
| Auto Retry | Maximum 1 retry |
| Auto Cooldown | 120 seconds after successful remediation |
| Manual Retry | No automatic retry |
| Verification Failed | No automatic retry |
| Management Blocked | No execution |
| Duplicate Active Job | Skip execution |

Auto Retry chỉ áp dụng cho Execution Failed khi đáp ứng điều kiện retry.

### Step 6 – Verify Recovery

Kiểm tra trạng thái dịch vụ sau remediation.

| Target | Verification Endpoint | Expected |
|---|---|---|
| WEB01 | http://192.168.10.11:80 | HTTP 200 |
| APP01 | http://192.168.10.12:8080 | HTTP 200 |
| WIN01 | http://192.168.10.13:9182/metrics | HTTP 200 |
| AZURE01 | http://20.243.24.91:80 | HTTP 200 |

Chỉ ghi nhận Remediation SUCCESS khi execution và verification đều thành công.

HTTP 200 xác nhận khả năng phản hồi của endpoint tại thời điểm kiểm tra, không thay thế kiểm tra đầy đủ chức năng nghiệp vụ.

### Step 7 – Update Incident Status

| Remediation Result | Incident Handling |
|---|---|
| SUCCESS | Cho phép chuyển sang RESOLVED |
| EXECUTION_FAILED | Giữ Incident chưa được giải quyết |
| VERIFICATION_FAILED | Giữ Incident chưa được giải quyết |
| MANAGEMENT_BLOCKED | Yêu cầu kiểm tra thủ công |
| APPROVAL_PENDING | Chờ phê duyệt |
| DUPLICATE_SKIPPED | Theo dõi remediation job hiện tại |

Không tự động Resolve Incident khi chưa xác minh dịch vụ phục hồi.

### Step 8 – Close Incident

Trước khi đóng Incident:

- Xác nhận dịch vụ đã phục hồi.
- Kiểm tra Remediation Job Result.
- Kiểm tra Incident Timeline.
- Kiểm tra Audit Trail.
- Ghi nhận kết quả xử lý cuối cùng.
- Thực hiện Close Incident theo quyền được cấp.

## 7. Failure Handling

### Execution Failed

- Kiểm tra Ansible output.
- Xác định nguyên nhân thực thi thất bại.
- Cho phép tối đa một lần Auto Retry nếu đủ điều kiện.
- Chuyển sang Manual Handling nếu vẫn thất bại.

### Verification Failed

- Kiểm tra trạng thái dịch vụ.
- Kiểm tra HTTP endpoint.
- Kiểm tra service log.
- Không tự động retry.
- Không tự động Resolve Incident.

### Management Blocked

- Kiểm tra kết nối mạng.
- Kiểm tra Firewall và Management Port.
- Kiểm tra SSH hoặc WinRM.
- Kiểm tra Ansible Connectivity.
- Chỉ thực hiện remediation sau khi management channel được khôi phục và đủ điều kiện thực thi.

### Recurring Incident

- Kiểm tra Incident và Remediation History.
- Kiểm tra cooldown.
- Kiểm tra sự cố có thực sự tái diễn sau khi đã phục hồi.
- Ghi nhận sự cố tái diễn theo cơ chế Incident Management phía Application.
- Không bỏ qua Risk Level và Approval Policy.

## 8. RBAC and Approval

| Role | Permission |
|---|---|
| Admin | Quản lý Incident, thực hiện remediation và phê duyệt action theo Risk Level |
| Operator | Xử lý Incident, thực hiện LOW action và gửi yêu cầu MEDIUM action |
| Viewer | Chỉ xem Incident, trạng thái và kết quả |

HIGH action chỉ dành cho Admin và phải tuân thủ Approval Workflow.

Auto Remediation sử dụng SYSTEM làm actor.

Manual Remediation ghi nhận tài khoản người thực hiện.

Quyền cụ thể đối với từng thao tác Incident Lifecycle cần được xác nhận trong Integration Testing.

## 9. Audit Trail Requirements

Các thông tin cần ghi nhận:

- Incident ID.
- Alert ID hoặc Detection Source.
- Target và Service.
- Incident Status.
- Remediation Job ID.
- Remediation Action.
- Remediation Mode.
- Risk Level.
- Actor.
- Approval Status.
- Execution Result.
- Verification Result.
- Timestamp.
- Failure Reason.

Không ghi plaintext credential hoặc thông tin xác thực nhạy cảm vào log.

## 10. Responsibility Mapping

| Component | Responsibility |
|---|---|
| Infrastructure | Monitoring, Connectivity, Ansible và Service Verification |
| Application | Incident Lifecycle, Portal, RBAC, Approval và Audit Trail |
| Integration | Alert Mapping, Job Mapping, Status Synchronization và End-to-End Validation |

Infrastructure chịu trách nhiệm xác minh trạng thái thực tế của target và dịch vụ.

Application chịu trách nhiệm quản lý Incident Lifecycle và hiển thị kết quả xử lý trên Portal.

## 11. Kết luận

Incident Handling Runbook được xây dựng dựa trên các thành phần và chính sách đã triển khai từ Tuần 1 đến Tuần 9.

Không thay đổi Infrastructure Architecture, Monitoring Configuration, Ansible Inventory hoặc Production Playbook.

Runbook là cơ sở để thực hiện Incident Management Integration Testing trong Tuần 10.

**Runbook Status: Prepared**

**Integration Validation: Pending**

**Next Step: Incident Integration Test Plan.**
