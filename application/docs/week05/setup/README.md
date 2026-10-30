# Chạy portal tuần 5

Cách chạy giống tuần 4, trong thư mục `application/`.

1. `AUTOMATION_EXECUTOR=ansible`.
2. `ANSIBLE_CONTROLLER_HOST=192.168.10.10` và user SSH trên MON01.
3. `AUTO_REMEDIATION_ENABLED=false`.
4. `flask run --host 127.0.0.1 --port 5000`. Sửa code hoặc `.env` xong thì tắt process và chạy lại.

Pre-check SSH và WinRM được hỏi từ MON01, không phải từ cổng mở trên laptop.
