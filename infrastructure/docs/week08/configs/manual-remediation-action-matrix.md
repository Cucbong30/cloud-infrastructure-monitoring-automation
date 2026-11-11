# Manual Remediation Action Matrix

## 1. Objective

Chuẩn hóa các remediation action được phép sử dụng cho từng target trong hệ thống.

Mỗi action được xác định theo:

```text
Target
→ Service
→ Action
→ Management Channel
→ Pre-check
→ Verification
→ Risk
```

---

## 2. Action Matrix

| Target | Service | Action | Management | Pre-check | Verification | Risk |
|---|---|---|---|---|---|---|
| WEB01 | Nginx | `restart_nginx` | SSH | SSH available | HTTP `:80` | LOW |
| APP01 | Docker Application | `restart_container` | SSH | SSH + Docker available | HTTP `:8080` | LOW |
| WIN01 | Windows Exporter | `restart_windows_exporter` | WinRM | WinRM available | `/metrics :9182` | LOW |
| AZURE01 | Nginx | `restart_nginx` | SSH | SSH available | HTTP `:80` | LOW |

---

## 3. WEB01

Playbook:

```text
restart-nginx.yml
```

Flow:

```text
SSH Pre-check
→ Restart Nginx
→ Wait for port 80
→ HTTP verification
```

Expected result:

```text
HTTP 200
```

---

## 4. APP01

Playbook:

```text
restart-app-container.yml
```

Flow:

```text
SSH Pre-check
→ Check Docker
→ Start/Restart app01-web
→ Wait for port 8080
→ HTTP verification
```

Expected result:

```text
Container Running
HTTP 200
```

---

## 5. WIN01

Playbook:

```text
restart-windows-exporter.yml
```

Flow:

```text
WinRM Pre-check
→ Start/Restart Windows Exporter
→ Wait for port 9182
→ Verify /metrics
```

Expected result:

```text
windows_exporter Running
Metrics Endpoint Available
```

---

## 6. AZURE01

Playbook:

```text
restart-azure-nginx.yml
```

Flow:

```text
SSH Pre-check
→ Restart Nginx
→ Wait for port 80
→ HTTP verification
```

Expected result:

```text
HTTP 200
```

---

## 7. Policy

Các action trên hiện được phân loại là:

```text
Risk: LOW
Mode: AUTO / MANUAL
```

Manual Remediation không được bỏ qua các bước:

```text
Management Pre-check
→ Execute
→ Verification
```

Nếu pre-check fail:

```text
BLOCKED
```

Nếu execution fail:

```text
EXECUTION_FAILED
```

Nếu execution thành công nhưng verification fail:

```text
VERIFICATION_FAILED
```

Các action ngoài danh sách trên không được tự động chạy nếu chưa được định nghĩa trong policy.
