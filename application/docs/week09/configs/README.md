# Cấu hình tuần 9

| Mục | Lab tối 20/11 |
| --- | --- |
| `APPROVAL_TIMEOUT_MINUTES` | `5` |
| LOW | Nginx, App container, Windows Exporter. Không tạo approval. |
| MEDIUM | `restart_docker_service` trên APP01. Operator request, Admin approve. |
| HIGH | `reboot_server` trên AZURE01. Chỉ Admin. |
| Mail requested | gửi email của user Admin |
| Mail success và resolved | nhóm Info `KLTN-Alert-Info@cucbong.id.vn` |
