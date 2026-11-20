# Week 9 – HIGH Risk Remediation Testing

## 1. Mục tiêu

Kiểm thử cơ chế Approval đối với remediation action có Risk Level = HIGH, bảo đảm hệ thống chỉ thực thi sau khi được Admin phê duyệt và không thực thi khi request bị từ chối.

## 2. Action Definition

| Thuộc tính | Giá trị |
|---|---|
| Target | AZURE01 – 20.243.24.91 |
| Action | `reboot_server` |
| Risk Level | HIGH |
| Approval Required | Yes |
| Requester | Admin |
| Approver | Admin khác |
| Playbook | `reboot-azure01.yml` |
| Verification | Boot ID, Uptime, SSH, HTTP |

**Approval Policy:**
- `PENDING_APPROVAL`: Không thực thi Ansible.
- `APPROVED`: Cho phép reboot server.
- `REJECTED`: Không thực thi.
- `APPROVAL_EXPIRED`: Không thực thi.

## 3. TC04 – HIGH Approved

**Mục đích:** Xác nhận hệ thống thực hiện reboot AZURE01 sau khi Admin phê duyệt.

### Các bước kiểm thử

**Bước 1 – Pre-check**

Trên MON01:

```bash
ansible AZURE01 -m ping
ansible AZURE01 -m command -a "cat /proc/sys/kernel/random/boot_id"
ansible AZURE01 -m command -a "uptime -s"
curl -I --max-time 5 http://20.243.24.91
```

Ghi nhận Boot ID, thời gian khởi động và trạng thái HTTP trước reboot.

**Bước 2 – Request Approval**

Admin tạo request trên Portal:

- Target: AZURE01
- Action: `reboot_server`
- Risk: HIGH
- Mode: MANUAL

Request chuyển sang `PENDING_APPROVAL`. Chưa được thực thi Ansible.

**Bước 3 – Admin Approve**

Admin khác phê duyệt request trên Portal.

Backend tự động gọi Ansible trên MON01 để thực thi playbook `reboot-azure01.yml`.

**Bước 4 – Verification**

Sau khi AZURE01 khởi động lại, trên MON01:

```bash
ansible AZURE01 -m ping
ansible AZURE01 -m command -a "cat /proc/sys/kernel/random/boot_id"
ansible AZURE01 -m command -a "uptime -s"
curl -I --max-time 5 http://20.243.24.91
```

### Điều kiện PASS

- Approval Status = `APPROVED`.
- Ansible chỉ thực thi sau khi được duyệt.
- Boot ID thay đổi so với trước reboot.
- Boot Time được cập nhật.
- AZURE01 kết nối SSH/Ansible trở lại.
- HTTP hoạt động bình thường.
- Portal ghi nhận Job SUCCESS.

## 4. TC05 – HIGH Rejected

**Mục đích:** Xác nhận hệ thống không reboot AZURE01 khi Admin từ chối request.

### Các bước kiểm thử

1. Tạo request mới cho `AZURE01 → reboot_server`.
2. Xác nhận request ở trạng thái `PENDING_APPROVAL`.
3. Admin thực hiện Reject trên Portal.
4. Kiểm tra Approval Status chuyển sang `REJECTED`.
5. Xác nhận không có Ansible execution.
6. Kiểm tra Boot ID của AZURE01 không thay đổi do request bị từ chối.

### Điều kiện PASS

- Approval Status = `REJECTED`.
- Không thực thi playbook `reboot-azure01.yml`.
- AZURE01 không bị reboot bởi request này.
- Audit Log ghi nhận quyết định Reject.

## 5. Test Evidence

Screenshots lưu tại:

`infrastructure/docs/week09/screenshots/risk-matrix/high-risk/`

| File | Nội dung |
|---|---|
| `01-high-approved-precheck.png` | Trạng thái AZURE01 trước reboot |
| `02-high-approved-recovery.png` | Boot ID thay đổi và HTTP phục hồi |
| `03-high-rejected-no-execution.png` | Không thực thi reboot khi Reject |

Evidence Approval và Job Detail do nhóm Application quản lý.

## 6. Expected Results

| Test Case | Expected Result |
|---|---|
| TC04 – HIGH Approved | Approved → Reboot → Verification PASS |
| TC05 – HIGH Rejected | Rejected → No Execution |

**Kết quả kiểm thử:** TC04 PASS, TC05 PASS.
