# APP01 Node Exporter Setup

## 1. Mục tiêu

Cài đặt Node Exporter trên `APP01` để Prometheus trên `MON01` có thể thu thập metrics hệ thống Linux.

APP01 sử dụng địa chỉ:

`192.168.10.12`

Node Exporter sử dụng port:

`9100`

---

## 2. Tải Node Exporter

Chuyển tới thư mục tạm:

```
cd /tmp
```

Tải Node Exporter version `1.9.1`:

```
wget https://github.com/prometheus/node_exporter/releases/download/v1.9.1/node_exporter-1.9.1.linux-amd64.tar.gz
```

Giải nén:

```
tar -xvf node_exporter-1.9.1.linux-amd64.tar.gz
```

---

## 3. Cài đặt Node Exporter Binary

Copy binary vào `/usr/local/bin/`:

```
sudo cp node_exporter-1.9.1.linux-amd64/node_exporter /usr/local/bin/
```

Tạo service account:

```
sudo useradd --no-create-home --shell /bin/false node_exporter
```

Phân quyền binary:

```
sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter
```

Kiểm tra phiên bản:

```
node_exporter --version
```

---

## 4. Tạo Systemd Service

Tạo file service:

```
sudo nano /etc/systemd/system/node_exporter.service
```

Nội dung:

```
[Unit]
Description=Prometheus Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

---

## 5. Khởi động Node Exporter

Reload systemd:

```
sudo systemctl daemon-reload
```

Enable và start Node Exporter:

```
sudo systemctl enable --now node_exporter
```

Kiểm tra trạng thái:

```
sudo systemctl status node_exporter --no-pager
```

---

## 6. Kiểm tra Port 9100

Kiểm tra Node Exporter đang listen:

```
ss -lntp | grep 9100
```

Kết quả mong đợi:

```text
*:9100
```

---

## 7. Kiểm tra Metrics trên APP01

Kiểm tra metrics trực tiếp trên APP01:

```
curl http://localhost:9100/metrics | head
```


## 8. Kiểm tra từ MON01

Trên `MON01`, kiểm tra kết nối tới Node Exporter của APP01:

```
curl http://192.168.10.12:9100/metrics | head
```

MON01 có thể truy cập Node Exporter của APP01 thành công.

---

## 9. Kiểm tra trên Prometheus

Truy cập Prometheus Targets:

```
http://192.168.10.10:9090/targets
```

Sau khi Node Exporter trên APP01 hoạt động, target:

```
192.168.10.12:9100
```

 có trạng thái:

```
UP
```

Các target hiện tại:

| Target | Trạng thái mong đợi |
|---|---|
| localhost:9090 | UP |
| 192.168.10.11:9100 | UP |
| 192.168.10.12:9100 | UP |
| 192.168.10.13:9182 | UP |

---

## 10. Kết quả

Node Exporter đã được cài đặt thành công trên APP01.

Kết quả:

- Node Exporter version `1.9.1`
- Systemd service hoạt động
- Port `9100` đang listen
- Metrics có thể truy cập từ APP01
- MON01 có thể truy cập metrics qua `192.168.10.12:9100`
- Prometheus hiển thị APP01 ở trạng thái `UP`
- Toàn bộ các monitoring target hiện tại đã được Prometheus scrape thành công
