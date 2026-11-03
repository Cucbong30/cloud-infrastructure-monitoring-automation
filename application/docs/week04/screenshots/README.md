# Ảnh test case tuần 4

Chụp trên portal lab, giờ UTC+7, ngày 23/10/2026 cho các job và 27/10/2026 cho trang Audit lúc mở lại portal.

| File | Nội dung |
| --- | --- |
| `01-unreachable-instead-of-restart.png` | WEB01, APP01, WIN01 đang Unreachable. Trang Jobs hiện một thông báo, không còn nút restart tương ứng. |
| `02-three-playbooks-success.png` | Ba job Success: `restart_windows_exporter`, `restart_container`, `restart_nginx`. Phía dưới là các job Failed lúc chưa SSH được. |
| `03-playbook-unreachable-failed.png` | APP01 và WEB01 Failed vì `No route to host`. Output playbook vẫn nằm trên job. |
| `04-web01-server-detail.png` | WEB01 status down. Không có nút Restart Nginx. Có thông báo Unreachable và job Failed. |
| `05-audit-job-events.png` | Audit Log có `job.request` và `job.result` cho job automation. |
