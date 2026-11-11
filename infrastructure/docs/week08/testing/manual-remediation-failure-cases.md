# Manual Remediation Failure Cases

## 1. Objective

Kiểm tra Manual Remediation khi target gặp các trạng thái lỗi thực tế.

Các trường hợp được kiểm tra:

```text
Execution Failed
Verification Failed
Management Blocked
```

Case `DUPLICATE_SKIPPED` sẽ được kiểm tra chung với Portal/Application ở bước sau.

---

## 2. Execution Failed

Target sử dụng:

```text
AZURE01
Service: Nginx
```

Tạo Nginx configuration không hợp lệ:

```text
invalid_directive;
```

Kiểm tra:

```text
sudo nginx -t
```

Kết quả configuration validation failed.

Sau đó dừng Nginx và chạy remediation từ MON01:

```text
ansible-playbook /home/bong/ansible/playbooks/restart-azure-nginx.yml
```

Kết quả:

```text
Execution: FAILED
Verification: NOT REACHED
```

Nguyên nhân là Nginx không thể restart khi configuration không hợp lệ.

Sau khi test, file lỗi được xóa và Nginx được restore về trạng thái bình thường.

---

## 3. Verification Failed

Target:

```text
AZURE01
Service: Nginx
Expected Port: 80
```

Nginx được cấu hình hợp lệ nhưng thay đổi listening port từ `80` sang `8081`.

Configuration vẫn pass:

```text
sudo nginx -t
```

Sau đó Nginx được stop và remediation được chạy từ MON01.

Kết quả:

```text
Restart Nginx: SUCCESS
Verification Port 80: FAILED
```

Flow:

```text
Execution SUCCESS
→ Verification FAILED
→ Manual intervention required
```

Case này xác nhận remediation command có thể thành công nhưng service vẫn không đạt trạng thái mong đợi sau post-check.

Sau khi test, configuration được restore về port `80`.

---

## 4. Management Blocked

Target:

```text
AZURE01
```

Tạo trạng thái:

```text
Nginx: DOWN
SSH: DOWN
```

Sau đó kiểm tra từ MON01:

```text
ansible AZURE01 -m ping
```

Kết quả:

```text
UNREACHABLE
```

Do management channel không hoạt động, remediation không thể được thực hiện.

Expected flow:

```text
Management Pre-check Failed
→ BLOCKED
→ No Playbook Execution
→ MANUAL_REQUIRED
```

SSH và Nginx sau đó được khôi phục thông qua công cụ quản trị của Azure.

---

## 5. Result

Kết quả kiểm thử:

```text
Execution Failed     → PASS
Verification Failed  → PASS
Management Blocked   → PASS
```

Ba case đều được tạo bằng trạng thái thật của target, không chỉnh sửa production remediation logic để tạo lỗi.

Case `DUPLICATE_SKIPPED` sẽ được kiểm tra riêng khi tích hợp Manual Remediation với Portal.
