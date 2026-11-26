# Week 10 – Service Verification Baseline

## 1. Mục đích

Kiểm tra trạng thái các dịch vụ trước khi thực hiện
Incident Management Integration Testing.

Kết quả được sử dụng làm baseline để đối chiếu
trạng thái dịch vụ trước và sau khi remediation.

## 2. Môi trường kiểm tra

- Execution Host: MON01
- IP Address: 192.168.10.10
- Testing Date: 26/11/2026
- Verification Method: HTTP Request
- Request Timeout: 5 seconds

## 3. Service Verification Mapping

| Target | Service | Port | Verification |
|---|---|---|---|
| WEB01 | Nginx | 80 | HTTP 200 |
| APP01 | Application Container | 8080 | HTTP 200 |
| WIN01 | Windows Exporter | 9182 | HTTP 200 |
| AZURE01 | Nginx | 80 | HTTP 200 |

## 4. Lệnh kiểm tra

Thực hiện trên MON01:

```bash
for item in \
"WEB01|http://192.168.10.11:80" \
"APP01|http://192.168.10.12:8080" \
"WIN01|http://192.168.10.13:9182/metrics" \
"AZURE01|http://20.243.24.91:80"
do
    name="${item%%|*}"
    url="${item#*|}"

    printf "%-10s " "$name"
    curl -sS --max-time 5 -o /dev/null \
        -w "HTTP %{http_code} | Response: %{time_total}s\n" "$url"
done
```

## 5. Kết quả kiểm tra

| Target | Expected Result | Status |
|---|---|---|
| WEB01 | HTTP 200 | PASS |
| APP01 | HTTP 200 | PASS |
| WIN01 | HTTP 200 | PASS |
| AZURE01 | HTTP 200 | PASS |

Kết quả PASS dựa trên xác nhận kiểm tra của
người thực hiện. Chi tiết HTTP response và
response time được lưu trong ảnh minh chứng.

## 6. Minh chứng

![Service Verification Baseline](../screenshots/09-service-verification-baseline.png)

## 7. Verification Policy

- Kiểm tra trạng thái dịch vụ trước khi tạo lỗi.
- Kiểm tra lại dịch vụ sau khi remediation.
- Không chỉ dựa vào Ansible Exit Code để kết luận
  dịch vụ đã phục hồi.
- Chỉ ghi nhận remediation SUCCESS khi đáp ứng
  điều kiện verification tương ứng.
- Verification Failed không tự động retry.
- Không tự động Resolve Incident khi verification
  thất bại.

HTTP 200 xác nhận endpoint có phản hồi tại thời
điểm kiểm tra, không đại diện cho toàn bộ trạng
thái hoặc chức năng nghiệp vụ của ứng dụng.

## 8. Kết luận

Đã hoàn thành kiểm tra Service Verification Baseline
cho các target trong môi trường Hybrid Cloud.

Kết quả được sử dụng để đối chiếu trong các test case
Remediation Success, Verification Failed và Manual Recovery.

Không thay đổi cấu hình dịch vụ hoặc production playbook.

**Final Result: PASS**

**Next Step: Management Pre-check.**
