# BẢN CAM KẾT SẢN PHẨM CUỐI CÙNG VÀ BỘ METRIC ĐÁNH GIÁ

## 1. Thông tin đề tài

**Tên đề tài:** Xây dựng hệ thống giám sát và tự động hóa vận hành hạ tầng trong môi trường Hybrid Cloud.

**Thành viên thực hiện:**

- Đỗ Đăng Thái Bảo – Infrastructure / System / Cloud.
- Nguyễn Thế Gia Bảo – Application / Integration.

## 2. Cam kết sản phẩm cuối cùng

Nhóm cam kết xây dựng một nền tảng hỗ trợ giám sát, phát hiện và xử lý sự cố hạ tầng trong môi trường Hybrid Cloud. Hệ thống hỗ trợ tự động khôi phục các dịch vụ trong phạm vi cho phép, kiểm soát quyền thực thi và lưu lại thông tin phục vụ quá trình vận hành.

### 2.1. Các thành phần sản phẩm

| STT | Thành phần | Kết quả sản phẩm cam kết |
|---|---|---|
| 1 | Hybrid Cloud Infrastructure | Môi trường gồm 5 máy chủ MON01, WEB01, APP01, WIN01 và AZURE01, bao gồm Linux, Windows và Microsoft Azure. |
| 2 | Monitoring System | Giám sát tập trung bằng Prometheus, Grafana và Alertmanager. |
| 3 | Operations Portal | Giao diện quản lý máy chủ, metrics, cảnh báo, automation job, approval, incident và audit log. |
| 4 | Automation Engine | Sử dụng Ansible để thực hiện Auto-remediation và Manual Remediation. |
| 5 | Controlled Remediation | Hỗ trợ Pre-check, Verification, Cooldown, Retry, Duplicate Handling và Manual Required. |
| 6 | Approval Workflow | Kiểm soát các action theo mức rủi ro LOW, MEDIUM và HIGH. |
| 7 | Incident Management | Quản lý vòng đời sự cố và liên kết Incident với Alert, Target và Automation Job. |
| 8 | Identity & Access Management | Đăng nhập SSO qua Microsoft Entra ID và phân quyền Admin, Operator, Viewer. |
| 9 | Email Notification | Gửi thông báo qua Microsoft Graph theo mức Critical, Warning và Info. |
| 10 | Audit Trail | Ghi nhận người thực hiện, thời gian, action, target và kết quả xử lý. |
| 11 | Runbook & Documentation | Tài liệu kiến trúc, triển khai, cấu hình, vận hành và xử lý sự cố. |
| 12 | Testing & Evaluation | Bộ test case, kết quả đo lường và minh chứng kiểm thử trên môi trường thực tế của đề tài. |

### 2.2. Các remediation action cam kết hỗ trợ

| Target | Action | Risk Level | Verification |
|---|---|---|---|
| WEB01 | Restart Nginx | LOW | HTTP port 80 |
| APP01 | Restart Application Container | LOW | Container Running và HTTP port 8080 |
| WIN01 | Restart Windows Exporter | LOW | Metrics endpoint port 9182 |
| AZURE01 | Restart Nginx | LOW | HTTP port 80 |
| APP01 | Restart Docker Service | MEDIUM | Docker Service, Container và HTTP port 8080 |
| AZURE01 | Reboot Server | HIGH | Boot ID, SSH và HTTP port 80 |

## 3. Bộ metric đánh giá sản phẩm

Các metric được sử dụng để đánh giá khả năng giám sát, hiệu quả tự động hóa, độ chính xác, tính an toàn và mức độ hoàn thiện của sản phẩm.

Các ngưỡng dưới đây là mục tiêu nghiệm thu dự kiến, không phải kết quả đã đo được.

### 3.1. Monitoring & Performance Metrics

| ID | Metric | Phương pháp đo | Mục tiêu |
|---|---|---|---|
| M01 | Monitoring Coverage | Số máy chủ được giám sát đầy đủ / Tổng số máy chủ | 5/5 máy chủ |
| M02 | Failure Detection Rate | Số sự cố được phát hiện / Tổng số sự cố được tạo × 100% | ≥ 95% |
| M03 | Mean Time to Detect (MTTD) | Thời gian trung bình từ lúc xảy ra sự cố đến khi Portal nhận cảnh báo | ≤ 60 giây |
| M04 | Alert Delivery Rate | Số cảnh báo hợp lệ được Portal tiếp nhận / Tổng số cảnh báo gửi từ Alertmanager × 100% | ≥ 95% |
| M05 | Metric Collection Availability | Số lần thu thập metrics thành công / Tổng số lần thu thập dự kiến × 100% trong điều kiện vận hành bình thường | ≥ 99% |

### 3.2. Automation & Recovery Metrics

| ID | Metric | Phương pháp đo | Mục tiêu |
|---|---|---|---|
| M06 | Auto-remediation Success Rate | Số sự cố đủ điều kiện auto-remediation được khôi phục và verification thành công / Tổng số sự cố đủ điều kiện × 100% | ≥ 90% |
| M07 | Mean Time to Recover (MTTR) | Thời gian trung bình từ lúc xảy ra sự cố đến khi dịch vụ được xác nhận phục hồi | ≤ 180 giây đối với sự cố LOW Risk có thể tự khôi phục |
| M08 | Recovery Time Improvement | So sánh MTTR giữa xử lý thủ công và Auto-remediation | Giảm ≥ 30% |
| M09 | Manual Remediation Success Rate | Số lần Manual Remediation thành công / Tổng số lần chạy trong điều kiện có thể khôi phục × 100% | ≥ 90% |
| M10 | Verification Accuracy | Số kết quả verification khớp với trạng thái dịch vụ thực tế / Tổng số lần kiểm tra × 100% | 100% |
| M11 | Management Pre-check Accuracy | Số trường hợp mất SSH/WinRM được phát hiện và chặn đúng / Tổng số trường hợp mất kết nối quản trị × 100% | 100% |
| M12 | Retry Policy Compliance | Số trường hợp tuân thủ đúng giới hạn retry / Tổng số trường hợp kiểm thử retry × 100% | 100% |
| M13 | Cooldown Compliance | Số trường hợp Auto-remediation tuân thủ cooldown 120 giây / Tổng số trường hợp kiểm thử cooldown × 100% | 100% |
| M14 | Duplicate Prevention Rate | Số yêu cầu trùng lặp được chặn / Tổng số yêu cầu trùng lặp được tạo × 100% | 100% |

### 3.3. Security & Approval Metrics

| ID | Metric | Phương pháp đo | Mục tiêu |
|---|---|---|---|
| M15 | SSO Login Success Rate | Số lần đăng nhập hợp lệ thành công / Tổng số lần đăng nhập hợp lệ × 100% | ≥ 95% |
| M16 | RBAC Enforcement Rate | Số trường hợp phân quyền đúng / Tổng số test case RBAC × 100% | 100% |
| M17 | Approval Policy Compliance | Số action MEDIUM/HIGH được kiểm soát đúng theo approval / Tổng số test case approval × 100% | 100% |
| M18 | Unauthorized Execution Count | Số action được thực thi khi người dùng không đủ quyền | 0 |
| M19 | Rejected/Expired Execution Count | Số playbook được thực thi từ request bị từ chối hoặc hết hạn | 0 |
| M20 | Credential Exposure Count | Số password, private key hoặc client secret thực tế bị lưu dưới dạng plain text trong mã nguồn và Git history | 0 |

### 3.4. Incident Management & Traceability Metrics

| ID | Metric | Phương pháp đo | Mục tiêu |
|---|---|---|---|
| M21 | Incident Lifecycle Accuracy | Số trường hợp chuyển trạng thái Incident đúng quy trình / Tổng số test case lifecycle × 100% | 100% |
| M22 | Incident Traceability | Số Incident có đầy đủ liên kết với Alert, Target và các Job phát sinh / Tổng số Incident kiểm thử × 100% | 100% |
| M23 | False Resolution Count | Số Incident bị chuyển sang Resolved khi dịch vụ thực tế chưa phục hồi | 0 |
| M24 | Audit Log Completeness | Số thao tác được ghi đầy đủ các trường Audit bắt buộc / Tổng số thao tác cần audit × 100% | 100% |
| M25 | Notification Delivery Rate | Số Email thực tế nhận được đúng nhóm severity / Tổng số Email dự kiến gửi × 100% | ≥ 95% |
| M26 | Notification Latency | Thời gian trung bình từ lúc phát sinh sự kiện cần thông báo đến khi Email được nhận | ≤ 60 giây |

### 3.5. Product Completion Metrics

| ID | Metric | Phương pháp đo | Mục tiêu |
|---|---|---|---|
| M27 | Feature Completion Rate | Số chức năng cam kết đã triển khai và nghiệm thu / Tổng số chức năng cam kết × 100% | 100% |
| M28 | Test Case Pass Rate | Số test case đạt / Tổng số test case đã xác định × 100% | ≥ 95% |
| M29 | Critical Test Case Pass Rate | Số test case an toàn và bảo mật bắt buộc đạt / Tổng số test case bắt buộc × 100% | 100% |
| M30 | Runbook Coverage | Số nhóm trạng thái xử lý có Runbook / Tổng số nhóm trạng thái đã xác định | 5/5 |
| M31 | Documentation Completion | Số tài liệu hoàn thành / Tổng số tài liệu trong danh sách bàn giao × 100% | 100% |

## 4. Phương pháp kiểm thử và đo lường

### 4.1. Môi trường kiểm thử

Thực hiện kiểm thử trên các máy chủ:

- MON01: Monitoring và Ansible Control Node.
- WEB01: Nginx Web Server.
- APP01: Docker Application Server.
- WIN01: Windows Server và Windows Exporter.
- AZURE01: Azure Virtual Machine và Nginx.

Các sự cố được tạo có kiểm soát trên môi trường lab, không thực hiện trên hệ thống production.

### 4.2. Các kịch bản kiểm thử

| STT | Nhóm kiểm thử | Kịch bản |
|---|---|---|
| 1 | Monitoring | Host Down, Service Down, Exporter Down. |
| 2 | Auto-remediation | Nginx Down, Container Down, Windows Exporter Down. |
| 3 | Execution Failure | Playbook kết nối được target nhưng không thực thi thành công. |
| 4 | Management Blocked | SSH hoặc WinRM không khả dụng. |
| 5 | Verification Failure | Playbook chạy xong nhưng dịch vụ chưa đạt trạng thái mong muốn. |
| 6 | Retry & Cooldown | Sự cố lặp lại, vượt giới hạn retry hoặc chưa hết cooldown. |
| 7 | Duplicate Handling | Nhiều yêu cầu remediation cho cùng target và action. |
| 8 | RBAC | Kiểm thử quyền Admin, Operator và Viewer. |
| 9 | Approval | Approved, Rejected, Unauthorized và Timeout. |
| 10 | Incident Management | Incident Created, Resolved, Manual Required, Closed và Recurring Incident. |
| 11 | Notification | Kiểm tra Email theo severity và trạng thái xử lý. |
| 12 | Audit Trail | Kiểm tra khả năng truy vết toàn bộ quá trình xử lý sự cố. |

### 4.3. Quy mô kiểm thử

- Tối thiểu 40 test case chức năng và tích hợp.
- Mỗi loại sự cố LOW Risk được kiểm thử tối thiểu 5 lần ở mỗi chế độ Manual và Auto-remediation.
- Thực hiện tối thiểu 20 lần kiểm thử Auto-remediation trên bốn target server.
- Thực hiện tối thiểu 20 lần kiểm thử Manual Remediation tương ứng để so sánh.
- Kiểm thử thu thập metrics liên tục trong tối thiểu 24 giờ ở điều kiện vận hành bình thường.
- Các test case về bảo mật, phân quyền và Approval phải đạt 100%.

Các trường hợp cố tình tạo Execution Failed, Management Blocked hoặc Verification Failed được đánh giá riêng, không tính vào tỷ lệ khôi phục của nhóm sự cố có thể tự xử lý.

### 4.4. Đo thời gian phát hiện và khôi phục

Ghi nhận các mốc thời gian:

| Mốc | Ý nghĩa |
|---|---|
| T0 | Thời điểm bắt đầu xảy ra sự cố |
| T1 | Thời điểm Portal nhận cảnh báo |
| T2 | Thời điểm bắt đầu thực thi remediation |
| T3 | Thời điểm kết thúc Ansible execution |
| T4 | Thời điểm verification xác nhận dịch vụ đã phục hồi |

Công thức:

- Detection Time = T1 - T0.
- Response Time = T2 - T1.
- Execution Time = T3 - T2.
- Recovery Time = T4 - T0.
- MTTD = Trung bình Detection Time.
- MTTR = Trung bình Recovery Time của các lần khôi phục thành công.

Các lần không khôi phục được phải ghi nhận riêng cùng tỷ lệ thành công, không tự loại bỏ khỏi báo cáo.

### 4.5. So sánh Manual và Auto-remediation

Thực hiện cùng một loại sự cố trên cùng target server với điều kiện tương đương.

Manual Remediation được tính từ thời điểm xảy ra sự cố, bao gồm thời gian phát hiện, người vận hành tiếp nhận cảnh báo, thực hiện action và verification.

Auto-remediation được tính từ thời điểm xảy ra sự cố đến khi hệ thống tự xử lý và verification thành công.

Công thức đánh giá:

Recovery Time Improvement (%) =
(MTTR Manual - MTTR Auto) / MTTR Manual × 100%

Mục tiêu là đánh giá mức giảm thời gian xử lý thực tế trong môi trường kiểm thử, không sử dụng thời gian giả định.

## 5. Minh chứng đánh giá

| Nguồn minh chứng | Nội dung |
|---|---|
| Prometheus | Metrics, trạng thái target và thời điểm phát hiện sự cố. |
| Alertmanager | Alert Firing, Resolved và thời gian gửi cảnh báo. |
| Grafana | Biểu đồ metrics và trạng thái hệ thống. |
| Ansible | Execution Log, Exit Code và kết quả Playbook. |
| Operations Portal | Automation Job, Approval, Incident và Verification. |
| Audit Log | Actor, Role, Action, Timestamp và Result. |
| Email | Nội dung, nhóm người nhận và thời gian nhận thông báo. |
| Target Server | Systemctl, Docker, HTTP, SSH, WinRM và Boot ID. |
| GitHub | Mã nguồn, cấu hình, tài liệu, test case và commit history. |

## 6. Sản phẩm bàn giao

| STT | Sản phẩm bàn giao |
|---|---|
| 1 | Mã nguồn Operations Portal. |
| 2 | Cấu hình Infrastructure, Network và Microsoft Azure. |
| 3 | Cấu hình Prometheus, Grafana và Alertmanager. |
| 4 | Ansible Inventory, Playbook và Remediation Policy. |
| 5 | Cấu hình tích hợp SSO, RBAC và Notification. |
| 6 | Tài liệu System Architecture và Deployment Guide. |
| 7 | Tài liệu Runbook và hướng dẫn vận hành. |
| 8 | Bộ test case và kết quả đo lường metric. |
| 9 | Báo cáo tổng kết đề tài. |
| 10 | Slide và kịch bản demo bảo vệ đề tài. |

## 7. Điều kiện nghiệm thu

Sản phẩm được xem là đạt mục tiêu khi:

- Hoàn thành các chức năng đã cam kết trong phạm vi đề tài.
- Các máy chủ Local và Cloud được giám sát tập trung.
- Auto-remediation và Manual Remediation hoạt động đúng policy.
- Không có action trái quyền hoặc vượt qua Approval Policy.
- Không ghi nhận Success hoặc Resolved sai khi dịch vụ chưa phục hồi.
- Các metric bắt buộc về an toàn và bảo mật đạt 100% hoặc không phát sinh vi phạm.
- Các metric hiệu năng và tỷ lệ thành công đạt ngưỡng đã thống nhất với GVHD.
- Có đầy đủ tài liệu và minh chứng để kiểm tra lại kết quả.

## 8. Phạm vi cam kết

Sản phẩm được triển khai và đánh giá trong môi trường Hybrid Cloud Lab của đề tài.

Nhóm không cam kết khả năng xử lý mọi loại sự cố, triển khai ở quy mô production, High Availability hoặc đáp ứng SLA doanh nghiệp khi chưa có điều kiện kiểm thử tương ứng.

Các kết quả đánh giá cuối cùng được ghi nhận dựa trên số liệu đo thực tế.

## 9. Xác nhận cam kết

Hai thành viên cam kết thực hiện các nội dung sản phẩm, kiểm thử và đánh giá theo phạm vi đã thống nhất.

| Thành viên | Vai trò |
|---|---|
| Đỗ Đăng Thái Bảo | Infrastructure / System / Cloud |
| Nguyễn Thế Gia Bảo | Application / Integration |


