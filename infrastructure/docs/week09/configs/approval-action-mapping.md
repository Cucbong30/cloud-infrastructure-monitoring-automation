# Approval Action Mapping

## 1. Objective

Xác định action thực tế được sử dụng cho từng mức risk trong Approval Workflow của Week 9.

Mỗi action được map theo:

```text
Target
→ Service / Component
→ Action
→ Risk
→ Playbook
→ Management Pre-check
→ Verification
```

---

## 2. LOW Risk Actions

### WEB01

```text
Target: WEB01
Service: Nginx
Action: restart_nginx
Risk: LOW
Playbook: restart-nginx.yml
```

Pre-check:

```text
SSH available
```

Verification:

```text
HTTP :80
Expected: 200 OK
```

Flow:

```text
Request
→ LOW
→ No Approval
→ SSH Pre-check
→ Restart Nginx
→ Verify HTTP :80
```

---

### APP01

```text
Target: APP01
Service: app01-web
Action: restart_container
Risk: LOW
Playbook: restart-app-container.yml
```

Pre-check:

```text
SSH available
Docker available
```

Verification:

```text
Container: app01-web Running
HTTP :8080
```

---

### WIN01

```text
Target: WIN01
Service: Windows Exporter
Action: restart_windows_exporter
Risk: LOW
Playbook: restart-windows-exporter.yml
```

Pre-check:

```text
WinRM available
```

Verification:

```text
windows_exporter Running
/metrics :9182 available
```

---

### AZURE01

```text
Target: AZURE01
Service: Nginx
Action: restart_nginx
Risk: LOW
Playbook: restart-azure-nginx.yml
```

Pre-check:

```text
SSH available
```

Verification:

```text
HTTP :80
Expected: 200 OK
```

---

## 3. MEDIUM Risk Action

### APP01

Action được chọn:

```text
Target: APP01
Component: Docker Runtime
Action: restart_docker_service
Risk: MEDIUM
```

Mục đích:

```text
Restart Docker daemon trên APP01
```

Impact:

```text
Có thể ảnh hưởng đến nhiều container trên cùng target
```

Approval:

```text
Required
```

Management Pre-check:

```text
SSH available
```

Execution dự kiến:

```text
systemctl restart docker
```

Verification:

```text
Docker service active
app01-web Running
HTTP :8080 available
```

Flow:

```text
Request
→ MEDIUM
→ PENDING_APPROVAL
→ APPROVED
→ SSH Pre-check
→ Restart Docker
→ Verify Docker
→ Verify app01-web
→ Verify HTTP :8080
```

---

## 4. HIGH Risk Action

### AZURE01

Action được chọn:

```text
Target: AZURE01
Component: Operating System
Action: reboot_server
Risk: HIGH
```

Impact:

```text
Toàn bộ host bị restart
SSH tạm thời unavailable
Nginx tạm thời unavailable
Node Exporter tạm thời unavailable
Monitoring target có thể DOWN trong thời gian reboot
```

Approval:

```text
Admin Approval Required
```

Management Pre-check:

```text
SSH available trước khi reboot
```

Execution dự kiến:

```text
reboot
```

Verification:

```text
Host reachable again
SSH available
Nginx active
Node Exporter active
HTTP :80 available
Metrics :9100 available
```

Flow:

```text
Request
→ HIGH
→ PENDING_APPROVAL
→ Admin APPROVED
→ SSH Pre-check
→ Reboot Server
→ Wait for Host Recovery
→ Verify SSH
→ Verify Nginx
→ Verify Node Exporter
→ Verify HTTP / Metrics
```

---

## 5. Action Mapping Summary

| Target | Action | Risk | Approval | Verification |
|---|---|---:|---|---|
| WEB01 | `restart_nginx` | LOW | No | HTTP :80 |
| APP01 | `restart_container` | LOW | No | Container + HTTP :8080 |
| WIN01 | `restart_windows_exporter` | LOW | No | Service + :9182 |
| AZURE01 | `restart_nginx` | LOW | No | HTTP :80 |
| APP01 | `restart_docker_service` | MEDIUM | Required | Docker + Container + HTTP |
| AZURE01 | `reboot_server` | HIGH | Admin | SSH + Nginx + Node Exporter + HTTP |

---

## 6. Guardrail

Các action MEDIUM và HIGH chỉ được execute khi approval hợp lệ.

Approval không bỏ qua:

```text
Management Pre-check
→ Execute
→ Verification
→ Audit
→ Notification
```

Nếu verification thất bại sau execution:

```text
VERIFICATION_FAILED
→ MANUAL_REQUIRED
```

Nếu approval bị reject hoặc expired:

```text
NO EXECUTION
```

## 7. Result

Action Mapping của Week 9 xác định rõ action nào sẽ được dùng để kiểm thử Approval Workflow ở từng mức risk.

Các action MEDIUM và HIGH sẽ được triển khai thành playbook thật ở bước tiếp theo.
