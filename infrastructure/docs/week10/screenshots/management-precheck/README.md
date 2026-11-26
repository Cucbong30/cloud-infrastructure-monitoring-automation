# Management Pre-check – Evidence

## 1. Mục đích

Lưu minh chứng kiểm tra khả năng kết nối SSH và WinRM
trước khi thực hiện Incident Management Integration Testing.

## 2. Danh sách minh chứng

| STT | Screenshot | Nội dung |
|---|---|---|
| 10 | 10-management-precheck.png | Kiểm tra trạng thái Management Channel |

## 3. Kết quả

| Target | Protocol | Port | Status |
|---|---|---|---|
| WEB01 | SSH | 22 | AVAILABLE |
| APP01 | SSH | 22 | AVAILABLE |
| WIN01 | WinRM | 5985 | AVAILABLE |
| AZURE01 | SSH | 22 | AVAILABLE |

Các management channel đều khả dụng tại thời điểm kiểm tra.

Kết quả được sử dụng làm baseline cho quá trình
kiểm thử Management Blocked trong Tuần 10.

**Final Result: PASS**
