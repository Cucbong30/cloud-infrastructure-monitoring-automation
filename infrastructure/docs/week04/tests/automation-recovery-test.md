# Automation Recovery Test - Week 4

## Mục tiêu

Kiểm tra khả năng recovery service bằng Ansible trên ba môi trường khác nhau:

- Linux service trên WEB01.
- Docker container trên APP01.
- Windows service trên WIN01.

Các test được thực hiện sau khi kết nối Portal với MON01 và MON01 đã có thể điều khiển target server bằng SSH hoặc WinRM.

---

## Test 1 - WEB01 Nginx Recovery

### Trạng thái ban đầu

Nginx trên WEB01 được dừng:

```
sudo systemctl stop nginx
```

Kiểm tra:

```
systemctl status nginx
```

Kết quả:

```
inactive
```

Port 80 không phản hồi.

Portal hiển thị WEB01 ở trạng thái DEGRADED.

### Recovery

Automation chạy playbook:

```
restart-nginx.yml
```

Luồng:

```
Portal
→ MON01
→ Ansible
→ WEB01
→ restart nginx
```

### Kiểm tra sau recovery

Kiểm tra từ MON01:

```
curl -I http://192.168.10.11
```

Kết quả mong đợi:

```
HTTP/1.1 200 OK
```

Nginx hoạt động lại và Portal hiển thị WEB01 HEALTHY.

---

## Test 2 - APP01 Docker Container Recovery

### Trạng thái ban đầu

Container `app01-web` được dừng:

```bash
docker stop app01-web
```

Kiểm tra:

```bash
docker ps -a
```

Container ở trạng thái Exited.

Port 8080 không phản hồi và Portal hiển thị APP01 DEGRADED.

### Recovery

Automation chạy playbook:

```
restart-app-container.yml
```

Luồng:

```
Portal
→ MON01
→ Ansible
→ APP01
→ start app01-web
```

### Kiểm tra sau recovery

Kiểm tra từ MON01:

```
curl -I http://192.168.10.12:8080
```

Kết quả mong đợi:

```
HTTP/1.1 200 OK
```

Container hoạt động lại và APP01 quay về HEALTHY.

---

## Test 3 - WIN01 Windows Exporter Recovery

### Trạng thái ban đầu

Trên WIN01:

```
Stop-Service windows_exporter
Get-Service windows_exporter
```

Kết quả:

```
Status: Stopped
```

WinRM vẫn hoạt động trên port 5985 để MON01 còn có thể quản lý WIN01.

Port 9182 không phản hồi và Portal hiển thị WIN01 ở trạng thái DEGRADED.

### Recovery

Automation chạy playbook:

```
restart-windows-exporter.yml
```

Luồng:

```
Portal
→ MON01
→ Ansible
→ WinRM
→ WIN01
→ start windows_exporter
```

### Kiểm tra sau recovery

Kiểm tra từ MON01:

```
curl http://192.168.10.13:9182/metrics | head
```

Sau khi recovery, endpoint `/metrics` trả lại dữ liệu của Windows Exporter.

Portal hiển thị WIN01 HEALTHY.

---

## Kết quả

Cả ba test case đều recovery thành công.

| Test | Failure | Management Channel | Recovery | Kết quả |
|---|---|---|---|---|
| WEB01 | Nginx down | SSH | Restart Nginx | Success |
| APP01 | app01-web down | SSH | Start container | Success |
| WIN01 | windows_exporter down | WinRM | Start service | Success |

Qua ba test có thể xác nhận MON01 đã hoạt động như Ansible Controller và có thể xử lý automation trên cả Linux, Docker và Windows Server.

---

## Nhận xét

Automation hiện tại chỉ recovery được khi management channel vẫn còn hoạt động.

Ví dụ:

- Nginx down nhưng SSH còn hoạt động → recovery được.
- Container down nhưng SSH còn hoạt động → recovery được.
- Windows Exporter down nhưng WinRM còn hoạt động → recovery được.
- SSH down → MON01 không thể điều khiển Linux target qua SSH.
- WinRM down → MON01 không thể điều khiển WIN01 qua WinRM.
- VM down hoàn toàn → cần recovery ở tầng hypervisor hoặc cloud.

Đây là giới hạn của service-level remediation hiện tại và sẽ được xem xét ở các giai đoạn tiếp theo.
