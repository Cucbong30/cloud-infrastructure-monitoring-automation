# Week 10 – Management Pre-check

## 1. Mục đích

Kiểm tra khả năng kết nối đến các kênh quản trị SSH
và WinRM trước khi thực hiện Incident Management
Integration Testing.

Đảm bảo Ansible không thực thi remediation khi
kênh quản trị của target không khả dụng.

## 2. Môi trường kiểm tra

- Execution Host: MON01
- IP Address: 192.168.10.10
- Testing Date: 26/11/2026
- Connection Timeout: 3 seconds

## 3. Management Channel Mapping

| Target | Protocol | Port |
|---|---|---|
| WEB01 | SSH | 22 |
| APP01 | SSH | 22 |
| WIN01 | WinRM | 5985 |
| AZURE01 | SSH | 22 |

## 4. Lệnh kiểm tra

Thực hiện trên MON01:

```bash
for item in \
"WEB01:192.168.10.11:22" \
"APP01:192.168.10.12:22" \
"WIN01:192.168.10.13:5985" \
"AZURE01:20.243.24.91:22"
do
    IFS=: read -r name ip port <<< "$item"

    if timeout 3 bash -c "echo > /dev/tcp/$ip/$port" 2>/dev/null; then
        echo "$name | Port $port | AVAILABLE"
    else
        echo "$name | Port $port | BLOCKED"
    fi
done
```

## 5. Kết quả kiểm tra

| Target | Expected Result | Status |
|---|---|---|
| WEB01 | AVAILABLE | PASS |
| APP01 | AVAILABLE | PASS |
| WIN01 | AVAILABLE | PASS |
| AZURE01 | AVAILABLE | PASS |

Kết quả dựa trên xác nhận của người thực hiện.

Kiểm tra TCP chỉ xác nhận khả năng kết nối đến
management port, không thay thế kiểm tra xác thực
SSH, WinRM và Ansible Connectivity.

## 6. Minh chứng

![Management Pre-check](../screenshots/10-management-precheck.png)

## 7. Management Pre-check Policy

Tiếp tục sử dụng chính sách đã triển khai từ
những tuần trước:

- Kiểm tra management channel trước khi chạy Ansible.
- Nếu SSH hoặc WinRM không khả dụng, ghi nhận
  MANAGEMENT_BLOCKED.
- Không thực thi playbook khi management channel bị chặn.
- Không sử dụng ngân sách retry cho Management Blocked.
- Không tự động Resolve Incident khi chưa xác nhận
  dịch vụ đã phục hồi.
- Ghi nhận nguyên nhân để người vận hành tiếp tục xử lý.

Các điều kiện liên quan đến Incident Lifecycle
sẽ được kiểm chứng trong Integration Testing
với Application.

## 8. Kết luận

Đã hoàn thành Management Pre-check cho các target
trong môi trường Hybrid Cloud.

Không thay đổi Firewall, SSH, WinRM, Ansible Inventory
hoặc Production Playbook.

Kết quả được sử dụng làm baseline cho test case
Management Blocked trong Tuần 10.

**Baseline Result: PASS**

**Integration Validation: Pending**

**Next Step: Incident Handling Runbook.**
