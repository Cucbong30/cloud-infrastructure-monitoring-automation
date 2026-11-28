# Chạy portal tuần 10

Cách chạy giống tuần 9, trong thư mục `application/`.

1. Giữ Ansible, Entra, Graph, cooldown, retry và approval của các tuần trước.
2. Chạy migration `e7c1a9d44b10_incident_lifecycle`.
3. LOW vẫn là Nginx, App container và Windows Exporter. MEDIUM vẫn là restart Docker service trên APP01.
4. Recovery của dịch vụ HTTP cần mã 200. Mã 403 không đóng incident.
5. `flask run --host 127.0.0.1 --port 5000`. Trang incident nằm ở `/incidents`.
