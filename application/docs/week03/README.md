# Báo cáo Application — Tuần 3

Nguyễn Thế Gia Bảo – Application / Integration

Trạng thái: hoàn thành nội dung Tuần 3. Code và evidence trên nhánh `application`, đã merge `application/` vào `main`. Không đẩy phần Application lên nhánh `infra`.

## Công việc được phân công

- Chuẩn bị tích hợp Web Portal với Prometheus API.
- Xây dựng service layer lấy dữ liệu monitoring.
- Hiển thị trạng thái server và metrics thật trên Dashboard.
- Chuẩn bị cấu trúc tích hợp Ansible.
- Hoàn thiện xử lý lỗi và giao diện các module hiện tại.

## Kết quả thực hiện

1. **Prometheus API.** Portal trên laptop gọi `http://192.168.10.10:9090` (laptop → Tailscale → MGMT01 → MON01). `PrometheusClient` bọc instant/range query, list alerts, `/-/healthy`; timeout 3 giây; token không lộ trong lỗi. Cấu hình: `PROMETHEUS_BASE_URL`, `PROMETHEUS_TIMEOUT_SECONDS`.
2. **Service layer.** `app/services/prometheus.py`, `metrics.py` (PromQL Linux `node_*` / Windows `windows_*`), `inventory.py` map `192.168.10.11:9100` → WEB01, `:12:9100` → APP01, `:13:9182` → WIN01, `:10:9100` → MON01. Metric host MON01 lấy Node Exporter `:9100`, không nhầm Prometheus `:9090` (Monitoring Backend).
3. **Dashboard live.** Bốn nhóm: Host Healthy/Degraded/Unreachable; CPU/RAM/Disk/Uptime; exporter UP/DOWN; probe WEB01 Nginx `:80`, APP01 App `:8080`, WIN01 WinRM `:5985`, MON01 Prometheus `:9090` / Alertmanager `:9093` / Grafana `:3000`. Poll `/dashboard/snapshot`; bấm DOWN mở `/dashboard/events/<host>`.
4. **Fail-closed.** Prometheus/MON01 chết: dashboard HTTP 200, metrics N/A, Monitoring Backend Down, host Unreachable; Inventory/Alerts/Jobs/Audit vẫn mở.
5. **Ansible (chuẩn bị, chưa chạy lab).** Mock executor mặc định. `AnsibleRunnerExecutor` không spawn process. Allow-list `restart_service` / `restart_container` / `disk_cleanup`. `automation_group` theo host. `AUTO_REMEDIATION_ENABLED=false`.
6. **Bổ sung webhook Alertmanager** `POST /api/alerts/webhook`: map instance → host, fingerprint dedupe, firing → resolved, audit `alert.received` / `alert.resolved` / `prometheus.unavailable`.
7. **UI Operations Portal** (dark), seed 4 máy lab, cây `docs/week03/` (setup, configs, scripts, tests, screenshots).
8. **Evidence 4 test case:** Nginx down, App container down, Grafana down, WIN01 down.

Báo cáo Markdown: [bao-cao-tuan-3.md](bao-cao-tuan-3.md). Khai báo AI: [khai-bao-ai.md](khai-bao-ai.md).

## Kết quả trên GitHub

| Kết quả | Commit message | Link | Commit |
| --- | --- | --- | --- |
| Nhánh Application | Add live lab monitoring, Alertmanager webhook, and host health dashboard. | [application/](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/application/application) | [6f6fda8](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b) |
| Prometheus client | add Prometheus API client and fail-closed health | [prometheus.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/app/services/prometheus.py) | cùng commit |
| Service layer metrics | add PromQL host metrics, exporter and HTTP/TCP probes | [metrics.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/app/services/metrics.py) | [probes.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/app/services/probes.py) |
| Lab inventory | map WEB01/APP01/WIN01/MON01 | [inventory.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/app/services/inventory.py) | cùng commit |
| Dashboard live | add live dashboard snapshot, host health and event log | [dashboard.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/app/blueprints/dashboard.py) | [dashboard.html](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/app/templates/dashboard.html) |
| Alertmanager webhook | add webhook ingest and fingerprint dedupe | [webhooks.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/app/blueprints/webhooks.py) | [alert_webhook.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/app/services/alert_webhook.py) |
| Ansible adapter | mock default; executor + allow-listed playbooks | [ansible.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/app/executors/ansible.py) | [playbooks](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/automation/ansible/playbooks) |
| Tests tuần 3 | Prometheus, probe, webhook, inventory | [tests](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/tests) | [test_prometheus.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/tests/test_prometheus.py) |
| Docs week03 | setup, configs, scripts, tests | [docs/week03](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/application/application/docs/week03) | cùng nhánh |
| Ảnh 4 test case | Nginx, App, Grafana, WIN01 down | [screenshots](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/application/application/docs/week03/screenshots) | [ed3ee4f](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/ed3ee4fa739ff12ebd863765c08aa41d30bfc7aa) |
| Merge vào main | Merge week 3 portal updates into application on main | [main/application](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/main/application) | [1917297](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/191729749fafc36533490adae0f2c8228439b5d6) |

## Máy chủ lab

| Tên | IP | Target |
| --- | --- | --- |
| MGMT01 | 192.168.10.5 | — |
| MON01 | 192.168.10.10 | Prometheus `:9090`, Grafana `:3000`, Alertmanager `:9093`, Node Exporter `:9100` |
| WEB01 | 192.168.10.11 | `192.168.10.11:9100`, Nginx `:80` |
| APP01 | 192.168.10.12 | `192.168.10.12:9100`, App `:8080` |
| WIN01 | 192.168.10.13 | `192.168.10.13:9182`, WinRM `:5985` |

## Luồng sự cố

- Service HTTP chết, exporter còn: WEB01/APP01 **Degraded**, đúng service DOWN, vẫn có CPU/RAM/Disk.
- Grafana/Prometheus chết: Grafana DOWN; nếu API Prometheus chết thì Monitoring Backend Down, host Unreachable.
- WIN01 down: `:9182` / `:5985` timeout → Unreachable, N/A.
- WEB01 exporter down: Prometheus InstanceDown → Alertmanager → webhook → SQLite → Alerts UI; lên lại cùng fingerprint **resolved**.

Trên GitHub nhóm: `application/docs/week03/`.
