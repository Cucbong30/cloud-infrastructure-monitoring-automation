# APP01 Failure Handling Test

## Target

- Server: APP01
- IP: `192.168.10.12`
- Service: `app01-web :8080`
- Management Channel: SSH `:22`

## 1. SSH Pre-check

Kiểm tra SSH từ MON01:

```
nc -zv 192.168.10.12 22
```

Khi SSH hoạt động:

```
Connection succeeded
```

## 2. Stop SSH

Trên APP01:

```
sudo systemctl stop ssh
sudo systemctl stop ssh.socket
```

Kiểm tra lại từ MON01:

```
nc -zv 192.168.10.12 22
```

Kết quả:

```
Connection refused
```

## 3. Restore SSH

Trên APP01:

```
sudo systemctl start ssh.socket
sudo systemctl start ssh
```

Kiểm tra lại:

```
nc -zv 192.168.10.12 22
```

SSH port `22` hoạt động lại bình thường.

## 4. Ansible Execution Failure

Chạy playbook test:

```
ansible-playbook ~/ansible/playbooks/restart-app-container-fail-test.yml
```

Kết quả:

```
rc=1
unreachable=0
failed=1
```

Ansible vẫn kết nối được APP01 nhưng Docker task bị lỗi.

## 5. Container Recovery Post-check

Chạy production playbook:

```
ansible-playbook ~/ansible/playbooks/restart-app-container.yml
```

Kiểm tra service:

```
curl -I http://192.168.10.12:8080
```

Kết quả:

```
HTTP/1.1 200 OK
```

## 6. Verification Failure

Chạy playbook test với verification port sai `8081`:

```
ansible-playbook ~/ansible/playbooks/restart-app-container-verification-fail.yml
```

Kết quả:

```
Start app01-web: changed
Wait for port 8081: timeout
unreachable=0
failed=1
```

## Result

Đã kiểm tra được:

- SSH pre-check PASS/FAIL
- SSH restore
- Ansible Execution Failed
- Container recovery success
- HTTP post-check success
- Verification Failed
