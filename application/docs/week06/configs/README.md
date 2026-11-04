# Cấu hình tuần 6

Giữ Ansible controller của tuần 4 và pre-check của tuần 5. Tuần 6 bật auto remediation.

| Biến | Lab tối 4/11 |
| --- | --- |
| `AUTO_REMEDIATION_ENABLED` | `true` |
| `AUTO_REMEDIATION_COOLDOWN_SECONDS` | `120` |
| `AUTO_REMEDIATION_MAX_RETRIES` | `1` |
| `AUTOMATION_EXECUTOR` | `ansible` |
| `ANSIBLE_CONTROLLER_HOST` | `192.168.10.10` |

Ba action auto: `restart_nginx` trên WEB01, `restart_container` trên APP01 với `container_name=app01-web`, `restart_windows_exporter` trên WIN01 với `service_name=windows_exporter`.
