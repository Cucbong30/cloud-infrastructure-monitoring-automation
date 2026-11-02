# Week 6 - Quy tắc Auto-remediation

## Mục tiêu

Week 6 tập trung vào controlled auto-remediation, tức là hệ thống chỉ tự động xử lý những lỗi đã xác định rõ, có mức rủi ro thấp và có bước kiểm tra kết quả sau khi xử lý.

Không phải lỗi nào cũng được tự động restart. Trước khi chạy remediation, hệ thống cần kiểm tra trạng thái service, management channel và loại action được phép thực hiện.

## Các action được phép Auto-remediation

| Target | Sự cố | Management Channel | Action | Verification |
|---|---|---|---|---|
| WEB01 | Nginx DOWN | SSH :22 | restart_nginx | HTTP :80 |
| APP01 | Container DOWN | SSH :22 | restart_container | HTTP :8080 |
| WIN01 | Windows Exporter DOWN | WinRM :5985 | restart_windows_exporter | /metrics :9182 |

## Luồng xử lý chung

```
Phát hiện lỗi
→ Kiểm tra management channel
→ Kiểm tra action có được phép Auto hay không
→ Chạy remediation
→ Kiểm tra lại service
→ SUCCESS / RETRY / BLOCKED / MANUAL_REQUIRED
```

## Case 1 - Auto-remediation thành công

Điều kiện:

```
Service DOWN
Management channel UP
Cấu hình service bình thường
```

Hệ thống thực hiện:

```
Run remediation
→ Verify service
→ SUCCESS
```

Ví dụ WEB01:

```
Nginx DOWN
+ SSH UP
→ restart_nginx
→ HTTP :80 trả về 200
→ SUCCESS
```

Đây là trường hợp service chỉ bị dừng và có thể phục hồi bằng action đã được kiểm thử trước.

## Case 2 - Remediation chạy thất bại

Có những trường hợp server vẫn quản trị được nhưng restart service không giải quyết được lỗi.

Ví dụ WEB01:

```
Nginx DOWN
+ SSH UP
+ Nginx configuration lỗi
→ restart_nginx FAILED
```

Hệ thống xử lý:

```
Execution Failed
→ Retry 1 lần
→ Retry vẫn Failed
→ MANUAL_REQUIRED
```

Retry chỉ được thực hiện một lần để tránh tạo vòng lặp restart liên tục.

## Case 3 - Management Channel không khả dụng

Điều kiện:

```
Service DOWN
Management channel DOWN
```

Ví dụ:

```
Nginx DOWN
+ SSH DOWN
```

Hệ thống không được chạy remediation.

Kết quả:

```
BLOCKED
→ Không gọi playbook
→ Warning: Management channel unavailable
→ MANUAL_REQUIRED
```

Trường hợp này được tách riêng với Execution Failed vì hệ thống chưa thể kết nối tới target để thực hiện action.

## Case 4 - Verification Failed

Có trường hợp command restart chạy thành công nhưng service sau khi khởi động lại vẫn không đạt trạng thái mong muốn.

Ví dụ WEB01:

```
Nginx restart SUCCESS
+ Nginx chạy ở port :8081
+ Hệ thống yêu cầu HTTP :80
→ Verification FAILED
```

Hệ thống xử lý:

```
Execution SUCCESS
→ Verification FAILED
→ Dừng Auto-remediation
→ MANUAL_REQUIRED
```

Trường hợp này không retry tự động vì action đã chạy thành công nhưng service vẫn không trở về trạng thái mong muốn.

## Các trường hợp không Auto-remediation

Các action sau không được tự động thực hiện trong Week 6:

- Reboot hoặc shutdown server.
- Thay đổi network.
- Thay đổi firewall.
- Xóa file.
- Disk cleanup.
- CPU, RAM hoặc Disk usage cao nhưng chưa xác định được remediation an toàn.

Các trường hợp này chỉ thực hiện diagnostic và chuyển cho người vận hành kiểm tra.

## Trạng thái cuối

| Điều kiện | Kết quả |
|---|---|
| Service phục hồi và verification pass | SUCCESS |
| Execution fail lần đầu | RETRY |
| Retry vẫn execution fail | MANUAL_REQUIRED |
| Management channel unavailable | BLOCKED |
| Execution success nhưng verification fail | MANUAL_REQUIRED |
| Action không nằm trong nhóm được Auto | MANUAL_REQUIRED |

## Nguyên tắc

```
Detect
→ Check
→ Remediate
→ Verify
→ Dừng đúng lúc nếu automation không đủ khả năng xử lý
```

Mục tiêu của hệ thống không phải tự động sửa mọi sự cố mà là tự xử lý các lỗi đã biết, có mức rủi ro thấp và chuyển sang manual khi không còn đủ điều kiện để xử lý an toàn.
