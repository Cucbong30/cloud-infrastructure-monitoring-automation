# Service Verification – Evidence

## 1. Mục đích

Lưu minh chứng kiểm tra trạng thái dịch vụ trước
khi thực hiện Incident Management Integration Testing.

## 2. Danh sách minh chứng

| STT | Screenshot | Nội dung |
|---|---|---|
| 09 | 09-service-verification-baseline.png | Kiểm tra HTTP response của các target |

## 3. Kết quả

| Target | Service | Status |
|---|---|---|
| WEB01 | Nginx | PASS |
| APP01 | Application Container | PASS |
| WIN01 | Windows Exporter | PASS |
| AZURE01 | Nginx | PASS |

Kết quả được sử dụng làm baseline để đối chiếu
trạng thái dịch vụ trước và sau remediation.

**Final Result: PASS**
