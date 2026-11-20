# TC01 – Kiểm thử LOW Risk Direct Execution

## 1. Mục tiêu

Kiểm tra khả năng thực thi remediation action có mức rủi ro LOW mà không cần thông qua Approval Workflow, đồng thời bảo đảm các cơ chế kiểm soát hiện có như Management Pre-check, Execution và Verification vẫn hoạt động bình thường.

Bài kiểm thử sử dụng tình huống Nginx trên WEB01 ngừng hoạt động để đánh giá khả năng phát hiện và tự động khôi phục dịch vụ.

## 2. Môi trường kiểm thử

| Thành phần | Thông tin |
|---|---|
| Target | WEB01 |
| IP Address | 192.168.10.11 |
| Service | Nginx |
| Action | `restart_nginx` |
| Risk | LOW |
| Approval | Không yêu cầu |
| Playbook | `restart-nginx.yml` |
| Monitoring | Prometheus |
| Automation | Ansible |

## 3. Kịch bản kiểm thử

Chủ động dừng dịch vụ Nginx trên WEB01 để tạo sự cố thực tế.

Sau khi dịch vụ ngừng hoạt động, hệ thống Monitoring phát hiện trạng thái bất thường và kích hoạt quy trình remediation theo policy đã cấu hình.

Luồng xử lý mong đợi:

```text
Nginx Running
→ Stop Nginx
→ Service DOWN
→ Risk = LOW
→ No Approval Required
→ Remediation Execution
→ Verification
→ SUCCESS
```

## 4. Các bước thực hiện

### Bước 1 – Kiểm tra trạng thái ban đầu

Trên MON01, thực hiện:

```bash
ansible WEB01 -m ping
ansible WEB01 -m command -a "systemctl is-active nginx"
curl -I http://192.168.10.11
```

Mục đích:

- Xác nhận MON01 có thể kết nối tới WEB01 thông qua Ansible.
- Kiểm tra trạng thái dịch vụ Nginx.
- Xác nhận HTTP port 80 hoạt động bình thường trước khi tạo sự cố.

### Bước 2 – Tạo sự cố Nginx Down

Trên WEB01, thực hiện:

```bash
sudo systemctl stop nginx
systemctl is-active nginx
```

Dịch vụ Nginx được chủ động dừng để mô phỏng sự cố Service Down.

Hệ thống Monitoring ghi nhận trạng thái bất thường của dịch vụ.

### Bước 3 – Kiểm tra LOW Risk Remediation

Theo dõi quá trình xử lý trên Application Portal.

Các nội dung cần xác nhận:

- Action `restart_nginx` được phân loại LOW Risk.
- Không yêu cầu Approval trước khi thực thi.
- Remediation Job được kích hoạt để khôi phục Nginx.
- Execution và Verification hoàn thành thành công.
- Job kết thúc với trạng thái SUCCESS.

### Bước 4 – Xác nhận dịch vụ đã phục hồi

Sau khi remediation hoàn tất, trên MON01 thực hiện:

```bash
ansible WEB01 -m command -a "systemctl is-active nginx"
curl -I http://192.168.10.11
```

Kết quả mong đợi:

```text
Nginx: active
HTTP: 200 OK
```

Kết quả này xác nhận Nginx đã hoạt động trở lại và dịch vụ HTTP có thể truy cập bình thường.

## 5. Kết quả kiểm thử

| Nội dung kiểm tra | Kết quả |
|---|---|
| Management Pre-check | PASS |
| Tạo sự cố Nginx Down | PASS |
| Phân loại LOW Risk | PASS |
| Không yêu cầu Approval | PASS |
| Remediation Execution | PASS |
| Verification | PASS |
| Khôi phục dịch vụ Nginx | PASS |

**Kết quả tổng thể: PASS**

## 6. Hình ảnh

Các hình ảnh được lưu tại:

`infrastructure/docs/week09/screenshots/low-risk/`

| Tên hình | Nội dung |
|---|---|
| `01-low-risk-precheck.png` | Kiểm tra kết nối WEB01 và trạng thái dịch vụ trước khi tạo sự cố |
| `02-low-risk-nginx-down.png` | Trạng thái Nginx Down sau khi chủ động dừng dịch vụ |
| `03-low-risk-remediation-success.png` | Kết quả remediation trên Portal, bao gồm Execution và Verification |

## 7. Kết luận

Kết quả kiểm thử cho thấy hệ thống có thể xử lý sự cố Nginx Down trên WEB01 thông qua remediation action `restart_nginx` thuộc mức LOW Risk.

Action được thực thi mà không yêu cầu Approval, đồng thời vẫn tuân thủ các bước Management Pre-check, Execution và Verification.

Sau remediation, dịch vụ Nginx hoạt động trở lại và HTTP trả về trạng thái 200 OK.

Kết quả TC01 được sử dụng làm cơ sở đối chiếu với các kịch bản MEDIUM và HIGH Risk, trong đó remediation action phải trải qua Approval Workflow trước khi thực thi.
