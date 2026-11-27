# Requirements and Design

Tài liệu đặc tả yêu cầu và thiết kế của đề tài **Xây dựng hệ thống giám sát và tự động hóa vận hành hạ tầng trong môi trường Hybrid Cloud**.

Phần Application do Nguyễn Thế Gia Bảo phụ trách. Các sơ đồ DG-04, DG-06 và DG-07 được đối chiếu với SQLAlchemy models, migrations và luồng xử lý của Operations Portal đến hết Tuần 9. Vòng đời Incident đầy đủ thuộc phạm vi đang thực hiện của Tuần 10.

## Cấu trúc

| Tài liệu | Nội dung |
|---|---|
| [SRS.md](SRS.md) | Yêu cầu chức năng, phi chức năng, use case và business rules. |
| [SDD.md](SDD.md) | Thiết kế kiến trúc, dữ liệu, automation, approval, incident, SSO, RBAC và triển khai. |
| [requirements-traceability-matrix.md](requirements-traceability-matrix.md) | Liên kết yêu cầu, thiết kế, sơ đồ và mức độ đã triển khai. |
| [diagrams/system-architecture.md](diagrams/system-architecture.md) | DG-01 System Architecture. |
| [diagrams/network-topology.md](diagrams/network-topology.md) | DG-02 Network Topology. |
| [diagrams/use-case-diagram.md](diagrams/use-case-diagram.md) | DG-03 Use Case và phân quyền. |
| [diagrams/database-erd.md](diagrams/database-erd.md) | DG-04 Database ERD theo schema hiện tại. |
| [diagrams/remediation-sequence.md](diagrams/remediation-sequence.md) | DG-05 Remediation Sequence. |
| [diagrams/approval-workflow.md](diagrams/approval-workflow.md) | DG-06 Approval Activity Diagram. |
| [diagrams/incident-state-diagram.md](diagrams/incident-state-diagram.md) | DG-07 Incident State Diagram. |
| [diagrams/deployment-diagram.md](diagrams/deployment-diagram.md) | DG-08 Deployment Diagram. |

## Cách đọc

1. Đọc SRS để biết hệ thống phải làm gì.
2. Đọc SDD để biết từng module được thiết kế thế nào.
3. Đọc sơ đồ tương ứng khi cần luồng, dữ liệu hoặc vị trí triển khai.
4. Dùng RTM để biết yêu cầu nào đã có trong Portal và yêu cầu nào còn là mục tiêu Tuần 10.

Các sơ đồ dùng Mermaid để xem trực tiếp trên GitHub.
