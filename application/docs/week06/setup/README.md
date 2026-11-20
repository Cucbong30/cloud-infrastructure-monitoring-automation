# Chạy portal tuần 6

Cách chạy giống tuần 5, trong thư mục `application/`.

1. `AUTOMATION_EXECUTOR=ansible`.
2. `ANSIBLE_CONTROLLER_HOST=192.168.10.10` và user SSH trên MON01.
3. `AUTO_REMEDIATION_ENABLED=true`.
4. `AUTO_REMEDIATION_COOLDOWN_SECONDS=120`.
5. `AUTO_REMEDIATION_MAX_RETRIES=1`.
6. `flask run --host 127.0.0.1 --port 5000`. Sửa code hoặc `.env` xong thì tắt process và chạy lại.

Pre-check SSH và WinRM vẫn được hỏi từ MON01. Post-check hỏi Nginx `:80`, App `:8080`, Windows Exporter `:9182`.
