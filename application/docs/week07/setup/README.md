# Chạy portal tuần 7

Cách chạy giống tuần 6, trong thư mục `application/`.

1. Giữ `AUTOMATION_EXECUTOR=ansible`, controller MON01 `192.168.10.10`, cooldown 120 giây, retry 1 lần.
2. Điền `ENTRA_TENANT_ID`, `ENTRA_CLIENT_ID`, `ENTRA_CLIENT_SECRET`. Redirect là `http://localhost:5000/auth/callback`.
3. `NOTIFY_ENABLED=true`. `GRAPH_SENDER_MAILBOX` là mailbox generic được phép gửi. Ba biến `ALERT_RECIPIENT_CRITICAL`, `ALERT_RECIPIENT_WARNING`, `ALERT_RECIPIENT_INFO` là ba distribution group.
4. `AZURE01_IP`, `AZURE01_NGINX_URL` và `AZURE01_PLAYBOOK`. Playbook mặc định là `~/ansible/playbooks/restart-azure-nginx.yml`.
5. `flask run --host 127.0.0.1 --port 5000`, hoặc `docker compose up --build`. File `.env` không được copy vào image.

Client secret không commit. Mẫu để trống nằm ở `.env.example`.
