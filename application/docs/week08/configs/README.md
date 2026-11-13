# Cấu hình tuần 8

Giữ Entra, Graph và auto-remediation của các tuần trước. Tuần 8 tách key SSH tới MON01 khỏi key của AZURE01.

| Biến | Lab tối 13/11 |
| --- | --- |
| `ANSIBLE_CONTROLLER_HOST` | `192.168.10.10` |
| `ANSIBLE_CONTROLLER_KEY` | key tới MON01, hoặc để trống |
| Inventory trên MON01 | `/etc/ansible/hosts` |
| Key AZURE01 | `azure01_ed25519`, chỉ trên MON01 |
| `AUTO_REMEDIATION_MAX_RETRIES` | `1` |
| `ALERT_RECIPIENT_CRITICAL` | `KLTN-Alert-Critical@cucbong.id.vn` |
| `ALERT_RECIPIENT_WARNING` | `KLTN-Alert-Warning@cucbong.id.vn` |

`ENTRA_CLIENT_SECRET` và private key không nằm trong repo.
