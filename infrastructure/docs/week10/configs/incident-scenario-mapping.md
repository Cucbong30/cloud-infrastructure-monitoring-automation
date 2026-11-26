# Week 10 – Incident Scenario Mapping

## 1. Mục đích

Xác định mối liên hệ giữa sự cố hạ tầng, nguồn phát hiện,
Remediation Action và Verification Result để phục vụ
tích hợp Incident Management Workflow.

Tái sử dụng các Alert Rule, Remediation Policy và
Ansible Playbook đã triển khai từ những tuần trước.

## 2. Kiểm tra Alert Rule hiện tại

Thực hiện kiểm tra trên MON01 vào ngày 26/11/2026.

| Thuộc tính | Giá trị |
|---|---|
| Alert Name | InstanceDown |
| Expression | up == 0 |
| Severity | critical |
| Total Alert Rules | 1 |
| Prometheus Targets | 6/6 UP |

Rule InstanceDown phát hiện các target không thể
thu thập metrics.

Các sự cố ở cấp độ dịch vụ như Nginx hoặc Docker
không được phát hiện trực tiếp bởi rule này.

### Minh chứng

![Incident Scenario Mapping](../screenshots/08-incident-scenario-mapping.png)

## 3. Incident Scenario Mapping

| Target | Failure Scenario | Remediation Action | Risk | Verification |
|---|---|---|---|---|
| WEB01 | Nginx Down | restart_nginx | LOW | HTTP 80 |
| APP01 | Container Down | restart_container | LOW | HTTP 8080 |
| WIN01 | Windows Exporter Down | restart_windows_exporter | LOW | HTTP 9182 |
| AZURE01 | Nginx Down | restart_nginx | LOW | HTTP 80 |
| APP01 | Docker Service Down | restart_docker_service | MEDIUM | Docker Service và HTTP 8080 |
| AZURE01 | Reboot Request | reboot_server | HIGH | Boot ID, SSH và HTTP |

Reboot Request là tác vụ vận hành cần phê duyệt,
không mặc định là một Incident phát sinh từ Alert.

## 4. Detection Source

| Detection Source | Mục đích | Trạng thái |
|---|---|---|
| Prometheus InstanceDown | Phát hiện exporter hoặc scrape target không khả dụng | Đã xác nhận |
| Portal Service Probe | Phát hiện lỗi dịch vụ | Cần đối chiếu với Application |
| Manual Request | Yêu cầu xử lý thủ công | Tái sử dụng |
| Approval Workflow | Kiểm soát action MEDIUM và HIGH | Tái sử dụng |

Không mặc định InstanceDown luôn đồng nghĩa với
máy chủ hoặc dịch vụ ứng dụng bị dừng.

## 5. Remediation Policy

Giữ nguyên các chính sách đã triển khai:

- Auto-remediation chỉ áp dụng cho action LOW
  đủ điều kiện và nằm trong allow-list.
- MEDIUM và HIGH phải được phê duyệt.
- Approval Timeout: 5 phút.
- Cooldown: 120 giây sau SUCCESS.
- Auto Retry: tối đa một lần khi Execution Failed.
- Manual Remediation không tự động retry.
- Verification Failed không tự động retry.
- Management Blocked không thực thi playbook.
- Không thực thi trùng target và action đang active.

## 6. Incident Resolution Mapping

| Remediation Result | Expected Incident Behavior |
|---|---|
| SUCCESS | Tự động Resolve khi verification thành công |
| EXECUTION_FAILED | Giữ Incident chưa được Resolve |
| VERIFICATION_FAILED | Không tự động Resolve |
| MANAGEMENT_BLOCKED | Không thực thi playbook, không Resolve |
| MANUAL_REQUIRED | Yêu cầu người vận hành xử lý |
| DUPLICATE_SKIPPED | Không tạo thêm lần thực thi trùng |
| Manual Recovery | Cho phép Resolve sau khi xác nhận dịch vụ phục hồi |

Đây là kết quả mong đợi phục vụ Integration Testing,
chưa phải kết quả kiểm thử thực tế của Tuần 10.

## 7. Kết luận

Đã xác định các tình huống sự cố, Remediation Action
và phương pháp Verification tương ứng.

Không bổ sung Alert Rule, Inventory hoặc Ansible
Playbook mới trong hạng mục này.

Incident Scenario Mapping phía Infrastructure đã được
chuẩn bị để phối hợp kiểm thử với Application.

**Status: Infrastructure Mapping Completed**

**Integration Validation: Pending**

**Next Step: Service Verification Baseline.**
