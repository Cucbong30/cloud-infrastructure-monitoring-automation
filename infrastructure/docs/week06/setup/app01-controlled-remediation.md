# APP01 - Controlled Remediation Setup

## Target

- Server: APP01
- IP: 192.168.10.12
- Service: Docker container `app01-web`
- Application Port: 8080
- Management Channel: SSH :22
- Production Playbook: `/home/bong/ansible/playbooks/restart-app-container.yml`

## Case 1 - Auto-remediation thành công

Điều kiện:

```
Container DOWN
SSH UP
```

Tạo lỗi trên APP01:

```
docker stop app01-web
```

Kiểm tra:

```
curl -I http://localhost:8080
```

Production remediation:

```
sudo -n docker start app01-web
```

Kết quả mong đợi:

```
Container được start
HTTP :8080 hoạt động
SUCCESS
```

## Case 2 - Execution Failed

Để kiểm tra trường hợp remediation không thể chạy, container được đổi tên để production playbook không tìm thấy `app01-web`.

Tạo lỗi:

```
docker stop app01-web
docker rename app01-web app01-web-week6-original
```

Production playbook vẫn gọi:

```
sudo -n docker start app01-web
```

Kết quả:

```
No such container: app01-web
Execution Failed
```

Theo policy của Week 6:

```
Execution Failed
→ Retry 1 lần
→ Retry vẫn Failed
→ MANUAL_REQUIRED
```

Restore:

```
docker rename app01-web-week6-original app01-web
docker start app01-web
```

Kiểm tra:

```
curl -I http://localhost:8080
```

## Case 3 - Management Channel Blocked

Điều kiện:

```
Container DOWN
SSH DOWN
```

Tạo lỗi trên APP01:

```
docker stop app01-web
sudo systemctl stop ssh
sudo systemctl stop ssh.socket
```

Kiểm tra từ MON01:

```
curl -I http://192.168.10.12:8080
ansible APP01 -m ping
```

Kết quả:

```
Application unavailable
APP01 UNREACHABLE
```

Khi management channel không hoạt động, hệ thống không chạy remediation.

```
BLOCKED
→ Không gọi playbook
→ MANUAL_REQUIRED
```

Restore từ VMware console:

```
sudo systemctl start ssh.socket
sudo systemctl start ssh
docker start app01-web
```

Kiểm tra lại từ MON01:

```
ansible APP01 -m ping
curl -I http://192.168.10.12:8080
```

## Case 4 - Verification Failed

Case này kiểm tra trường hợp container được start thành công nhưng service không hoạt động đúng port mong đợi.

Container gốc được giữ lại:

```
docker stop app01-web
docker rename app01-web app01-web-week6-original
```

Tạo container mới sử dụng port 8081:

```
docker run -d \
  --name app01-web \
  --restart unless-stopped \
  -p 8081:80 \
  nginx:alpine
```

Kiểm tra:

```
curl -I http://localhost:8081
curl -I http://localhost:8080
```

Kết quả:

```
8081 → HTTP 200
8080 → unavailable
```

Stop container trước khi remediation:

```
docker stop app01-web
```

Production playbook vẫn có thể start container thành công:

```
sudo -n docker start app01-web
```

Tuy nhiên verification vẫn kiểm tra port 8080.

Kết quả:

```
Execution SUCCESS
Verification FAILED
MANUAL_REQUIRED
```

Restore:

```
docker rm -f app01-web
docker rename app01-web-week6-original app01-web
docker start app01-web
```

Kiểm tra:

```
curl -I http://localhost:8080
```

## Kết quả

APP01 đã kiểm thử các trạng thái:

- SUCCESS
- EXECUTION FAILED
- BLOCKED
- VERIFICATION FAILED
- MANUAL REQUIRED

Các case đều sử dụng production playbook và thay đổi trạng thái thật trên APP01 để kiểm tra luồng remediation.
