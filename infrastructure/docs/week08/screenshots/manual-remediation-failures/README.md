# Manual Remediation Failure Screenshots

Thư mục này lưu evidence cho các failure case của Manual Remediation trong Week 8.

- `01-azure01-manual-execution-failed.png`  
  AZURE01 gặp lỗi Nginx configuration invalid làm remediation execution thất bại.

- `02-azure01-manual-verification-failed.png`  
  Nginx restart thành công nhưng service không còn listen trên port 80, làm bước verification thất bại.

- `03-azure01-manual-management-blocked.png`  
  SSH trên AZURE01 bị tắt nên MON01 không thể kết nối đến target và remediation bị block ở bước management pre-check.
