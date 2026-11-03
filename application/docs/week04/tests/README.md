# Test tuần 4

Pytest nằm ở `application/tests/`, không copy vào thư mục này.

- `tests/test_automation.py`: allow-list, job Success/Failed, trang server chỉ hiện thông báo khi WEB01 `down`.
- `tests/test_remediation.py`: alert map đúng action, job lỗi thì retry được một lần.
- `tests/test_auth_rbac.py`: viewer không tạo job.

Test dùng mock executor. Ba playbook HTTP 200 là lần chạy trên lab, ghi trong Job History, không nằm trong pytest.
