# Plan các cổng dịch vụ

| Dịch vụ | Port | Nguồn | Đích | Mục đích |
|---|---:|---|---|---|
| SSH | 22 | MON01 | WEB01, APP01 | Quản trị Linux và Ansible |
| WinRM | 5985/5986 | MON01 | WIN01 | Quản trị Windows |
| Prometheus | 9090 | Web Portal / Grafana | MON01 | Truy vấn metrics |
| Grafana | 3000 | User | MON01 | Dashboard giám sát |
| Alertmanager | 9093 | Prometheus | MON01 | Quản lý cảnh báo |
| Node Exporter | 9100 | MON01 | WEB01, APP01 | Thu thập metrics Linux |
| Windows Exporter | 9182 | MON01 | WIN01 | Thu thập metrics Windows |
| Flask Web Portal | 5000 | User | MON01 | Truy cập portal |
| HTTP | 80 | User / MON01 | WEB01 | Kiểm tra Web Service |
| HTTPS | 443 | User / MON01 | WEB01 | Truy cập Web Service bảo mật |
