# 🛡️ Secure IoT Data Backup System

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![AWS S3](https://img.shields.io/badge/AWS-S3_Object_Storage-FF9900?style=for-the-badge&logo=amazons3&logoColor=white)](https://aws.amazon.com/s3/)
[![AWS IAM](https://img.shields.io/badge/Security-AWS_IAM_RBAC-232F3E?style=for-the-badge&logo=amazonwebservices&logoColor=white)](https://aws.amazon.com/iam/)
[![License](https://img.shields.io/badge/Course-Cloud_Computing_SA-10B981?style=for-the-badge)](https://github.com)
[![Build Status](https://img.shields.io/badge/Tests-8%2F8%20Passed%20(100%25)-0ea5e9?style=for-the-badge)]()

> **Cloud Computing Individual Project Submission**  
> **Student Name:** Vasani Jeel  
> **Registration Number:** 24UG00241  
> **Assignment Number:** Assignment 18: Secure IoT Data Backup System  
> **Evaluation:** SA Component (15 Marks: 10 Marks Work + 5 Marks Presentation)  

---

## 📌 Executive Summary

The **Secure IoT Data Backup System** is an enterprise-grade cloud architecture designed to ingest, protect, version, and manage mission-critical Internet of Things (IoT) sensor telemetry. Deployed on a Cloud Virtual Machine (AWS EC2 / Azure VM) with Cloud Object Storage (Amazon S3 / Azure Blob), the system solves fundamental vulnerabilities in edge archiving: unauthorized data deletion, ransomware tampering, overprivileged device credentials, and escalating cloud storage costs.

---

## 🚀 Key Features

* **📦 Cloud Object Storage with Object Versioning:** Full AWS S3 API compatibility. Retains immutable version history for every daily sensor archive (`v_YYYYMMDD_...`), providing zero-loss point-in-time recovery and protection against accidental deletion or ransomware.
* **🛡️ Least-Privilege IAM Access Control:**
  * `BackupAdminRole`: Full administrative access (create, delete, restore, manage bucket policies, inspect audit logs).
  * `SensorApplicationRole`: Scoped write-only permission (`s3:PutObject` on `sensors/*`). Explicitly denied from deleting files or altering policies.
  * `ComplianceAuditorRole`: Read-only verification access.
  * `PublicAnonymousUser`: 100% blocked by S3 Block Public Access.
* **🌐 Public APIs Integration:** Ingests live real-time atmospheric sensor data from the **Open-Meteo Real-Time Weather API** (showcased from `https://github.com/public-apis/public-apis`) to correlate ambient meteorological metrics with edge machinery telemetry.
* **🔄 S3 Storage Lifecycle & Multi-Tier Optimization:**
  * **Day 0–30:** `S3 Standard` ($0.023/GB-mo) for real-time dashboards and hot queries.
  * **Day 31–90:** `S3 Standard-IA` ($0.0125/GB-mo, 45% savings) for infrequent analytical access.
  * **Day 91–365:** `S3 Glacier` ($0.004/GB-mo, 82% savings) for compliance archiving.
  * **> 365 Days:** Permanent expiration of non-current versions.
* **🔐 Cryptographic SHA-256 Integrity Verification:** Every backup generates a client-side SHA-256 hash. Re-verified on download/restore with built-in Tamper Attack simulation to prove cryptographic tamper detection.
* **🔑 Secure Pre-Signed URLs:** Time-limited (15-minute TTL), HMAC-signed download URLs for secure file retrieval without public bucket exposure.
* **📜 Immutable CloudTrail Audit Trail:** Chronological log tracking Timestamp, Principal Role, Cloud Action, Resource ARN, IP Address, and Allow/Deny status.

---

## 🏗️ System Architecture

```
+-----------------------------------------------------------------------------+
|                      IoT Edge & External Ingestion Tier                     |
|  - ENV-STATION-01 (Weather Mast)      - TURBINE-EDGE-04 (Machinery)         |
|  - SMART-METER-09 (Energy Grid)       - Open-Meteo Public Weather API       |
+---------------------------------------+-------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------+
|               Cloud VM Ingestion & Security Gateway (AWS EC2)               |
|  - Python 3.11 / Flask Daemon         - SHA-256 Cryptographic Checksum Engine|
|  - IAM Policy Engine (Least Privilege)- CloudTrail Audit Event Logger       |
|  - Pre-Signed URL Generator (HMAC)    - Real-Time Interactive Web Dashboard |
+---------------------------------------+-------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------+
|                   Amazon S3 Cloud Object Storage Vault                      |
|  - Bucket: iot-secure-telemetry-vault                                       |
|  - Block Public Access: ENABLED (All 4 flags active)                       |
|  - Server-Side Encryption: SSE-S3 AES-256                                   |
|  - Object Versioning: ENABLED (v1, v2, v3 ... immutable snapshots)         |
|                                                                             |
|  +-----------------------------------------------------------------------+  |
|  |                 S3 Storage Lifecycle Progression Rules                |  |
|  |  Day 0-30: STANDARD  -->  Day 31-90: STANDARD_IA  -->  Day 91+: GLACIER |  |
|  +-----------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------+
```

---

## 📁 Repository Directory Structure

```
Secure-IoT-Data-Backup-System/
├── app.py                      # Flask Application Server (Dashboard & REST API)
├── config.py                   # Configuration & Cloud Constants
├── test_system.py              # Automated 8-Scenario Cloud Verification Suite
├── requirements.txt            # Python Dependencies (Flask, Boto3, Requests, etc.)
├── run_demo.bat                # Windows 1-Click Launch Script
├── Dockerfile                  # Container Configuration for Cloud VMs
├── docker-compose.yml          # Multi-service Container Orchestration
├── deploy_ec2.sh               # AWS EC2 / Linux VM Automated Deployment Script
├── .env.example                # Sample Cloud Credentials Template
├── .gitignore                  # Git Ignore Rules
├── core/
│   ├── storage_engine.py       # S3 Storage Engine with Versioning & Pre-signed URLs
│   ├── iam_manager.py          # IAM Policy Evaluator & Least-Privilege Rules
│   ├── sensor_ingestion.py     # Multi-Sensor Generator + Open-Meteo Public API Ingestor
│   ├── lifecycle_engine.py     # S3 Lifecycle Transition & Cost Optimizer
│   └── integrity_verifier.py   # SHA-256 Checksum Engine & Tamper Simulator
├── templates/
│   ├── base.html               # Base Cyber-Industrial Glassmorphic Layout
│   ├── index.html              # Main Analytics Dashboard & Real-Time Monitoring
│   ├── backups.html            # Backup Storage Catalog & Filter Table
│   ├── version_history.html    # S3 Object Versioning & Point-in-Time Restore Center
│   ├── iam_security.html       # IAM Role-Based Access Control (RBAC) Simulator
│   ├── lifecycle.html          # S3 Lifecycle & Multi-Tier Cost Calculator
│   ├── live_sensor_feed.html   # Real-Time Telemetry Stream & Public API Showcase
│   ├── audit_logs.html         # CloudTrail Event Log Explorer
│   └── report.html             # Printable 8-Page Academic Technical Report
├── static/
│   ├── css/style.css           # Custom Glassmorphic Dark UI Theme
│   └── js/app.js               # Client Logic, Chart.js Visualizations, API Calls
└── docs/
    ├── PROJECT_REPORT.md       # Full 8-Page Academic Project Submission Report
    └── VIVA_QUESTIONS.md       # Top 20 Viva/Presentation Q&A (5 Marks Prep)
```

---

## ⚡ Quick Start & Demonstration

### 1. Prerequisites
* Python 3.10+ installed
* Git installed

### 2. Run on Windows (One-Click)
Double-click `run_demo.bat` or run:
```powershell
python app.py
```
Open your browser at: **`http://127.0.0.1:5000`**

### 3. Run Automated Tests
Execute the verification test suite to prove all 8 test cases pass:
```powershell
python test_system.py
```
Output:
```
=================================================================
 CLOUD SECURITY & S3 OBJECT STORAGE AUTOMATED TEST RUNNER
 Student: Vasani Jeel | Reg: 24UG00241 | Assignment 18
=================================================================
[TC-01] Daily Multi-Sensor Ingestion via SensorDevice Role:       PASSED
[TC-02] S3 Bucket Object Versioning Verification:                  PASSED
[TC-03] Enforcing PoLP: SensorDevice Denied on s3:DeleteObject:   PASSED
[TC-04] Full Administrative Privilege for BackupAdmin Role:       PASSED
[TC-05] Cryptographic SHA-256 Verification & Tamper Detection:    PASSED
[TC-06] Point-in-Time Recovery (Restoring Historical Snapshot):   PASSED
[TC-07] Pre-Signed Temporary Access Token Generation & Download:  PASSED
[TC-08] Live Public APIs Integration (Open-Meteo Weather Stream): PASSED
=================================================================
 TEST SUITE SUMMARY: 8/8 TESTS PASSED (100% SUCCESS RATE)
=================================================================
```

---

## ☁️ Cloud VM Deployment (AWS EC2 / Azure VM)

To deploy on a remote Linux Cloud VM:
```bash
# Clone the repository
git clone <YOUR_GITHUB_REPO_URL>
cd Secure-IoT-Data-Backup-System

# Run the automated deployment script
chmod +x deploy_ec2.sh
./deploy_ec2.sh
```
The script automatically configures Python 3, Gunicorn as a systemd background service, and Nginx reverse proxy on port 80.

---

## 🎓 Deliverables Summary for Evaluation

| Deliverable Required in Syllabus | Implementation in Project | Location |
|---|---|---|
| **Backup Architecture Diagram** | High-level cloud diagram with Mermaid & UI flow | Section 2.1 & `docs/PROJECT_REPORT.md` |
| **Data Upload Evidence** | Daily multi-sensor batch generation + SHA-256 | `/sensor-feed` & `/backups` |
| **Restore Operation Evidence** | Point-in-time version restore with verification | `/versions/<key>` |
| **Version History Evidence** | Immutable S3 VersionId tracking and diffs | `/versions/<key>` |
| **BackupAdmin Role Configuration** | Complete IAM JSON policy document | `/iam` & `docs/PROJECT_REPORT.md` |
| **Object Versioning Evidence** | S3 bucket versioning status and manifest | `/api/stats` & `data/storage/` |
| **Lifecycle Management Policy** | Multi-tier rules (Standard &rarr; IA &rarr; Glacier) | `/lifecycle` |
| **Access Control & Security** | RBAC matrix, S3 Block Public Access, Pre-Signed URLs | `/iam` |
| **Final Project Report (5–8 pages)** | Complete academic paper formatted for PDF print | `/report` & `docs/PROJECT_REPORT.md` |
| **Demo Application** | Full interactive responsive web console | `http://127.0.0.1:5000` |

---

## 👤 Author
* **Vasani Jeel** (Reg. No: **24UG00241**)  
* Department of Computer Science & Engineering  
* Cloud Computing Course
