# TC01 – LOW Risk Evidence

Thư mục này lưu các hình ảnh minh chứng cho quá trình kiểm thử LOW Risk Direct Execution trên WEB01 trong Week 9.

## Danh sách minh chứng

| Tên hình | Nội dung |
|---|---|
| `01-low-risk-precheck.png` | Kiểm tra trạng thái ban đầu của WEB01, Nginx và HTTP |
| `02-low-risk-nginx-down.png` | Tạo sự cố thực tế bằng cách dừng dịch vụ Nginx |
| `03-low-risk-remediation-success.png` | Kết quả thực thi remediation và verification trên Portal |

## Kết quả

- **Target:** WEB01
- **Action:** `restart_nginx`
- **Risk:** LOW
- **Approval:** Không yêu cầu
- **Test Result:** PASS

Các minh chứng thể hiện quá trình từ trạng thái ban đầu, tạo sự cố, thực thi remediation đến khi dịch vụ phục hồi thành công.
