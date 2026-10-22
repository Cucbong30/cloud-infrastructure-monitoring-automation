# AI Usage Documentation - Week 3

## 1. Công cụ AI sử dụng

Trong Tuần 3, nhóm sử dụng **ChatGPT** để hỗ trợ quá trình triển khai, kiểm thử và tài liệu hóa hệ thống.

AI được sử dụng như một công cụ hỗ trợ kỹ thuật. Các cấu hình, lệnh và kết quả đều được nhóm trực tiếp kiểm tra trên môi trường lab trước khi đưa vào hệ thống hoặc tài liệu dự án.

---

## 2. Phạm vi sử dụng AI

Trong Tuần 3, AI được sử dụng để hỗ trợ các nội dung sau:

### Thiết kế và rà soát kiến trúc

- Rà soát kiến trúc monitoring và remote management.
- Phân tách vai trò giữa:
  - MGMT01
  - MON01
  - WEB01
  - APP01
  - WIN01
  - Application Portal
- Đề xuất bổ sung MGMT01 làm Tailscale Subnet Router.
- Rà soát các failure scenario và cách hệ thống phản ứng khi từng thành phần gặp lỗi.

### Hỗ trợ cấu hình hạ tầng

AI hỗ trợ tham khảo các bước cấu hình cho:

- Tailscale Subnet Router trên MGMT01.
- IP forwarding trên Linux.
- Prometheus trên MON01.
- Node Exporter trên các Linux server.
- Grafana.
- Alertmanager.
- Prometheus alert rules.
- Docker và các service phục vụ việc kiểm thử.

Các lệnh được thực hiện và kiểm tra trực tiếp trên các máy ảo trước khi ghi nhận kết quả.

### Troubleshooting

AI được sử dụng để hỗ trợ phân tích một số lỗi trong quá trình triển khai, bao gồm:

- Prometheus configuration bị trùng `job_name`.
- Prometheus target không UP.
- Node Exporter chưa chạy trên một số server.
- Kiểm tra kết nối service qua các port.
- Phân biệt giữa host failure và service failure.
- Kiểm tra trạng thái Grafana, Nginx, Docker container và WinRM.
- Phân tích trường hợp Windows Exporter không trả đầy đủ một số metric trên Portal.

### Thiết kế logic trạng thái hệ thống

AI hỗ trợ đề xuất mô hình trạng thái:

- `HEALTHY`
- `DEGRADED`
- `UNREACHABLE`

Logic này được sử dụng để phân biệt giữa:

- Server hoạt động bình thường.
- Server vẫn hoạt động nhưng một service bị lỗi.
- Server không thể truy cập.

### Hỗ trợ kiểm thử

AI hỗ trợ xây dựng các test scenario cho service health monitoring:

- WEB01 - Nginx Down.
- APP01 - Application Container Down.
- MON01 - Grafana Down.
- WIN01 - WinRM Down.

Nhóm trực tiếp thực hiện các test case và xác nhận kết quả trên Operations Portal.

### Hỗ trợ tài liệu hóa

AI hỗ trợ:

- Chuẩn hóa cấu trúc tài liệu Week 3.
- Viết nháp tài liệu setup.
- Chuẩn hóa test case.
- Đề xuất tên file và commit message.
- Cải thiện cách trình bày nội dung Markdown.

---

## 3. Nội dung do nhóm trực tiếp thực hiện

Nhóm trực tiếp thực hiện các công việc sau:

- Tạo và cấu hình các máy ảo.
- Cấu hình network.
- Cài đặt MGMT01.
- Cấu hình Tailscale.
- Cài đặt Prometheus.
- Cài đặt Node Exporter.
- Cài đặt Grafana.
- Cài đặt Alertmanager.
- Cấu hình alert rule.
- Cài đặt và kiểm thử Docker.
- Thực hiện các failure scenario.
- Kiểm tra kết quả trên Prometheus, Grafana, Alertmanager và Operations Portal.
- Chụp screenshot làm evidence.
- Review và điều chỉnh các nội dung do AI đề xuất trước khi sử dụng.

---

## 4. Nguyên tắc sử dụng AI

Nhóm không sử dụng kết quả từ AI một cách tự động.

Mọi nội dung kỹ thuật do AI hỗ trợ đều được:

1. Review trước khi áp dụng.
2. Thực hiện trên môi trường lab.
3. Kiểm tra kết quả thực tế.
4. Điều chỉnh nếu không phù hợp với kiến trúc dự án.
5. Chỉ đưa vào repository khi đã được xác nhận hoạt động.

AI không thay thế việc triển khai, kiểm thử hoặc đánh giá kỹ thuật của nhóm.

---

## 5. Kết luận

Trong Tuần 3, AI chủ yếu được sử dụng để hỗ trợ troubleshooting, rà soát kiến trúc, xây dựng test scenario và chuẩn hóa tài liệu.

Các thành phần hạ tầng và kết quả kiểm thử được nhóm trực tiếp triển khai và xác nhận trên môi trường thực tế của dự án.
