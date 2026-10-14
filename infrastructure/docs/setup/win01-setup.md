# WIN01 Setup

## 1. Server Information
- Hostname: WIN01
- OS: Windows Server 2022
- IP Address: 192.168.10.13
- Subnet: 192.168.10.0/24
- Default Gateway: 192.168.10.2
- Role: Windows Server / Remote Management Target / Monitoring Target

## 2. Server Role and Function

WIN01 được sử dụng để mô phỏng một Windows Server trong môi trường vận hành hỗn hợp Linux/Windows.

Chức năng chính:
- Là monitoring target của Prometheus thông qua Windows Exporter.
- Cho phép quản trị từ xa thông qua WinRM / PowerShell Remoting.
- Được sử dụng cho các kịch bản kiểm thử liên quan đến Windows Service.
- Là target để MON01 thực hiện automation trong các giai đoạn sau.

Các kịch bản dự kiến:
- Windows Service bị dừng.
- WinRM unavailable.
- CPU / memory usage cao.
- Disk usage cao.
- Server connectivity failure.
- Tự động restart Windows Service bằng Ansible/PowerShell.

## 3. Network Configuration

WIN01 được cấu hình static IP.

Configuration:
- IP Address: `192.168.10.13`
- Subnet Mask: `255.255.255.0`
- Gateway: `192.168.10.2`
- DNS:
  - `8.8.8.8`
  - `1.1.1.1`

Connectivity has been verified with:
- MON01
- WEB01
- APP01
- Internet access

## 4. WinRM Configuration

Windows Remote Management (WinRM) has been enabled to support remote administration and future automation.

Configuration:
- Transport: HTTP
- Port: `5985`
- Listener: Enabled
- Remote Access: Enabled
- Basic Authentication: Enabled
- Allow Unencrypted: Enabled

Listener address:
- `192.168.10.13`

Configuration commands used:

```powershell
Enable-PSRemoting -Force
winrm quickconfig
winrm enumerate winrm/config/listener
