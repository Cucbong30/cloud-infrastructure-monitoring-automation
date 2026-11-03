# Screenshots — test case tuần 3

Bằng chứng dashboard (lab 22/10/2026):

| File | Case | Kết quả trên portal |
| --- | --- | --- |
| `01-web01-nginx-down.png` | WEB01 – Nginx down | WEB01 **Degraded**, exporter UP, **Nginx :80 DOWN** |
| `02-app01-container-down.png` | APP01 – Application container down | APP01 **Degraded**, exporter UP, **App :8080 DOWN** |
| `03-mon01-grafana-down.png` | MON01 – Grafana down | MON01 **Unreachable**, probe **Grafana :3000** (event log) |
| `04-win01-down.png` | WIN01 – down | WIN01 **Unreachable**, CPU/Memory/Disk N/A |

Case 1–2: Prometheus còn sống, host còn metric, chỉ service HTTP chết. Case 3–4: backend/host không trả lời, status Unreachable.
