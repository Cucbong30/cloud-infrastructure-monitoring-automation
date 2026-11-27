# SOFTWARE DESIGN DESCRIPTION (SDD)

## HỆ THỐNG GIÁM SÁT VÀ TỰ ĐỘNG HÓA VẬN HÀNH HẠ TẦNG TRONG MÔI TRƯỜNG HYBRID CLOUD

## 1. Thông tin tài liệu

| Hạng mục | Thông tin |
|---|---|
| Tên tài liệu | Software Design Description |
| Phiên bản | 1.0 |
| Ngày cập nhật | 26/11/2026 |
| Infrastructure / System / Cloud | Đỗ Đặng Thái Bảo |
| Application / Integration | Nguyễn Thế Gia Bảo |
| Tài liệu tham chiếu | Software Requirements Specification (SRS) |
| Trạng thái | Bản thiết kế, chờ rà soát và xác nhận |

## 2. Tổng quan thiết kế

### 2.1. Mục tiêu thiết kế

Hệ thống được thiết kế theo hướng tập trung giám sát và điều phối các thao tác vận hành thông qua Operations Portal.

Các thành phần Monitoring, Automation, Application và Identity được phân tách theo chức năng nhưng có khả năng trao đổi dữ liệu với nhau.

Thiết kế hướng đến các mục tiêu:

- Quản lý đồng thời hạ tầng Local và Microsoft Azure.
- Tập trung dữ liệu giám sát và cảnh báo.
- Tách biệt chức năng phát hiện sự cố và thực thi remediation.
- Kiểm soát automation theo quyền, mức rủi ro và trạng thái thực tế của dịch vụ.
- Hạn chế việc thực thi lặp hoặc thực thi ngoài phạm vi cho phép.
- Lưu lại lịch sử để phục vụ vận hành và kiểm tra.
- Có khả năng bổ sung target server, remediation action và monitoring rule.

### 2.2. Nguyên tắc thiết kế

| Nguyên tắc | Cách áp dụng |
|---|---|
| Separation of Concerns | Phân tách Monitoring, Automation, Application và Identity. |
| Least Privilege | Người dùng và tài khoản quản trị chỉ được cấp quyền cần thiết. |
| Fail-closed | Không thực thi action khi không xác định được quyền hoặc điều kiện an toàn. |
| Controlled Automation | Automation phải tuân thủ allow-list, pre-check, retry, cooldown và approval. |
| Verification-based Recovery | Kết quả khôi phục được xác nhận bằng trạng thái thực tế của dịch vụ. |
| Traceability | Các thao tác và kết quả xử lý được ghi nhận để truy vết. |
| Maintainability | Tách cấu hình, playbook, business logic và giao diện để thuận tiện bảo trì. |

## 3. System Architecture

### 3.1. Kiến trúc tổng thể

Hệ thống được chia thành sáu lớp chức năng.

| Lớp | Thành phần | Trách nhiệm |
|---|---|---|
| Presentation Layer | Operations Portal, Grafana | Hiển thị thông tin và cung cấp giao diện vận hành. |
| Application Layer | Flask Application | Xử lý yêu cầu, business logic, RBAC và workflow. |
| Data Layer | SQLite | Lưu thông tin nghiệp vụ và lịch sử vận hành. |
| Monitoring Layer | Prometheus, Alertmanager, Exporters | Thu thập metrics, đánh giá alert rule và gửi cảnh báo. |
| Automation Layer | Ansible Control Node, Inventory, Playbooks | Thực thi remediation trên target server. |
| Infrastructure Layer | Local Servers, Azure VM, MGMT01 | Cung cấp môi trường chạy dịch vụ và kết nối quản trị. |

Microsoft Entra ID và Microsoft Graph là các dịch vụ bên ngoài được tích hợp với Application Layer để hỗ trợ xác thực và gửi Email Notification.

### 3.2. Luồng hoạt động tổng thể

1. Prometheus thu thập metrics từ các máy chủ Local và Cloud.
2. Prometheus đánh giá alert rule dựa trên dữ liệu giám sát.
3. Khi điều kiện cảnh báo được đáp ứng, Prometheus gửi alert đến Alertmanager.
4. Alertmanager chuyển cảnh báo đến Operations Portal.
5. Portal lưu thông tin cảnh báo và xác định remediation action phù hợp.
6. Hệ thống kiểm tra quyền, Risk Level và các điều kiện thực thi.
7. Ansible thực hiện playbook trên target server.
8. Hệ thống kiểm tra trạng thái dịch vụ sau khi thực thi.
9. Portal cập nhật Automation Job, Incident và Audit Log.
10. Microsoft Graph được sử dụng để gửi thông báo theo sự kiện và severity.

### 3.3. Sơ đồ kiến trúc

Sơ đồ System Architecture được quản lý tại:

`diagrams/system-architecture.md`

## 4. Infrastructure Design

### 4.1. Danh sách máy chủ

| Server | Hệ điều hành | Môi trường | Địa chỉ | Vai trò |
|---|---|---|---|---|
| MGMT01 | Ubuntu Server | Local | 192.168.10.5 | Management Gateway, Tailscale Subnet Router |
| MON01 | Ubuntu Server | Local | 192.168.10.10 | Prometheus, Grafana, Alertmanager, Ansible |
| WEB01 | Ubuntu Server | Local | 192.168.10.11 | Nginx Web Server |
| APP01 | Ubuntu Server | Local | 192.168.10.12 | Docker Application Server |
| WIN01 | Windows Server 2022 | Local | 192.168.10.13 | Windows Service, Windows Exporter |
| AZURE01 | Ubuntu Server 24.04 | Microsoft Azure | 172.16.0.4 (Private IP) | Cloud Web Server |

MGMT01 là máy chủ hỗ trợ kết nối quản trị từ xa, không thuộc năm monitoring target chính được xác định trong SRS và bộ metric đánh giá.

Địa chỉ Public IP của AZURE01 được quản lý trong cấu hình triển khai và có thể thay đổi theo môi trường.

### 4.2. Phân bố dịch vụ

| Server | Thành phần triển khai |
|---|---|
| MGMT01 | Tailscale, IP Forwarding, Subnet Routing |
| MON01 | Prometheus, Grafana, Alertmanager, Node Exporter, Ansible |
| WEB01 | Nginx, Node Exporter, SSH |
| APP01 | Docker Engine, Application Container, Node Exporter, SSH |
| WIN01 | Windows Exporter, WinRM |
| AZURE01 | Nginx, Node Exporter, SSH |

### 4.3. Phân tách Management và Monitoring

MGMT01 được triển khai riêng để cung cấp khả năng truy cập từ xa vào mạng Lab.

MON01 tập trung đảm nhiệm chức năng Monitoring và Automation. Việc tách MGMT01 khỏi MON01 giúp thành viên phụ trách Application vẫn có thể truy cập các target server khi thực hiện kiểm thử sự cố trên MON01, với điều kiện MGMT01 và mạng Lab vẫn hoạt động.

## 5. Network Design

### 5.1. Local Network

| Hạng mục | Cấu hình |
|---|---|
| Network | 192.168.10.0/24 |
| Môi trường ảo hóa | VMware |
| Remote Access | Tailscale |
| Subnet Router | MGMT01 |
| Monitoring Node | MON01 |
| Linux Management | SSH |
| Windows Management | WinRM |

Application Laptop kết nối vào Tailscale Network và truy cập các máy chủ Local thông qua subnet route được cấu hình trên MGMT01.

### 5.2. Microsoft Azure Network

| Thành phần | Vai trò |
|---|---|
| Resource Group | Quản lý tập trung các tài nguyên Azure của đề tài. |
| Virtual Network | Cung cấp mạng riêng cho Azure VM. |
| Subnet | Phân vùng mạng cho AZURE01. |
| Network Security Group | Kiểm soát lưu lượng truy cập đến Azure VM. |
| Public IP | Cung cấp địa chỉ kết nối từ môi trường Local đến Azure. |
| Virtual Machine | Chạy Nginx và Node Exporter. |

MON01 kết nối đến AZURE01 thông qua Public IP và các cổng được NSG cho phép.

Kết nối Hybrid Cloud trong phạm vi đề tài không sử dụng Azure VPN Gateway hoặc ExpressRoute.

### 5.3. Port Design

| Port | Protocol | Thành phần | Mục đích |
|---|---|---|---|
| 22 | TCP | Linux Server | SSH và Ansible Management |
| 80 | TCP | WEB01, AZURE01 | Nginx HTTP Service |
| 3000 | TCP | MON01 | Grafana |
| 5000 | TCP | Application Host | Flask Operations Portal |
| 5985 | TCP | WIN01 | WinRM HTTP |
| 8080 | TCP | APP01 | Application Container |
| 9090 | TCP | MON01 | Prometheus API và Web UI |
| 9093 | TCP | MON01 | Alertmanager |
| 9100 | TCP | Linux Server | Node Exporter |
| 9182 | TCP | WIN01 | Windows Exporter |
| 443 | TCP | Microsoft Cloud Services | Entra ID và Microsoft Graph |

Port 5000 được sử dụng trong môi trường phát triển và kiểm thử Application. Cấu hình triển khai cuối cùng cần xác định lại địa chỉ truy cập Portal và phương thức bảo vệ kết nối.

Các cổng quản trị và monitoring không được mở rộng ra Internet nếu không cần thiết.

### 5.4. Network Security

- Sử dụng SSH Key để quản trị Linux Server.
- Giới hạn nguồn truy cập SSH và Node Exporter trên Azure bằng NSG.
- Giới hạn WinRM trong mạng quản trị được phép.
- Sử dụng Ansible Vault để bảo vệ credential Windows.
- Không lưu credential thực tế trong mã nguồn.
- Kiểm soát truy cập từ xa thông qua Tailscale.

WinRM port 5985 được sử dụng trong môi trường Lab. Thiết kế này không đồng nghĩa với việc WinRM HTTP phù hợp để mở trực tiếp ra Internet.

### 5.5. Sơ đồ mạng

Sơ đồ Network Topology được quản lý tại:

`diagrams/network-topology.md`

## 6. Technology Stack

| Nhóm | Công nghệ | Mục đích sử dụng |
|---|---|---|
| Virtualization | VMware | Triển khai Local Lab |
| Linux | Ubuntu Server | Chạy Monitoring, Automation và Web Service |
| Windows | Windows Server 2022 | Kiểm thử quản trị và giám sát Windows |
| Cloud | Microsoft Azure | Triển khai Cloud VM |
| Remote Access | Tailscale | Kết nối Application với Local Lab |
| Monitoring | Prometheus | Thu thập và truy vấn metrics |
| Visualization | Grafana | Hiển thị biểu đồ Monitoring |
| Alerting | Alertmanager | Điều phối cảnh báo |
| Exporter | Node Exporter | Thu thập metrics Linux |
| Exporter | Windows Exporter | Thu thập metrics Windows |
| Automation | Ansible | Thực thi remediation |
| Credential Management | Ansible Vault | Bảo vệ credential Ansible |
| Backend | Python, Flask | Xử lý Application Logic |
| Database | SQLite | Lưu dữ liệu nghiệp vụ |
| ORM | SQLAlchemy | Quản lý truy cập dữ liệu |
| Frontend | HTML, CSS, JavaScript, Jinja2 | Giao diện Operations Portal |
| Container | Docker | Chạy workload và hỗ trợ đóng gói Application |
| Identity | Microsoft Entra ID | SSO và App Roles |
| Notification | Microsoft Graph | Gửi Email |
| Version Control | Git, GitHub | Quản lý mã nguồn và tài liệu |
| Testing | Pytest, Integration Testing | Kiểm thử chức năng và workflow |

## 7. Application Architecture

### 7.1. Mô hình Application

Operations Portal sử dụng kiến trúc Modular Monolith dựa trên Flask.

Các chức năng được phân chia thành module theo nghiệp vụ nhưng cùng hoạt động trong một Application.

| Thành phần | Trách nhiệm |
|---|---|
| Presentation | Hiển thị giao diện và tiếp nhận thao tác người dùng. |
| Controller / Blueprint | Xử lý HTTP request và điều hướng chức năng. |
| Service Layer | Xử lý business logic, monitoring, remediation và approval. |
| Integration Adapter | Giao tiếp với Prometheus, Ansible, Entra ID và Microsoft Graph. |
| Data Access Layer | Truy vấn và cập nhật dữ liệu thông qua ORM. |
| Database | Lưu dữ liệu nghiệp vụ và lịch sử xử lý. |

### 7.2. Các module chức năng

| Module | Trách nhiệm | SRS Reference |
|---|---|---|
| Authentication | Đăng nhập, đăng xuất và xác định identity. | FR-AUTH |
| Dashboard | Hiển thị metrics và trạng thái hệ thống. | FR-MON |
| Server Inventory | Quản lý thông tin target server. | FR-INV |
| Alerts | Tiếp nhận, hiển thị và quản lý cảnh báo. | FR-ALT |
| Automation | Điều phối Manual và Auto-remediation. | FR-MAN, FR-AUTO |
| Automation Jobs | Quản lý trạng thái và lịch sử thực thi. | FR-JOB |
| Approval | Quản lý yêu cầu phê duyệt. | FR-APR |
| Incidents | Quản lý vòng đời sự cố. | FR-INC |
| Notification | Điều phối gửi Email. | FR-NOT |
| Audit | Ghi nhận và hiển thị lịch sử thao tác. | FR-AUD |

### 7.3. Cấu trúc logic của Application

    Operations Portal
    ├── Presentation / Templates
    ├── Blueprints / Controllers
    ├── Services
    │   ├── Monitoring
    │   ├── Alerts
    │   ├── Remediation
    │   ├── Approval
    │   ├── Incident
    │   └── Notification
    ├── Integration Adapters
    │   ├── Prometheus
    │   ├── Ansible
    │   ├── Microsoft Entra ID
    │   └── Microsoft Graph
    ├── Database Models
    ├── Configuration
    └── Tests

Cấu trúc trên thể hiện cách phân chia trách nhiệm trong thiết kế, không phải danh sách chính xác toàn bộ thư mục và file trong mã nguồn.

## 8. Database Design

### 8.1. Database Architecture

SQLite được sử dụng để lưu trữ dữ liệu nghiệp vụ của Operations Portal.

Metrics được truy vấn trực tiếp từ Prometheus. Portal không cần sao chép toàn bộ dữ liệu time-series vào SQLite.

Database nghiệp vụ tập trung lưu:

- Thông tin người dùng và phân quyền.
- Server Inventory.
- Cảnh báo và Incident.
- Automation Job và Approval Request.
- Lịch sử Audit và thông tin Notification cần truy vết.

### 8.2. Logical Data Model

| Entity | Mục đích |
|---|---|
| User | Quản lý identity và role của người dùng. |
| Server | Lưu thông tin máy chủ và monitoring target. |
| Alert | Lưu cảnh báo nhận từ Monitoring System. |
| Automation Job | Lưu thông tin và kết quả remediation. |
| Approval Request | Quản lý yêu cầu và quyết định phê duyệt. |
| Incident | Quản lý sự cố và vòng đời xử lý. |
| Audit Log | Lưu lịch sử thao tác và sự kiện hệ thống. |

### 8.3. Logical Data Dictionary

| Entity | Các thuộc tính nghiệp vụ chính |
|---|---|
| User | ID, Identity, Email, Role |
| Server | ID, Hostname, Address, OS, Environment, Monitoring Target |
| Alert | ID, Server Reference, Fingerprint, Severity, Status, Started Time, Resolved Time |
| Automation Job | ID, Server Reference, Incident Reference, Action, Mode, Actor, Execution Status, Verification Result, Final Status, Timestamp |
| Approval Request | ID, Target Reference, Action, Risk Level, Requester, Approver, Decision, Created Time, Expiration Time, Job Reference |
| Incident | ID, Server Reference, Alert Reference, Action, Status `open`/`resolved`, Retry Count, Manual Required, Verification Failed, Blocked, Reason, Opened Time, Closed Time. Severity, Assigned User và các trạng thái ACKNOWLEDGED, IN_PROGRESS, CLOSED là thiết kế Tuần 10, chưa có column riêng. |
| Audit Log | ID, Actor, Role, Action, Target, Result, Timestamp |

Tên thuộc tính trong bảng là tên mô tả nghiệp vụ. Tên column, kiểu dữ liệu và constraint vật lý cần được đối chiếu với SQLAlchemy Models và Database Migration.

### 8.4. Quan hệ dữ liệu

| Entity A | Entity B | Quan hệ thiết kế | Ý nghĩa |
|---|---|---|---|
| Server | Alert | 1:N | Một máy chủ có thể phát sinh nhiều cảnh báo. |
| Server | Automation Job | 1:N | Một máy chủ có thể có nhiều remediation job. |
| Server | Incident | 1:N | Một máy chủ có thể phát sinh nhiều sự cố. |
| Alert | Incident | Liên kết nghiệp vụ | Incident được tạo hoặc liên kết từ cảnh báo phù hợp. |
| Incident | Automation Job | 1:N | Một sự cố có thể có nhiều lần remediation. |
| Approval Request | Automation Job | 1:0..1 | Request chưa được duyệt không có execution job; request được duyệt có thể tạo một job. |
| User | Approval Request | 1:N | Người dùng có thể tạo nhiều yêu cầu theo quyền. |
| User | Audit Log | Liên kết nghiệp vụ | Ghi nhận các thao tác do người dùng thực hiện. |

Audit Log cũng hỗ trợ actor SYSTEM đối với các thao tác tự động.

Quan hệ dữ liệu trên là thiết kế logic. Cardinality, Foreign Key và các trường nullable sẽ được xác nhận lại từ database schema thực tế trước khi hoàn thiện ERD.

### 8.5. Database ERD

Sơ đồ Entity Relationship Diagram được quản lý tại:

`diagrams/database-erd.md`

## 9. Monitoring & Alerting Design

### 9.1. Monitoring Architecture

Prometheus được triển khai trên MON01 và thu thập metrics theo mô hình pull.

| Target | Exporter | Endpoint |
|---|---|---|
| MON01 | Node Exporter | 192.168.10.10:9100 |
| WEB01 | Node Exporter | 192.168.10.11:9100 |
| APP01 | Node Exporter | 192.168.10.12:9100 |
| WIN01 | Windows Exporter | 192.168.10.13:9182 |
| AZURE01 | Node Exporter | Azure Public IP:9100 |

Grafana sử dụng Prometheus làm Data Source để hiển thị dữ liệu giám sát.

Operations Portal truy vấn Prometheus API để lấy metrics và trạng thái target.

### 9.2. Monitoring Metrics

| Nhóm | Dữ liệu giám sát |
|---|---|
| CPU | CPU Utilization |
| Memory | Memory Utilization |
| Disk | Disk Utilization |
| Network | Network Traffic |
| Availability | Exporter Availability, Target Status |
| System | System Uptime |
| Service | HTTP/TCP Endpoint và trạng thái dịch vụ được cấu hình |

Exporter Availability không đồng nghĩa với toàn bộ máy chủ hoặc dịch vụ đang hoạt động bình thường. Portal cần kết hợp metrics và service probe để xác định trạng thái phù hợp.

### 9.3. Server Health Status

| Trạng thái | Điều kiện thiết kế |
|---|---|
| HEALTHY | Có dữ liệu giám sát hợp lệ và các dịch vụ được kiểm tra đang hoạt động. |
| DEGRADED | Máy chủ vẫn có thể truy cập nhưng một hoặc nhiều dịch vụ gặp lỗi. |
| UNREACHABLE | Không xác nhận được khả năng truy cập hoặc trạng thái máy chủ theo logic kiểm tra. |
| N/A | Không có dữ liệu hợp lệ cho metric tương ứng. |

Khi Prometheus không khả dụng, Portal phải thông báo Monitoring Backend Down và không được hiển thị dữ liệu giả.

Trạng thái UNREACHABLE trong trường hợp này không phải bằng chứng khẳng định máy chủ vật lý đã tắt.

### 9.4. Alert Processing

1. Prometheus đánh giá các alert rule.
2. Alert được gửi đến Alertmanager khi đáp ứng điều kiện.
3. Alertmanager gửi webhook đến Portal.
4. Portal xác định target dựa trên thông tin instance.
5. Alert được lưu hoặc cập nhật dựa trên fingerprint.
6. Hệ thống xác định severity và remediation action nếu có.
7. Incident và Automation Workflow được xử lý theo policy.

### 9.5. Alert Lifecycle

| Trạng thái | Ý nghĩa |
|---|---|
| Firing | Điều kiện cảnh báo đang xảy ra. |
| Resolved | Điều kiện cảnh báo không còn được đáp ứng. |

Alert Lifecycle và Incident Lifecycle được quản lý riêng.

Một Alert chuyển sang Resolved không nhất thiết đồng nghĩa Incident đã được người vận hành xác nhận và đóng.

## 10. Automation & Remediation Design

### 10.1. Automation Architecture

Ansible Control Node được triển khai trên MON01.

Operations Portal chịu trách nhiệm điều phối remediation và chỉ được gọi các action nằm trong allow-list.

Ansible chịu trách nhiệm kết nối target server và thực thi playbook tương ứng.

### 10.2. Management Channel

| Target | Phương thức kết nối |
|---|---|
| WEB01 | SSH |
| APP01 | SSH |
| WIN01 | WinRM |
| AZURE01 | SSH với key riêng |

Credential được quản lý tại môi trường thực thi Ansible, không truyền private key hoặc password qua giao diện Portal.

### 10.3. Action Risk Matrix

| Target | Action | Risk | Execution Policy | Verification |
|---|---|---|---|---|
| WEB01 | Restart Nginx | LOW | Auto / Manual | HTTP 80 |
| APP01 | Restart Container | LOW | Auto / Manual | Container Running, HTTP 8080 |
| WIN01 | Restart Windows Exporter | LOW | Auto / Manual | Metrics Endpoint 9182 |
| AZURE01 | Restart Nginx | LOW | Auto / Manual | HTTP 80 |
| APP01 | Restart Docker Service | MEDIUM | Admin Approval | Docker Service, Container, HTTP 8080 |
| AZURE01 | Reboot Server | HIGH | Admin Approval | SSH 22 và Nginx HTTP. Playbook trên MON01 còn kiểm tra Nginx, Node Exporter, cổng 80 và 9100. Boot ID không nằm trong verification hiện tại. |

Action LOW chỉ được tự động thực thi khi đáp ứng Auto-remediation Policy.

### 10.4. Remediation Workflow

1. Tiếp nhận yêu cầu từ người dùng hoặc cảnh báo.
2. Xác định target và action.
3. Kiểm tra allow-list và Risk Level.
4. Kiểm tra quyền hoặc Approval nếu cần.
5. Kiểm tra Duplicate Job và Cooldown theo policy.
6. Kiểm tra management channel.
7. Thực thi Ansible playbook.
8. Kiểm tra execution result.
9. Thực hiện verification.
10. Cập nhật kết quả Job và Incident.
11. Ghi nhận Audit Log và gửi Notification.

### 10.5. Remediation Result

| Kết quả | Điều kiện | Cách xử lý |
|---|---|---|
| SUCCESS | Execution và Verification thành công. | Ghi nhận phục hồi, áp dụng cooldown nếu phù hợp. |
| EXECUTION_FAILED | Playbook thực thi thất bại. | Auto-remediation có thể retry theo policy. |
| VERIFICATION_FAILED | Playbook thực thi nhưng dịch vụ chưa đạt trạng thái mong muốn. | Không tự retry, yêu cầu kiểm tra thủ công. |
| MANAGEMENT_BLOCKED | SSH hoặc WinRM không khả dụng. | Không gọi playbook. |
| DUPLICATE_SKIPPED | Đã có job cùng target và action đang hoạt động. | Không thực thi thêm playbook. |
| MANUAL_REQUIRED | Hệ thống không thể tiếp tục tự xử lý theo policy. | Chuyển cho người vận hành. |

Các kết quả trên thể hiện trạng thái nghiệp vụ. Execution Status, Verification Status và Final Status cần được phân biệt trong thiết kế dữ liệu.

### 10.6. Retry Policy

- Chỉ áp dụng auto-retry cho trường hợp Execution Failed đủ điều kiện.
- Retry tối đa một lần cho mỗi Incident.
- Không tự retry Manual Job.
- Không tự retry Verification Failed.
- Management Blocked không tiêu hao lượt retry do playbook chưa thực thi.
- Khi hết lượt retry mà sự cố vẫn chưa được xử lý, chuyển sang Manual Required.
- Incident mới có retry counter riêng.

### 10.7. Cooldown Policy

Sau khi Auto-remediation thành công, hệ thống áp dụng thời gian cooldown 120 giây đối với cùng target và action.

Trong thời gian này, yêu cầu tự động thực thi lại cùng action không được phép tạo thêm execution.

### 10.8. Duplicate Handling

Hệ thống kiểm tra các job đang ở trạng thái Queued hoặc Running.

Nếu đã tồn tại job cùng target và action, yêu cầu trùng được ghi nhận DUPLICATE_SKIPPED và không thực thi playbook.

Cơ chế kiểm tra và tạo job cần đảm bảo không phát sinh race condition khi nhiều yêu cầu đến đồng thời.

### 10.9. Verification Design

| Action | Verification |
|---|---|
| Restart Nginx | Kiểm tra HTTP endpoint phản hồi hợp lệ. |
| Restart Container | Kiểm tra container Running và HTTP endpoint. |
| Restart Windows Exporter | Kiểm tra Windows Exporter metrics endpoint. |
| Restart Docker Service | Kiểm tra Docker Service, container và HTTP endpoint. |
| Reboot Server | Portal chỉ kết luận thành công khi SSH cổng 22 và Nginx đều phản hồi. Playbook `reboot-azure01.yml` chờ máy khởi động lại rồi kiểm tra Nginx, Node Exporter, cổng 80 và 9100. |

Exit Code 0 của Ansible không đủ để kết luận remediation thành công nếu chưa có kết quả verification phù hợp.

### 10.10. Sequence Diagram

Sơ đồ Remediation Sequence được quản lý tại:

`diagrams/remediation-sequence.md`

## 11. Approval Workflow Design

### 11.1. Risk-based Execution

| Risk Level | Admin | Operator | Viewer | Auto-remediation |
|---|---|---|---|---|
| LOW | Thực thi | Thực thi | Không | Có điều kiện |
| MEDIUM | Yêu cầu và phê duyệt | Yêu cầu | Không | Không |
| HIGH | Yêu cầu và phê duyệt | Không | Không | Không |

Các action MEDIUM và HIGH phải được phê duyệt trước khi tạo execution job.

### 11.2. Approval Status

| Trạng thái | Ý nghĩa |
|---|---|
| PENDING_APPROVAL | Yêu cầu đang chờ phê duyệt. Chưa có Automation Job. |
| APPROVED | Admin đã chấp thuận. Portal mới được tạo job và gọi Ansible. |
| REJECTED | Admin từ chối. Không gọi playbook. |
| APPROVAL_EXPIRED | Quá `APPROVAL_TIMEOUT_MINUTES`, hiện là 5 phút. Không tự duyệt và không gọi playbook. |

### 11.3. Approval Processing

1. Người dùng yêu cầu action MEDIUM hoặc HIGH.
2. Portal kiểm tra quyền của requester.
3. Nếu hợp lệ, tạo Approval Request ở trạng thái PENDING.
4. Gửi thông báo đến Admin.
5. Admin xem thông tin target, action và Risk Level.
6. Admin thực hiện approve hoặc reject.
7. Nếu Approved, chuyển yêu cầu sang Remediation Workflow.
8. Nếu Rejected hoặc Expired, không gọi Ansible.
9. Lưu lịch sử quyết định và Audit Log.

### 11.4. Approval Constraints

- Chỉ Admin được approve hoặc reject.
- Request Pending có thời hạn 5 phút.
- Request hết hạn không được phê duyệt để thực thi.
- Approval hợp lệ không được sử dụng để bỏ qua Pre-check hoặc Verification.
- Request bị từ chối hoặc hết hạn không được tạo execution job.
- Quyết định approval và kết quả remediation được quản lý riêng.

Thiết kế hiện tại cho phép Admin yêu cầu và phê duyệt action theo quyền. Chưa áp dụng bắt buộc cơ chế phê duyệt bởi một Admin độc lập với requester.

### 11.5. Approval Activity Diagram

Sơ đồ Approval Workflow được quản lý tại:

`diagrams/approval-workflow.md`

## 12. Incident Management Design

### 12.1. Mục tiêu

Incident Management được thiết kế để quản lý sự cố từ thời điểm phát hiện đến khi được xử lý và đóng.

Module liên kết dữ liệu Monitoring, Alert, Automation Job và Audit Trail thành một luồng xử lý thống nhất.

### 12.2. Incident Lifecycle

| Trạng thái | Ý nghĩa |
|---|---|
| OPEN | Sự cố được ghi nhận và chưa tiếp nhận xử lý. |
| ACKNOWLEDGED | Sự cố đã được người vận hành tiếp nhận. |
| IN_PROGRESS | Sự cố đang được xử lý. |
| RESOLVED | Dịch vụ đã được xác nhận phục hồi. |
| CLOSED | Sự cố đã được rà soát và kết thúc. |

### 12.3. State Transition Design

| Trạng thái hiện tại | Sự kiện | Trạng thái tiếp theo |
|---|---|---|
| OPEN | Người vận hành tiếp nhận | ACKNOWLEDGED |
| OPEN | Auto-remediation bắt đầu | IN_PROGRESS |
| ACKNOWLEDGED | Bắt đầu xử lý | IN_PROGRESS |
| IN_PROGRESS | Verification thành công | RESOLVED |
| IN_PROGRESS | Execution hoặc Verification thất bại | IN_PROGRESS |
| IN_PROGRESS | Cần người vận hành can thiệp | IN_PROGRESS, ghi nhận Manual Required |
| RESOLVED | Người có quyền xác nhận đóng | CLOSED |

Manual Required là kết quả hoặc điều kiện xử lý, không bắt buộc phải trở thành một trạng thái riêng trong Incident Lifecycle.

Các trường hợp phục hồi ngoài luồng remediation cần có bằng chứng xác nhận dịch vụ đã hoạt động trước khi chuyển Incident sang RESOLVED.

### 12.4. Incident Correlation

Incident được liên kết với:

- Target Server.
- Alert hoặc nguồn phát hiện sự cố.
- Remediation Action.
- Automation Job History.
- Approval Request nếu có.
- Audit Trail.

Một Incident có thể liên kết với nhiều Automation Job, bao gồm lần thực thi ban đầu, retry và manual remediation.

### 12.5. Recurring Incident

Khi dịch vụ đã phục hồi nhưng sự cố phát sinh lại, hệ thống phải ghi nhận lần phát sinh mới và giữ nguyên lịch sử xử lý trước đó.

Các quy tắc correlation cần phân biệt cảnh báo gửi lặp trong cùng sự cố với sự cố mới sau khi dịch vụ đã phục hồi.

### 12.6. Incident State Diagram

Sơ đồ Incident Lifecycle được quản lý tại:

`diagrams/incident-state-diagram.md`

Phần Incident Management trong tài liệu này là thiết kế mục tiêu của Tuần 10, cần đối chiếu lại sau khi Application và Infrastructure hoàn thành kiểm thử tích hợp.

## 13. Security & Identity Design

### 13.1. Microsoft Entra ID Integration

Operations Portal tích hợp Microsoft Entra ID để hỗ trợ Single Sign-On.

| Thành phần | Thiết kế |
|---|---|
| App Registration | KLTN-Operations-Portal |
| Tenant Type | Single Tenant |
| Authentication | OpenID Connect / OAuth 2.0 |
| App Roles | Admin, Operator, Viewer |
| Development Redirect URI | http://localhost:5000/auth/callback |
| Role Mapping | Dựa trên App Role được cấp cho người dùng |

### 13.2. Authentication Flow

1. Người dùng truy cập Operations Portal.
2. Portal chuyển người dùng đến Microsoft Entra ID.
3. Người dùng thực hiện xác thực.
4. Entra ID trả về authorization response.
5. Portal xử lý callback và xác minh thông tin xác thực.
6. Portal xác định role của người dùng.
7. Tạo phiên đăng nhập và cho phép truy cập theo quyền.

Nếu người dùng không có App Role phù hợp, hệ thống không được cấp quyền Admin hoặc Operator.

### 13.3. RBAC Matrix

| Chức năng | Admin | Operator | Viewer |
|---|---|---|---|
| Xem Dashboard | Có | Có | Có |
| Xem Server Inventory | Có | Có | Có |
| Quản lý Inventory | Có | Không | Không |
| Xem Alert | Có | Có | Có |
| Acknowledge Alert | Có | Có | Không |
| Manual Remediation LOW | Có | Có | Không |
| Request MEDIUM | Có | Có | Không |
| Request HIGH | Có | Không | Không |
| Approve / Reject | Có | Không | Không |
| Xem Automation Jobs | Có | Có | Có |
| Xem Incident | Có | Có | Có |
| Xử lý Incident | Có | Có | Không |

Quyền xem Audit Log, Approval History và các thao tác Incident chi tiết cần được đối chiếu với chính sách RBAC thực tế của Application.

### 13.4. Backend Authorization

Việc ẩn hoặc vô hiệu hóa button trên giao diện không được xem là cơ chế bảo mật đầy đủ.

Backend phải kiểm tra quyền trước khi:

- Tạo remediation job.
- Tạo approval request.
- Approve hoặc reject request.
- Thay đổi Inventory.
- Thay đổi trạng thái Incident.
- Thực hiện các thao tác quản trị khác.

Request đã xác thực nhưng không đủ quyền phải bị từ chối, không tạo execution job và không gọi Ansible.

### 13.5. Credential Management

| Credential | Phương thức quản lý |
|---|---|
| Linux SSH Private Key | Lưu trên môi trường thực thi Ansible với quyền truy cập giới hạn. |
| Windows WinRM Credential | Ansible Vault |
| Entra ID Client Secret | Environment Variable hoặc cấu hình riêng ngoài Git. |
| Microsoft Graph Credential | Environment Variable hoặc cấu hình riêng ngoài Git. |
| Application Secret | Cấu hình riêng của môi trường triển khai. |

File chứa credential thực tế không được commit lên GitHub hoặc đóng gói vào Docker Image.

### 13.6. Integration Security

Webhook từ Alertmanager cần được giới hạn nguồn truy cập và kiểm tra dữ liệu đầu vào.

Các integration endpoint phải có cơ chế xử lý timeout, dữ liệu không hợp lệ và lỗi kết nối.

Cơ chế bảo vệ webhook, session và cấu hình HTTPS của môi trường bàn giao cần được kiểm tra trước khi nghiệm thu.

## 14. Notification Design

### 14.1. Notification Architecture

Operations Portal sử dụng Microsoft Graph API để gửi Email Notification.

Microsoft Graph được cấu hình với Application Permission Mail.Send và Admin Consent phù hợp.

Application xác định sự kiện, severity, nhóm người nhận và nội dung Email trước khi gửi yêu cầu.

### 14.2. Severity Routing

| Severity | Distribution Group | Sự kiện |
|---|---|---|
| Critical | KLTN-Alert-Critical | Service Down, Execution Failed, Verification Failed, Manual Required |
| Warning | KLTN-Alert-Warning | Remediation Started, Retry, Management Blocked |
| Info | KLTN-Alert-Info | Remediation Success, Service Resolved |

Các thông báo liên quan đến Approval được điều phối đến Admin hoặc người nhận phù hợp với loại sự kiện.

### 14.3. Notification Content

Email cần chứa các thông tin phù hợp với sự kiện:

- Target Server.
- Service.
- Event.
- Event Time.
- Severity.
- Remediation Action.
- Final Status.
- Reason.
- Approval Decision nếu có.

### 14.4. Notification Failure Handling

Nếu Microsoft Graph không khả dụng hoặc gửi Email thất bại, Application phải ghi nhận lỗi nhưng không làm gián đoạn remediation đang thực thi.

HTTP 202 từ Microsoft Graph chỉ xác nhận yêu cầu gửi Email đã được tiếp nhận. Kết quả nhận Email thực tế cần được kiểm tra tại mailbox hoặc Distribution Group trong quá trình đánh giá metric.

## 15. Audit Trail Design

### 15.1. Audit Data

| Trường | Nội dung |
|---|---|
| Actor | Người dùng hoặc SYSTEM |
| Role | Vai trò tại thời điểm thực hiện nếu áp dụng |
| Mode | AUTO hoặc MANUAL nếu áp dụng |
| Action | Thao tác được thực hiện |
| Target | Đối tượng bị tác động |
| Timestamp | Thời điểm xảy ra sự kiện |
| Result | Kết quả xử lý |
| Reference | Job, Approval hoặc Incident liên quan nếu có |

### 15.2. Audit Events

| Nhóm | Sự kiện cần ghi nhận |
|---|---|
| Authentication | Đăng nhập, đăng xuất và các sự kiện xác thực thuộc phạm vi audit. |
| Inventory | Thêm, sửa hoặc xóa thông tin máy chủ. |
| Remediation | Requested, Started, Blocked, Failed, Verified, Success. |
| Retry | Retry Scheduled, Retry Executed, Manual Required. |
| Duplicate | Duplicate Skipped. |
| Approval | Requested, Approved, Rejected, Expired. |
| Incident | Created, Acknowledged, In Progress, Resolved, Closed. |
| Security | Permission Denied đối với thao tác cần kiểm soát. |

Tên event trong bảng là nhóm sự kiện nghiệp vụ cần ghi nhận. Event key chính xác được xác định theo implementation của Application.

### 15.3. Audit Integrity

Audit Log được thiết kế theo hướng append-only tại Application Layer.

Người dùng vận hành thông thường không được cung cấp chức năng sửa hoặc xóa lịch sử Audit.

Thiết kế này không đồng nghĩa với cơ chế lưu trữ bất biến ở cấp Database hoặc chống sửa đổi bởi người có quyền truy cập trực tiếp vào hệ điều hành.

## 16. API & Integration Design

### 16.1. Integration Interfaces

| Source | Destination | Interface | Mục đích |
|---|---|---|---|
| Browser | Operations Portal | HTTP/HTTPS | Truy cập Application |
| Portal | Prometheus | HTTP API | Truy vấn metrics |
| Grafana | Prometheus | HTTP API | Hiển thị biểu đồ |
| Prometheus | Alertmanager | HTTP | Gửi cảnh báo |
| Alertmanager | Portal | HTTP Webhook | Chuyển cảnh báo |
| Portal | Ansible Control Node | Execution Adapter | Điều phối playbook |
| Ansible | Linux Server | SSH | Thực thi action |
| Ansible | Windows Server | WinRM | Thực thi action |
| Portal | Entra ID | OIDC / OAuth 2.0 | Xác thực |
| Portal | Microsoft Graph | REST API | Gửi Email |

### 16.2. External API Endpoints

| Service | Method | Endpoint | Mục đích |
|---|---|---|---|
| Prometheus | GET | /api/v1/query | Truy vấn metrics tại một thời điểm. |
| Prometheus | GET | /api/v1/query_range | Truy vấn metrics theo khoảng thời gian. |
| Prometheus | GET | /api/v1/alerts | Lấy danh sách cảnh báo. |
| Prometheus | GET | /-/healthy | Kiểm tra trạng thái Prometheus. |
| Operations Portal | POST | /api/alerts/webhook | Nhận cảnh báo từ Alertmanager. |
| Microsoft Graph | POST | /v1.0/users/{mailbox}/sendMail | Gửi Email bằng mailbox được cấu hình. |
| Operations Portal | GET | /auth/callback | Xử lý callback xác thực. |

Các API nội bộ phục vụ Inventory, Automation, Approval và Incident cần được bổ sung từ route definition thực tế của Flask Application.

### 16.3. Error Handling

| Trường hợp | Cách xử lý |
|---|---|
| Prometheus Timeout | Hiển thị N/A và trạng thái Monitoring Backend không khả dụng. |
| Invalid Monitoring Response | Không sử dụng dữ liệu không hợp lệ để hiển thị trạng thái Healthy. |
| Invalid Webhook Payload | Từ chối hoặc ghi nhận lỗi dữ liệu đầu vào. |
| Management Connection Failed | Không thực thi playbook. |
| Ansible Execution Failed | Ghi nhận lỗi và xử lý retry theo policy. |
| Unauthorized Request | Từ chối thao tác. |
| Microsoft Graph Failure | Ghi nhận lỗi Notification, không làm gián đoạn remediation. |
| Database Error | Không ghi nhận thành công nếu thao tác lưu dữ liệu thất bại. |

## 17. Deployment Design

### 17.1. Deployment Components

| Môi trường | Thành phần |
|---|---|
| Application Host | Flask Operations Portal, SQLite, Application Configuration |
| MGMT01 | Tailscale Subnet Router |
| MON01 | Prometheus, Grafana, Alertmanager, Ansible |
| Local Target Servers | WEB01, APP01, WIN01 |
| Microsoft Azure | AZURE01, VNet, NSG, Public IP |
| Microsoft Cloud Services | Entra ID, Microsoft Graph |

Trong quá trình phát triển, Application được chạy trên laptop của thành viên phụ trách Application và kết nối Local Lab thông qua Tailscale.

Vị trí triển khai Portal trong môi trường bàn giao cuối cùng cần được xác nhận trước khi hoàn thiện Deployment Diagram.

### 17.2. Configuration Management

Các nhóm cấu hình cần được quản lý riêng:

| Nhóm cấu hình | Nội dung |
|---|---|
| Monitoring Configuration | Prometheus scrape config, alert rule và Alertmanager routing. |
| Automation Configuration | Ansible Inventory, Playbook, Action Mapping và Vault. |
| Application Configuration | Database, Integration URL, Timeout và Application Secret. |
| Identity Configuration | Tenant ID, Client ID, Client Secret và Redirect URI. |
| Notification Configuration | Mailbox, Recipient Group và Severity Mapping. |
| Network Configuration | IP Address, Port, NSG và Tailscale Route. |

Mã nguồn và cấu hình mẫu được lưu trên GitHub. Credential thực tế được quản lý bên ngoài repository.

### 17.3. Deployment Diagram

Sơ đồ Deployment được quản lý tại:

`diagrams/deployment-diagram.md`

## 18. Non-functional Design

| Yêu cầu | Giải pháp thiết kế | Metric |
|---|---|---|
| Giảm thời gian phát hiện sự cố | Prometheus scrape, alert rule và Alertmanager webhook. | M02, M03 |
| Giảm thời gian khôi phục | Controlled Auto-remediation bằng Ansible. | M06, M07, M08 |
| Đảm bảo khả năng thu thập metrics | Monitoring target và exporter được cấu hình riêng. | M01, M05 |
| Ngăn kết quả thành công sai | Verification độc lập với Ansible Exit Code. | M10, M23 |
| Kiểm soát management channel | SSH/WinRM Pre-check. | M11 |
| Hạn chế automation lặp | Retry, Cooldown và Duplicate Handling. | M12, M13, M14 |
| Kiểm soát quyền | Entra ID App Roles và Backend Authorization. | M15, M16, M18 |
| Kiểm soát action rủi ro | Approval Workflow. | M17, M19 |
| Bảo vệ credential | SSH Key, Ansible Vault và Environment Variable. | M20 |
| Quản lý vòng đời sự cố | Incident Lifecycle và Incident-Job Mapping. | M21, M22 |
| Đảm bảo truy vết | Audit Trail và Execution History. | M24 |
| Thông báo vận hành | Microsoft Graph và Severity Routing. | M25, M26 |
| Chuẩn hóa vận hành | Runbook và Deployment Documentation. | M30, M31 |

Các giải pháp trên được lựa chọn để đáp ứng yêu cầu phi chức năng trong SRS. Mức độ đáp ứng thực tế phải được xác nhận thông qua kiểm thử và số liệu đo lường.

## 19. Design Decisions & Trade-offs

| Quyết định thiết kế | Lý do lựa chọn | Hạn chế |
|---|---|---|
| Modular Monolith thay vì Microservices | Phù hợp với quy mô đề tài và nhóm hai thành viên. | Khả năng mở rộng độc lập từng module còn hạn chế. |
| SQLite thay vì Database Server riêng | Dễ triển khai và quản lý trong môi trường Lab. | Hạn chế khi có nhiều thao tác ghi đồng thời. |
| Prometheus thay vì tự xây dựng Monitoring Engine | Có sẵn hệ thống thu thập metrics và alert rule. | Phụ thuộc vào exporter và cấu hình Monitoring. |
| Ansible thay vì thực thi command trực tiếp từ Portal | Chuẩn hóa automation bằng Inventory và Playbook. | Phụ thuộc vào management channel và quyền trên target. |
| MGMT01 tách khỏi MON01 | Phân tách Remote Access và Monitoring Failure Domain. | Phát sinh thêm một máy chủ cần quản lý. |
| Tailscale cho Remote Access | Hỗ trợ kết nối giữa Application Laptop và Local Lab. | Phụ thuộc vào kết nối và dịch vụ Tailscale. |
| Azure VM cho Hybrid Cloud | Kiểm chứng khả năng tích hợp Local và Cloud. | Chưa đánh giá các mô hình Cloud quy mô lớn. |
| Entra ID cho Authentication | Tận dụng dịch vụ xác thực và App Roles. | Phụ thuộc vào Microsoft Identity Service. |
| Risk-based Approval | Hạn chế thao tác có ảnh hưởng lớn được thực thi tự động. | Tăng thời gian xử lý đối với action cần phê duyệt. |
| Verification-based Recovery | Đánh giá dựa trên trạng thái thực tế của dịch vụ. | Phải xây dựng verification riêng cho từng action. |

## 20. Design Limitations

Hệ thống được thiết kế và đánh giá trong phạm vi Hybrid Cloud Lab.

Các giới hạn hiện tại:

- MON01 là điểm tập trung của Monitoring và Automation, chưa có High Availability.
- Application và SQLite chưa được thiết kế cho tải lớn hoặc nhiều người dùng đồng thời.
- Auto-remediation chỉ hỗ trợ các action được định nghĩa trước.
- Hệ thống không tự động phân tích nguyên nhân gốc của mọi sự cố.
- Việc xử lý phụ thuộc vào SSH, WinRM và khả năng kết nối đến target.
- SSO và Email Notification phụ thuộc vào dịch vụ Microsoft.
- Kết nối đến Azure sử dụng Public IP với NSG, chưa triển khai private hybrid connectivity chuyên dụng.
- Chưa đánh giá khả năng vận hành liên tục theo SLA doanh nghiệp.
- Các thiết kế Incident Management và một số cơ chế bảo mật cần được kiểm thử trước khi nghiệm thu.

## 21. Danh sách sơ đồ thiết kế

| ID | Sơ đồ | File |
|---|---|---|
| DG-01 | System Architecture Diagram | diagrams/system-architecture.md |
| DG-02 | Network Topology Diagram | diagrams/network-topology.md |
| DG-03 | Use Case Diagram | diagrams/use-case-diagram.md |
| DG-04 | Database ERD | diagrams/database-erd.md |
| DG-05 | Remediation Sequence Diagram | diagrams/remediation-sequence.md |
| DG-06 | Approval Activity Diagram | diagrams/approval-workflow.md |
| DG-07 | Incident State Diagram | diagrams/incident-state-diagram.md |
| DG-08 | Deployment Diagram | diagrams/deployment-diagram.md |

Các sơ đồ được quản lý riêng để thuận tiện cập nhật và đối chiếu với mã nguồn.

## 22. Requirements Traceability

Các nhóm thiết kế trong SDD được liên kết với yêu cầu tương ứng trong SRS.

| Requirement Group | Design Reference | Diagram |
|---|---|---|
| FR-AUTH | Security & Identity Design | DG-03 |
| FR-INV | Application Architecture, Database Design | DG-03, DG-04 |
| FR-MON | Monitoring & Alerting Design | DG-01, DG-02 |
| FR-ALT | Monitoring & Alerting Design | DG-01, DG-05 |
| FR-MAN | Automation & Remediation Design | DG-05 |
| FR-AUTO | Automation & Remediation Design | DG-05 |
| FR-JOB | Automation Design, Database Design | DG-04, DG-05 |
| FR-APR | Approval Workflow Design | DG-06 |
| FR-INC | Incident Management Design | DG-04, DG-07 |
| FR-NOT | Notification Design | DG-01, DG-05 |
| FR-AUD | Audit Trail Design | DG-04, DG-05 |
| NFR | Non-functional Design | Các sơ đồ liên quan |

Ma trận truy vết chi tiết nằm tại [requirements-traceability-matrix.md](requirements-traceability-matrix.md).

## 23. Tài liệu tham chiếu

- [Software Requirements Specification](SRS.md)
- [Bản cam kết sản phẩm và bộ metric đánh giá](../project-management/product-commitment-and-metrics.md)
- [Bảng phân công công việc](../project-management/work-assignment.md)
- [Báo cáo tiến độ theo tuần](../project-management/weekly-progress/)
- [Infrastructure Repository](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/infra/infrastructure)
- [Application Repository](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/application/application)

## 24. Lịch sử cập nhật

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 26/11/2026 | Xây dựng tài liệu thiết kế tổng thể dựa trên SRS, kiến trúc hệ thống và kết quả triển khai đến Tuần 9. |
| 1.1 | 27/11/2026 | Bổ sung DG-04, DG-06, DG-07 và RTM. Đối chiếu tên trạng thái approval, schema Incident và verification reboot với models và playbook hiện hành. |
