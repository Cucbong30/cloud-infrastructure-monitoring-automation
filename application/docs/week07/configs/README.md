# Cấu hình tuần 7

Giữ Ansible và auto-remediation của tuần 6. Tuần 7 thêm Entra, Graph và AZURE01. Giá trị secret để trống trong repo.

| Biến | Lab |
| --- | --- |
| `ENTRA_REDIRECT_URI` | `http://localhost:5000/auth/callback` |
| `NOTIFY_ENABLED` | `true` khi gửi mail |
| `GRAPH_SENDER_MAILBOX` | mailbox generic, không ghi vào git |
| `ALERT_RECIPIENT_CRITICAL` | `KLTN-Alert-Critical@cucbong.id.vn` |
| `ALERT_RECIPIENT_WARNING` | `KLTN-Alert-Warning@cucbong.id.vn` |
| `ALERT_RECIPIENT_INFO` | `KLTN-Alert-Info@cucbong.id.vn` |
| `AZURE01_IP` | `20.243.24.91` |
| `AZURE01_PLAYBOOK` | `~/ansible/playbooks/restart-azure-nginx.yml` |
| `AUTO_REMEDIATION_COOLDOWN_SECONDS` | `120` |
| `AUTO_REMEDIATION_MAX_RETRIES` | `1` |

`ENTRA_CLIENT_SECRET` chỉ nằm trên máy lab.
