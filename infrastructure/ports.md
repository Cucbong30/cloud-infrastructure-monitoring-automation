# Plan các cổng dịch vụ

| Dịch vụ | Port | Nguồn | Đích | Mục đích |
|---|---:|---|---|---|
| SSH | 22 | MON01 | WEB01, APP01 | Quản trị Linux và thực thi Ansible |
| SSH | 22 | Administrator | MGMT01 | Quản trị Management Gateway |
| WinRM | 5985/5986 | MON01 | WIN01 | Quản trị Windows và thực thi automation |
| Prometheus | 9090 | Flask Portal / Grafana / Administrator | MON01 | Truy vấn metrics và trạng thái monitoring |
| Grafana | 3000 | User / Administrator | MON01 | Truy cập dashboard giám sát |
| Alertmanager | 9093 | Prometheus / Administrator | MON01 | Quản lý và kiểm tra cảnh báo |
| Node Exporter | 9100 | MON01 | WEB01, APP01 | Thu thập metrics Linux |
| Windows Exporter | 9182 | MON01 | WIN01 | Thu thập metrics Windows |
| Flask Web Portal | 5000 | User | Application Laptop | Truy cập Operations Portal |
| Flask Alert Webhook | 5000 | MON01 / Alertmanager | Application Laptop | Gửi cảnh báo từ Alertmanager tới Portal |
| HTTP | 80 | User / MON01 | WEB01 | Kiểm tra Web Service |
| HTTPS | 443 | User / MON01 | WEB01 | Truy cập Web Service bảo mật |
| Application Service | 8080 | User / MON01 | APP01 | Kiểm tra application/container workload |
| Tailscale | UDP 41641* | Tailscale Nodes | MGMT01 / Application Laptop | Overlay network và remote connectivity |

## Ghi chú

- MGMT01 đóng vai trò Tailscale Subnet Router cho mạng Lab `192.168.10.0/24`.
- Flask Web Portal chạy độc lập trên laptop của thành viên Application trong giai đoạn phát triển và tích hợp.
- Portal truy cập Prometheus trên MON01 thông qua đường kết nối Tailscale.
- Alertmanager gửi webhook cảnh báo từ MON01 tới Flask Portal.
- MON01 vẫn là Ansible Controller để thực thi automation tới các target server.
- Các port quản trị và monitoring chỉ nên được cho phép từ các nguồn cần thiết trong môi trường Lab.
- `UDP 41641` là cổng kết nối trực tiếp thường được Tailscale sử dụng; Tailscale cũng có thể sử dụng các cơ chế kết nối khác khi direct connection không khả dụng.
