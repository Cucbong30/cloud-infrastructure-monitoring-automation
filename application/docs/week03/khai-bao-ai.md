# Khai báo sử dụng AI — Tuần 3 (Application)

## Công cụ sử dụng

- Cursor (Grok)
- Dùng trong quá trình lập trình và biên soạn báo cáo tuần 3

## Mục đích sử dụng

Hỗ trợ phân tích yêu cầu tích hợp Prometheus, thiết kế service layer, PromQL, webhook Alertmanager, xử lý lỗi fail-closed, test pytest, giao diện dashboard và soạn báo cáo.

AI không thay thế phần triển khai trên lab, kiểm tra kết quả thực tế, hay quyết định kỹ thuật cuối cùng của sinh viên.

## Nội dung AI hỗ trợ

AI hỗ trợ đề xuất cách gọi Prometheus HTTP API từ Flask (instant query, health `/-/healthy`, timeout, không lộ token trong thông báo lỗi) và tách Monitoring Backend `:9090` khỏi metric host MON01 lấy từ Node Exporter `:9100`.

AI hỗ trợ thiết kế service layer: `PrometheusClient`, inventory mapping WEB01/APP01/WIN01/MON01, PromQL Linux (`node_cpu_seconds_total`, `node_memory_*`, `node_filesystem_*`, `node_boot_time_seconds`) và Windows (`windows_cpu_time_total`, `windows_cs_physical_memory_bytes`, `windows_logical_disk_*`, `windows_os_start_time`), cộng probe HTTP/TCP cho Nginx `:80`, App `:8080`, WinRM `:5985`, Prometheus `:9090`, Alertmanager `:9093`, Grafana `:3000`.

AI hỗ trợ đề xuất trạng thái host theo bốn nhóm trên Dashboard: Healthy/Degraded/Unreachable; CPU/RAM/Disk/Uptime; exporter UP/DOWN; service probe. Gợi ý poll `/dashboard/snapshot` và event log `/dashboard/events/<host>` khi bấm service DOWN.

AI hỗ trợ khung webhook Alertmanager `POST /api/alerts/webhook`: CSRF exempt, map instance `192.168.10.11:9100` về WEB01, chống trùng fingerprint, cập nhật firing thành resolved, ghi audit `alert.received` / `alert.resolved` / `prometheus.unavailable`.

AI hỗ trợ hướng xử lý lỗi fail-closed: Prometheus timeout hoặc malformed thì dashboard vẫn HTTP 200, metrics N/A, Monitoring Backend Down, Inventory/Alerts/Jobs/Audit vẫn mở. Gợi ý test pytest cho Prometheus, probe, webhook, inventory và trang dashboard.

AI hỗ trợ gợi ý cấu trúc Ansible (mock executor mặc định, `AnsibleRunnerExecutor` chưa spawn process, allow-list `restart_service` / `restart_container` / `disk_cleanup`, `AUTO_REMEDIATION_ENABLED=false`) và bản nháp giao diện Operations Portal cùng báo cáo tuần 3 (bảng link GitHub/commit, chú thích bốn ảnh test case).

## Phần sinh viên tự thực hiện

- Lựa chọn giải pháp, tích hợp và chỉnh sửa mã trên lab thật (WEB01, APP01, WIN01, MON01).
- Chạy portal trên laptop qua Tailscale.
- Kiểm tra luồng nghiệp vụ: Nginx down, container down, Grafana down, WIN01 down.
- Tự chụp evidence.
- Quản lý Git/GitHub (nhánh `application` và merge vào `main`).
- Chịu trách nhiệm về mã nguồn, kết quả kiểm thử và nội dung báo cáo cuối cùng.
