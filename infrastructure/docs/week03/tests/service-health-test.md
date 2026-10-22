# Week 3 - Service Health Validation

## 1. Mục tiêu kiểm thử

Kiểm tra khả năng giám sát trạng thái dịch vụ trên các server trong hệ thống.

Mục tiêu là xác minh Portal có thể phân biệt được:

- Server vẫn hoạt động bình thường.
- Monitoring Agent vẫn kết nối được.
- Một dịch vụ quan trọng trên server bị dừng.
- Trạng thái tổng thể của server chuyển từ `HEALTHY` sang `DEGRADED`.
- Sau khi dịch vụ được khởi động lại, trạng thái server quay về `HEALTHY`.

---

## 2. Môi trường kiểm thử

| Server | IP Address | Monitoring Agent | Service được kiểm thử |
|---|---|---|---|
| MON01 | 192.168.10.10 | Node Exporter :9100 | Grafana :3000 |
| WEB01 | 192.168.10.11 | Node Exporter :9100 | Nginx :80 |
| APP01 | 192.168.10.12 | Node Exporter :9100 | Application Container :8080 |
| WIN01 | 192.168.10.13 | Windows Exporter :9182 | WinRM :5985 |

---

# 3. Test Case 1 - WEB01 Nginx Down

## Mục tiêu

Kiểm tra trường hợp WEB01 vẫn hoạt động và Node Exporter vẫn UP nhưng dịch vụ Nginx bị dừng.

## Thực hiện

Trên WEB01:

```
sudo systemctl stop nginx
```

Kiểm tra trạng thái:

```
sudo systemctl status nginx --no-pager
```

Kiểm tra Node Exporter:

```
curl http://localhost:9100/metrics | head
```

Kiểm tra Nginx từ server khác:

```
curl http://192.168.10.11
```

## Kết quả mong muốn

- WEB01 vẫn reachable.
- Node Exporter vẫn UP.
- Metrics của WEB01 vẫn được Prometheus thu thập.
- Nginx port 80 không phản hồi.
- Portal hiển thị:

```
WEB01 = DEGRADED
```

## Khôi phục

```
sudo systemctl start nginx
```

Kiểm tra lại:

```
sudo systemctl status nginx --no-pager
```

## Kết quả sau khôi phục

```
WEB01 = HEALTHY
```

## Kết quả

**PASS**

---

# 4. Test Case 2 - APP01 Application Container Down

## Mục tiêu

Kiểm tra trường hợp APP01 vẫn hoạt động nhưng application container bị dừng.

## Thực hiện

Kiểm tra container hiện tại:

```
docker ps
```

Dừng application container:

```
docker stop app01-web
```

Kiểm tra lại:

```
docker ps -a
```

Kiểm tra Node Exporter:

```
curl http://localhost:9100/metrics | head
```

Kiểm tra application endpoint từ server khác:

```
curl http://192.168.10.12:8080
```

## Kết quả mong muốn

- APP01 vẫn reachable.
- Node Exporter vẫn UP.
- Host metrics vẫn được Prometheus thu thập.
- Application port 8080 không phản hồi.
- Portal hiển thị:

```
APP01 = DEGRADED
```

## Khôi phục

```
docker start app01-web
```

Kiểm tra:

```
docker ps
```

## Kết quả sau khôi phục

```
APP01 = HEALTHY
```

## Kết quả

**PASS**

---

# 5. Test Case 3 - MON01 Grafana Down

## Mục tiêu

Kiểm tra trường hợp MON01 vẫn hoạt động nhưng Grafana bị dừng.

Prometheus, Alertmanager và Node Exporter vẫn tiếp tục hoạt động.

## Thực hiện

Dừng Grafana:

```
sudo systemctl stop grafana-server
```

Kiểm tra trạng thái:

```
sudo systemctl status grafana-server --no-pager
```

Kiểm tra port Grafana:

```
curl -I http://localhost:3000
```

Kiểm tra các dịch vụ monitoring khác:

```
sudo systemctl status prometheus --no-pager
sudo systemctl status alertmanager --no-pager
sudo systemctl status node_exporter --no-pager
```

## Kết quả mong muốn

- MON01 vẫn reachable.
- Node Exporter vẫn UP.
- Prometheus vẫn UP.
- Alertmanager vẫn UP.
- Grafana port 3000 không phản hồi.
- Portal hiển thị:

```text
MON01 = DEGRADED
```

## Khôi phục

```
sudo systemctl start grafana-server
```

Kiểm tra:

```
sudo systemctl status grafana-server --no-pager
```

Kiểm tra port:

```
curl -I http://localhost:3000
```

## Kết quả sau khôi phục

```
MON01 = HEALTHY
```

## Kết quả

**PASS**

---

# 6. Test Case 4 - WIN01 WinRM Down

## Mục tiêu

Kiểm tra trường hợp WIN01 vẫn hoạt động và Windows Exporter vẫn UP nhưng WinRM bị dừng.

## Thực hiện

Trên WIN01 PowerShell:

```
Stop-Service WinRM
```

Kiểm tra trạng thái:

```
Get-Service WinRM
```

Kiểm tra Windows Exporter:

```
Test-NetConnection 192.168.10.13 -Port 9182
```

Kiểm tra WinRM:

```
Test-NetConnection 192.168.10.13 -Port 5985
```

Có thể kiểm tra từ Application Laptop:

```
Test-NetConnection 192.168.10.13 -Port 5985
```

## Kết quả mong muốn

- WIN01 vẫn reachable.
- Windows Exporter port 9182 vẫn UP.
- Metrics của WIN01 vẫn được Prometheus thu thập.
- WinRM port 5985 không phản hồi.
- Portal hiển thị:

```
WIN01 = DEGRADED
```

## Khôi phục

```
Start-Service WinRM
```

Kiểm tra:

```
Get-Service WinRM
```

Kiểm tra port:

```
Test-NetConnection 192.168.10.13 -Port 5985
```

## Kết quả sau khôi phục

```
WIN01 = HEALTHY
```

## Kết quả

**PASS**

---

# 7. Kết quả tổng hợp

| Test Case | Failure Scenario | Expected State | Recovery State | Result |
|---|---|---|---|---|
| TC01 | WEB01 Nginx Down | DEGRADED | HEALTHY | PASS |
| TC02 | APP01 Application Container Down | DEGRADED | HEALTHY | PASS |
| TC03 | MON01 Grafana Down | DEGRADED | HEALTHY | PASS |
| TC04 | WIN01 WinRM Down | DEGRADED | HEALTHY | PASS |

---

# 8. Kết luận

Các test case đã xác minh hệ thống có khả năng phân biệt giữa:

```
Server Down
```

và:

```
Server vẫn hoạt động nhưng một dịch vụ quan trọng bị lỗi
```

Trong cả bốn trường hợp kiểm thử:

- Monitoring Agent vẫn hoạt động.
- Server vẫn reachable.
- Một service cụ thể bị dừng.
- Portal xác định trạng thái server là `DEGRADED`.
- Sau khi service được khởi động lại, server quay về trạng thái `HEALTHY`.

Service health monitoring hoạt động đúng với thiết kế của hệ thống trong Week 3.
