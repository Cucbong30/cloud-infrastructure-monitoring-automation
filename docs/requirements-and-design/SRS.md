# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

## HỆ THỐNG GIÁM SÁT VÀ TỰ ĐỘNG HÓA VẬN HÀNH HẠ TẦNG TRONG MÔI TRƯỜNG HYBRID CLOUD

## 1. Thông tin tài liệu

| Hạng mục | Thông tin |
|---|---|
| Tên tài liệu | Software Requirements Specification |
| Phiên bản | 1.0 |
| Ngày cập nhật | 26/11/2026 |
| Thành viên | Đỗ Đăng Thái Bảo |
| Thành viên | Nguyễn Thế Gia Bảo |

## 2. Giới thiệu

### 2.1. Bối cảnh

Trong môi trường Hybrid Cloud, doanh nghiệp có thể sử dụng đồng thời các máy chủ Linux, Windows và dịch vụ Cloud để vận hành hệ thống.

Việc giám sát và xử lý sự cố trên nhiều môi trường thường yêu cầu người vận hành sử dụng nhiều công cụ khác nhau. Khi xảy ra sự cố, người vận hành phải kiểm tra cảnh báo, xác định nguyên nhân, kết nối đến máy chủ, thực hiện thao tác khôi phục và xác nhận kết quả.

Nếu các bước này được thực hiện thủ công, thời gian xử lý phụ thuộc nhiều vào khả năng phát hiện sự cố và kinh nghiệm của người vận hành. Ngoài ra, việc quản lý quyền thực thi và truy vết các thao tác cũng gặp khó khăn nếu không có hệ thống ghi nhận tập trung.

### 2.2. Bài toán cần giải quyết

| ID | Vấn đề | Ảnh hưởng |
|---|---|---|
| BP-01 | Giám sát phân tán giữa các môi trường. | Khó theo dõi trạng thái tổng thể của hạ tầng. |
| BP-02 | Phát hiện sự cố phụ thuộc vào người vận hành. | Tăng thời gian phát hiện và xử lý. |
| BP-03 | Các thao tác khôi phục được thực hiện thủ công và lặp lại. | Tốn thời gian và có nguy cơ sai sót. |
| BP-04 | Automation thiếu cơ chế kiểm soát. | Có thể thực thi sai, chạy lặp hoặc gây ảnh hưởng đến dịch vụ. |
| BP-05 | Thiếu quy trình phê duyệt đối với action có rủi ro cao. | Tăng nguy cơ thực hiện thao tác ngoài thẩm quyền. |
| BP-06 | Thiếu thông tin truy vết tập trung. | Khó xác định ai đã thực hiện action và kết quả xử lý. |
| BP-07 | Chưa quản lý đầy đủ vòng đời sự cố. | Khó theo dõi sự cố đang xử lý, đã phục hồi hoặc tái diễn. |

### 2.3. Mục tiêu hệ thống

- Giám sát tập trung các máy chủ trong môi trường Local và Cloud.
- Phát hiện và hiển thị cảnh báo khi xảy ra sự cố.
- Tự động khôi phục các dịch vụ nằm trong phạm vi cho phép.
- Hỗ trợ người vận hành thực hiện Manual Remediation.
- Kiểm soát automation bằng Pre-check, Verification, Retry và Cooldown.
- Phân quyền người dùng và phê duyệt các action có rủi ro.
- Quản lý vòng đời sự cố và lịch sử xử lý.
- Ghi nhận đầy đủ thông tin phục vụ kiểm tra và truy vết.
- Đánh giá hiệu quả vận hành thông qua các metric định lượng.

## 3. Phạm vi hệ thống

### 3.1. Phạm vi Infrastructure

| Máy chủ | Môi trường | Vai trò |
|---|---|---|
| MON01 | Local – Linux | Monitoring và Ansible Control Node |
| WEB01 | Local – Linux | Nginx Web Server |
| APP01 | Local – Linux | Docker Application Server |
| WIN01 | Local – Windows Server | Windows Service và Windows Exporter |
| AZURE01 | Microsoft Azure – Linux | Cloud Web Server |

### 3.2. Phạm vi chức năng

Hệ thống bao gồm các nhóm chức năng:

- Authentication và Authorization.
- Server Inventory.
- Monitoring Dashboard.
- Alert Management.
- Manual Remediation.
- Controlled Auto-remediation.
- Automation Job Management.
- Approval Workflow.
- Incident Management.
- Email Notification.
- Audit Trail.
- Runbook.

### 3.3. Ngoài phạm vi

- Tự động xử lý mọi loại sự cố hạ tầng.
- Quản lý đồng thời nhiều nhà cung cấp Cloud.
- Tự động phân tích nguyên nhân sự cố bằng AI hoặc Machine Learning.
- Quản lý Kubernetes Cluster.
- High Availability và Disaster Recovery ở quy mô production.
- Tích hợp đầy đủ với các nền tảng ITSM bên ngoài.
- Cam kết SLA vận hành cho hệ thống doanh nghiệp thực tế.

## 4. Stakeholders và đối tượng sử dụng

### 4.1. Stakeholders

| Stakeholder | Nhu cầu |
|---|---|
| IT Administrator | Quản lý hạ tầng, phân quyền, phê duyệt và kiểm soát automation. |
| IT Operator | Theo dõi cảnh báo, xử lý sự cố và thực hiện remediation. |
| IT Viewer | Theo dõi trạng thái hệ thống và kết quả vận hành. |
| IT Management | Theo dõi hiệu quả xử lý sự cố và khả năng truy vết. |
| Nhóm phát triển | Triển khai, bảo trì, kiểm thử và cập nhật hệ thống. |

Các stakeholder trên là nhóm đối tượng sử dụng mục tiêu của sản phẩm.

### 4.2. Vai trò người dùng

| Vai trò | Mô tả |
|---|---|
| Admin | Quản trị hệ thống, thực hiện remediation và phê duyệt các action có rủi ro. |
| Operator | Giám sát, xử lý cảnh báo, thực hiện action LOW và yêu cầu action MEDIUM. |
| Viewer | Chỉ được xem thông tin, không được thực hiện các thao tác thay đổi hệ thống. |
| SYSTEM | Actor đại diện cho các tác vụ tự động, không phải tài khoản đăng nhập của người dùng. |

## 5. Business Requirements

| ID | Yêu cầu nghiệp vụ | Tiêu chí chấp nhận |
|---|---|---|
| BR-01 | Giám sát tập trung hạ tầng Hybrid Cloud. | Theo dõi được trạng thái của 5/5 máy chủ trong phạm vi đề tài. |
| BR-02 | Phát hiện sự cố kịp thời. | Tỷ lệ phát hiện sự cố đạt tối thiểu 95%. |
| BR-03 | Giảm thời gian xử lý sự cố. | MTTR của Auto-remediation giảm tối thiểu 30% so với Manual Remediation trong điều kiện kiểm thử tương đương. |
| BR-04 | Tự động hóa các thao tác vận hành lặp lại. | Tỷ lệ Auto-remediation thành công đạt tối thiểu 90% đối với sự cố đủ điều kiện. |
| BR-05 | Kiểm soát rủi ro khi thực thi automation. | Không có action trái quyền hoặc vượt qua Approval Policy. |
| BR-06 | Quản lý toàn bộ quá trình xử lý sự cố. | Incident có trạng thái và liên kết với Alert, Target và Job phát sinh. |
| BR-07 | Đảm bảo khả năng truy vết. | 100% thao tác thuộc phạm vi audit được ghi nhận đầy đủ. |
| BR-08 | Thông báo kịp thời cho người vận hành. | Tối thiểu 95% Email kiểm thử được nhận đúng nhóm severity. |

## 6. Functional Requirements

### 6.1. Authentication & Authorization

| ID | Yêu cầu chức năng | Acceptance Criteria | Ưu tiên |
|---|---|---|---|
| FR-AUTH-01 | Đăng nhập bằng Microsoft Entra ID. | Người dùng có tài khoản hợp lệ đăng nhập được vào Portal. | Must |
| FR-AUTH-02 | Xác định vai trò người dùng. | Hệ thống xác định đúng Admin, Operator hoặc Viewer dựa trên thông tin phân quyền. | Must |
| FR-AUTH-03 | Kiểm soát quyền truy cập chức năng. | Người dùng không đủ quyền bị chặn tại cả giao diện và backend. | Must |
| FR-AUTH-04 | Đăng xuất khỏi hệ thống. | Sau khi đăng xuất, người dùng không thể truy cập chức năng yêu cầu xác thực bằng phiên đăng nhập cũ. | Must |

### 6.2. Server Inventory

| ID | Yêu cầu chức năng | Acceptance Criteria | Ưu tiên |
|---|---|---|---|
| FR-INV-01 | Hiển thị danh sách máy chủ. | Hiển thị được MON01, WEB01, APP01, WIN01 và AZURE01. | Must |
| FR-INV-02 | Hiển thị thông tin máy chủ. | Có hostname, địa chỉ kết nối, hệ điều hành, môi trường và trạng thái. | Must |
| FR-INV-03 | Quản lý thông tin máy chủ. | Admin có thể quản lý thông tin Inventory theo quyền được cấp. | Must |
| FR-INV-04 | Kiểm tra dữ liệu đầu vào. | Không chấp nhận hostname hoặc địa chỉ kết nối không hợp lệ theo quy tắc validation. | Must |

### 6.3. Monitoring Dashboard

| ID | Yêu cầu chức năng | Acceptance Criteria | Ưu tiên |
|---|---|---|---|
| FR-MON-01 | Thu thập metrics từ các máy chủ. | Thu thập được CPU, RAM, Disk và Uptime từ các target đã cấu hình. | Must |
| FR-MON-02 | Hiển thị metrics trên Dashboard. | Giá trị hiển thị được lấy từ nguồn Monitoring thực tế. | Must |
| FR-MON-03 | Hiển thị trạng thái máy chủ và dịch vụ. | Phân biệt được Healthy, Degraded và Unreachable. | Must |
| FR-MON-04 | Giám sát dịch vụ. | Phát hiện được trạng thái bất thường của các dịch vụ nằm trong phạm vi giám sát. | Must |
| FR-MON-05 | Xử lý khi nguồn metrics không khả dụng. | Hiển thị N/A hoặc trạng thái không khả dụng, không sử dụng dữ liệu giả để báo Healthy. | Must |
| FR-MON-06 | Hiển thị biểu đồ Monitoring. | Người dùng có thể theo dõi metrics và xu hướng thông qua Grafana. | Must |

### 6.4. Alert Management

| ID | Yêu cầu chức năng | Acceptance Criteria | Ưu tiên |
|---|---|---|---|
| FR-ALT-01 | Tiếp nhận cảnh báo từ Alertmanager. | Cảnh báo hợp lệ được tiếp nhận và lưu trên Portal. | Must |
| FR-ALT-02 | Quản lý trạng thái cảnh báo. | Hiển thị đúng trạng thái Firing và Resolved. | Must |
| FR-ALT-03 | Phân loại mức độ cảnh báo. | Cảnh báo được phân loại theo severity đã cấu hình. | Must |
| FR-ALT-04 | Hạn chế cảnh báo trùng lặp. | Các lần gửi lại cùng một cảnh báo đang hoạt động không tạo bản ghi trùng không cần thiết. | Must |
| FR-ALT-05 | Gợi ý remediation action. | Hiển thị action phù hợp với target và dịch vụ gặp lỗi nếu có action mapping. | Must |
| FR-ALT-06 | Xác nhận cảnh báo. | Người dùng có quyền thực hiện acknowledge và thao tác được ghi nhận. | Must |

### 6.5. Manual Remediation

| ID | Yêu cầu chức năng | Acceptance Criteria | Ưu tiên |
|---|---|---|---|
| FR-MAN-01 | Thực hiện remediation thủ công. | Admin hoặc Operator có thể yêu cầu action phù hợp với quyền và Risk Level. | Must |
| FR-MAN-02 | Kiểm tra management channel. | Không thực thi playbook khi SSH hoặc WinRM không khả dụng. | Must |
| FR-MAN-03 | Thực thi action được cho phép. | Chỉ các action nằm trong allow-list được gọi thông qua Portal. | Must |
| FR-MAN-04 | Xác nhận trạng thái sau thực thi. | Chỉ ghi nhận SUCCESS khi verification thành công. | Must |
| FR-MAN-05 | Thực hiện lại remediation. | Khi người dùng chạy lại action, hệ thống tạo job mới và giữ nguyên lịch sử job cũ. | Must |

### 6.6. Controlled Auto-remediation

| ID | Yêu cầu chức năng | Acceptance Criteria | Ưu tiên |
|---|---|---|---|
| FR-AUTO-01 | Tự động tạo remediation job từ cảnh báo. | Job chỉ được tạo để thực thi tự động khi action đủ điều kiện theo policy. | Must |
| FR-AUTO-02 | Thực hiện Pre-check. | Kiểm tra target và management channel trước khi gọi Ansible. | Must |
| FR-AUTO-03 | Giới hạn Retry. | Execution Failed chỉ được tự động retry tối đa một lần cho mỗi Incident. | Must |
| FR-AUTO-04 | Áp dụng Cooldown. | Không tự động chạy lại cùng target và action trong vòng 120 giây sau remediation thành công. | Must |
| FR-AUTO-05 | Chống Duplicate Job. | Không thực thi thêm playbook khi cùng target và action đang Queued hoặc Running. | Must |
| FR-AUTO-06 | Xử lý Verification Failed. | Không tự động retry khi playbook thực thi xong nhưng verification thất bại. | Must |
| FR-AUTO-07 | Chuyển sang Manual Required. | Khi không thể tự khôi phục theo policy, hệ thống ghi nhận trạng thái cần người vận hành can thiệp. | Must |
| FR-AUTO-08 | Kiểm soát Risk Level. | Chỉ action LOW được phép Auto-remediation. MEDIUM và HIGH phải qua Approval Workflow. | Must |

### 6.7. Automation Job Management

| ID | Yêu cầu chức năng | Acceptance Criteria | Ưu tiên |
|---|---|---|---|
| FR-JOB-01 | Hiển thị danh sách Automation Job. | Người dùng xem được lịch sử job và trạng thái thực thi. | Must |
| FR-JOB-02 | Hiển thị Job Detail. | Có target, action, trigger, thời gian, execution result và verification result. | Must |
| FR-JOB-03 | Phân biệt chế độ thực thi. | Job được xác định là AUTO hoặc MANUAL. | Must |
| FR-JOB-04 | Phân biệt kết quả xử lý. | Hiển thị đúng Success, Execution Failed, Verification Failed, Blocked, Duplicate Skipped hoặc Manual Required theo từng trường hợp. | Must |
| FR-JOB-05 | Lưu lịch sử thực thi. | Các job đã thực hiện không bị ghi đè khi chạy remediation mới. | Must |

### 6.8. Approval Workflow

| ID | Yêu cầu chức năng | Acceptance Criteria | Ưu tiên |
|---|---|---|---|
| FR-APR-01 | Phân loại Risk Level. | Mỗi remediation action được xác định là LOW, MEDIUM hoặc HIGH. | Must |
| FR-APR-02 | Thực thi action LOW. | Action LOW được thực thi trực tiếp nếu đáp ứng các điều kiện kiểm soát khác. | Must |
| FR-APR-03 | Yêu cầu approval cho MEDIUM và HIGH. | Không tạo execution job trước khi yêu cầu được Admin phê duyệt. | Must |
| FR-APR-04 | Kiểm soát quyền yêu cầu. | Operator được yêu cầu MEDIUM nhưng không được yêu cầu HIGH. | Must |
| FR-APR-05 | Kiểm soát quyền phê duyệt. | Chỉ Admin được approve hoặc reject request. | Must |
| FR-APR-06 | Xử lý yêu cầu hết hạn. | Request Pending hết hạn sau 5 phút và không được thực thi. | Must |
| FR-APR-07 | Xử lý yêu cầu bị từ chối. | Request Rejected không gọi Ansible playbook. | Must |
| FR-APR-08 | Lưu lịch sử phê duyệt. | Ghi nhận requester, approver, decision, timestamp và action. | Must |

### 6.9. Incident Management

| ID | Yêu cầu chức năng | Acceptance Criteria | Ưu tiên |
|---|---|---|---|
| FR-INC-01 | Tạo Incident từ cảnh báo phù hợp. | Incident được tạo và liên kết với Alert và Target tương ứng. | Must |
| FR-INC-02 | Quản lý vòng đời Incident. | Hỗ trợ OPEN, ACKNOWLEDGED, IN_PROGRESS, RESOLVED và CLOSED theo quy tắc chuyển trạng thái. | Must |
| FR-INC-03 | Liên kết Incident với Automation Job. | Một Incident có thể truy vết nhiều job phát sinh trong quá trình xử lý. | Must |
| FR-INC-04 | Tự động xác nhận phục hồi. | Incident đủ điều kiện được chuyển sang RESOLVED khi remediation và verification thành công. | Must |
| FR-INC-05 | Xử lý remediation thất bại. | Incident không tự chuyển sang RESOLVED hoặc CLOSED khi dịch vụ chưa phục hồi. | Must |
| FR-INC-06 | Hỗ trợ xử lý Incident thủ công. | Người dùng có quyền có thể cập nhật Incident theo quy trình được cho phép. | Must |
| FR-INC-07 | Quản lý sự cố tái diễn. | Sự cố phát sinh lại sau khi phục hồi được ghi nhận và không làm mất lịch sử Incident trước đó. | Must |
| FR-INC-08 | Hiển thị lịch sử Incident. | Người dùng xem được trạng thái, các job và thao tác liên quan đến Incident. | Must |

### 6.10. Email Notification

| ID | Yêu cầu chức năng | Acceptance Criteria | Ưu tiên |
|---|---|---|---|
| FR-NOT-01 | Gửi Email thông báo. | Hệ thống gửi yêu cầu gửi Email thông qua Microsoft Graph. | Must |
| FR-NOT-02 | Phân loại người nhận. | Email được gửi đến Distribution Group tương ứng với Critical, Warning hoặc Info. | Must |
| FR-NOT-03 | Hiển thị nội dung sự cố. | Email có target, service, event, timestamp, action và trạng thái xử lý. | Must |
| FR-NOT-04 | Xử lý lỗi Notification. | Lỗi gửi Email được ghi nhận nhưng không làm gián đoạn remediation đang thực thi. | Must |

### 6.11. Audit Trail

| ID | Yêu cầu chức năng | Acceptance Criteria | Ưu tiên |
|---|---|---|---|
| FR-AUD-01 | Ghi nhận thao tác người dùng. | Lưu actor, role, action, target, timestamp và result đối với thao tác cần audit. | Must |
| FR-AUD-02 | Ghi nhận thao tác tự động. | Các Auto-remediation Job được ghi nhận với actor SYSTEM và mode AUTO. | Must |
| FR-AUD-03 | Ghi nhận Approval Workflow. | Lưu thông tin yêu cầu, phê duyệt, từ chối và hết hạn. | Must |
| FR-AUD-04 | Ghi nhận thay đổi Incident. | Các thao tác thay đổi trạng thái Incident được lưu lại. | Must |
| FR-AUD-05 | Bảo vệ lịch sử Audit. | Không cung cấp chức năng sửa hoặc xóa Audit Log thông qua giao diện vận hành thông thường. | Must |

## 7. Non-functional Requirements

### 7.1. Performance & Reliability

| ID | Yêu cầu | Ràng buộc định lượng | Metric |
|---|---|---|---|
| NFR-PER-01 | Thời gian phát hiện sự cố. | MTTD ≤ 60 giây. | M03 |
| NFR-PER-02 | Thời gian khôi phục sự cố LOW Risk đủ điều kiện tự xử lý. | MTTR ≤ 180 giây. | M07 |
| NFR-PER-03 | Hiệu quả Auto-remediation. | Giảm MTTR tối thiểu 30% so với Manual Remediation. | M08 |
| NFR-REL-01 | Khả năng thu thập metrics. | Tỷ lệ thu thập thành công ≥ 99% trong 24 giờ vận hành bình thường. | M05 |
| NFR-REL-02 | Tỷ lệ Auto-remediation thành công. | ≥ 90% đối với sự cố đủ điều kiện. | M06 |
| NFR-REL-03 | Tỷ lệ phát hiện sự cố. | ≥ 95%. | M02 |
| NFR-REL-04 | Khả năng gửi thông báo. | Tỷ lệ nhận Email đúng nhóm ≥ 95%. | M25 |
| NFR-REL-05 | Thời gian thông báo. | Thời gian trung bình từ sự kiện đến khi nhận Email ≤ 60 giây. | M26 |

### 7.2. Security & Safety

| ID | Yêu cầu | Ràng buộc định lượng | Metric |
|---|---|---|---|
| NFR-SEC-01 | Kiểm soát quyền thực thi. | 100% test case RBAC đạt. | M16 |
| NFR-SEC-02 | Ngăn chặn thao tác trái quyền. | 0 lần thực thi action trái quyền. | M18 |
| NFR-SEC-03 | Kiểm soát Approval. | 100% test case Approval Policy đạt. | M17 |
| NFR-SEC-04 | Ngăn thực thi request không hợp lệ. | 0 playbook được thực thi từ request Rejected hoặc Expired. | M19 |
| NFR-SEC-05 | Bảo vệ credential. | 0 credential thực tế được lưu dưới dạng plain text trong mã nguồn và Git history. | M20 |
| NFR-SEC-06 | Kiểm tra kết nối quản trị. | 100% trường hợp mất SSH/WinRM trong bộ test được chặn đúng. | M11 |
| NFR-SEC-07 | Đảm bảo kết quả Verification. | 100% kết quả verification trong bộ test khớp với trạng thái thực tế. | M10 |

### 7.3. Maintainability & Traceability

| ID | Yêu cầu | Ràng buộc định lượng | Metric |
|---|---|---|---|
| NFR-MNT-01 | Chuẩn hóa Runbook. | Có đủ Runbook cho 5/5 nhóm trạng thái xử lý đã xác định. | M30 |
| NFR-MNT-02 | Hoàn thiện tài liệu. | 100% tài liệu trong danh sách bàn giao được hoàn thành. | M31 |
| NFR-TRC-01 | Truy vết thao tác. | 100% thao tác thuộc phạm vi audit có đầy đủ trường bắt buộc. | M24 |
| NFR-TRC-02 | Truy vết Incident. | 100% Incident kiểm thử có liên kết với Alert, Target và Job phát sinh. | M22 |

Các ngưỡng định lượng được sử dụng thống nhất với bản cam kết sản phẩm và bộ metric đánh giá.

## 8. Use Case Specification

### 8.1. Danh sách Use Case

| ID | Use Case | Actor | Acceptance Criteria |
|---|---|---|---|
| UC-01 | Đăng nhập hệ thống | Admin, Operator, Viewer | Đăng nhập hợp lệ và xác định đúng role. |
| UC-02 | Theo dõi Dashboard | Admin, Operator, Viewer | Hiển thị metrics và trạng thái từ nguồn thực tế. |
| UC-03 | Quản lý Server Inventory | Admin | Thông tin máy chủ được quản lý và kiểm tra hợp lệ. |
| UC-04 | Theo dõi và xác nhận Alert | Admin, Operator | Alert được acknowledge và ghi nhận người thực hiện. |
| UC-05 | Thực hiện Manual Remediation | Admin, Operator | Action đúng quyền, qua Pre-check và Verification. |
| UC-06 | Thực hiện Auto-remediation | SYSTEM | Tuân thủ allow-list, retry, cooldown và verification. |
| UC-07 | Theo dõi Automation Job | Admin, Operator, Viewer | Xem được lịch sử và kết quả job theo quyền. |
| UC-08 | Yêu cầu action MEDIUM/HIGH | Admin, Operator theo quyền | Tạo approval request hợp lệ, chưa gọi playbook. |
| UC-09 | Phê duyệt hoặc từ chối action | Admin | Chỉ Approved mới được phép chuyển sang thực thi. |
| UC-10 | Quản lý Incident | Admin, Operator | Chuyển trạng thái đúng quy trình và ghi nhận Audit. |
| UC-11 | Tự động cập nhật Incident | SYSTEM | Chỉ xác nhận phục hồi khi đáp ứng điều kiện verification. |
| UC-12 | Gửi Email Notification | SYSTEM | Gửi đúng nội dung và nhóm severity. |
| UC-13 | Tra cứu Audit Log | Người dùng có quyền | Xem được lịch sử thao tác và thông tin truy vết. |
| UC-14 | Đăng xuất | Admin, Operator, Viewer | Phiên đăng nhập Portal được kết thúc. |

### 8.2. UC-05 – Manual Remediation

| Thuộc tính | Nội dung |
|---|---|
| Actor | Admin, Operator |
| Trigger | Người vận hành chọn remediation action. |
| Pre-condition | Đã đăng nhập, có quyền và action nằm trong allow-list. |
| Post-condition | Kết quả xử lý được lưu trong Automation Job và Audit Log. |
| Requirement | FR-MAN-01 đến FR-MAN-05 |

Luồng chính:

1. Người vận hành chọn target và remediation action.
2. Hệ thống kiểm tra quyền và Risk Level.
3. Hệ thống kiểm tra management channel.
4. Ansible thực thi playbook tương ứng.
5. Hệ thống thực hiện verification.
6. Portal hiển thị kết quả và ghi nhận Audit Log.

Luồng thay thế:

- Không đủ quyền: từ chối yêu cầu.
- Action MEDIUM/HIGH: chuyển sang Approval Workflow.
- Management channel down: không gọi playbook.
- Execution Failed: ghi nhận lỗi thực thi.
- Verification Failed: không ghi nhận SUCCESS.

Acceptance Criteria:

- Không thực thi action trái quyền.
- Không gọi playbook khi Pre-check thất bại.
- Chỉ ghi nhận SUCCESS khi verification thành công.

### 8.3. UC-06 – Controlled Auto-remediation

| Thuộc tính | Nội dung |
|---|---|
| Actor | SYSTEM |
| Trigger | Nhận cảnh báo Firing đủ điều kiện xử lý tự động. |
| Pre-condition | Có action mapping và action được phép Auto-remediation. |
| Post-condition | Dịch vụ được xác nhận phục hồi hoặc chuyển sang trạng thái cần xử lý thủ công. |
| Requirement | FR-AUTO-01 đến FR-AUTO-08 |

Luồng chính:

1. Portal tiếp nhận cảnh báo.
2. Xác định target và remediation action.
3. Kiểm tra Risk Level, Duplicate Job và Cooldown.
4. Kiểm tra management channel.
5. Tạo và thực thi Automation Job.
6. Thực hiện verification.
7. Cập nhật Job, Incident, Audit và Notification.

Luồng thay thế:

- Duplicate Job: bỏ qua thực thi trùng.
- Chưa hết Cooldown: không thực thi action.
- Management Blocked: không gọi playbook.
- Execution Failed: retry tối đa một lần nếu đủ điều kiện.
- Retry thất bại: chuyển Manual Required.
- Verification Failed: không tự động retry.

Acceptance Criteria:

- Không thực thi action MEDIUM/HIGH tự động.
- Không vượt quá giới hạn retry.
- Không thực thi job trùng.
- Tuân thủ Cooldown 120 giây.
- Không ghi nhận thành công khi dịch vụ chưa phục hồi.

### 8.4. UC-09 – Approval Workflow

| Thuộc tính | Nội dung |
|---|---|
| Actor | Admin |
| Trigger | Có request MEDIUM hoặc HIGH đang Pending. |
| Pre-condition | Request hợp lệ và chưa hết hạn. |
| Post-condition | Request được Approved, Rejected hoặc Expired. |
| Requirement | FR-APR-01 đến FR-APR-08 |

Luồng chính:

1. Admin xem thông tin yêu cầu.
2. Admin kiểm tra target, action và Risk Level.
3. Admin thực hiện approve hoặc reject.
4. Hệ thống ghi nhận quyết định.
5. Nếu Approved, hệ thống chuyển sang luồng thực thi có kiểm soát.
6. Kết quả được ghi nhận trong Job và Audit Log.

Luồng thay thế:

- Người dùng không đủ quyền: từ chối thao tác.
- Request hết hạn: chuyển Expired.
- Request bị từ chối: chuyển Rejected và không gọi playbook.

Acceptance Criteria:

- Chỉ Admin được phê duyệt.
- Request Pending hết hạn sau 5 phút.
- Rejected và Expired không được thực thi.
- Có lịch sử requester, approver và decision.

### 8.5. UC-10 – Incident Management

| Thuộc tính | Nội dung |
|---|---|
| Actor | Admin, Operator |
| Trigger | Incident được tạo từ cảnh báo phù hợp. |
| Pre-condition | Người dùng đã đăng nhập và có quyền xử lý Incident. |
| Post-condition | Incident được cập nhật theo trạng thái thực tế và có lịch sử xử lý. |
| Requirement | FR-INC-01 đến FR-INC-08 |

Luồng chính:

1. Hệ thống tạo Incident khi phát hiện sự cố.
2. Người vận hành tiếp nhận Incident.
3. Incident chuyển sang trạng thái xử lý.
4. Thực hiện remediation nếu cần.
5. Xác nhận dịch vụ đã phục hồi.
6. Incident chuyển sang RESOLVED.
7. Người dùng có quyền kiểm tra và đóng Incident.

Luồng thay thế:

- Remediation thất bại: Incident tiếp tục được theo dõi.
- Management Blocked: yêu cầu người vận hành can thiệp.
- Verification Failed: không tự động resolve.
- Sự cố tái diễn: ghi nhận lần phát sinh mới và giữ lịch sử trước đó.

Acceptance Criteria:

- Incident có liên kết với Alert và Target.
- Truy vết được các Automation Job phát sinh.
- Không tự động đóng Incident khi dịch vụ chưa phục hồi.
- Các thay đổi trạng thái được ghi nhận trong Audit Log.

## 9. Business Rules

| ID | Quy tắc |
|---|---|
| RULE-01 | Viewer không được thực hiện thao tác thay đổi hệ thống. |
| RULE-02 | Operator được thực thi action LOW và yêu cầu action MEDIUM. |
| RULE-03 | Operator không được yêu cầu action HIGH hoặc phê duyệt request. |
| RULE-04 | Chỉ Admin được phê duyệt action MEDIUM/HIGH. |
| RULE-05 | Action không nằm trong allow-list không được thực thi. |
| RULE-06 | MEDIUM và HIGH không được thực hiện bằng Auto-remediation. |
| RULE-07 | Management channel phải khả dụng trước khi thực thi playbook. |
| RULE-08 | Auto-remediation được retry tối đa một lần khi Execution Failed. |
| RULE-09 | Manual Remediation không tự động retry. |
| RULE-10 | Verification Failed không kích hoạt auto-retry. |
| RULE-11 | Cooldown là 120 giây sau remediation thành công. |
| RULE-12 | Không thực thi trùng cùng target và action đang Queued hoặc Running. |
| RULE-13 | Approval request Pending hết hạn sau 5 phút. |
| RULE-14 | Request Rejected hoặc Expired không được gọi Ansible. |
| RULE-15 | Chỉ ghi nhận SUCCESS khi verification thành công. |
| RULE-16 | Incident không tự động resolve khi dịch vụ chưa phục hồi. |
| RULE-17 | Job mới không được ghi đè lịch sử job cũ. |
| RULE-18 | Lỗi Notification không được làm gián đoạn remediation. |

## 10. External Interface Requirements

| Thành phần | Giao tiếp | Mục đích |
|---|---|---|
| Web Browser | HTTP/HTTPS | Truy cập Operations Portal. |
| Prometheus | HTTP API | Truy vấn metrics và trạng thái Monitoring. |
| Alertmanager | HTTP Webhook | Gửi cảnh báo đến Portal. |
| Grafana | Web Interface | Hiển thị biểu đồ Monitoring. |
| Ansible | Execution Interface | Thực thi remediation playbook. |
| Linux Server | SSH | Quản trị và thực thi action trên Linux. |
| Windows Server | WinRM | Quản trị và thực thi action trên Windows. |
| Microsoft Entra ID | OpenID Connect / OAuth 2.0 | Xác thực và lấy thông tin phân quyền. |
| Microsoft Graph | REST API | Gửi Email Notification. |
| Azure Virtual Machine | SSH và Monitoring Endpoint | Quản lý và giám sát Cloud Server. |

Chi tiết API endpoint, cấu hình giao tiếp và luồng dữ liệu được mô tả trong tài liệu SDD.

## 11. Data Requirements

| Nhóm dữ liệu | Thông tin cần quản lý |
|---|---|
| User | Identity, Role và thông tin tài khoản. |
| Server | Hostname, Address, OS, Environment và Status. |
| Alert | Target, Severity, Fingerprint, Status và Timestamp. |
| Automation Job | Target, Action, Mode, Actor, Execution Result và Verification Result. |
| Approval | Requester, Approver, Risk Level, Decision và Expiration. |
| Incident | Alert, Target, Severity, Status, Job History và các mốc thời gian. |
| Audit Log | Actor, Role, Action, Target, Timestamp và Result. |
| Notification | Event, Severity, Recipient Group và Delivery Result. |

Các nhóm dữ liệu trên thể hiện yêu cầu lưu trữ nghiệp vụ, không phải danh sách bảng vật lý của Database.

Database Schema, Primary Key, Foreign Key và quan hệ giữa các bảng được mô tả trong SDD.

## 12. Constraints & Assumptions

### 12.1. Ràng buộc

- Hệ thống được triển khai trong môi trường Hybrid Cloud Lab.
- Phần Cloud sử dụng Microsoft Azure.
- Monitoring sử dụng Prometheus, Grafana và Alertmanager.
- Automation sử dụng Ansible.
- Operations Portal sử dụng Flask và SQLite.
- Các remediation action được giới hạn theo Action Risk Matrix.
- Hệ thống phụ thuộc vào khả năng kết nối giữa các thành phần Local và Cloud.
- SSO và Email Notification phụ thuộc vào các dịch vụ Microsoft tương ứng.

### 12.2. Giả định

- Các máy chủ đã được cấu hình địa chỉ và kết nối phù hợp.
- SSH và WinRM được cấu hình đúng trên target server.
- Người dùng được cấp tài khoản và quyền phù hợp.
- Microsoft Entra ID và Microsoft Graph khả dụng trong quá trình kiểm thử.
- Các máy chủ được đồng bộ thời gian để đảm bảo tính chính xác của log và metric.
- Các tình huống sự cố được tạo có kiểm soát trong môi trường lab.

## 13. Acceptance & Evaluation

Sản phẩm được nghiệm thu dựa trên:

- Mức độ hoàn thành các Functional Requirements.
- Kết quả kiểm thử Non-functional Requirements.
- Acceptance Criteria của từng Use Case.
- Kết quả kiểm thử Business Rules.
- Bộ metric đánh giá đã thống nhất.
- Mã nguồn, tài liệu và minh chứng thực tế.

Mỗi yêu cầu phải có mã định danh để liên kết với thiết kế và test case tương ứng.

Các yêu cầu chưa được triển khai hoặc chưa kiểm thử không được ghi nhận là đã nghiệm thu.

## 14. Tài liệu liên quan

- [Bản cam kết sản phẩm và bộ metric đánh giá](../project-management/product-commitment-and-metrics.md)
- [Bảng phân công công việc](../project-management/work-assignment.md)
- [Tiến độ thực hiện theo tuần](../project-management/weekly-progress/)
- Software Design Description (SDD) – cập nhật sau.
- Requirements Traceability Matrix (RTM) – cập nhật sau.

## 15. Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 26/11/2026 | Xây dựng bản đặc tả yêu cầu hệ thống và tiêu chí chấp nhận. |
