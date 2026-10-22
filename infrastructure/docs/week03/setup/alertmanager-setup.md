# Alertmanager Setup on MON01

## 1. Mục tiêu

Cài đặt Alertmanager trên `MON01`, kết nối với Prometheus và kiểm tra luồng cảnh báo khi một monitoring target bị mất kết nối.

Luồng kiểm thử:

`WEB01 Node Exporter → Prometheus → Alert Rule → Alertmanager`

---

## 2. Cài đặt Alertmanager

Chuyển tới thư mục tạm:

```
cd /tmp
```

Tải Alertmanager version `0.28.1`:

```
wget https://github.com/prometheus/alertmanager/releases/download/v0.28.1/alertmanager-0.28.1.linux-amd64.tar.gz
```

Giải nén:

```
tar -xvf alertmanager-0.28.1.linux-amd64.tar.gz
```

Truy cập thư mục:

```
cd alertmanager-0.28.1.linux-amd64
```

Copy binary:

```
sudo cp alertmanager /usr/local/bin/
sudo cp amtool /usr/local/bin/
```

Tạo service account:

```
sudo useradd --no-create-home --shell /bin/false alertmanager
```

Tạo thư mục cấu hình và dữ liệu:

```
sudo mkdir -p /etc/alertmanager
sudo mkdir -p /var/lib/alertmanager
```

Phân quyền:

```
sudo chown alertmanager:alertmanager /usr/local/bin/alertmanager
sudo chown alertmanager:alertmanager /usr/local/bin/amtool
sudo chown -R alertmanager:alertmanager /etc/alertmanager
sudo chown -R alertmanager:alertmanager /var/lib/alertmanager
```

Kiểm tra phiên bản:

```
alertmanager --version
amtool --version
```

---

## 3. Cấu hình Alertmanager

Tạo file cấu hình:

```
sudo nano /etc/alertmanager/alertmanager.yml
```

Nội dung:

```
global:
  resolve_timeout: 5m

route:
  receiver: "default"

receivers:
  - name: "default"
```

Kiểm tra cấu hình:

```
amtool check-config /etc/alertmanager/alertmanager.yml
```

---

## 4. Tạo Systemd Service

Tạo service file:

```
sudo nano /etc/systemd/system/alertmanager.service
```

Nội dung:

```
[Unit]
Description=Prometheus Alertmanager
Wants=network-online.target
After=network-online.target

[Service]
User=alertmanager
Group=alertmanager
Type=simple

ExecStart=/usr/local/bin/alertmanager \
  --config.file=/etc/alertmanager/alertmanager.yml \
  --storage.path=/var/lib/alertmanager \
  --web.listen-address=0.0.0.0:9093

Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Reload systemd:

```
sudo systemctl daemon-reload
```

Enable và start Alertmanager:

```
sudo systemctl enable --now alertmanager
```

Kiểm tra service:

```
sudo systemctl status alertmanager --no-pager
```

Kiểm tra port:

```
ss -lntp | grep 9093
```

Kiểm tra health endpoint:

```
curl http://localhost:9093/-/healthy
```

---

## 5. Kết nối Prometheus với Alertmanager

Cập nhật:

```
sudo nano /etc/prometheus/prometheus.yml
```

Thêm:

```
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - "localhost:9093"

rule_files:
  - "/etc/prometheus/alert_rules.yml"
```

---

## 6. Tạo Alert Rule

Tạo file:

```
sudo nano /etc/prometheus/alert_rules.yml
```

Nội dung:

```
groups:
  - name: infrastructure-alerts
    rules:
      - alert: InstanceDown
        expr: up == 0
        for: 30s
        labels:
          severity: critical
        annotations:
          summary: "Instance {{ $labels.instance }} is down"
          description: "Prometheus cannot scrape {{ $labels.instance }} for more than 30 seconds."
```

Phân quyền:

```
sudo chown prometheus:prometheus /etc/prometheus/alert_rules.yml
```

Kiểm tra rule:

```
promtool check rules /etc/prometheus/alert_rules.yml
```

Kiểm tra Prometheus config:

```
promtool check config /etc/prometheus/prometheus.yml
```

Restart Prometheus:

```
sudo systemctl restart prometheus
```

Kiểm tra service:

```
sudo systemctl status prometheus --no-pager
```

---

## 7. Kiểm tra Alert Rule

Truy cập:

```
http://192.168.10.10:9090/alerts
```

Rule:

```
InstanceDown
```

ở trạng thái bình thường:

```
INACTIVE
```

---

## 8. Kiểm thử InstanceDown

Dừng Node Exporter trên WEB01:

```
sudo systemctl stop node_exporter
```

Prometheus phát hiện:

```
192.168.10.11:9100
```

Alert chuyển qua:

```
PENDING
```

và sau 30 giây:

```
FIRING
```

Alertmanager nhận alert với các thông tin:

```
alertname="InstanceDown"
instance="192.168.10.11:9100"
job="linux-servers"
severity="critical"
```

---

## 9. Khôi phục WEB01

Khởi động lại Node Exporter:

```
sudo systemctl start node_exporter
```

Kiểm tra:

```
sudo systemctl status node_exporter --no-pager
```

Sau khi Prometheus scrape lại thành công, alert `InstanceDown` trở về:

```
INACTIVE
```

Alert không còn active trên Alertmanager.

---

## 10. Kết quả

Alertmanager đã được cài đặt và kết nối thành công với Prometheus.

Luồng kiểm thử đã xác nhận:

`WEB01 Node Exporter Down → Prometheus Detect → InstanceDown FIRING → Alertmanager Receive → WEB01 Recover → Alert Resolved`

Hệ thống monitoring hiện đã có khả năng phát hiện sự cố và chuyển cảnh báo từ Prometheus sang Alertmanager.
