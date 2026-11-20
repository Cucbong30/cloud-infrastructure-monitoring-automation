# Week 9 – MEDIUM Risk Remediation Testing

## 1. Mục tiêu

Kiểm thử cơ chế Approval đối với các remediation action có Risk Level = MEDIUM, bảo đảm hệ thống chỉ thực thi Ansible khi yêu cầu đã được phê duyệt.

## 2. Action Definition

| Thuộc tính | Giá trị |
|---|---|
| Target | APP01 – 192.168.10.12 |
| Action | `restart_docker_service` |
| Risk Level | MEDIUM |
| Approval Required | Yes |
| Requester | Operator |
| Approver | Admin |
| Playbook | `restart-docker-service.yml` |
| Verification | Docker Service, app01-web, HTTP 8080 |

**Approval Policy:**
- `PENDING_APPROVAL`: Không thực thi Ansible.
- `APPROVED`: Cho phép thực thi remediation.
- `REJECTED`: Không thực thi remediation.
- `APPROVAL_EXPIRED`: Không thực thi remediation.

## 3. TC02 – MEDIUM Approved

**Mục đích:** Kiểm tra hệ thống tự động khôi phục dịch vụ sau khi Admin phê duyệt.

### Các bước thực hiện

**Bước 1 – Pre-check**

Trên MON01, kiểm tra kết nối và quyền Ansible:

```bash
ansible APP01 -m ping
ansible APP01 -b -m command -a "id -u"
```

Trên APP01, kiểm tra trạng thái ban đầu:

```bash
systemctl is-active docker.service
sudo docker ps
curl -I http://localhost:8080
```

**Bước 2 – Tạo sự cố thực tế**

Trên APP01:

```bash
sudo systemctl stop docker.service docker.socket
systemctl is-active docker.service docker.socket
```

Xác nhận Docker đã dừng.

**Bước 3 – Request Approval**

Operator tạo request trên Portal:

- Target: APP01
- Action: `restart_docker_service`
- Risk: MEDIUM
- Mode: MANUAL

Request phải chuyển sang `PENDING_APPROVAL` và chưa được thực thi.

**Bước 4 – Admin Approve**

Admin mở Approval Queue và phê duyệt request.

Backend tự động gọi Ansible trên MON01 để thực thi playbook `restart-docker-service.yml`.

**Bước 5 – Verification**

Trên APP01:

```bash
systemctl is-active docker.service docker.socket
sudo docker ps
curl -I http://localhost:8080
```

### Điều kiện PASS

- Request được Admin phê duyệt.
- Ansible chỉ thực thi sau khi Approved.
- Docker Service hoạt động trở lại.
- Container `app01-web` đang chạy.
- HTTP 8080 phản hồi thành công.
- Portal ghi nhận Job SUCCESS và Verification PASS.

## 4. TC03 – MEDIUM Rejected

**Mục đích:** Kiểm tra hệ thống ngăn chặn remediation khi Admin từ chối yêu cầu.

### Các bước thực hiện

1. Operator tạo request mới với action `restart_docker_service` trên APP01.
2. Xác nhận trạng thái `PENDING_APPROVAL`.
3. Admin mở Approval Queue và chọn Reject.
4. Kiểm tra Approval Status chuyển sang `REJECTED`.
5. Kiểm tra Job History và Audit Log để xác nhận không có Ansible execution từ request này.

### Điều kiện PASS

- Approval Status = `REJECTED`.
- Không có Ansible playbook được thực thi.
- Không phát sinh remediation execution từ request bị từ chối.
- Audit Log ghi nhận quyết định Reject.

## 5. Test Evidence

Screenshots được lưu tại:

`infrastructure/docs/week09/screenshots/medium-risk/`

| File | Nội dung |
|---|---|
| `01-medium-approved-precheck.png` | Kiểm tra trạng thái ban đầu |
| `02-medium-approved-docker-down.png` | Tạo lỗi Docker Down |
| `03-medium-approved-recovery.png` | Kiểm tra phục hồi sau Approved |
| `04-medium-rejected-no-execution.png` | Xác nhận không thực thi khi Rejected |

## 6. Expected Results

| Test Case | Expected Result |
|---|---|
| TC02 – MEDIUM Approved | Approval → Ansible Execution → Service Recovery |
| TC03 – MEDIUM Rejected | Rejected → No Execution |

Hai test case được sử dụng để xác minh cơ chế kiểm soát remediation theo MEDIUM Risk Approval Policy.
