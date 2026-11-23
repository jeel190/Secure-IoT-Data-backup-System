import os
import subprocess
import base64

def get_base64_img(path):
    with open(path, "rb") as f:
        ext = os.path.splitext(path)[1].lower()
        mime = "image/png" if ext == ".png" else "image/jpeg"
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode('utf-8')

img_dir = r"C:\Users\dell\.gemini\antigravity\brain\0bddacab-2752-4390-9234-c31f912ae85e\.user_uploaded"
img_vm = get_base64_img(r"D:\Gen Ai\Secure-IoT-Data-Backup-System\vm_screenshot_fresh.png")
img_web = get_base64_img(r"D:\Gen Ai\Secure-IoT-Data-Backup-System\webapp_screenshot_live.png")
img1 = get_base64_img(os.path.join(img_dir, "media_1795373189475_d5922d62.png"))
img2 = get_base64_img(os.path.join(img_dir, "media_1795373189479_c7fd30a9.png"))
img3 = get_base64_img(os.path.join(img_dir, "media_1795373189483_ca56fabe.png"))
img4 = get_base64_img(os.path.join(img_dir, "media_1795373189487_38f691cc.png"))
img5 = get_base64_img(os.path.join(img_dir, "media_1795373189490_5b30b138.png"))

html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Secure IoT Data Backup System - Technical Project Report</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 12mm 15mm 12mm 15mm;
  }}
  * {{
    box-sizing: border-box;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.5;
    font-size: 9pt;
    margin: 0;
    padding: 0;
  }}
  .page {{
    page-break-after: always;
    display: flex;
    flex-direction: column;
    min-height: 100%;
  }}
  .page:last-child {{
    page-break-after: avoid;
  }}
  h1 {{
    color: #1e3a8a;
    font-size: 19.5pt;
    text-align: center;
    margin: 0 0 4px 0;
    font-weight: 800;
    letter-spacing: -0.3px;
  }}
  .subtitle {{
    text-align: center;
    color: #64748b;
    font-size: 9.5pt;
    margin: 0 0 14px 0;
    font-weight: 500;
  }}
  .header-card {{
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }}
  .header-card-title {{
    background: #1e3a8a;
    color: #ffffff;
    font-weight: 700;
    font-size: 8.5pt;
    padding: 5px 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  table.info-grid {{
    width: 100%;
    border-collapse: collapse;
    font-size: 8.5pt;
  }}
  table.info-grid td {{
    padding: 6px 12px;
    border: 1px solid #f1f5f9;
    vertical-align: middle;
  }}
  table.info-grid tr:nth-child(even) {{
    background: #f8fafc;
  }}
  .lbl {{
    font-weight: 700;
    color: #1e3a8a;
    display: inline-block;
    min-width: 130px;
  }}
  .val {{
    color: #1e293b;
  }}
  .links-box {{
    background: #f0fdf4;
    border: 1.5px solid #86efac;
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 14px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px 12px;
    font-size: 8.2pt;
  }}
  .links-box a {{
    color: #15803d;
    font-weight: 700;
    text-decoration: underline;
    word-break: break-all;
  }}
  .links-box strong {{
    color: #166534;
  }}
  h2 {{
    color: #1e3a8a;
    font-size: 11.5pt;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 4px;
    margin: 8px 0 8px 0;
    font-weight: 700;
  }}
  table.index-table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    margin-bottom: 6px;
    font-size: 8.5pt;
  }}
  table.index-table th {{
    background: #1e3a8a;
    color: #ffffff;
    padding: 6px 10px;
    text-align: left;
    font-weight: 700;
  }}
  table.index-table td {{
    padding: 6px 10px;
    border: 1px solid #e2e8f0;
  }}
  table.index-table tr:nth-child(even) {{
    background: #f8fafc;
  }}
  .idx-num {{
    font-weight: 700;
    color: #1e3a8a;
    width: 15%;
  }}
  .idx-title {{
    width: 67%;
    color: #334155;
  }}
  .idx-page {{
    width: 18%;
    font-weight: 700;
    color: #4f46e5;
    text-align: right;
  }}
  table.matrix {{
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0 12px 0;
    font-size: 8.2pt;
  }}
  table.matrix th {{
    background: #1e3a8a;
    color: #ffffff;
    padding: 6px 10px;
    text-align: left;
    font-weight: 700;
  }}
  table.matrix td {{
    padding: 5px 10px;
    border: 1px solid #e2e8f0;
  }}
  table.matrix tr:nth-child(even) {{
    background: #f8fafc;
  }}
  .verified {{
    color: #059669;
    font-weight: 700;
  }}
  .figure-card {{
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 12px;
    background: #ffffff;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  }}
  .figure-title {{
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
    padding: 6px 12px;
    font-weight: 700;
    color: #312e81;
    font-size: 9.5pt;
  }}
  .img-wrapper {{
    text-align: center;
    background: #090d16;
    padding: 3px 0;
  }}
  .img-wrapper img {{
    max-width: 100%;
    max-height: 250px;
    object-fit: contain;
    display: inline-block;
  }}
  .img-wrapper-compact img {{
    max-width: 100%;
    max-height: 200px;
    object-fit: contain;
    display: inline-block;
  }}
  .caption {{
    font-size: 7.8pt;
    color: #64748b;
    font-style: italic;
    text-align: center;
    padding: 3px 8px;
    background: #ffffff;
    border-bottom: 1px solid #f1f5f9;
  }}
  .explanation {{
    background: #fbfcfe;
    padding: 8px 12px;
    font-size: 8.5pt;
    color: #1e293b;
    line-height: 1.45;
  }}
  .explanation strong {{
    color: #1e3a8a;
  }}
  .footer-sign {{
    background: #eef2ff;
    border: 1.5px solid #c7d2fe;
    border-radius: 8px;
    padding: 10px 14px;
    margin-top: 14px;
    font-size: 8.5pt;
    color: #1e3a8a;
    line-height: 1.55;
  }}
  .footer-sign a {{
    color: #4338ca;
    text-decoration: underline;
    font-weight: 700;
  }}
  p {{
    margin: 0 0 8px 0;
  }}
  .page-indicator {{
    text-align: right;
    font-size: 8pt;
    color: #94a3b8;
    margin-top: auto;
    padding-top: 4px;
  }}
</style>
</head>
<body>

<!-- ========================================================================= -->
<!-- PAGE 1: COVER HEADER, METADATA, LINKS & REPORT INDEX                      -->
<!-- ========================================================================= -->
<div class="page">
  <h1>SECURE IOT DATA BACKUP SYSTEM</h1>
  <div class="subtitle">Cloud Computing Project Report & Comprehensive Technical Verification | Assignment 18</div>

  <div class="header-card">
    <div class="header-card-title">Academic Submission & Candidate Credentials</div>
    <table class="info-grid">
      <tr>
        <td><span class="lbl">Student Name:</span> <span class="val"><strong>Vasani Jeel</strong></span></td>
        <td><span class="lbl">Academic Program:</span> <span class="val">Bachelor of Computer Applications (BCA)</span></td>
      </tr>
      <tr>
        <td><span class="lbl">Registration Number:</span> <span class="val"><strong>24UG00241</strong></span></td>
        <td><span class="lbl">Evaluation Component:</span> <span class="val">Cloud Computing SA Evaluation (15 Marks)</span></td>
      </tr>
      <tr>
        <td><span class="lbl">Project Scope:</span> <span class="val">Secure Cloud Telemetry Vault</span></td>
        <td><span class="lbl">Cloud Infrastructure:</span> <span class="val">AWS EC2 Linux VM & Amazon S3 Object Storage</span></td>
      </tr>
    </table>
  </div>

  <div class="links-box">
    <div><strong>Live Cloud VM Web App:</strong> <br/><a href="http://3.25.136.151:5000/">http://3.25.136.151:5000/</a></div>
    <div><strong>Public DNS Endpoint:</strong> <br/><a href="http://ec2-3-25-136-151.ap-southeast-2.compute.amazonaws.com:5000/">ec2-3-25-136-151.ap-southeast-2...</a></div>
    <div><strong>GitHub Code Repository:</strong> <br/><a href="https://github.com/jeel190/Secure-IoT-Data-backup-System">github.com/jeel190/Secure-IoT-Data-backup-System</a></div>
    <div><strong>Target Cloud Resources:</strong> <br/><span>AWS EC2: i-05ce0744eaeecba10 | S3: iot-sensor-vault-jeel</span></div>
  </div>

  <h2>Table of Contents / Report Index</h2>
  <table class="index-table">
    <thead>
      <tr>
        <th style="width: 15%;">Section / Fig</th>
        <th style="width: 67%;">Deliverable Content & Architecture Verification</th>
        <th style="width: 18%; text-align: right;">Target Page</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="idx-num">Section 1</td>
        <td class="idx-title">Project Executive Overview & Technical Problem Statement</td>
        <td class="idx-page">Page 2</td>
      </tr>
      <tr>
        <td class="idx-num">Section 2</td>
        <td class="idx-title">Syllabus Compliance Matrix (9 Mandatory Tasks & Cloud Artifacts)</td>
        <td class="idx-page">Page 2</td>
      </tr>
      <tr>
        <td class="idx-num">Figure 1</td>
        <td class="idx-title">AWS EC2 Cloud Virtual Machine (VM) Specification & Active Running Status</td>
        <td class="idx-page">Page 3</td>
      </tr>
      <tr>
        <td class="idx-num">Figure 2</td>
        <td class="idx-title">Live IoT Backup Web Application Deployed on EC2 Public IP (Port 5000)</td>
        <td class="idx-page">Page 4</td>
      </tr>
      <tr>
        <td class="idx-num">Figure 3</td>
        <td class="idx-title">Daily IoT Sensor Telemetry Ingestion into Amazon S3 Bucket Vault</td>
        <td class="idx-page">Page 5</td>
      </tr>
      <tr>
        <td class="idx-num">Figure 4</td>
        <td class="idx-title">Storage Lifecycle Management Policy Configuration (S3 Multi-Tier Rules)</td>
        <td class="idx-page">Page 5</td>
      </tr>
      <tr>
        <td class="idx-num">Figure 5</td>
        <td class="idx-title">S3 Object Versioning Lineage & Point-in-Time Restore Operation Evidence</td>
        <td class="idx-page">Page 6</td>
      </tr>
      <tr>
        <td class="idx-num">Figure 6</td>
        <td class="idx-title">Principle of Least Privilege: Restrict Write Permissions IAM Policy</td>
        <td class="idx-page">Page 6</td>
      </tr>
      <tr>
        <td class="idx-num">Figure 7 & Sec 4</td>
        <td class="idx-title">BackupAdmin IAM Role Authority, Technical Conclusion & Official Sign-off</td>
        <td class="idx-page">Page 7</td>
      </tr>
    </tbody>
  </table>
  <div class="page-indicator">Page 1 of 7</div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 2: EXECUTIVE OVERVIEW & COMPLIANCE MATRIX                            -->
<!-- ========================================================================= -->
<div class="page">
  <h2>1. Project Executive Overview & Objectives</h2>
  <p>
    This project develops an enterprise-grade cloud backup and recovery solution tailored for high-frequency IoT sensor telemetry.
    Industrial IoT devices across environmental monitoring, power grids, wind turbines, and cleanroom HVAC plants generate daily logs
    that must be safely archived against accidental deletion, physical edge storage failures, and ransomware tampering.
  </p>
  <p>
    Using an AWS EC2 Cloud Virtual Machine (VM) running Linux (Ubuntu 24.04 LTS) and an Amazon S3 Object Storage Vault, the system implements:
    (1) continuous automated sensor file ingestion, (2) immutable point-in-time snapshot recovery using S3 Object Versioning,
    (3) cost-optimized storage tiering through S3 Lifecycle Rules, and (4) strict Role-Based Access Control (RBAC) enforcing the
    Principle of Least Privilege (PoLP) via custom AWS IAM policies.
  </p>

  <div style="height: 6px;"></div>

  <h2>2. Syllabus & Evaluation Requirements Compliance Matrix</h2>
  <p style="color: #64748b; font-size: 8.5pt; margin-bottom: 6px;">
    The implementation rigorously satisfies all mandatory course curriculum deliverables, cloud security tasks, and evaluation criteria:
  </p>

  <table class="matrix">
    <thead>
      <tr>
        <th style="width: 32%;">Requirement / Deliverable</th>
        <th style="width: 48%;">AWS Service / Architecture Artifact</th>
        <th style="width: 20%;">Verification Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Cloud Virtual Machine (VM)</strong></td>
        <td>AWS EC2 (i-05ce0744eaeecba10, t3.micro, Ubuntu 24.04 LTS)</td>
        <td class="verified">✔ Verified (Figure 1)</td>
      </tr>
      <tr>
        <td><strong>Live Web Application on VM</strong></td>
        <td>Python Flask Gateway listening on Public IP 3.25.136.151:5000</td>
        <td class="verified">✔ Verified (Figure 2)</td>
      </tr>
      <tr>
        <td><strong>Cloud Object Storage Vault</strong></td>
        <td>Amazon S3 (Bucket: iot-sensor-vault-jeel, Region: ap-southeast-2)</td>
        <td class="verified">✔ Fully Operational</td>
      </tr>
      <tr>
        <td><strong>Upload Daily Sensor Files</strong></td>
        <td>S3 Ingestion API supporting JSON and LoRaWAN AgroSense CSV files</td>
        <td class="verified">✔ Verified (Figure 3)</td>
      </tr>
      <tr>
        <td><strong>Storage Lifecycle Policy</strong></td>
        <td>S3 Lifecycle Configuration: Standard &rarr; Standard-IA (30d) &rarr; Glacier (90d)</td>
        <td class="verified">✔ Verified (Figure 4)</td>
      </tr>
      <tr>
        <td><strong>S3 Object Versioning Evidence</strong></td>
        <td>Bucket Versioning Enabled: immutable multi-version tracking per object</td>
        <td class="verified">✔ Verified (Figure 5)</td>
      </tr>
      <tr>
        <td><strong>Restore Operation Execution</strong></td>
        <td>Snapshot rollback promoting previous version as active after deletion</td>
        <td class="verified">✔ Verified (Figure 5)</td>
      </tr>
      <tr>
        <td><strong>Restrict Write to Sensors</strong></td>
        <td>IAM Policy: RestrictSensorWriteOnlyPolicy (Allow PutObject, Deny Delete)</td>
        <td class="verified">✔ Verified (Figure 6)</td>
      </tr>
      <tr>
        <td><strong>Create BackupAdmin Role</strong></td>
        <td>IAM Role: BackupAdminRole attached with AmazonS3FullAccess</td>
        <td class="verified">✔ Verified (Figure 7)</td>
      </tr>
      <tr>
        <td><strong>Block Public Access</strong></td>
        <td>Private S3 Vault: Block all public access enabled with signed HMAC access</td>
        <td class="verified">✔ S3 Properties</td>
      </tr>
    </tbody>
  </table>
  <div class="page-indicator">Page 2 of 7</div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 3: FIGURE 1 (AWS EC2 VM SPECIFICATION & RUNNING STATUS)              -->
<!-- ========================================================================= -->
<div class="page">
  <h2>3. System Verification Evidence & Focused Screenshot Analysis</h2>
  <p style="color: #64748b; font-size: 8.5pt; margin-bottom: 8px;">
    Each figure below presents authentic graphical verification captured directly from the live AWS cloud deployment, accompanied by detailed technical analysis.
  </p>

  <!-- FIGURE 1: AWS EC2 VM SPECIFICATION & RUNNING STATUS -->
  <div class="figure-card">
    <div class="figure-title">Figure 1: AWS EC2 Cloud Virtual Machine (VM) Specification & Active Running Status</div>
    <div class="img-wrapper"><img src="{img_vm}"/></div>
    <div class="caption">AWS EC2 Management Console: Instance summary for i-05ce0744eaeecba10 (Secure-IoT-Backup-VM) confirming 'Running' state</div>
    <div class="explanation">
      <strong>• Specific Evidence Explanation:</strong><br/>
      Figure 1 provides direct verification for the Cloud Virtual Machine (VM) resource requirement and active operational status.
      The AWS EC2 console details the complete architecture and deployment state for instance 'i-05ce0744eaeecba10' (Secure-IoT-Backup-VM):<br/>
      <strong>(1) Active Running Status:</strong> The instance state is actively confirmed as 'Running' (indicated by the green status indicator and 3/3 checks passed), proving that the cloud virtual machine is operational, healthy, and executing the background Python Flask ingestion gateway.<br/>
      <strong>(2) Virtual Machine Specifications:</strong> Provisioned on an AWS Free Tier 't3.micro' instance running 64-bit Linux (Ubuntu 24.04 LTS), providing a stable environment for continuous edge sensor ingestion.<br/>
      <strong>(3) Network Connectivity:</strong> Configured with Public IPv4 address '3.25.136.151' and Public DNS 'ec2-3-25-136-151.ap-southeast-2.compute.amazonaws.com' listening on port 5000, allowing direct access for live project demonstrations.<br/>
      <strong>(4) Attached Security Role:</strong> The instance profile is attached with 'BackupAdminRole', enabling the VM to securely interact with the Amazon S3 storage vault ('s3://iot-sensor-vault-jeel') via temporary STS credentials.
    </div>
  </div>
  <div class="page-indicator">Page 3 of 7</div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 4: FIGURE 2 (LIVE WEB APP UI ON VM)                                  -->
<!-- ========================================================================= -->
<div class="page">
  <!-- FIGURE 2: LIVE WEB APP UI ON VM -->
  <div class="figure-card">
    <div class="figure-title">Figure 2: Live IoT Backup Web Application Deployed on EC2 Public IP (Port 5000)</div>
    <div class="img-wrapper"><img src="{img_web}"/></div>
    <div class="caption">Live Browser Execution on http://3.25.136.151:5000: Operational dashboard with active IAM delete denial alert</div>
    <div class="explanation">
      <strong>• Specific Evidence Explanation:</strong><br/>
      Figure 2 illustrates the live execution of the IoT Backup Vault application served directly from the AWS EC2 Virtual Machine (3.25.136.151:5000):<br/>
      <strong>(1) System Online & Metric Telemetry:</strong> The top metric widgets verify active communication with the cloud storage vault: 13 daily backup files stored across 4 industrial streams, 42 immutable object versions tracked, and Private S3 Vault protection active with public access blocked.<br/>
      <strong>(2) Real-Time Least Privilege Enforcement:</strong> The toast alert in the bottom-right corner displays an active 'Unauthorized Delete Attempt' returning '403 Forbidden', verifying that the 'SensorWriteOnlyPolicy' successfully intercepted and denied an illegal 's3:DeleteObject' call on a telemetry file.<br/>
      <strong>(3) Role Switcher & Multi-Device Monitoring:</strong> Supports stream segregation (Environmental, Wind Turbine, Smart Grid, HVAC) under the active 'BackupAdmin' administrative session.
    </div>
  </div>
  <div class="page-indicator">Page 4 of 7</div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 5: FIGURE 3 (DATA UPLOAD) & FIGURE 4 (LIFECYCLE POLICY)              -->
<!-- ========================================================================= -->
<div class="page">
  <!-- FIGURE 3: DATA UPLOAD -->
  <div class="figure-card">
    <div class="figure-title">Figure 3: Successful Daily Sensor File Ingestion into S3 Bucket Vault</div>
    <div class="img-wrapper img-wrapper-compact"><img src="{img1}"/></div>
    <div class="caption">AWS S3 Upload Status: Ingestion of security_alerts.json into s3://iot-sensor-vault-jeel</div>
    <div class="explanation">
      <strong>• Specific Evidence Explanation:</strong><br/>
      Figure 3 provides direct evidence of the Daily Sensor File Upload feature (Deliverable 2).
      The AWS S3 console displays a confirmed upload status banner ('Upload succeeded') with a 100.00% success rate and zero failures.
      The telemetry package (security_alerts.json, size: 104.5 KB) is ingested into destination bucket 's3://iot-sensor-vault-jeel' with standard server-side encryption (SSE-S3 AES-256).
      This validates the cloud data pathway where local IoT sensor packages and operational logs are reliably dispatched and written to centralized cloud storage without data corruption.
    </div>
  </div>

  <!-- FIGURE 4: LIFECYCLE MANAGEMENT POLICY -->
  <div class="figure-card">
    <div class="figure-title">Figure 4: Storage Lifecycle Management Policy Configuration (S3 Multi-Tier Rules)</div>
    <div class="img-wrapper img-wrapper-compact"><img src="{img2}"/></div>
    <div class="caption">AWS S3 Lifecycle Configuration: Rule 'IoT-Sensor-Data-Lifecycle' active on entire bucket</div>
    <div class="explanation">
      <strong>• Specific Evidence Explanation:</strong><br/>
      Figure 4 illustrates the automated Storage Lifecycle Management Policy (Deliverable 5) configured under the bucket's Management tab.
      The rule named 'IoT-Sensor-Data-Lifecycle' is actively enabled for the entire bucket scope.
      It enforces automated storage optimization across the object lifecycle:
      <strong>(1) Standard (HOT):</strong> Recent sensor uploads reside in high-availability S3 Standard storage for real-time querying (Days 0-30).
      <strong>(2) Standard-IA (COOL):</strong> Telemetry objects older than 30 days automatically transition to S3 Standard-Infrequent Access, cutting storage expenses by over 40%.
      <strong>(3) Glacier Flexible Retrieval (ARCHIVE):</strong> After 90 days, historical logs transition to deep glacier storage for regulatory compliance.
      <strong>(4) Automated Deletion:</strong> Noncurrent versions are permanently expired after 365 days, preventing unbounded storage accumulation.
    </div>
  </div>
  <div class="page-indicator">Page 5 of 7</div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 6: FIGURE 5 (OBJECT VERSIONING & RESTORE) & FIGURE 6 (IAM POLICY)    -->
<!-- ========================================================================= -->
<div class="page">
  <!-- FIGURE 5: OBJECT VERSIONING & RESTORE OPERATION -->
  <div class="figure-card">
    <div class="figure-title">Figure 5: S3 Object Versioning Lineage & Point-in-Time Restore Operation Evidence</div>
    <div class="img-wrapper img-wrapper-compact"><img src="{img3}"/></div>
    <div class="caption">AWS S3 Objects View with 'Show versions' toggled ON showing historical snapshots and restore action</div>
    <div class="explanation">
      <strong>• Specific Evidence Explanation:</strong><br/>
      Figure 5 demonstrates S3 Object Versioning and the Restore Operation (Deliverables 2 & 4).
      With the 'Show versions' toggle active, the bucket lists two simultaneous, immutable versions of security_alerts.json:
      the latest version (Version ID: cXhoJihObcunFqAmy8oOB7WPpVZHIaQw, uploaded at 23:52:21) and the earlier version (Version ID: 2twtVLSbaBMYFtYKncU_8M6yQudgiGGQ, uploaded at 23:47:05).
      The green banner ('Successfully deleted objects') documents the point-in-time recovery action: when an unauthorized or corrupted latest version is deleted, Amazon S3 automatically promotes the previous historical snapshot back to the active state.
      This confirms non-destructive recovery, guaranteeing zero data loss.
    </div>
  </div>

  <!-- FIGURE 6: LEAST PRIVILEGE IAM POLICY -->
  <div class="figure-card">
    <div class="figure-title">Figure 6: Principle of Least Privilege: Restrict Write Permissions IAM Policy</div>
    <div class="img-wrapper img-wrapper-compact"><img src="{img4}"/></div>
    <div class="caption">AWS IAM Policy Summary: RestrictSensorWriteOnlyPolicy showing Allow PutObject and Deny DeleteObject</div>
    <div class="explanation">
      <strong>• Specific Evidence Explanation:</strong><br/>
      Figure 6 provides verification for Security Task 2: 'Restrict write permissions to sensor applications' (Deliverable 6).
      The custom policy 'RestrictSensorWriteOnlyPolicy' defines two explicit security boundaries:
      <strong>(1) Limited Write Allow:</strong> Permits automated sensor applications to invoke 's3:PutObject' strictly on the resource path 'sensors/*' within 'iot-sensor-vault-jeel', allowing daily telemetry ingestion.
      <strong>(2) Explicit Deny:</strong> Forbids 's3:DeleteObject' and 's3:DeleteObjectVersion' across the entire bucket resource.
      Under AWS IAM evaluation logic, an explicit Deny unconditionally overrides any Allow, preventing edge sensor nodes from overwriting historical archives or executing malicious deletion commands.
    </div>
  </div>
  <div class="page-indicator">Page 6 of 7</div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 7: FIGURE 7 (BACKUPADMIN ROLE), CONCLUSION & SUBMISSION SIGN-OFF     -->
<!-- ========================================================================= -->
<div class="page">
  <!-- FIGURE 7: BACKUPADMIN ROLE CONFIGURATION -->
  <div class="figure-card">
    <div class="figure-title">Figure 7: BackupAdmin IAM Role Configuration & Full Administrative Authority</div>
    <div class="img-wrapper img-wrapper-compact"><img src="{img5}"/></div>
    <div class="caption">AWS IAM Role Creation Screen: BackupAdminRole with AmazonS3FullAccess policy attached</div>
    <div class="explanation">
      <strong>• Specific Evidence Explanation:</strong><br/>
      Figure 7 verifies Security Task 1: 'Create BackupAdmin role' (Deliverable 3).
      The IAM role named 'BackupAdminRole' is configured with an EC2 service trust policy ('ec2.amazonaws.com'),
      enabling the cloud virtual machine hosting the backup gateway to assume credentials securely via the AWS metadata service.
      Attached with the managed policy 'AmazonS3FullAccess', the BackupAdmin role possesses elevated privileges required for disaster recovery operations:
      executing point-in-time snapshot rollbacks, managing bucket encryption keys (SSE-KMS), auditing CloudTrail access events, and maintaining bucket lifecycle automation policies.
    </div>
  </div>

  <h2>4. Technical Summary & Architectural Conclusion</h2>
  <p>
    The Secure IoT Data Backup System successfully bridges cloud infrastructure, edge computing reliability, and information security.
    By deploying on an AWS EC2 virtual machine and enforcing Amazon S3 Object Versioning, the platform provides immutable defense against data loss.
    By structuring granular IAM policies, the Principle of Least Privilege is rigidly upheld between administrative operators and field IoT devices.
    Finally, the implementation of automated storage lifecycle rules guarantees that enterprise telemetry archives remain compliant and cost-effective over long retention horizons.
    All evaluation deliverables assigned by the course curriculum have been constructed, validated on live AWS cloud resources, and verified.
  </p>

  <div class="footer-sign">
    <strong>Submitted by:</strong> Vasani Jeel (Reg. No: 24UG00241) | Bachelor of Computer Applications (BCA)<br/>
    <strong>Course:</strong> Cloud Computing - SA Evaluation (15 Marks) | <strong>Assignment 18:</strong> Secure IoT Data Backup System<br/>
    <strong>Live Cloud Project URL:</strong> <a href="http://3.25.136.151:5000/">http://3.25.136.151:5000/</a> (AWS EC2 i-05ce0744eaeecba10, t3.micro, State: Running)<br/>
    <strong>GitHub Code Repository:</strong> <a href="https://github.com/jeel190/Secure-IoT-Data-backup-System">https://github.com/jeel190/Secure-IoT-Data-backup-System</a> | <strong>S3 Vault:</strong> s3://iot-sensor-vault-jeel
  </div>
  <div class="page-indicator">Page 7 of 7</div>
</div>

</body>
</html>
"""

temp_html = r"D:\Gen Ai\Secure-IoT-Data-Backup-System\report_temp.html"
with open(temp_html, "w", encoding="utf-8") as f:
    f.write(html_content)

pdf_out = r"C:\Users\dell\Downloads\Secure_IoT_Data_Backup_Report_Vasani_Jeel.pdf"
edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

cmd = [
    edge_exe,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    "--run-all-compositor-stages-before-draw",
    f"--print-to-pdf={pdf_out}",
    temp_html
]

print("[*] Running Edge to export clean 7-page PDF...")
res = subprocess.run(cmd, capture_output=True, text=True)
if os.path.exists(pdf_out):
    print(f"[+] PDF generated successfully at: {pdf_out} (Size: {os.path.getsize(pdf_out)} bytes)")
else:
    print(f"[-] Failed to generate PDF: {res.stderr}")
