# Tailscale Setup

## 1. Mục tiêu

Cài đặt Tailscale trên `MGMT01` và cấu hình máy chủ này làm Subnet Router để laptop bên ngoài có thể truy cập mạng Lab `192.168.10.0/24`.

Luồng kết nối:

`Application Laptop → Tailscale → MGMT01 → 192.168.10.0/24`

---

## 2. Cài đặt Tailscale

Cập nhật package:

```
sudo apt update
```

Cài đặt Tailscale:

```
curl -fsSL https://tailscale.com/install.sh | sh
```

Kiểm tra phiên bản:

```
tailscale version
```

---

## 3. Đăng nhập Tailscale

Khởi tạo Tailscale:

```
sudo tailscale up
```

Sau khi chạy lệnh, hệ thống cung cấp URL xác thực.

Mở URL trên trình duyệt và đăng nhập bằng tài khoản Tailscale Personal.

Kiểm tra trạng thái kết nối:

```
tailscale status
```

Kiểm tra địa chỉ Tailscale IPv4:

```
tailscale ip -4
```

---

## 4. Bật IP Forwarding

Tạo cấu hình IP forwarding:

```
sudo tee /etc/sysctl.d/99-tailscale.conf > /dev/null <<'EOF'
net.ipv4.ip_forward = 1
EOF
```

Áp dụng cấu hình:

```
sudo sysctl --system
```

Kiểm tra:

```
sysctl net.ipv4.ip_forward
```

Kết quả mong đợi:

```
net.ipv4.ip_forward = 1
```

---

## 5. Cấu hình Tailscale Subnet Router

Cấu hình MGMT01 quảng bá mạng Lab:

```
sudo tailscale set --advertise-routes=192.168.10.0/24
```

Kiểm tra trạng thái:

```
tailscale status
```

---

## 6. Approve Subnet Route

Truy cập Tailscale Admin Console.

Chọn thiết bị:

`MGMT01`

Enable / Approve route:

`192.168.10.0/24`

Sau khi route được bật, các thiết bị trong cùng Tailnet có thể truy cập mạng Lab thông qua MGMT01.

---

## 7. Kết nối từ Application Laptop

Cài Tailscale Client trên laptop Application và đăng nhập bằng cùng tài khoản Tailscale.

Kiểm tra trạng thái:

```powershell
tailscale status
```

Kiểm tra kết nối tới MGMT01:

```powershell
ping 192.168.10.5
```

Kiểm tra MON01:

```powershell
ping 192.168.10.10
```

Kiểm tra WEB01:

```powershell
ping 192.168.10.11
```

Kiểm tra APP01:

```powershell
ping 192.168.10.12
```

Kiểm tra WIN01:

```powershell
ping 192.168.10.13
```

---

## 8. Kiểm tra Service Connectivity

Kiểm tra WEB01:

```powershell
Test-NetConnection 192.168.10.11 -Port 80
```

Kiểm tra APP01:

```powershell
Test-NetConnection 192.168.10.12 -Port 8080
```

Kiểm tra Windows Exporter:

```powershell
Test-NetConnection 192.168.10.13 -Port 9182
```

Kiểm tra WinRM:

```powershell
Test-NetConnection 192.168.10.13 -Port 5985
```

Kiểm tra Prometheus trên MON01:

```powershell
Test-NetConnection 192.168.10.10 -Port 9090
```

---

## 9. Kết quả

Tailscale đã được cài đặt và cấu hình thành công trên MGMT01.

MGMT01 hiện đóng vai trò:

- Tailscale Client
- Tailscale Subnet Router
- Remote Access Gateway
- Advertise route `192.168.10.0/24`

Application Laptop có thể truy cập các máy chủ trong mạng Lab thông qua MGMT01 mà không cần cài Tailscale trực tiếp trên từng máy ảo.
