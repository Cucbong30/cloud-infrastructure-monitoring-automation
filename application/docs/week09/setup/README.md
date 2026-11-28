# Chạy portal tuần 9

Cách chạy giống tuần 8, trong thư mục `application/`.

1. Giữ Ansible, Entra, Graph, cooldown và retry của các tuần trước.
2. `APPROVAL_TIMEOUT_MINUTES=5`.
3. LOW: `restart_nginx`, `restart_container`, `restart_windows_exporter`.
4. MEDIUM: `restart_docker_service` trên APP01, playbook `restart-docker-service.yml`.
5. HIGH: `reboot_server` trên AZURE01, playbook `reboot-azure01.yml`. Chỉ Admin request và approve.
6. `flask run --host 127.0.0.1 --port 5000`.
