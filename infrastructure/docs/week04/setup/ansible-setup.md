# Ansible Setup - Week 4

## 1. Cài đặt Ansible trên MON01

Trên MON01:

```
sudo apt update
sudo apt install -y ansible
```

Kiểm tra version:

```
ansible --version
```

Kiểm tra Ansible chạy local:

```
ansible localhost -m ping
```

Kết quả mong đợi:

```
localhost | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

---

## 2. SSH từ MON01 tới Linux Server

MON01 sử dụng SSH key để quản lý WEB01 và APP01.

Kiểm tra key trên MON01:

```
ls -la ~/.ssh
```

Key sử dụng:

```
~/.ssh/id_ed25519
~/.ssh/id_ed25519.pub
```

Public key của MON01 được thêm vào:

```
WEB01: /home/bong/.ssh/authorized_keys
APP01: /home/bong/.ssh/authorized_keys
```

Kiểm tra kết nối:

```
ssh bong@192.168.10.11
```

```
ssh bong@192.168.10.12
```

Sau đó kiểm tra bằng Ansible:

```
ansible linux_web -m ping
```

```
ansible linux_app -m ping
```

Kết quả mong đợi:

```
SUCCESS
ping: pong
```

---

## 3. WinRM trên WIN01

WIN01 sử dụng WinRM để Ansible trên MON01 quản lý Windows Server.

Trên WIN01 kiểm tra WinRM:

```
Get-Service WinRM
```

Kiểm tra listener:

```
winrm enumerate winrm/config/listener
```

WinRM được cấu hình trên:

```
Port: 5985
Protocol: HTTP
```

Từ MON01 sử dụng:

```
Connection: WinRM
Transport: NTLM
User: WIN01\Administrator
```

Kiểm tra module Python WinRM trên MON01:

```
dpkg -l | grep python3-winrm
```

Kiểm tra kết nối:

```
ansible windows -m win_ping
```

Kết quả:

```
WIN01 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

Trong quá trình cấu hình có gặp lỗi:

```
ntlm: the specified credentials were rejected by the server
```

Kiểm tra trên WIN01:

```
whoami
```

Kết quả:

```text
win01\administrator
```

Sau khi sửa username trong inventory thành:

```
WIN01\Administrator
```

Ansible `win_ping` hoạt động bình thường.

---

## 4. Kết nối Portal tới MON01

Web Portal chạy trên laptop Windows riêng và không chạy trực tiếp trên MON01.

Portal cần SSH tới MON01 để gọi Ansible playbook.

Trên máy Windows chạy Portal tạo SSH key:

```powershell
ssh-keygen -t ed25519
```

Private key được giữ trên máy chạy Portal.

Public key được thêm vào MON01:

```
/home/bong/.ssh/authorized_keys
```

Kiểm tra từ máy Portal:

```
ssh bong@192.168.10.10
```

Kết nối phải thực hiện được mà không cần nhập password.

Luồng thực tế:

```text
Windows Laptop / Portal
        |
        | SSH
        v
MON01 / Ansible Controller
        |
        +--> WEB01 via SSH
        |
        +--> APP01 via SSH
        |
        +--> WIN01 via WinRM
```

---
