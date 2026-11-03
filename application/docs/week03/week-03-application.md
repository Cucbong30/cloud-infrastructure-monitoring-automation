# Báo cáo Tuần 3

Nguyễn Thế Gia Bảo – Application / Integration

Khai báo AI: [ai-usage.md](ai-usage.md)

## Công việc được phân công

- Chuẩn bị tích hợp Web Portal với Prometheus API.
- Xây dựng service layer lấy dữ liệu monitoring.
- Hiển thị trạng thái server và metrics thật trên Dashboard.
- Chuẩn bị cấu trúc tích hợp Ansible.
- Hoàn thiện xử lý lỗi và giao diện các module hiện tại.

## Kết quả thực hiện

Em trỏ portal trên laptop tới Prometheus tại `http://192.168.10.10:9090`. Máy em đi Tailscale qua MGMT01 rồi tới MON01. Portal gọi được instant query, range query, danh sách cảnh báo và đường kiểm tra sức khỏe. Hết 3 giây không trả lời thì bỏ qua, không để treo trang. Token nếu có thì không in ra trong thông báo lỗi. Hai biến em dùng là `PROMETHEUS_BASE_URL` và `PROMETHEUS_TIMEOUT_SECONDS`.

Số liệu từng máy em tách riêng. Linux dùng metric `node`, Windows dùng metric `windows`. Em gắn `192.168.10.11:9100` với WEB01, `192.168.10.12:9100` với APP01, `192.168.10.13:9182` với WIN01 và `192.168.10.10:9100` với MON01. Lúc đầu em suýt lấy CPU của MON01 từ cổng 9090. Cổng đó là Prometheus, không phải số liệu máy. Em sửa lại: CPU, RAM, Disk và Uptime của MON01 lấy từ Node Exporter cổng 9100. Cổng 9090 chỉ để biết Prometheus còn chạy.

Lúc tưởng MON01 tắt, `Test-NetConnection` từ laptop vẫn thấy cổng 9090, 9100 và 9093 mở. Máy chưa tắt khỏi đường laptop. Grafana `:3000` thì curl thất bại nhưng dashboard vẫn Healthy, vì lúc đó chưa probe `:3000`. Sau khi thêm probe, connection refused thì Grafana DOWN.

Em thử tắt đường tới Prometheus. Trang không bị crash. Dashboard vẫn trả về HTTP 200, số liệu thành N/A, Monitoring Backend hiện Down, máy hiện Unreachable. Inventory, Alerts, Jobs và Audit em vẫn vào được. Pytest em chạy thêm các ca timeout, dữ liệu Prometheus sai định dạng, webhook và map instance.

Ansible em chưa cho chạy trên lab. Job mặc định dùng mock. Khi gọi executor Ansible, chương trình trả về lỗi cố ý: "Real Ansible execution is disabled in MVP". Ba việc được phép khai báo là `restart_service`, `restart_container` và `disk_cleanup`.

Portal nhận cảnh báo do Alertmanager gửi sang. Route webhook em miễn CSRF vì Alertmanager không gửi token form. Instance `192.168.10.11:9100` em gắn vào WEB01 rồi lưu SQLite. Cùng fingerprint thì không thêm dòng mới. Hết sự cố thì trạng thái chuyển từ firing sang resolved. Audit em thấy ba loại: `alert.received`, `alert.resolved` và `prometheus.unavailable`.

Dashboard em sửa lại giao diện thành bốn nhóm cho dễ nhìn.

- Một là trạng thái máy: Healthy, Degraded hoặc Unreachable.
- Hai là CPU, Memory, Disk và Uptime.
- Ba là exporter UP hay DOWN.
- Bốn là probe dịch vụ: Nginx cổng 80 trên WEB01, ứng dụng cổng 8080 trên APP01, WinRM cổng 5985 trên WIN01, còn MON01 thì có Prometheus cổng 9090, Alertmanager cổng 9093 và Grafana cổng 3000.

Trang tự làm mới khoảng 5 giây một lần. Bấm một dịch vụ đang DOWN thì mở log của máy đó, trong log có probe, cảnh báo, audit và job liên quan.

Giao diện em đổi nền tối để trạng thái nổi hơn, nhìn vào là biết lab đang thế nào. Trang có các ô Total, Healthy, Degraded, Unreachable, phần Alerts overview, Service status và thanh CPU, RAM, Disk. Dữ liệu mẫu em để đúng bốn máy WEB01, APP01, WIN01 và MON01.

Em đã chụp test case trên lab. Tắt Nginx trên WEB01: máy Degraded, exporter vẫn UP, Nginx cổng 80 DOWN. Tắt container trên APP01: cổng 8080 DOWN. Tắt Grafana trên MON01: cổng 3000 DOWN. Tắt WIN01: máy Unreachable, cổng 9182 và WinRM cổng 5985 không kết nối được.

## Kết quả trên GitHub

Trạng thái: Hoàn thành nội dung Tuần 3. Code và evidence nằm trên nhánh `application`, đã merge thư mục `application/` vào `main`.

| Kết quả | Commit message | Link | Commit |
| --- | --- | --- | --- |
| Nhánh Application | Add live lab monitoring, Alertmanager webhook, and host health dashboard. | [application/](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/application/application) | [6f6fda8](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b) |
| Prometheus client | add Prometheus API client and fail-closed health | [prometheus.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/app/services/prometheus.py) | cùng commit |
| Service layer metrics | add PromQL host metrics, exporter and HTTP/TCP probes | [metrics.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/app/services/metrics.py) | [probes.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/app/services/probes.py) |
| Lab inventory mapping | map WEB01/APP01/WIN01/MON01 monitoring targets | [inventory.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/app/services/inventory.py) | cùng commit |
| Dashboard live | add live dashboard snapshot, host health and event log | [dashboard.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/app/blueprints/dashboard.py) | [dashboard.html](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/app/templates/dashboard.html) |
| Alertmanager webhook | add Alertmanager webhook ingest and fingerprint dedupe | [webhooks.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/app/blueprints/webhooks.py) | [alert_webhook.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/app/services/alert_webhook.py) |
| Ansible adapter | keep mock default; Ansible executor and allow-listed playbooks | [ansible.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/app/executors/ansible.py) | [playbooks](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/automation/ansible/playbooks) |
| Tests tuần 3 | add Prometheus, probe, webhook and inventory tests | [tests](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/tests) | [test_prometheus.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/6f6fda8a47b0b9d7ad2bde4db8cb0269f9e3de6b/application/tests/test_prometheus.py) |
| Docs week03 | add application/docs/week03 setup, configs, scripts, tests | [docs/week03](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/application/application/docs/week03) | cùng nhánh |
| Ảnh WEB01 Nginx down | add week 3 dashboard evidence for Nginx down | [01-web01-nginx-down.png](screenshots/01-web01-nginx-down.png) | [ed3ee4f](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/ed3ee4fa739ff12ebd863765c08aa41d30bfc7aa) |
| Ảnh APP01 container down | add week 3 dashboard evidence for App :8080 down | [02-app01-container-down.png](screenshots/02-app01-container-down.png) | [ed3ee4f](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/ed3ee4fa739ff12ebd863765c08aa41d30bfc7aa) |
| Ảnh MON01 Grafana down | add week 3 dashboard evidence for Grafana :3000 down | [03-mon01-grafana-down.png](screenshots/03-mon01-grafana-down.png) | [ed3ee4f](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/ed3ee4fa739ff12ebd863765c08aa41d30bfc7aa) |
| Ảnh WIN01 down | add week 3 dashboard evidence for WIN01 Unreachable | [04-win01-down.png](screenshots/04-win01-down.png) | [ed3ee4f](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/ed3ee4fa739ff12ebd863765c08aa41d30bfc7aa) |
| Merge vào main | Merge week 3 portal updates and test-case screenshots into application on main. | [main/application](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/main/application) | [1917297](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/191729749fafc36533490adae0f2c8228439b5d6) |

## Luồng sự cố đã kiểm tra

- Service HTTP chết, exporter còn sống: tắt Nginx trên WEB01 hoặc container trên APP01 thì Dashboard Degraded, đúng hàng service DOWN, metric CPU/RAM/Disk vẫn có vì `:9100` còn up.
- Grafana chết: probe `http://192.168.10.10:3000/` thất bại thì Grafana DOWN. Nếu cả Prometheus API cũng không trả lời thì Monitoring Backend Down và MON01 Unreachable.
- WIN01 down: ping, `:9182` và `:5985` timeout thì Unreachable, số liệu N/A. Alertmanager trên MON01 không gửi được webhook nếu chính MON01 chết. Portal vẫn phát hiện bằng probe.
- WEB01 exporter down: Prometheus InstanceDown, Alertmanager gửi `POST /api/alerts/webhook`, portal lưu SQLite và hiện trên Alerts. Khi máy lên lại, cùng fingerprint chuyển resolved.
