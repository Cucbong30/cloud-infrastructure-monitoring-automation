# WEB01 Failure Handling Test

## Target

- Server: WEB01
- IP: `192.168.10.11`
- Service: Nginx `:80`
- Management Channel: SSH `:22`

## 1. Ansible Failure Handling

Test để phân biệt giữa `failed` và `unreachable`.

Kết quả:

```
Execution Failed
unreachable=0
failed=1
```

```
Target Unreachable
unreachable=1
failed=0
```

## 2. SSH Pre-check

Kiểm tra SSH từ MON01:

```
nc -zv 192.168.10.11 22
```

Khi SSH hoạt động:

```
Connection succeeded
```

## 3. Stop SSH

Trên WEB01:

```
sudo systemctl stop ssh
sudo systemctl stop ssh.socket
```

Kiểm tra lại từ MON01:

```
nc -zv 192.168.10.11 22
```

Kết quả:

```
Connection refused
```

## 4. Restore SSH

Trên WEB01:

```
sudo systemctl start ssh.socket
sudo systemctl start ssh
```

Kiểm tra lại:

```
nc -zv 192.168.10.11 22
```

SSH port `22` hoạt động lại bình thường.

## 5. Nginx Recovery Post-check

Chạy production playbook:

```
ansible-playbook ~/ansible/playbooks/restart-nginx.yml
```

Kiểm tra Nginx:

```
curl -I http://192.168.10.11
```

Kết quả:

```
HTTP/1.1 200 OK
```

## 6. Verification Failure

Chạy playbook test với verification port sai `81`:

```
ansible-playbook ~/ansible/playbooks/restart-nginx-verification-fail.yml
```

Kết quả:

```
Restart nginx: changed
Wait for port 81: timeout
unreachable=0
failed=1
```

## Result

Đã kiểm tra được:

- Execution Failed
- Target Unreachable
- SSH pre-check PASS/FAIL
- SSH restore
- Nginx recovery success
- Verification Failed
