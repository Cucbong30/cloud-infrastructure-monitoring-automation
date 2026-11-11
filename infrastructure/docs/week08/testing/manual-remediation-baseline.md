# Manual Remediation Baseline Test

## 1. Objective

Kiểm tra các remediation action có thể được chạy thủ công trực tiếp từ MON01 trước khi tích hợp đầy đủ vào Manual Remediation trên Portal.

Mỗi target được kiểm tra theo flow:

```text
Management Pre-check
→ Execute Remediation
→ Verification
→ SUCCESS
```

---

## 2. WEB01

Target:

```text
WEB01
Service: Nginx
Action: restart_nginx
Verification: HTTP :80
```

Kiểm tra Ansible connectivity:

```text
ansible WEB01 -m ping
```

Chạy remediation:

```text
ansible-playbook /home/bong/ansible/playbooks/restart-nginx.yml
```

Verification:

```text
curl -I http://192.168.10.11
```

Kết quả:

```text
Ansible: SUCCESS
Remediation: SUCCESS
HTTP :80: 200 OK
```

---

## 3. APP01

Target:

```text
APP01
Service: Docker Application
Action: restart_container
Container: app01-web
Verification: HTTP :8080
```

Kiểm tra Ansible connectivity:

```text
ansible APP01 -m ping
```

Chạy remediation:

```text
ansible-playbook /home/bong/ansible/playbooks/restart-app-container.yml
```

Kiểm tra container:

```text
ansible APP01 -m shell -a "docker ps"
```

Verification:

```text
curl -I http://192.168.10.12:8080
```

Kết quả:

```text
Ansible: SUCCESS
Container: Running
Remediation: SUCCESS
HTTP :8080: 200 OK
```

---

## 4. WIN01

Target:

```text
WIN01
Service: Windows Exporter
Action: restart_windows_exporter
Verification: /metrics :9182
```

Kiểm tra WinRM:

```text
ansible WIN01 -m win_ping
```

Chạy remediation:

```text
ansible-playbook /home/bong/ansible/playbooks/restart-windows-exporter.yml
```

Kiểm tra service:

```text
ansible WIN01 -m win_shell -a "Get-Service windows_exporter"
```

Verification:

```text
curl http://192.168.10.13:9182/metrics
```

Kết quả:

```text
WinRM: SUCCESS
Windows Exporter: Running
Remediation: SUCCESS
Metrics Endpoint: Available
```

---

## 5. AZURE01

Target:

```text
AZURE01
Environment: Azure Cloud
Service: Nginx
Action: restart_nginx
Verification: HTTP :80
```

Kiểm tra Ansible connectivity:

```text
ansible AZURE01 -m ping
```

Chạy remediation:

```text
ansible-playbook /home/bong/ansible/playbooks/restart-azure-nginx.yml
```

Kiểm tra service:

```text
ansible AZURE01 -m shell -a "systemctl is-active nginx"
```

Verification:

```text
curl -I http://20.243.24.91
```

Kết quả:

```text
Ansible: SUCCESS
Nginx: active
Remediation: SUCCESS
HTTP :80: 200 OK
```

---

## 6. Result

Cả bốn target đều chạy được remediation thủ công trực tiếp từ MON01:

```text
WEB01    → SUCCESS
APP01    → SUCCESS
WIN01    → SUCCESS
AZURE01  → SUCCESS
```

Kết quả này xác nhận các playbook hiện tại có thể tiếp tục được sử dụng cho chức năng Manual Remediation trên Portal mà không cần tạo riêng một bộ remediation action khác.
