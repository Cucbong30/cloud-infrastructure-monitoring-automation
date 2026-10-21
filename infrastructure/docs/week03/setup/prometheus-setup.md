# Prometheus Setup on MON01

## 1. Mục tiêu

Cài đặt Prometheus trên `MON01` để thu thập metrics từ các server trong môi trường Lab.

Prometheus sẽ giám sát:

- WEB01 - `192.168.10.11:9100`
- APP01 - `192.168.10.12:9100`
- WIN01 - `192.168.10.13:9182`

MON01 sử dụng địa chỉ:

`192.168.10.10`

---

## 2. Cập nhật hệ thống

```
sudo apt update
sudo apt upgrade -y
```

---

## 3. Tạo Prometheus User và Directory

Tạo user dành riêng cho Prometheus:

```
sudo useradd --no-create-home --shell /bin/false prometheus
```

Tạo thư mục cấu hình và lưu dữ liệu:

```
sudo mkdir -p /etc/prometheus
sudo mkdir -p /var/lib/prometheus
```

Phân quyền cho thư mục lưu dữ liệu:

```
sudo chown prometheus:prometheus /var/lib/prometheus
```

---

## 4. Download Prometheus

Chuyển tới thư mục tạm:

```
cd /tmp
```

Download Prometheus version `3.7.3`:

```
wget https://github.com/prometheus/prometheus/releases/download/v3.7.3/prometheus-3.7.3.linux-amd64.tar.gz
```

Giải nén:

```
tar -xvf prometheus-3.7.3.linux-amd64.tar.gz
```

Truy cập thư mục:

```
cd prometheus-3.7.3.linux-amd64
```

---

## 5. Cài đặt Prometheus Binary

Copy Prometheus binary:

```
sudo cp prometheus /usr/local/bin/
```

Copy Promtool:

```
sudo cp promtool /usr/local/bin/
```

Phân quyền:

```
sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool
```

Kiểm tra phiên bản:

```
prometheus --version
promtool --version
```

---

## 6. Cấu hình Prometheus

Copy file cấu hình mặc định:

```
sudo cp prometheus.yml /etc/prometheus/prometheus.yml
```

Phân quyền:

```
sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
```

Mở file cấu hình:

```
sudo nano /etc/prometheus/prometheus.yml
```

Cấu hình:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets:
          - "localhost:9090"

  - job_name: "linux-servers"
    static_configs:
      - targets:
          - "192.168.10.11:9100"
          - "192.168.10.12:9100"

  - job_name: "windows-server"
    static_configs:
      - targets:
          - "192.168.10.13:9182"
```

---

## 7. Kiểm tra Prometheus Configuration

Kiểm tra syntax:

```
promtool check config /etc/prometheus/prometheus.yml
```

Kết quả mong đợi:

```
SUCCESS: /etc/prometheus/prometheus.yml is valid prometheus config file syntax
```

---

## 8. Tạo Systemd Service

Tạo service file:

```
sudo nano /etc/systemd/system/prometheus.service
```

Nội dung:

```
[Unit]
Description=Prometheus Monitoring System
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple

ExecStart=/usr/local/bin/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/var/lib/prometheus \
  --web.listen-address=0.0.0.0:9090

Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

---

## 9. Khởi động Prometheus

Reload systemd:

```
sudo systemctl daemon-reload
```

Enable và start Prometheus:

```
sudo systemctl enable --now prometheus
```

Kiểm tra trạng thái:

```
sudo systemctl status prometheus --no-pager
```

---

## 10. Kiểm tra Prometheus Health

Kiểm tra health endpoint:

```
curl http://localhost:9090/-/healthy
```

Kết quả mong đợi:

```
Prometheus Server is Healthy.
```

Kiểm tra port:

```
ss -lntp | grep 9090
```

Prometheus phải listen trên:

```
*:9090
```

---

## 11. Truy cập Prometheus Web UI

Truy cập:

```
http://192.168.10.10:9090
```

Trang Targets:

```
http://192.168.10.10:9090/targets
```

Các target dự kiến:

| Target | Port | Loại |
|---|---:|---|
| localhost | 9090 | Prometheus |
| WEB01 | 9100 | Node Exporter |
| APP01 | 9100 | Node Exporter |
| WIN01 | 9182 | Windows Exporter |

---

## 12. Kiểm tra Targets

WEB01:

```
curl http://192.168.10.11:9100/metrics | head
```

APP01:

```
curl http://192.168.10.12:9100/metrics | head
```

WIN01:

```
curl http://192.168.10.13:9182/metrics | head
```

 exporter hoạt động bình thường, Prometheus hiển thị trạng thái:

```
UP
```

---

## 13. Kết quả

Prometheus đã được cài đặt thành công trên MON01 với:

- Version `3.7.3`
- Systemd service hoạt động
- Port `9090` đang listen
- Prometheus health check thành công
- WEB01 được scrape qua Node Exporter
- WIN01 được scrape qua Windows Exporter
- APP01 đã được cấu hình làm target và đang chờ Node Exporter được triển khai

Prometheus hiện sẵn sàng cho bước tiếp theo là cấu hình Grafana, Alertmanager và Alert Rules.
