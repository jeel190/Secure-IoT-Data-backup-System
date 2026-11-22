# Presentation & Viva Voce Preparation Guide (5 Marks)
## Assignment 18: Secure IoT Data Backup System
**Student:** Vasani Jeel | **Reg. No:** 24UG00241

Here are the top 20 questions external examiners and professors frequently ask during the 3-5 minute demonstration, with crystal-clear answers:

---

### **Q1: What is the primary objective of your project?**
**Answer:** The objective is to build a secure, resilient, and cost-optimized cloud backup system for IoT sensor data. It utilizes Cloud Object Storage (Amazon S3 / Azure Blob) with Object Versioning to prevent data loss, enforces AWS IAM Least-Privilege policies to isolate IoT edge devices from administrative capabilities, applies automated storage lifecycle tiering to minimize cloud costs, and validates SHA-256 cryptographic hashes for tamper detection.

---

### **Q2: Why did you choose Object Storage (S3 / Blob) over a Relational or NoSQL Database for IoT backups?**
**Answer:** IoT backups consist of large immutable batches of sensor files (daily telemetry dumps, binary logs, JSON arrays). Object storage offers:
1. **Infinite Scalability:** Unbounded storage capacity without schema migrations or table partitioning.
2. **Superior Cost-Efficiency:** S3 storage costs are significantly lower than active provisioned databases (RDS/DynamoDB).
3. **Built-in Versioning & Lifecycle:** S3 natively supports version tracking and automatic transitions to archival tiers like Glacier ($0.004/GB/mo).

---

### **Q3: How does Object Versioning protect against ransomware and accidental deletion?**
**Answer:** With S3 Versioning enabled, every upload to an existing key creates a new immutable version with a unique `VersionId`. 
* If a delete command is issued without a `VersionId`, S3 only adds a `DeleteMarker`; the underlying data versions remain intact and can be restored anytime.
* If a compromised sensor tries to overwrite a file with corrupt data, a new version is created rather than overwriting the original. The administrator can instantly restore the previous version.

---

### **Q4: Explain the Principle of Least Privilege (PoLP) implemented in your system.**
**Answer:** Least privilege ensures entities only hold permissions essential to their function.
* **SensorApplicationRole:** Can only execute `s3:PutObject` on `sensors/*`. It is explicitly denied from deleting objects (`s3:DeleteObject`), modifying bucket policies (`s3:PutBucketPolicy`), or altering lifecycle settings.
* **BackupAdminRole:** Holds full administrative privileges to restore, delete, reconfigure lifecycle rules, and inspect audit logs.
* **ComplianceAuditorRole:** Holds read-only access (`s3:GetObject`, `s3:ListBucket`, `cloudtrail:LookupEvents`).

---

### **Q5: In AWS IAM, what happens if an action is matched by both an Allow and a Deny statement?**
**Answer:** In AWS IAM, an **Explicit Deny always overrides an Allow**, regardless of the order or policy. For example, if `SensorApplicationRole` has an allow for all writes but an explicit deny on `s3:DeleteObject`, any delete request is immediately rejected with HTTP 403 Forbidden.

---

### **Q6: What is S3 Block Public Access and why is it important for IoT backups?**
**Answer:** S3 Block Public Access is a centralized security control with four settings that prevent accidental or malicious public exposure of bucket data via ACLs or bucket policies. For IoT backups, enabling Block Public Access ensures that telemetry containing proprietary industrial machinery or infrastructure data can never be leaked to the public internet.

---

### **Q7: If public access is blocked, how do authorized users securely download backup files?**
**Answer:** Authorized users download files using **Pre-Signed URLs**. The cloud server signs a temporary URL using an HMAC cryptographic signature with a strictly enforced Time-To-Live (TTL, e.g., 15 minutes). The user downloads the specific object directly without needing permanent AWS credentials or exposing public bucket access.

---

### **Q8: Explain your S3 Storage Lifecycle policy and the cost benefits.**
**Answer:** 
* **Days 0–30:** S3 Standard ($0.023/GB) for hot operational access.
* **Days 31–90:** S3 Standard-IA ($0.0125/GB) for infrequent analytical access (45% cheaper).
* **Days 91–365:** S3 Glacier Flexible Retrieval ($0.004/GB) for cold compliance archive (82% cheaper).
* **> 365 Days:** Obsolete non-current versions are automatically purged.
This multi-tier policy reduces monthly storage costs by approximately 79% to 82% compared to retaining everything in S3 Standard.

---

### **Q9: How do you verify the integrity of a restored backup?**
**Answer:** Before uploading a sensor batch, the ingestion gateway calculates a cryptographic **SHA-256 hash** of the raw data and stores it in the object metadata. When restoring or retrieving the backup, the SHA-256 hash is recalculated on the fly. If even a single bit was corrupted or tampered with, the hashes mismatch and the restore is aborted.

---

### **Q10: What Public API did you integrate and what value does it add?**
**Answer:** We integrated the **Open-Meteo Real-Time Weather API** from the GitHub `public-apis` directory. It streams real-world ambient temperature, humidity, wind velocity, and barometric pressure in real time. We append this live meteorological feed into our daily IoT backup batches alongside edge turbine and grid readings, providing ambient environmental context for machinery analytics.

---

### **Q11: How did you implement non-destructive point-in-time recovery?**
**Answer:** When an administrator chooses to restore an older version (e.g., version 1), our system retrieves the data of version 1, validates its SHA-256 hash, and performs an `s3:PutObject` to write it as the new latest version. This preserves the entire version lineage without deleting intermediate versions.

---

### **Q12: What role does the Cloud Virtual Machine (EC2) play?**
**Answer:** The Cloud VM acts as the **Ingestion & Security Gateway**. It aggregates telemetry from distributed IoT sensors, communicates with external public APIs, computes SHA-256 cryptographic checksums, evaluates IAM role policies, logs every API call into an immutable CloudTrail audit log, and serves the management dashboard.

---

### **Q13: What happens when an unauthenticated anonymous user attempts to access the vault?**
**Answer:** The request is mapped to the `AnonymousUser` identity. Because S3 Block Public Access is enabled and no policy grants access to anonymous principals, the request is blocked with HTTP 403 Access Denied and logged in the audit trail.

---

### **Q14: What is the difference between S3 Standard and S3 Standard-IA?**
**Answer:** Both tiers offer identical sub-millisecond retrieval latency and 99.999999999% (11 9's) data durability. However, Standard-IA costs roughly 45% less for monthly storage, with a small per-GB data retrieval fee, making it ideal for data accessed less than once a month.

---

### **Q15: What is S3 Glacier and why is it used for IoT compliance backups?**
**Answer:** S3 Glacier is an extremely low-cost cloud storage tier designed for data archiving and long-term disaster recovery. At $0.004 per GB per month, it provides secure, durable preservation for regulatory compliance where data is rarely retrieved.

---

### **Q16: How does your application ensure auditability?**
**Answer:** Every operation (file uploads, version restores, deletion attempts, permission evaluations) generates a structured JSON audit event mimicking AWS CloudTrail. Each entry logs: Timestamp (UTC), Principal Role, Cloud Action, Resource ARN, IP Address, Status (`ALLOW` / `DENY`), and evaluation reasoning.

---

### **Q17: How did you demonstrate that tamper detection works?**
**Answer:** The application includes a "Test Tamper Detection" button that simulates a bit-flip attack by appending unauthorized bytes to a stored file. When "Verify Integrity" is executed, the calculated SHA-256 checksum fails to match the original manifest hash, immediately raising a `TAMPER_DETECTED` alarm and rejecting the file.

---

### **Q18: What is the purpose of Gunicorn and Nginx in the EC2 deployment script?**
**Answer:** Gunicorn serves as the production WSGI application server, managing multiple worker processes for concurrency and stability. Nginx acts as the reverse proxy on port 80, handling SSL termination, buffering client requests, and forwarding traffic securely to Gunicorn.

---

### **Q19: If an IoT sensor's local clock is inaccurate, how does the cloud system maintain consistent timestamps?**
**Answer:** The cloud ingestion gateway appends standardized UTC server timestamps to both the object metadata and the S3 manifest upon receiving the payload, ensuring chronological ordering regardless of edge clock drift.

---

### **Q20: What are three potential enterprise enhancements you would add in production?**
**Answer:** 
1. **Cross-Region Replication (CRR):** Replicating buckets across different AWS geographical regions for disaster recovery.
2. **S3 Object Lock (WORM):** Enforcing Write-Once-Read-Many retention to make backups legally immutable.
3. **AWS KMS Customer-Managed Keys (CMK):** Using dedicated encryption keys with automatic annual rotation and hardware security modules (HSM).
