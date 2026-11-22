# Deliverable 2 & 6: Screenshots & Demonstration Evidence Guide
## Assignment 18: Secure IoT Data Backup System
**Student:** Vasani Jeel | **Reg. No:** 24UG00241

Your professor requires original screenshots and evidence for the deliverables below. Follow this step-by-step guide to take clean, high-resolution screenshots from your running application (`http://127.0.0.1:5000`):

---

### Screenshot 1: Data Upload (Deliverable 2a)
* **Where to capture:** Navigate to `http://127.0.0.1:5000/sensor-feed` or click **"Create Backup"** on the Dashboard.
* **What to show:**
  * The **Live Sensor Telemetry** stream showing readings from `ENV-STATION-01`, `TURBINE-EDGE-04`, `SMART-METER-09`, and `FACTORY-HVAC-12`.
  * The toast notification: *"Daily backup ingested! S3 Version ID: v_..."* with SHA-256 digest calculated.
  * The raw JSON telemetry batch inspector at the bottom.

---

### Screenshot 2: Version History (Deliverable 2c & Deliverable 4)
* **Where to capture:** Navigate to `http://127.0.0.1:5000/backups`, find any sensor backup (e.g. `sensors/daily_telemetry_...json`), and click **"Versions"** (or go to `/versions/sensors/...json`).
* **What to show:**
  * The timeline showing multiple versions (`v3`, `v2`, `v1`) of the same file.
  * The **"Latest (Active)"** badge on the current version.
  * The unique `VersionId` strings, timestamps, file sizes, and SHA-256 integrity checksums.
  * This proves **Object Versioning Evidence (Deliverable 4)**.

---

### Screenshot 3: Restore Operation (Deliverable 2b)
* **Where to capture:** On the **Version History** page (`/versions/...`), click the **"Restore this Version"** button on an older snapshot (e.g., `v1`).
* **What to show:**
  * The popup alert: *"POINT-IN-TIME RESTORE COMPLETED! Restored from: v_... Promoted to New Version ID: v_..."*.
  * The updated timeline showing the promoted snapshot as the new active version, with previous versions still preserved intact.

---

### Screenshot 4: BackupAdmin Role Configuration (Deliverable 3)
* **Where to capture:** Navigate to `http://127.0.0.1:5000/iam`.
* **What to show:**
  * The **BackupAdmin** role card with permissions (`s3:PutObject`, `s3:GetObject`, `s3:RestoreObject`, `s3:DeleteObject`, `s3:PutLifecycleConfiguration`).
  * The official IAM JSON policy document from `docs/IAM_POLICIES.md`.

---

### Screenshot 5: Access Control & Least Privilege Enforcement (Deliverable 6)
* **Where to capture:** On the Access Control page (`http://127.0.0.1:5000/iam`):
  * **Demonstration 1:** In the role dropdown, switch role to **`SensorDevice`**.
  * Go to the **Permission Evaluator**, select action `s3:DeleteObject`, and click **Test**.
  * Capture the red box: **`403 ACCESS DENIED: Explicit Deny in policy 'SensorWriteOnlyPolicy'`**.
  * **Demonstration 2:** Switch role to **`BackupAdmin`**, test `s3:DeleteObject`, and capture the green box: **`ACTION PERMITTED`**.
  * Capture the **Role Permissions Matrix** table showing Allow/Deny across all 4 roles.

---

### Screenshot 6: Storage Lifecycle Management Policy (Deliverable 5)
* **Where to capture:** Navigate to `http://127.0.0.1:5000/lifecycle`.
* **What to show:**
  * The 4-stage pipeline: Hot Tier (Standard) &rarr; Warm Tier (Standard-IA) &rarr; Cold Archive (Glacier) &rarr; Expire Non-Current.
  * The **Retention Simulator** showing objects transitioning to Glacier.
  * The **Storage Cost Optimization** cards showing 79.1% monthly cloud savings.

---

### Screenshot 7: Automated Test Suite Output
* **Where to capture:** Run in terminal: `python test_system.py`.
* **What to show:**
  * All 8 test cases marked `PASSED` with `100% SUCCESS RATE`.
