# Chạy portal tuần 8

Cách chạy giống tuần 7, trong thư mục `application/`.

1. Giữ Ansible controller MON01 `192.168.10.10`, cooldown 120 giây, retry 1 lần, Entra và Graph như tuần 7.
2. `ANSIBLE_CONTROLLER_KEY` chỉ là key từ máy portal tới MON01. Để trống nếu dùng key mặc định của user đó.
3. Trên MON01, `/etc/ansible/hosts` khai AZURE01 với key `azure01_ed25519`. Portal không gửi key này.
4. Playbook AZURE01 vẫn là `~/ansible/playbooks/restart-azure-nginx.yml`.
5. `flask run --host 127.0.0.1 --port 5000`.

Private key không commit.
