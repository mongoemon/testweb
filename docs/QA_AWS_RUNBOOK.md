# QA AWS Runbook — ShoesHub

คู่มือสำหรับ QA ในการตรวจสอบระบบผ่าน AWS: CloudWatch (logs/metrics), SQS/SNS (async flow),
S3 (ไฟล์ผลลัพธ์), Load Test bottleneck analysis และแผน Disaster Recovery / Backup

> **สถานะปัจจุบัน (2026-09-02):**
> - ✅ AWS Agent Toolkit + MCP `aws-mcp` ติดตั้งแล้ว (profile `shoeshub-qa`, account `138415545281`, region `ap-southeast-1`) — เรียก AWS ผ่าน Claude Code ได้
> - ✅ Structured JSON logging + `x-request-id` middleware อยู่ใน `backend/observability.py` แล้ว
> - ⏳ ยังไม่มี resource บน AWS ที่แอปใช้ (log group / queue) — แอปยัง deploy บน Render.com + SQLite
> เอกสารนี้ครอบคลุมทั้ง (A) วิธี "ตรวจ" เมื่อระบบอยู่บน AWS แล้ว และ (B) สิ่งที่ต้องเพิ่ม ดู [7. Setup checklist](#7-setup-checklist)

---

## สารบัญ

1. [Prerequisites — IAM + เครื่องมือ](#1-prerequisites)
2. [ตั้งค่า AWS MCP servers ใน Claude Code](#2-aws-mcp-servers)
3. [CloudWatch Logs & Debug](#3-cloudwatch-logs--debug)
4. [SQS / SNS — Asynchronous Flow](#4-sqs--sns--asynchronous-flow)
5. [S3 — ไฟล์ผลลัพธ์และเอกสาร](#5-s3--ไฟล์ผลลัพธ์และเอกสาร)
6. [Load Test — สถิติและคอขวด (CloudWatch Metrics)](#6-load-test--สถิติและคอขวด)
7. [Setup checklist — ทำให้โปรเจกต์รองรับ](#7-setup-checklist)
8. [Disaster Recovery / Backup — แผนกู้คืน](#8-disaster-recovery--backup)
9. [ภาคผนวก — IAM policy สำหรับ QA](#9-ภาคผนวก--iam-policy-สำหรับ-qa)
10. [เทสเป็นทีม — เดินดูผลลัพธ์ใน AWS ร่วมกับเพื่อน](#10-เทสเป็นทีม--เดินดูผลลัพธ์ใน-aws)
11. [ฝึกมือ — ใส่ข้อมูลตัวอย่างเข้า CloudWatch แล้วลองดู](#11-ฝึกมือ--ใส่ข้อมูลตัวอย่างเข้า-cloudwatch)

---

## 1. Prerequisites

| สิ่งที่ต้องมี | คำสั่งติดตั้ง / ตรวจสอบ |
|---|---|
| AWS CLI v2 | `aws --version` |
| `uv` (รัน MCP servers) | `pip install uv` แล้ว `uvx --version` |
| Profile QA แบบ read-only | `aws configure sso --profile shoeshub-qa` |
| ทดสอบสิทธิ์ | `aws sts get-caller-identity --profile shoeshub-qa` |

- ตั้ง env ต่อ session: `export AWS_PROFILE=shoeshub-qa AWS_REGION=ap-southeast-1`
- IAM ต้องเป็น **read-only** เท่านั้น (ดู [ส่วน 9](#9-ภาคผนวก--iam-policy-สำหรับ-qa)) — เป็นเกราะกันแก้ prod โดยไม่ตั้งใจ

---

## 2. AWS MCP servers

Repo ทางการ: <https://github.com/awslabs/mcp>

| งาน | MCP server | ใช้ทำอะไร |
|---|---|---|
| Logs / metrics / alarms | `awslabs.cloudwatch-mcp-server` | query Logs Insights, ดึง metric, ดู active alarms, วิเคราะห์ anomaly |
| SQS / SNS | `awslabs.amazon-sns-sqs-mcp-server` | อ่าน queue/topic attributes, subscription |
| S3 / service อื่น ๆ | `awslabs.aws-api-mcp-server` | คุม AWS CLI ทุก service (ตั้ง `READ_OPERATIONS_ONLY=true`) |
| ถามวิธีใช้ AWS | `awslabs.aws-knowledge-mcp-server` | เอกสาร AWS |

### เปิดใช้งาน

```bash
cp .mcp.json.example .mcp.json
# แก้ AWS_PROFILE / AWS_REGION ในไฟล์ให้ตรงกับของคุณ
# ปิด-เปิด Claude Code ใหม่ แล้วรัน /mcp เพื่อเช็คว่าเชื่อมต่อได้
```

`.mcp.json` ควรอยู่ใน `.gitignore` (เพิ่มบรรทัด `.mcp.json` ถ้ายังไม่มี)

### ทดสอบเร็ว (พิมพ์ใน Claude Code)

- `list CloudWatch log groups`
- `get active CloudWatch alarms`
- `show SQS queue attributes for shoeshub-order-events-dlq`

> **ความปลอดภัย:** `READ_OPERATIONS_ONLY=true` + IAM read-only + `amazon-sns-sqs` ไม่เปิด
> `--allow-resource-creation` โดย default → QA query ได้ แต่แก้ทรัพยากรไม่ได้

---

## 3. CloudWatch Logs & Debug

### 3.1 ดู log แบบ real-time

```bash
aws logs tail /ecs/shoeshub-prod --follow --since 15m \
  --filter-pattern '"ERROR"'
```

### 3.2 Logs Insights — หา error + latency spike

```
fields @timestamp, level, request_id, method, path, status, latency_ms, message
| filter status >= 500 or latency_ms > 1000
| sort @timestamp desc
| limit 100
```

### 3.3 นับ error จัดกลุ่มตามข้อความ

```
fields @message
| filter level = "ERROR"
| stats count(*) as hits by message
| sort hits desc
```

### 3.4 trace หนึ่ง request ข้ามทุก service

```
fields @timestamp, @log, message
| filter request_id = "REPLACE-WITH-REQUEST-ID"
| sort @timestamp asc
```

### จุดที่ QA ต้องตรวจ

- [ ] ทุก log เป็น JSON และมี `request_id` (ตรงกับ response header `x-request-id`)
- [ ] error มี stack trace ครบ ไม่ถูกตัด
- [ ] ไม่มีข้อมูลลับ (password, token, เลขบัตร) โผล่ใน log
- [ ] retention ของ log group ตั้งไว้ (ไม่ใช่ Never expire) — เช่น 30–90 วัน
- [ ] มี metric filter → alarm สำหรับ error rate

### ผ่าน MCP

- _"errors ใน /ecs/shoeshub-prod ชั่วโมงล่าสุด จัดกลุ่มตาม message"_
- _"หา log ทั้งหมดของ request_id abc-123 เรียงตามเวลา"_

---

## 4. SQS / SNS — Asynchronous Flow

### 4.1 SQS metrics ที่ต้องเฝ้า

| Metric | ความหมาย | เกณฑ์เตือน |
|---|---|---|
| `ApproximateNumberOfMessagesVisible` | ข้อความรอ consume | พุ่งค้าง = consumer ตาย/ช้า |
| `ApproximateAgeOfOldestMessage` | อายุข้อความเก่าสุด (วินาที) | ค่อย ๆ ขึ้น = ตามไม่ทัน |
| `NumberOfMessagesReceived` vs `Sent` | อัตราเข้า/ออก | ออก < เข้า นาน ๆ = backlog |
| **DLQ** `ApproximateNumberOfMessagesVisible` | ข้อความที่ fail หมด retry | **ต้องเป็น 0** |

```bash
aws sqs get-queue-attributes --queue-url "$QUEUE_URL" --attribute-names All

# ดู payload ที่ fail (เฉพาะ non-prod)
aws sqs receive-message --queue-url "$DLQ_URL" --max-number-of-messages 10 \
  --message-attribute-names All --attribute-names All
```

### 4.2 SNS

```bash
aws sns get-topic-attributes --topic-arn "$TOPIC_ARN"
aws sns list-subscriptions-by-topic --topic-arn "$TOPIC_ARN"   # PendingConfirmation ไหม?
```

- เปิด **delivery status logging** ที่ topic → ดู success/failure rate ใน CloudWatch
- Metric: `NumberOfNotificationsFailed`, `NumberOfNotificationsFilteredOut`

### สิ่งที่ QA ต้องยืนยัน (end-to-end)

- [ ] ทำ action X แล้วมีข้อความถูก **publish** จริง (นับ `NumberOfMessagesPublished`)
- [ ] ข้อความถูก **consume ครั้งเดียว** — ทดสอบ idempotency ด้วยการส่งซ้ำ
- [ ] ทุก queue มี **DLQ** + `RedrivePolicy` (`maxReceiveCount` ~5)
- [ ] DLQ ว่างหลังจบ test; ถ้าไม่ว่าง → เปิดดู payload หาสาเหตุ
- [ ] latency ตั้งแต่ publish → ประมวลผลเสร็จ อยู่ใน SLA
- [ ] มี alarm: `DLQ depth > 0` และ `AgeOfOldestMessage > threshold`

### ผ่าน MCP

- _"queue attributes ของ shoeshub-order-events และ DLQ มีข้อความค้างไหม"_
- _"subscription ทั้งหมดของ topic shoeshub-notifications ยืนยันครบหรือยัง"_

---

## 5. S3 — ไฟล์ผลลัพธ์และเอกสาร

### โครงสร้างที่แนะนำ

```
s3://shoeshub-qa-artifacts/
  exports/{yyyy}/{mm}/{dd}/{run_id}/report.xlsx
  exports/{yyyy}/{mm}/{dd}/{run_id}/manifest.json
  loadtest/{run_id}/summary.json
```

### 5.1 ตรวจว่าไฟล์ถูกสร้าง

```bash
aws s3 ls s3://shoeshub-qa-artifacts/exports/2026/09/02/ --recursive --human-readable

aws s3api head-object --bucket shoeshub-qa-artifacts \
  --key exports/2026/09/02/RUN123/report.xlsx
# ดู: ContentLength, ContentType, ETag, LastModified,
#     ServerSideEncryption, Metadata.sha256, Metadata.run-id
```

### 5.2 ดาวน์โหลดมาเปิดตรวจเนื้อหา

```bash
aws s3 presign s3://shoeshub-qa-artifacts/exports/2026/09/02/RUN123/report.xlsx \
  --expires-in 900
```

### 5.3 ตรวจ config bucket (security)

```bash
aws s3api get-public-access-block --bucket shoeshub-qa-artifacts
aws s3api get-bucket-versioning   --bucket shoeshub-qa-artifacts
aws s3api get-bucket-encryption   --bucket shoeshub-qa-artifacts
aws s3api get-bucket-lifecycle-configuration --bucket shoeshub-qa-artifacts
```

### จุดที่ QA ต้องตรวจ

- [ ] ไฟล์เกิดภายใน SLA หลัง trigger
- [ ] `ContentLength` > 0 และใกล้เคียงค่าที่คาด; `ContentType` ถูกต้อง
- [ ] checksum ตรง — เทียบ `Metadata.sha256` หรือ `x-amz-checksum-sha256` กับไฟล์ที่ดาวน์โหลด
- [ ] Block Public Access = ON ทั้ง 4 ข้อ
- [ ] Encryption เปิด (SSE-S3 หรือ SSE-KMS)
- [ ] Versioning เปิด (กัน overwrite/ลบพลาด)
- [ ] Lifecycle rule มี (expire 30–90 วันสำหรับ artifact ชั่วคราว)

---

## 6. Load Test — สถิติและคอขวด

### 6.1 เครื่องมือยิงโหลด

- **Distributed Load Testing on AWS** (AWS Solution) — ยิงจากหลาย region, ผลเข้า CloudWatch อัตโนมัติ
- หรือ **k6 / Locust / JMeter** จาก CI แล้ว push custom metric เข้า CloudWatch
- สคริปต์ scenario อ้างอิง `TEST_PLAN.md`

### 6.2 Metric ต้องดูไล่ทีละชั้น — ชั้นไหนอิ่มตัวก่อน = คอขวด

| ชั้น | Namespace | Metrics สำคัญ |
|---|---|---|
| ALB | `AWS/ApplicationELB` | `RequestCount`, `TargetResponseTime` (p50/p90/p99), `HTTPCode_Target_5XX_Count`, `RejectedConnectionCount`, `TargetConnectionErrorCount` |
| ECS / Fargate | `AWS/ECS`, `ECS/ContainerInsights` | `CPUUtilization`, `MemoryUtilization`, `RunningTaskCount`, `DesiredTaskCount` |
| RDS | `AWS/RDS` | `CPUUtilization`, `DatabaseConnections`, `ReadLatency`, `WriteLatency`, `FreeableMemory`, `DiskQueueDepth`, `Deadlocks` |
| SQS | `AWS/SQS` | `ApproximateAgeOfOldestMessage` (ขึ้นเรื่อย ๆ = worker ตามไม่ทัน) |
| Lambda | `AWS/Lambda` | `Throttles`, `ConcurrentExecutions`, `Duration` p99, `Errors` |

### 6.3 ดึง metric เทียบกัน

```bash
aws cloudwatch get-metric-data \
  --start-time 2026-09-02T14:00:00Z --end-time 2026-09-02T14:30:00Z \
  --metric-data-queries file://queries.json
```

`queries.json` — เทียบ p99 latency กับ RDS CPU:

```json
[
  {"Id": "p99", "MetricStat": {
     "Metric": {"Namespace": "AWS/ApplicationELB",
                "MetricName": "TargetResponseTime",
                "Dimensions": [{"Name": "LoadBalancer", "Value": "app/shoeshub/abc123"}]},
     "Period": 60, "Stat": "p99"}},
  {"Id": "rdscpu", "MetricStat": {
     "Metric": {"Namespace": "AWS/RDS", "MetricName": "CPUUtilization",
                "Dimensions": [{"Name": "DBInstanceIdentifier", "Value": "shoeshub-prod"}]},
     "Period": 60, "Stat": "Average"}}
]
```

### 6.4 เจาะลึก

- **X-Ray / ADOT** — trace-level latency breakdown ต่อ downstream call
- **RDS Performance Insights** — top SQL, wait events
- **CloudWatch Contributor Insights** — top IP / path ที่กินทรัพยากร

### ส่งมอบ QA

- ตาราง baseline vs spike (RPS, p50/p95/p99, error %)
- ระบุชั้นที่ saturate ก่อน + ตัวเลขที่พิสูจน์
- แนบ dashboard snapshot + ช่วงเวลา

### ผ่าน MCP

- _"get_metric_data ของ ALB TargetResponseTime p99 กับ RDS CPUUtilization ช่วง 14:00–14:30 วันนี้"_
- _"active alarms ตอนนี้มีอะไรบ้าง"_

---

## 7. Setup checklist — ทำให้โปรเจกต์รองรับ

### 7.1 Structured logging + request id — ✅ ทำแล้ว

`backend/observability.py` (stdlib ล้วน ไม่มี dependency เพิ่ม) — register ใน `main.py` แล้ว:

- `JsonFormatter` → ทุก log line เป็น JSON ออก stdout
- `RequestContextMiddleware` → gen/รับ `x-request-id`, จับ `latency_ms`, log 1 บรรทัดต่อ request, ยก level เป็น `WARNING` เมื่อ ≥ 1000ms
- `log_event("name", **fields)` → เพิ่ม structured event ที่จุดอื่นได้ (เช่นใน `routes/orders.py`)

ที่เหลือเมื่อ deploy จริง:
- ECS/App Runner/Lambda → stdout เข้า CloudWatch Logs อัตโนมัติ ไม่ต้องทำอะไรเพิ่ม
- ยังอยู่ Render → ship stdout ด้วย `boto3` `put_log_events` หรือ OTLP exporter (opt-in, ต้องเพิ่ม dep)

### 7.2 Custom metrics (EMF — ฟรี)

```bash
pip install aws-embedded-metrics
```

```python
from aws_embedded_metrics import metric_scope


@metric_scope
def record_order_placed(metrics, amount: float):
    metrics.set_namespace("ShoesHub")
    metrics.put_metric("OrderPlaced", 1, "Count")
    metrics.put_metric("OrderAmount", amount, "None")
```

จุดที่ควรใส่: `OrderPlaced`, `DiscountValidateLatencyMs`, `LoginFailed`, `CheckoutError`

### 7.3 Async flow (เมื่อเพิ่มฟีเจอร์ เช่น ส่งอีเมล / export ใหญ่)

- Pattern: `SNS topic → SQS queue → worker (Lambda หรือ ECS service)`
- ทุก queue **ต้องมี DLQ** + `RedrivePolicy { maxReceiveCount: 5 }`
- IaC (CDK/Terraform) ประกาศ alarm: DLQ depth > 0, `AgeOfOldestMessage` > 300s
- worker ต้อง idempotent (เก็บ processed message id กัน double-process)

### 7.4 S3 artifact bucket — ✅ สร้างแล้ว

`s3://shoeshub-qa-artifacts` (region `ap-southeast-1`) ตั้งค่าไว้:

| ค่า | สถานะ |
|---|---|
| Block Public Access | ON ครบ 4 |
| Encryption | SSE-S3 (AES256) + Bucket Key |
| Versioning | Enabled |
| Lifecycle | prefix `exports/` → ลบ current 90 วัน, noncurrent 30 วัน, abort MPU 7 วัน |
| Tags | `project=shoeshub`, `env=qa`, `purpose=qa-artifacts`, `managed-by=claude-code` |

ที่เหลือ: ให้แอป/`create_test_excel.py` เขียนด้วย `boto3` ใส่ metadata `run-id`, `sha256`, `content-type`
ลบทิ้งเมื่อไม่ใช้: `aws s3 rb s3://shoeshub-qa-artifacts --force`

### 7.5 ย้าย target มา AWS (สำหรับ load test จริง)

- SQLite scale ไม่ได้ → ECS Fargate + ALB + **RDS PostgreSQL**
- เปิด Container Insights + RDS Performance Insights
- ปรับ `backend/config.py` `DATABASE_URL` ให้รองรับ Postgres (เพิ่ม `psycopg2`/`asyncpg` + SQLAlchemy หรือ migration layer)

### 7.6 IAM

- สร้าง role/profile `shoeshub-qa` แบบ read-only (ดูส่วน 9)
- ผูกกับ MCP servers ทุกตัวใน `.mcp.json`

### ลำดับลงมือ

1. `aws configure sso --profile shoeshub-qa` (+ IAM policy ส่วน 9)
2. `cp .mcp.json.example .mcp.json` → แก้ profile/region → เปิด Claude Code ใหม่ → ทดสอบ `/mcp`
3. เพิ่ม JSON logging + `RequestContextMiddleware` (7.1)
4. เพิ่ม EMF metrics จุดสำคัญ (7.2)
5. ถ้าย้าย AWS: เขียน IaC — ECS + ALB + RDS + S3 + (SQS/DLQ ถ้ามี async) + alarms
6. เขียน DR runbook (ส่วน 8) + นัด DR drill

---

## 8. Disaster Recovery / Backup

### 8.1 กำหนด RTO / RPO ก่อน

| ระบบ | RTO (กู้คืนภายใน) | RPO (ข้อมูลหายได้ไม่เกิน) |
|---|---|---|
| API (stateless) | _กรอก_ | n/a |
| ฐานข้อมูล (RDS) | _กรอก_ | _กรอก_ |
| ไฟล์ S3 | _กรอก_ | _กรอก_ |

### 8.2 สิ่งที่ต้องมี

- **RDS:** Multi-AZ, automated backup retention 7–35 วัน, PITR เปิด, copy snapshot ข้าม region
- **AWS Backup:** backup plan ครอบ RDS + S3 + (EFS ถ้ามี), vault แยก account/region ถ้าทำได้
- **S3:** Versioning + Cross-Region Replication, (พิจารณา) MFA delete / Object Lock
- **Route53:** failover routing + health check ไป region สำรอง
- **Config/Secrets:** อยู่ใน IaC + Secrets Manager (replicate ข้าม region)

### 8.3 คำสั่งตรวจ

```bash
aws backup list-backup-plans
aws backup list-backup-jobs --by-state COMPLETED --max-results 20
aws backup list-backup-jobs --by-state FAILED
aws rds describe-db-instances --db-instance-identifier shoeshub-prod \
  --query 'DBInstances[0].{MultiAZ:MultiAZ,Retention:BackupRetentionPeriod,PITR:LatestRestorableTime}'
aws rds describe-db-snapshots --db-instance-identifier shoeshub-prod \
  --snapshot-type automated --query 'reverse(sort_by(DBSnapshots,&SnapshotCreateTime))[:5]'
```

### 8.4 DR drill ที่ QA ต้องรัน (อย่างน้อยไตรมาสละครั้ง)

1. เลือก snapshot ล่าสุด → restore เข้า instance ใหม่ใน environment แยก
2. จับเวลาตั้งแต่เริ่ม → ระบบพร้อมใช้ = **RTO จริง**
3. ตรวจ data integrity: นับ row ตารางหลัก, spot-check order/discount ล่าสุด, ตรวจ referential integrity
4. รัน smoke test ชุด critical path (login → เพิ่มสินค้า → ใช้ discount → checkout)
5. ทดสอบ restore ไฟล์ S3 หนึ่งชุดจาก version ก่อนหน้า
6. บันทึกผล: RTO/RPO ที่วัดได้ vs เป้า, ขั้นตอนที่ติดขัด, สิ่งที่ต้องแก้

### Checklist review แผน DR

- [ ] RTO/RPO เขียนเป็นตัวเลขชัดเจน มีเจ้าของอนุมัติ
- [ ] runbook ทำตามทีละขั้นแล้วกู้คืนได้จริง (ไม่ต้องพึ่ง tribal knowledge)
- [ ] DR drill ครั้งล่าสุด < 3 เดือน + มีบันทึกผล
- [ ] backup ถูกเก็บคนละ region / คนละ account
- [ ] secrets, TLS cert, DNS, IaC state กู้คืนได้ครบ
- [ ] มี alarm เมื่อ backup job FAILED

---

## 9. ภาคผนวก — IAM policy สำหรับ QA

เริ่มจาก managed policy `ReadOnlyAccess` หรือใช้ scoped policy ด้านล่าง (แคบกว่า ปลอดภัยกว่า):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Logs",
      "Effect": "Allow",
      "Action": [
        "logs:StartQuery", "logs:StopQuery", "logs:GetQueryResults",
        "logs:FilterLogEvents", "logs:GetLogEvents",
        "logs:DescribeLogGroups", "logs:DescribeLogStreams"
      ],
      "Resource": "*"
    },
    {
      "Sid": "Metrics",
      "Effect": "Allow",
      "Action": [
        "cloudwatch:GetMetricData", "cloudwatch:GetMetricStatistics",
        "cloudwatch:ListMetrics", "cloudwatch:DescribeAlarms",
        "cloudwatch:GetDashboard", "cloudwatch:ListDashboards"
      ],
      "Resource": "*"
    },
    {
      "Sid": "Messaging",
      "Effect": "Allow",
      "Action": [
        "sqs:GetQueueAttributes", "sqs:GetQueueUrl", "sqs:ListQueues",
        "sqs:ReceiveMessage",
        "sns:ListTopics", "sns:ListSubscriptions", "sns:ListSubscriptionsByTopic",
        "sns:GetTopicAttributes", "sns:GetSubscriptionAttributes"
      ],
      "Resource": "*"
    },
    {
      "Sid": "ArtifactsBucket",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:GetObjectVersion", "s3:ListBucket",
                 "s3:GetBucketVersioning", "s3:GetEncryptionConfiguration",
                 "s3:GetLifecycleConfiguration", "s3:GetBucketPublicAccessBlock"],
      "Resource": [
        "arn:aws:s3:::shoeshub-*-artifacts",
        "arn:aws:s3:::shoeshub-*-artifacts/*"
      ]
    },
    {
      "Sid": "DrReadOnly",
      "Effect": "Allow",
      "Action": [
        "backup:List*", "backup:Describe*", "backup:Get*",
        "rds:Describe*", "elasticloadbalancing:Describe*",
        "ecs:Describe*", "ecs:List*", "route53:Get*", "route53:List*"
      ],
      "Resource": "*"
    }
  ]
}
```

> `sqs:ReceiveMessage` ให้สิทธิ์อ่านข้อความจาก DLQ ได้ — ถ้าไม่อยากให้ QA แตะ prod queue
> ให้จำกัด `Resource` เป็น ARN ของ queue ใน env ที่ไม่ใช่ prod เท่านั้น

---

## 10. เทสเป็นทีม — เดินดูผลลัพธ์ใน AWS

สถานการณ์: คุณกับเพื่อน QA รันเทส (functional / async / load) พร้อมกัน แล้วต้องดูผลใน AWS ทั้งคู่

### 10.1 ก่อนเทส — เตรียม (ทำครั้งเดียว)

| # | ทำอะไร | เครื่องมือ / ที่ไหน |
|---|---|---|
| 1 | ให้เพื่อนเข้าถึง account `138415545281` แบบ **read-only** | IAM console → Users → สร้าง user + แนบ policy จาก [§9](#9-ภาคผนวก--iam-policy-สำหรับ-qa) → ส่ง access key / หรือ Identity Center assign |
| 2 | ตกลง **region** ให้ตรงกัน | ทั้งทีมใช้ `ap-southeast-1` (เว้น toolkit endpoint = `us-east-1`) |
| 3 | จดชื่อ resource ที่จะดู | log group เช่น `/ecs/shoeshub-qa` · bucket `shoeshub-qa-artifacts` · queue/topic (ถ้ามี async) |
| 4 | สร้าง **CloudWatch dashboard** ชื่อ `shoeshub-qa-loadtest` รวมกราฟ ALB/ECS/RDS/SQS ไว้ที่เดียว | CloudWatch → Dashboards → Create → เพิ่ม widget → **Share** ลิงก์ให้เพื่อน |
| 5 | เปิด time zone ของ dashboard เป็น **Local** และช่วงเวลาเป็น relative (เช่น 1h) | มุมขวาบนของ dashboard |
| 6 | นัด **naming ของรอบเทส** | ใช้ `run_id` เดียวกัน เช่น `RUN-20260902-01` — ใส่ทั้งใน log field, S3 prefix, ชื่อ test report |

### 10.2 ระหว่างเทส — ใครดูอะไร ที่ไหน

| อยากรู้ | เครื่องมือ | เข้าไปที่ |
|---|---|---|
| Log ไหลสด + error ทันที | **CloudWatch Live Tail** | CloudWatch → Logs → **Live tail** → เลือก log group → filter `ERROR` หรือ `request_id=...` |
| Error / latency ย้อนหลัง | **Logs Insights** | CloudWatch → Logs Insights → paste query [§3.2](#3-cloudwatch-logs--debug) → เลือกช่วงเวลารอบเทส |
| กราฟ throughput / p99 / CPU ตอนยิงโหลด | **CloudWatch Dashboard** ที่แชร์ไว้ | เปิดลิงก์ dashboard `shoeshub-qa-loadtest` — เห็นเหมือนกันทั้งทีม real-time |
| คิวค้าง / DLQ | **SQS console** | SQS → เลือก queue → แท็บ **Monitoring**; DLQ ดู `Messages available` ต้องเป็น 0 |
| ไฟล์ผลลัพธ์ถูกสร้างครบไหม | **S3 console** | S3 → `shoeshub-qa-artifacts` → prefix `exports/2026/09/02/RUN-20260902-01/` → ดู Size / LastModified |
| อยาก query ข้าม service เร็ว ๆ | **Claude Code + `aws-mcp`** | พิมพ์เช่น _"error count ใน /ecs/shoeshub-qa ช่วง 5 นาทีล่าสุด แยกตาม path"_ แล้ว paste ผลให้เพื่อน |
| Alarm เด้งไหม | **CloudWatch Alarms** | CloudWatch → Alarms → All alarms → filter state `In alarm` |

> เพื่อนที่มีแค่ read-only ก็เปิดหน้าเหล่านี้ได้หมด (ยกเว้นกดปุ่มแก้/redrive) — ถ้าเพื่อนไม่มี access เลย ให้คนที่มี MCP รัน query แล้วแชร์ผล หรือ screen-share console

### 10.3 หลังเทส — เก็บหลักฐานใส่รายงาน

| หลักฐาน | วิธีเก็บ |
|---|---|
| Log ของรอบเทส | Logs Insights → รัน query → ปุ่ม **Export results** (CSV) หรือ **Add to dashboard** |
| ช่วง metric ที่ผิดปกติ | Dashboard → widget → **⋮ → Download image** หรือ **View in metrics** → Share URL (ฝัง start/end เวลา) |
| ไฟล์ผลลัพธ์ | `aws s3 cp s3://shoeshub-qa-artifacts/exports/.../RUN-20260902-01/ ./evidence/ --recursive` |
| สถานะ alarm ตอนพีค | screenshot หน้า Alarms + `aws cloudwatch describe-alarm-history --alarm-name ...` |
| สรุปตัวเลข | ตาราง baseline vs peak (RPS, p50/p95/p99, error %, ชั้นที่ saturate ก่อน) ตาม [§6](#6-load-test--สถิติและคอขวด) |

### 10.4 เช็กลิสต์รอบเทสเป็นทีม

- [ ] เพื่อนมี read-only access + login region ตรงกันแล้ว
- [ ] dashboard `shoeshub-qa-loadtest` แชร์ลิงก์แล้ว เปิดได้ทั้งคู่
- [ ] ตกลง `run_id` เดียวกัน ใส่ครบทั้ง log / S3 prefix / report
- [ ] ระหว่างเทส: 1 คนเฝ้า Live Tail, 1 คนเฝ้า dashboard
- [ ] หลังเทส: export log + download S3 + screenshot dashboard เข้าโฟลเดอร์ evidence
- [ ] DLQ = 0 และ alarm กลับ OK ก่อนปิดรอบ

---

## 11. ฝึกมือ — ใส่ข้อมูลตัวอย่างเข้า CloudWatch

ยังไม่ได้ deploy บน AWS ก็ฝึกใช้ CloudWatch ได้ — สคริปต์ `scripts/seed_cloudwatch_demo.py`
ยิง log + metric ปลอมแบบ "รอบ load test 45 นาที ที่มี error burst กลางรอบ" เข้า account จริง

### รัน

```bash
pip install boto3
python scripts/seed_cloudwatch_demo.py
# ผลลัพธ์ท้ายสุดจะพิมพ์ลิงก์ dashboard ให้
```

ใช้ credential จาก `aws login` เดิม (profile `shoeshub-qa`) โดยอัตโนมัติ

### สร้างอะไรบ้าง

| resource | รายละเอียด |
|---|---|
| Log group `/shoeshub/qa/demo` | retention 7 วัน · ~140 บรรทัด JSON (INFO/WARNING/ERROR) รูปแบบเดียวกับ `backend/observability.py` |
| Metric filter `error-count` | นับบรรทัด `level=ERROR` → metric `ShoesHub/QA / ErrorCountFromLogs` |
| Custom metrics `ShoesHub/QA` | `RequestLatencyP99Ms`, `RequestsPerSecond`, `ErrorCount`, `OrdersPlaced` — 1 จุด/นาที ย้อนหลัง 45 นาที |
| Alarm `shoeshub-qa-demo-errors` | `ErrorCount` (Sum, 5 นาที) > 0 |
| Dashboard `shoeshub-qa-demo` | 4 widget: p99 latency · Requests/sec · Errors & Orders · ตาราง Recent errors |

### เปิดดูที่ไหน — เห็นอะไร

> ทุกหน้า: Region = **ap-southeast-1**, ช่วงเวลามุมขวาบน = **Last 1 hour**

| ที่ | เห็นอะไร |
|---|---|
| **Dashboards → shoeshub-qa-demo** | p99 latency ไต่ขึ้น → พุ่ง ~800ms กลางกราฟ → ลง · Requests/sec ramp 20→80 · แท่ง error โผล่ช่วงพีค, orders คงที่ · ตาราง error 20 แถว |
| **Logs → Log groups → `/shoeshub/qa/demo`** | 1 stream — คลิกอ่าน JSON ทีละบรรทัด (`request_id`, `path`, `status`, `latency_ms`) |
| **Logs → Logs Insights** | เลือก log group `/shoeshub/qa/demo` → วาง query [§3.2](#3-cloudwatch-logs--debug) / [§3.3](#3-cloudwatch-logs--debug) → Run → ตาราง field ที่ parse แล้ว |
| **Metrics → All metrics → `ShoesHub/QA` → Environment** | 4 metric — กราฟได้, ลองเปลี่ยน stat (Average/p99/Sum) และ period |
| **Alarms → All alarms** | `shoeshub-qa-demo-errors` — ช่วงพีคเป็น **In alarm**, พอไม่มี data ใหม่กลับ OK/Insufficient |

### ลบทิ้ง

```bash
python scripts/seed_cloudwatch_demo.py --teardown
```

ลบ log group + alarm + dashboard · custom metric ลบเองไม่ได้ แต่พอไม่มี data ใหม่ เดือนถัดไปคิด $0
(S3 bucket `shoeshub-qa-artifacts` แยกต่างหาก ไม่โดนลบ)

---

## อ้างอิง

- AWS MCP servers: <https://github.com/awslabs/mcp>
- CloudWatch Logs Insights query syntax: AWS docs → "CloudWatch Logs Insights query syntax"
- Distributed Load Testing on AWS: AWS Solutions Library
- AWS Backup developer guide: AWS docs → "AWS Backup"
- Embedded Metric Format: AWS docs → "CloudWatch Embedded Metric Format"
