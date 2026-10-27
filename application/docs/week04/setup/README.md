# Chạy portal cho Jobs / Ansible

Từ thư mục `application/`:

1. Tạo virtualenv, cài dependency, copy `.env.example` thành `.env`.
2. Đặt `AUTOMATION_EXECUTOR=ansible`.
3. Đặt `ANSIBLE_CONTROLLER_HOST=192.168.10.10`, `ANSIBLE_CONTROLLER_USER` là user SSH trên MON01, và `ANSIBLE_CONTROLLER_KEY` là private key nằm trên laptop. Đường dẫn kiểu `/home/bong/.ssh/id_ed25519` là path trên MON01, laptop không mở được file đó.
4. `AUTO_REMEDIATION_ENABLED=false` nếu chỉ muốn bấm nút, không cho alert tự chạy playbook.
5. Chạy `flask run --host 127.0.0.1 --port 5000`. Sửa `.env` xong thì tắt và chạy lại, vì process chỉ đọc env lúc khởi động.

Laptop đi Tailscale tới MON01. Portal không cài Ansible local. Ansible chạy trên MON01.
