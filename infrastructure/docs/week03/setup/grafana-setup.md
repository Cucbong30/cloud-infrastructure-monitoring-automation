# Grafana Setup on MON01

## 1. Mục tiêu

Cài đặt Grafana trên `MON01` để trực quan hóa metrics được Prometheus thu thập từ các server trong môi trường Lab.

Grafana sử dụng Prometheus trên cùng MON01 làm data source.

---

## 2. Cài đặt Grafana

Cập nhật package:

```
sudo apt update
sudo apt install -y apt-transport-https software-properties-common wget
```

Tạo thư mục lưu GPG key:

```
sudo mkdir -p /etc/apt/keyrings
```

Thêm Grafana GPG key:

```
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
```

Thêm Grafana repository:

```
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
```

Cập nhật package list:

```
sudo apt update
```

Cài Grafana:

```
sudo apt install grafana -y
```

Kiểm tra phiên bản:

```
grafana-server -v
```

Version được sử dụng:

```
Grafana 13.2.4
```

---

## 3. Khởi động Grafana

Reload systemd:

```
sudo systemctl daemon-reload
```

Enable và start Grafana:

```
sudo systemctl enable --now grafana-server
```

Kiểm tra trạng thái:

```
sudo systemctl status grafana-server --no-pager
```

Kiểm tra port:

```
ss -lntp | grep 3000
```

Grafana sử dụng port:

```
3000
```

---

## 4. Truy cập Grafana

Truy cập:

```
http://192.168.10.10:3000
```

Tài khoản mặc định:

```
Username: admin
Password: admin
```


---

## 5. Cấu hình Prometheus Data Source

Trong Grafana:

```
Connections
→ Data sources
→ Add data source
→ Prometheus
```

Prometheus Server URL:

```
http://localhost:9090
```

Prometheus và Grafana cùng chạy trên MON01 nên sử dụng địa chỉ localhost.

Sau khi cấu hình, sử dụng chức năng:

```
Save & Test
```

để xác nhận Grafana có thể truy vấn Prometheus API.

---

## 6. Import Dashboard

Sử dụng dashboard template:

```
Node Exporter Full
```

Dashboard ID:

```
1860
```

Thực hiện:

```
Dashboards
→ New
→ Import
→ Dashboard ID: 1860
```

Chọn Prometheus làm data source và import dashboard.

---

## 7. Metrics được hiển thị

Dashboard Node Exporter Full cung cấp các thông tin giám sát như:

- CPU Usage
- Memory Usage
- Disk Usage
- Network Traffic
- System Load
- Uptime

Các Linux server có thể lựa chọn thông qua dashboard variables:

- WEB01
- APP01

---

## 8. Kiểm tra Dashboard

Dashboard đã hiển thị metrics thực tế của WEB01 từ:

```
192.168.10.11:9100
```

Thông tin hiển thị bao gồm:

- CPU
- RAM
- Disk
- Network
- Uptime

Điều này xác nhận luồng monitoring:

```
WEB01
→ Node Exporter
→ Prometheus
→ Grafana
```

hoạt động thành công.

---

## 9. Kết quả

Grafana đã được cài đặt và cấu hình thành công trên MON01.

Kết quả:

- Grafana service hoạt động
- Port `3000` đang listen
- Prometheus được cấu hình làm data source
- Dashboard `Node Exporter Full` được import thành công
- Metrics của WEB01 và APP01 có thể được trực quan hóa trên Grafana
