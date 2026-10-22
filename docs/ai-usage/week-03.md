# AI Usage Documentation - Week 3

## 1. Infrastructure Monitoring Setup

**Prompt**

> Hướng dẫn triển khai Prometheus, Node Exporter, Grafana và Alertmanager trên môi trường lab để giám sát Linux/Windows server.

**AI Output**

AI hỗ trợ đề xuất cấu hình, service, scrape target, alert rule và cách kiểm tra trạng thái UP/DOWN.

**Nhóm tự thực hiện**

- Cài đặt và cấu hình các thành phần trên máy ảo.
- Kiểm tra Prometheus targets.
- Kiểm tra Grafana dashboard.
- Test Alertmanager bằng cách dừng Node Exporter.
- Xác nhận alert chuyển Pending → Firing → Resolved.

---

## 2. Service Health Testing

**Prompt**

> Đề xuất các test case để kiểm tra trường hợp server vẫn online nhưng một service bị down.

**AI Output**

AI đề xuất test các dịch vụ như Nginx, application container, Grafana và WinRM với trạng thái mong muốn là `DEGRADED`.

**Nhóm tự thực hiện**

- WEB01: Nginx Down.
- APP01: Application Container Down.
- MON01: Grafana Down.
- WIN01: WinRM Down.

Kết quả được kiểm tra trực tiếp trên Operations Portal và các service được khôi phục sau khi test.

---

## 3. Prometheus Configuration Troubleshooting

**Prompt**

> Prometheus báo lỗi `found multiple scrape configs with job name "linux-servers"`. Nguyên nhân là gì và sửa như thế nào?

**AI Output**

AI xác định cấu hình có hai `job_name: "linux-servers"` bị trùng và đề xuất gộp các target Linux vào một scrape job duy nhất.

**Nhóm tự thực hiện**

- Kiểm tra lại `prometheus.yml`.
- Xóa cấu hình bị trùng.
- Kiểm tra bằng `promtool`.
- Restart Prometheus và xác nhận toàn bộ target trở lại trạng thái `UP`.
