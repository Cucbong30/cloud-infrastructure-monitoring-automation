# AZURE01 Hybrid Cloud Setup

## 1. Mục tiêu

Triển khai một Ubuntu Server trên Microsoft Azure để mở rộng hệ thống từ mô hình local lab sang Hybrid Cloud.

AZURE01 sẽ được sử dụng làm Cloud target cho các thành phần:
- Nginx
- Node Exporter
- Prometheus
- Ansible
- Auto-remediation

---

## 2. Tạo Azure Virtual Machine

Truy cập Microsoft Azure Portal và tạo một Virtual Machine mới.

Cấu hình sử dụng:

- **Resource Group:** `KLTN`
- **Virtual Machine Name:** `AZURE01`
- **Region:** `Japan East`
- **Availability Zone:** `Zone 1`
- **Image:** `Ubuntu Server 24.04 LTS`
- **Architecture:** `x64`
- **VM Size:** `B2ats_v2`
- **Authentication Type:** `SSH Public Key`

Tài khoản quản trị Linux:

```text
Username: bong
```

Tạo và tải SSH private key về máy quản trị.

---

## 3. Cấu hình Disk

Sử dụng OS Disk:

```text
Disk Type: Premium SSD LRS
Disk Size: 64 GiB
```

Giữ cấu hình disk mặc định cho mục đích lab.

---

## 4. Cấu hình Network

Tạo Virtual Network riêng cho AZURE01.

```text
Virtual Network: vnet-kltn
Subnet: 172.16.0.0/24
Private IP: 172.16.0.4
```

AZURE01 sử dụng Public IP để MON01 trong local lab có thể kết nối thông qua Internet.

Các port cần thiết:

```text
22    SSH
80    HTTP / Nginx
9100  Node Exporter
```

Chỉ mở các port cần thiết phục vụ quản trị, monitoring và web service.

---

## 5. SSH vào AZURE01

Từ máy Windows quản trị:

```text
ssh -i .\AZURE01_key.pem bong@<AZURE01_PUBLIC_IP>
```

Sau khi SSH thành công, update package:

```text
sudo apt update
sudo apt upgrade -y
```

Kiểm tra hostname:

```text
hostname
```

Nếu cần đặt lại hostname:

```text
sudo hostnamectl set-hostname AZURE01
```

---

## 6. Cài đặt Nginx

Cài Nginx:

```text
sudo apt install nginx -y
```

Enable service:

```text
sudo systemctl enable nginx
sudo systemctl start nginx
```

Kiểm tra:

```text
systemctl status nginx
```

Kiểm tra HTTP local:

```text
curl -I http://localhost
```

Kết quả mong đợi:

```text
HTTP/1.1 200 OK
```

---

## 7. Cấu hình Swap

Tạo swap file 4 GB:

```text
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

Kiểm tra:

```text
swapon --show
free -h
```

Thêm vào `/etc/fstab`:

```text
/swapfile none swap sw 0 0
```

Cấu hình swappiness:

```text
sudo sysctl vm.swappiness=20
```

Persist cấu hình:

```text
echo 'vm.swappiness=20' | sudo tee -a /etc/sysctl.conf
```

---

## 8. Cài Node Exporter

Tạo user cho Node Exporter:

```text
sudo useradd --no-create-home --shell /usr/sbin/nologin node_exporter
```

Download Node Exporter:

```text
cd /tmp
wget https://github.com/prometheus/node_exporter/releases/download/v1.12.1/node_exporter-1.12.1.linux-amd64.tar.gz
```

Giải nén:

```text
tar xvf node_exporter-1.12.1.linux-amd64.tar.gz
```

Copy binary:

```text
sudo cp node_exporter-1.12.1.linux-amd64/node_exporter /usr/local/bin/
sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter
```

Tạo systemd service:

```text
sudo nano /etc/systemd/system/node_exporter.service
```

Nội dung:

```text
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
```

Reload systemd:

```text
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
```

Kiểm tra:

```text
systemctl status node_exporter
```

Kiểm tra port:

```text
ss -lntp | grep 9100
```

Kiểm tra metrics:

```text
curl http://localhost:9100/metrics
```

---

## 9. Tạo SSH Key từ MON01 sang AZURE01

Trên MON01:

```text
ssh-keygen -t ed25519 -f ~/.ssh/azure01_ed25519 -C "mon01-to-azure01"
```

Hiển thị public key:

```text
cat ~/.ssh/azure01_ed25519.pub
```

Copy public key này sang:

```text
/home/bong/.ssh/authorized_keys
```

trên AZURE01.

Kiểm tra permission:

```text
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

---

## 10. Kiểm tra SSH từ MON01

Trên MON01:

```text
ssh -i ~/.ssh/azure01_ed25519 bong@<AZURE01_PUBLIC_IP>
```

Nếu kết nối thành công thì AZURE01 đã sẵn sàng cho Ansible quản lý.

---

## 11. Thêm AZURE01 vào Ansible Inventory

Trên MON01 mở:

```text
sudo nano /etc/ansible/hosts
```

Thêm:

```text
[azure]
AZURE01 ansible_host=<AZURE01_PUBLIC_IP> ansible_user=bong ansible_ssh_private_key_file=/home/bong/.ssh/azure01_ed25519
```

Kiểm tra connectivity:

```text
ansible AZURE01 -m ping
```

Kết quả mong đợi:

```text
SUCCESS
```

---

## 12. Hoàn tất

Sau khi hoàn thành các bước trên, AZURE01 đã có:

```text
Ubuntu Server
Nginx
Node Exporter
SSH Management
Ansible Connectivity
Azure Network Configuration
```

AZURE01 lúc này đã sẵn sàng để được tích hợp vào Prometheus monitoring và auto-remediation workflow.
