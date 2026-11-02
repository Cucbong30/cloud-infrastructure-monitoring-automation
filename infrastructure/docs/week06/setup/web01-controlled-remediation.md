# Week 6 - Controlled Auto-remediation

Week 6 tập trung kiểm thử controlled auto-remediation trên các server trong lab.

WEB01 được dùng để kiểm thử các trường hợp:

- Service failure có thể tự recovery.
- Remediation execution failed.
- Management channel unavailable.
- Verification failed.
- Manual intervention khi auto-remediation không thể xử lý.

Chi tiết WEB01:

- `setup/web01-controlled-remediation.md`
- `screenshots/web01/`

- # WEB01 - Controlled Remediation Setup

## Target

- Server: WEB01
- IP: 192.168.10.11
- Service: Nginx
- Service Port: 80
- Management Channel: SSH :22
- Production Playbook: `/home/bong/ansible/playbooks/restart-nginx.yml`

## Case 1 - Auto Remediation Success

Condition:

```
Nginx DOWN
SSH UP
Nginx configuration valid
```

Action:

```
restart_nginx
```

Expected result:

```
Nginx restarted
HTTP :80 returned 200
SUCCESS
```

## Case 2 - Execution Failed

A reusable invalid Nginx configuration was prepared:

```
/etc/nginx/week6-invalid.conf.sample
```

Enable failure:

```
sudo cp /etc/nginx/week6-invalid.conf.sample /etc/nginx/conf.d/week6-invalid.conf
sudo nginx -t
sudo systemctl stop nginx
```

Expected result:

```
Nginx DOWN
SSH UP
restart_nginx failed
Retry failed
MANUAL_REQUIRED
```

Restore:

```
sudo rm /etc/nginx/conf.d/week6-invalid.conf
sudo nginx -t
sudo systemctl start nginx
```

## Case 3 - Management Channel Blocked

Condition:

```
Nginx DOWN
SSH DOWN
```

Create condition:

```
sudo systemctl stop nginx
sudo systemctl stop ssh
sudo systemctl stop ssh.socket
```

Expected result:

```
HTTP :80 unavailable
SSH :22 unavailable
Ansible UNREACHABLE
BLOCKED
MANUAL_REQUIRED
```

Restore from server console:

```
sudo systemctl start ssh.socket
sudo systemctl start ssh
sudo systemctl start nginx
```

## Case 4 - Verification Failed

Two reusable Nginx profiles were prepared:

```
/etc/nginx/sites-available/default.week6-original
/etc/nginx/sites-available/default.week6-port8081
```

Normal profile:

```
listen 80
```

Fault profile:

```
listen 8081
```

Enable verification fault:

```
sudo cp /etc/nginx/sites-available/default.week6-port8081 /etc/nginx/sites-available/default
sudo nginx -t
sudo systemctl stop nginx
```

The production playbook can restart Nginx successfully, but verification on port 80 fails.

Expected result:

```
Execution SUCCESS
Verification FAILED
MANUAL_REQUIRED
```

Restore:

```
sudo cp /etc/nginx/sites-available/default.week6-original /etc/nginx/sites-available/default
sudo nginx -t
sudo systemctl restart nginx
```

## Result

WEB01 validated the following controlled remediation states:

- SUCCESS
- EXECUTION FAILED
- BLOCKED
- VERIFICATION FAILED
- MANUAL REQUIRED
