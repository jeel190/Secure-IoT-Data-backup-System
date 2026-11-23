import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def create_report():
    doc = docx.Document()

    # Set standard clean margins (0.7 in all sides for optimal page balance)
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    # Cohesive Color Palette
    COLOR_PRIMARY = RGBColor(30, 58, 138)     # Deep Navy (#1E3A8A)
    COLOR_SECONDARY = RGBColor(79, 70, 229)  # Indigo (#4F46E5)
    COLOR_TEXT = RGBColor(30, 41, 59)        # Slate 800 (#1E293B)
    COLOR_MUTED = RGBColor(100, 116, 139)    # Slate 500 (#64748B)
    COLOR_SUCCESS = RGBColor(5, 150, 105)    # Emerald 600 (#059669)

    def set_cell_shading(cell, color_hex):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
        tcPr.append(shd)

    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'''
            <w:tcMar {nsdecls("w")}>
                <w:top w:w="{top}" w:type="dxa"/>
                <w:bottom w:w="{bottom}" w:type="dxa"/>
                <w:left w:w="{left}" w:type="dxa"/>
                <w:right w:w="{right}" w:type="dxa"/>
            </w:tcMar>
        ''')
        tcPr.append(tcMar)

    def add_section_header(title_text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title_text)
        run.font.name = "Arial"
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY

    # =========================================================================
    # PAGE 1: COVER / EXECUTIVE HEADER, METADATA, LINKS & INDEX (TABLE OF CONTENTS)
    # =========================================================================

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(3)
    run_title = p_title.add_run("SECURE IOT DATA BACKUP SYSTEM")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(21)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_PRIMARY

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(10)
    run_sub = p_sub.add_run("Cloud Computing Project Report & Comprehensive Technical Verification | Assignment 18")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(10.5)
    run_sub.font.color.rgb = COLOR_MUTED

    # Student & Project Information Card (Table)
    info_table = doc.add_table(rows=3, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_table.autofit = False

    rows_data = [
        ("Student Name:", "Vasani Jeel", "Academic Program:", "Bachelor of Computer Applications (BCA)"),
        ("Registration Number:", "24UG00241", "Course Evaluation:", "Cloud Computing SA Evaluation (15 Marks)"),
        ("Project Scope:", "Secure Cloud Telemetry Vault", "Cloud Infrastructure:", "AWS EC2 Linux VM & Amazon S3 Object Storage")
    ]

    for i, (k1, v1, k2, v2) in enumerate(rows_data):
        row = info_table.rows[i]
        
        # Left cell
        c1 = row.cells[0]
        c1.width = Inches(3.5)
        set_cell_shading(c1, "F8FAFC" if i % 2 == 0 else "FFFFFF")
        set_cell_margins(c1, top=70, bottom=70, left=120, right=120)
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1_lbl = p1.add_run(k1 + " ")
        r1_lbl.bold = True
        r1_lbl.font.size = Pt(9.5)
        r1_lbl.font.color.rgb = COLOR_PRIMARY
        r1_val = p1.add_run(v1)
        r1_val.font.size = Pt(9.5)
        r1_val.font.color.rgb = COLOR_TEXT

        # Right cell
        c2 = row.cells[1]
        c2.width = Inches(3.5)
        set_cell_shading(c2, "F8FAFC" if i % 2 == 0 else "FFFFFF")
        set_cell_margins(c2, top=70, bottom=70, left=120, right=120)
        p2 = c2.paragraphs[0]
        p2.paragraph_format.space_after = Pt(0)
        r2_lbl = p2.add_run(k2 + " ")
        r2_lbl.bold = True
        r2_lbl.font.size = Pt(9.5)
        r2_lbl.font.color.rgb = COLOR_PRIMARY
        r2_val = p2.add_run(v2)
        r2_val.font.size = Pt(9.5)
        r2_val.font.color.rgb = COLOR_TEXT

    # Spacing between tables
    p_sp1 = doc.add_paragraph()
    p_sp1.paragraph_format.space_before = Pt(6)
    p_sp1.paragraph_format.space_after = Pt(4)

    # Cloud Deployment & Verification Links Banner Card
    link_table = doc.add_table(rows=2, cols=2)
    link_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    link_table.autofit = False

    link_data = [
        ("Live Cloud VM Web App:", "http://3.25.136.151:5000/"),
        ("Public DNS Endpoint:", "http://ec2-3-25-136-151.ap-southeast-2.compute.amazonaws.com:5000/"),
        ("GitHub Code Repository:", "https://github.com/jeel190/Secure-IoT-Data-backup-System"),
        ("Cloud Infrastructure:", "AWS EC2 VM: i-05ce0744eaeecba10 | S3 Vault: iot-sensor-vault-jeel")
    ]

    for idx, (label, val) in enumerate(link_data):
        r_idx = idx // 2
        c_idx = idx % 2
        cell = link_table.rows[r_idx].cells[c_idx]
        cell.width = Inches(3.5)
        set_cell_shading(cell, "EEF2FF")
        set_cell_margins(cell, top=70, bottom=70, left=110, right=110)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r_l = p.add_run(label + " ")
        r_l.bold = True
        r_l.font.size = Pt(8.5)
        r_l.font.color.rgb = COLOR_PRIMARY
        r_v = p.add_run(val)
        r_v.font.size = Pt(8.5)
        r_v.font.color.rgb = COLOR_SECONDARY
        if "http" in val:
            r_v.underline = True

    # Spacing
    p_sp2 = doc.add_paragraph()
    p_sp2.paragraph_format.space_before = Pt(6)
    p_sp2.paragraph_format.space_after = Pt(4)

    # TABLE OF CONTENTS / INDEX TABLE
    add_section_header("Table of Contents / Report Index")
    
    index_table = doc.add_table(rows=10, cols=3)
    index_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    index_table.autofit = False

    index_headers = ["Sec / Fig", "Topic / Deliverable Content", "Verification Target / Page"]
    hdr_row = index_table.rows[0]
    for j, h_text in enumerate(index_headers):
        c = hdr_row.cells[j]
        c.width = Inches(1.1) if j == 0 else (Inches(4.3) if j == 1 else Inches(1.6))
        set_cell_shading(c, "1E3A8A")
        set_cell_margins(c, top=70, bottom=70, left=90, right=90)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    index_items = [
        ("Section 1 & 2", "Project Overview & Syllabus Compliance Matrix (9 Cloud Deliverables)", "Page 2"),
        ("Figure 1", "AWS EC2 Cloud Virtual Machine (VM) Specification & Active Running Status", "Page 3"),
        ("Figure 2", "Live IoT Backup Web Application Deployed on EC2 Public IP (Port 5000)", "Page 4"),
        ("Figure 3 & 4", "Daily S3 Sensor File Ingestion & Storage Lifecycle Management Policy", "Page 5"),
        ("Figure 5 & 6", "S3 Object Versioning Lineage & Restrict Write Permissions IAM Policy", "Page 6"),
        ("Figure 7", "Role-Based Access Control (RBAC) & Least Privilege Enforcement Matrix", "Page 7"),
        ("Figure 8", "BackupAdmin IAM Role Configuration & Full Administrative Authority", "Page 8"),
        ("Section 4 & 5", "Technical Summary, Architectural Conclusion & Official Sign-off Card", "Page 8")
    ]

    for idx, (col0, col1, col2) in enumerate(index_items, 1):
        row = index_table.rows[idx]
        for col_idx, text_val in enumerate([col0, col1, col2]):
            c = row.cells[col_idx]
            c.width = Inches(1.1) if col_idx == 0 else (Inches(4.3) if col_idx == 1 else Inches(1.6))
            set_cell_shading(c, "F8FAFC" if idx % 2 == 1 else "FFFFFF")
            set_cell_margins(c, top=55, bottom=55, left=90, right=90)
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text_val)
            r.font.size = Pt(8.5)
            r.font.color.rgb = COLOR_TEXT
            if col_idx == 0:
                r.bold = True
                r.font.color.rgb = COLOR_PRIMARY
            elif col_idx == 2:
                r.bold = True
                r.font.color.rgb = COLOR_SECONDARY

    doc.add_page_break()

    # =========================================================================
    # PAGE 2: EXECUTIVE OVERVIEW & COMPLIANCE MATRIX
    # =========================================================================
    add_section_header("1. Project Executive Overview & Objectives")
    p_exec = doc.add_paragraph()
    p_exec.paragraph_format.space_before = Pt(4)
    p_exec.paragraph_format.space_after = Pt(8)
    p_exec.paragraph_format.line_spacing = 1.2
    run_exec = p_exec.add_run(
        "This project develops an enterprise-grade cloud backup and recovery solution tailored for high-frequency IoT sensor telemetry. "
        "Industrial IoT devices across environmental monitoring, power grids, wind turbines, and cleanroom HVAC plants generate daily logs "
        "that must be safely archived against accidental deletion, physical edge storage failures, and ransomware tampering.\n\n"
        "Using an AWS EC2 Cloud Virtual Machine (VM) running Linux (Ubuntu 24.04 LTS) and an Amazon S3 Object Storage Vault, the system implements: "
        "(1) continuous automated sensor file ingestion, (2) immutable point-in-time snapshot recovery using S3 Object Versioning, "
        "(3) cost-optimized storage tiering through S3 Lifecycle Rules, and (4) strict Role-Based Access Control (RBAC) enforcing the "
        "Principle of Least Privilege (PoLP) via custom AWS IAM policies."
    )
    run_exec.font.size = Pt(10)
    run_exec.font.color.rgb = COLOR_TEXT

    p_sp3 = doc.add_paragraph()
    p_sp3.paragraph_format.space_before = Pt(6)
    p_sp3.paragraph_format.space_after = Pt(6)

    add_section_header("2. Syllabus & Evaluation Requirements Compliance Matrix")
    p_comp = doc.add_paragraph()
    p_comp.paragraph_format.space_after = Pt(6)
    p_comp.paragraph_format.line_spacing = 1.15
    run_comp = p_comp.add_run(
        "The project rigorously fulfills all mandatory course curriculum deliverables, cloud security tasks, and evaluation criteria:"
    )
    run_comp.font.size = Pt(10)
    run_comp.font.color.rgb = COLOR_TEXT

    matrix_table = doc.add_table(rows=12, cols=3)
    matrix_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    matrix_table.autofit = False

    matrix_headers = ["Requirement / Deliverable", "AWS Service / Architecture Artifact", "Verification Status"]
    hdr_row = matrix_table.rows[0]
    for j, h_text in enumerate(matrix_headers):
        c = hdr_row.cells[j]
        c.width = Inches(2.3) if j < 2 else Inches(2.4)
        set_cell_shading(c, "1E3A8A")
        set_cell_margins(c, top=75, bottom=75, left=100, right=100)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    matrix_rows = [
        ("Cloud Virtual Machine (VM)", "AWS EC2 (i-05ce0744eaeecba10, t3.micro, State: Running)", "Verified (Figure 1)"),
        ("Live Web Application on VM", "Python Flask Gateway listening on Public IP 3.25.136.151:5000", "Verified (Figure 2)"),
        ("Cloud Object Storage Vault", "Amazon S3 (Bucket: iot-sensor-vault-jeel, Region: ap-southeast-2)", "Fully Operational"),
        ("Upload Daily Sensor Files", "S3 Ingestion API supporting JSON and LoRaWAN AgroSense CSV files", "Verified (Figure 3)"),
        ("Storage Lifecycle Policy", "S3 Lifecycle Configuration: Standard -> Standard-IA (30d) -> Glacier (90d)", "Verified (Figure 4)"),
        ("S3 Object Versioning Evidence", "Bucket Versioning Enabled: immutable multi-version tracking per object", "Verified (Figure 5)"),
        ("Restore Operation Execution", "Snapshot rollback promoting previous version as active after deletion", "Verified (Figure 5)"),
        ("Restrict Write to Sensors", "IAM Policy: RestrictSensorWriteOnlyPolicy (Allow PutObject, Deny Delete)", "Verified (Figure 6)"),
        ("RBAC Access Control Matrix", "Application Security Center: Multi-role permission matrix with delete block", "Verified (Figure 7)"),
        ("Create BackupAdmin Role", "IAM Role: BackupAdminRole attached with AmazonS3FullAccess", "Verified (Figure 8)"),
        ("Block Public Access", "Private S3 Vault: Block all public access enabled with signed HMAC access", "Verified (S3 Properties)")
    ]

    for idx, (req, art, stat) in enumerate(matrix_rows, 1):
        row = matrix_table.rows[idx]
        for col_idx, text_val in enumerate([req, art, stat]):
            c = row.cells[col_idx]
            c.width = Inches(2.3) if col_idx < 2 else Inches(2.4)
            set_cell_shading(c, "F8FAFC" if idx % 2 == 1 else "FFFFFF")
            set_cell_margins(c, top=55, bottom=55, left=100, right=100)
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text_val)
            r.font.size = Pt(8.5)
            r.font.color.rgb = COLOR_TEXT
            if col_idx == 2:
                r.bold = True
                r.font.color.rgb = COLOR_SUCCESS

    doc.add_page_break()

    # =========================================================================
    # PAGE 3: FIGURE 1 (AWS EC2 VM SPECIFICATION & RUNNING STATUS)
    # =========================================================================
    add_section_header("3. System Verification Evidence & Focused Screenshot Analysis")
    p_sec3 = doc.add_paragraph()
    p_sec3.paragraph_format.space_before = Pt(2)
    p_sec3.paragraph_format.space_after = Pt(8)
    p_sec3.paragraph_format.line_spacing = 1.15
    r_sec3 = p_sec3.add_run(
        "Each section below provides the direct graphical evidence captured from the live AWS cloud deployment, "
        "accompanied by detailed technical analysis verifying the active operational state of all cloud resources."
    )
    r_sec3.font.size = Pt(9.5)
    r_sec3.font.color.rgb = COLOR_MUTED

    img_dir = r"C:/Users/dell/.gemini/antigravity/brain/0bddacab-2752-4390-9234-c31f912ae85e/.user_uploaded"

    # --- FIGURE 1: AWS EC2 VM SPECIFICATION & RUNNING STATUS ---
    p_f1 = doc.add_paragraph()
    p_f1.paragraph_format.space_before = Pt(8)
    p_f1.paragraph_format.space_after = Pt(3)
    p_f1.paragraph_format.keep_with_next = True
    r_f1_title = p_f1.add_run("Figure 1: AWS EC2 Cloud Virtual Machine (VM) Specification & Active Running Status")
    r_f1_title.bold = True
    r_f1_title.font.size = Pt(11)
    r_f1_title.font.color.rgb = COLOR_SECONDARY

    img_vm_path = r"D:\Gen Ai\Secure-IoT-Data-Backup-System\vm_screenshot_fresh.png"
    if os.path.exists(img_vm_path):
        doc.add_picture(img_vm_path, width=Inches(6.5))
        p_cap1 = doc.add_paragraph()
        p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap1.paragraph_format.space_before = Pt(3)
        p_cap1.paragraph_format.space_after = Pt(6)
        r_cap1 = p_cap1.add_run("AWS EC2 Management Console: Instance summary for i-05ce0744eaeecba10 (Secure-IoT-Backup-VM) confirming 'Running' state")
        r_cap1.font.size = Pt(8.5)
        r_cap1.font.italic = True
        r_cap1.font.color.rgb = COLOR_MUTED

    p_f1_desc = doc.add_paragraph()
    p_f1_desc.paragraph_format.space_before = Pt(4)
    p_f1_desc.paragraph_format.space_after = Pt(12)
    p_f1_desc.paragraph_format.line_spacing = 1.25
    p_f1_desc.add_run(
        "• Specific Evidence Explanation:\n"
        "Figure 1 provides direct verification for the Cloud Virtual Machine (VM) resource requirement and active operational status. "
        "The AWS EC2 console details the complete architecture and deployment state for instance 'i-05ce0744eaeecba10' (Secure-IoT-Backup-VM):\n"
        "(1) Active Running Status: The instance state is actively confirmed as 'Running' (indicated by the green status indicator and 3/3 checks passed), proving that the cloud virtual machine is operational, healthy, and executing the background Python Flask ingestion gateway.\n"
        "(2) Virtual Machine Specifications: Provisioned on an AWS Free Tier 't3.micro' instance running 64-bit Linux (Ubuntu 24.04 LTS), providing a stable environment for continuous edge sensor ingestion.\n"
        "(3) Network Connectivity: Configured with Public IPv4 address '3.25.136.151' and Public DNS 'ec2-3-25-136-151.ap-southeast-2.compute.amazonaws.com' listening on port 5000, allowing direct access for live project demonstrations.\n"
        "(4) Attached Security Role: The instance profile is attached with 'BackupAdminRole', enabling the VM to securely interact with the Amazon S3 storage vault ('s3://iot-sensor-vault-jeel') via temporary STS credentials."
    ).font.size = Pt(9.5)

    doc.add_page_break()

    # =========================================================================
    # PAGE 4: FIGURE 2 (LIVE WEB APP UI ON VM)
    # =========================================================================
    p_f2_live = doc.add_paragraph()
    p_f2_live.paragraph_format.space_before = Pt(8)
    p_f2_live.paragraph_format.space_after = Pt(3)
    p_f2_live.paragraph_format.keep_with_next = True
    r_f2_live_title = p_f2_live.add_run("Figure 2: Live IoT Backup Web Application Deployed on EC2 Public IP (Port 5000)")
    r_f2_live_title.bold = True
    r_f2_live_title.font.size = Pt(11)
    r_f2_live_title.font.color.rgb = COLOR_SECONDARY

    img_web_path = r"D:\Gen Ai\Secure-IoT-Data-Backup-System\webapp_screenshot_live.png"
    if os.path.exists(img_web_path):
        doc.add_picture(img_web_path, width=Inches(6.5))
        p_cap2 = doc.add_paragraph()
        p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap2.paragraph_format.space_before = Pt(3)
        p_cap2.paragraph_format.space_after = Pt(6)
        r_cap2 = p_cap2.add_run("Live Browser Execution on http://3.25.136.151:5000: Operational dashboard with active IAM delete denial alert")
        r_cap2.font.size = Pt(8.5)
        r_cap2.font.italic = True
        r_cap2.font.color.rgb = COLOR_MUTED

    p_f2_live_desc = doc.add_paragraph()
    p_f2_live_desc.paragraph_format.space_before = Pt(4)
    p_f2_live_desc.paragraph_format.space_after = Pt(12)
    p_f2_live_desc.paragraph_format.line_spacing = 1.25
    p_f2_live_desc.add_run(
        "• Specific Evidence Explanation:\n"
        "Figure 2 illustrates the live execution of the IoT Backup Vault application served directly from the AWS EC2 Virtual Machine (3.25.136.151:5000):\n"
        "(1) System Online & Metric Telemetry: The top metric widgets verify active communication with the cloud storage vault: 13 daily backup files stored across 4 industrial streams, 42 immutable object versions tracked, and Private S3 Vault protection active with public access blocked.\n"
        "(2) Real-Time Least Privilege Enforcement: The toast alert in the bottom-right corner displays an active 'Unauthorized Delete Attempt' returning '403 Forbidden', verifying that the 'SensorWriteOnlyPolicy' successfully intercepted and denied an illegal 's3:DeleteObject' call on a telemetry file.\n"
        "(3) Role Switcher & Multi-Device Monitoring: Supports stream segregation (Environmental, Wind Turbine, Smart Grid, HVAC) under the active 'BackupAdmin' administrative session."
    ).font.size = Pt(9.5)

    doc.add_page_break()

    # =========================================================================
    # PAGE 5: FIGURE 3 (DATA UPLOAD) & FIGURE 4 (LIFECYCLE POLICY)
    # =========================================================================

    # --- FIGURE 3: DATA UPLOAD ---
    p_f3 = doc.add_paragraph()
    p_f3.paragraph_format.space_before = Pt(4)
    p_f3.paragraph_format.space_after = Pt(2)
    p_f3.paragraph_format.keep_with_next = True
    r_f3_title = p_f3.add_run("Figure 3: Successful Daily Sensor File Ingestion into S3 Bucket Vault")
    r_f3_title.bold = True
    r_f3_title.font.size = Pt(10)
    r_f3_title.font.color.rgb = COLOR_SECONDARY

    img1_path = os.path.join(img_dir, "media_1795373189475_d5922d62.png")
    if os.path.exists(img1_path):
        doc.add_picture(img1_path, width=Inches(6.4))
        p_cap3 = doc.add_paragraph()
        p_cap3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap3.paragraph_format.space_before = Pt(2)
        p_cap3.paragraph_format.space_after = Pt(3)
        r_cap3 = p_cap3.add_run("AWS S3 Upload Status: Ingestion of security_alerts.json into s3://iot-sensor-vault-jeel")
        r_cap3.font.size = Pt(8)
        r_cap3.font.italic = True
        r_cap3.font.color.rgb = COLOR_MUTED

    p_f3_desc = doc.add_paragraph()
    p_f3_desc.paragraph_format.space_before = Pt(2)
    p_f3_desc.paragraph_format.space_after = Pt(10)
    p_f3_desc.paragraph_format.line_spacing = 1.15
    p_f3_desc.add_run(
        "• Specific Evidence Explanation:\n"
        "Figure 3 provides direct evidence of the Daily Sensor File Upload feature (Deliverable 2). "
        "The AWS S3 console displays a confirmed upload status banner ('Upload succeeded') with a 100.00% success rate "
        "and zero failures. The telemetry package (security_alerts.json, size: 104.5 KB) is ingested into destination bucket "
        "'s3://iot-sensor-vault-jeel' with standard server-side encryption (SSE-S3 AES-256). "
        "This validates the cloud data pathway where local IoT sensor packages and operational logs are reliably dispatched "
        "and written to centralized cloud storage without data corruption."
    ).font.size = Pt(8.5)

    # --- FIGURE 4: LIFECYCLE MANAGEMENT POLICY ---
    p_f4 = doc.add_paragraph()
    p_f4.paragraph_format.space_before = Pt(6)
    p_f4.paragraph_format.space_after = Pt(2)
    p_f4.paragraph_format.keep_with_next = True
    r_f4_title = p_f4.add_run("Figure 4: Storage Lifecycle Management Policy Configuration (S3 Multi-Tier Rules)")
    r_f4_title.bold = True
    r_f4_title.font.size = Pt(10)
    r_f4_title.font.color.rgb = COLOR_SECONDARY

    img2_path = os.path.join(img_dir, "media_1795373189479_c7fd30a9.png")
    if os.path.exists(img2_path):
        doc.add_picture(img2_path, width=Inches(6.4))
        p_cap4 = doc.add_paragraph()
        p_cap4.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap4.paragraph_format.space_before = Pt(2)
        p_cap4.paragraph_format.space_after = Pt(3)
        r_cap4 = p_cap4.add_run("AWS S3 Lifecycle Configuration: Rule 'IoT-Sensor-Data-Lifecycle' active on entire bucket")
        r_cap4.font.size = Pt(8)
        r_cap4.font.italic = True
        r_cap4.font.color.rgb = COLOR_MUTED

    p_f4_desc = doc.add_paragraph()
    p_f4_desc.paragraph_format.space_before = Pt(2)
    p_f4_desc.paragraph_format.space_after = Pt(8)
    p_f4_desc.paragraph_format.line_spacing = 1.15
    p_f4_desc.add_run(
        "• Specific Evidence Explanation:\n"
        "Figure 4 illustrates the automated Storage Lifecycle Management Policy (Deliverable 5) configured under the bucket's Management tab. "
        "The rule named 'IoT-Sensor-Data-Lifecycle' is actively enabled for the entire bucket scope. "
        "It enforces automated storage optimization across the object lifecycle: "
        "(1) Standard (HOT): Recent sensor uploads reside in high-availability S3 Standard storage for real-time querying (Days 0-30). "
        "(2) Standard-IA (COOL): Telemetry objects older than 30 days automatically transition to S3 Standard-Infrequent Access, cutting storage expenses by over 40%. "
        "(3) Glacier Flexible Retrieval (ARCHIVE): After 90 days, historical logs transition to deep glacier storage for regulatory compliance. "
        "(4) Automated Deletion: Noncurrent versions are permanently expired after 365 days, preventing unbounded storage accumulation."
    ).font.size = Pt(8.5)

    doc.add_page_break()

    # =========================================================================
    # PAGE 6: FIGURE 5 (OBJECT VERSIONING & RESTORE) & FIGURE 6 (IAM LEAST PRIVILEGE)
    # =========================================================================

    # --- FIGURE 5: OBJECT VERSIONING & RESTORE OPERATION ---
    p_f5 = doc.add_paragraph()
    p_f5.paragraph_format.space_before = Pt(4)
    p_f5.paragraph_format.space_after = Pt(2)
    p_f5.paragraph_format.keep_with_next = True
    r_f5_title = p_f5.add_run("Figure 5: S3 Object Versioning Lineage & Point-in-Time Restore Operation Evidence")
    r_f5_title.bold = True
    r_f5_title.font.size = Pt(10)
    r_f5_title.font.color.rgb = COLOR_SECONDARY

    img3_path = os.path.join(img_dir, "media_1795373189483_ca56fabe.png")
    if os.path.exists(img3_path):
        doc.add_picture(img3_path, width=Inches(6.4))
        p_cap5 = doc.add_paragraph()
        p_cap5.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap5.paragraph_format.space_before = Pt(2)
        p_cap5.paragraph_format.space_after = Pt(3)
        r_cap5 = p_cap5.add_run("AWS S3 Objects View with 'Show versions' toggled ON showing historical snapshots and restore action")
        r_cap5.font.size = Pt(8)
        r_cap5.font.italic = True
        r_cap5.font.color.rgb = COLOR_MUTED

    p_f5_desc = doc.add_paragraph()
    p_f5_desc.paragraph_format.space_before = Pt(2)
    p_f5_desc.paragraph_format.space_after = Pt(10)
    p_f5_desc.paragraph_format.line_spacing = 1.15
    p_f5_desc.add_run(
        "• Specific Evidence Explanation:\n"
        "Figure 5 demonstrates S3 Object Versioning and the Restore Operation (Deliverables 2 & 4). "
        "With the 'Show versions' toggle active, the bucket lists two simultaneous, immutable versions of security_alerts.json: "
        "the latest version (Version ID: cXhoJihObcunFqAmy8oOB7WPpVZHIaQw, uploaded at 23:52:21) and the earlier version "
        "(Version ID: 2twtVLSbaBMYFtYKncU_8M6yQudgiGGQ, uploaded at 23:47:05). "
        "The green banner ('Successfully deleted objects') documents the point-in-time recovery action: "
        "when an unauthorized or corrupted latest version is deleted, Amazon S3 automatically promotes the previous historical "
        "snapshot back to the active state. This confirms non-destructive recovery, guaranteeing zero data loss."
    ).font.size = Pt(8.5)

    # --- FIGURE 6: LEAST PRIVILEGE IAM POLICY ---
    p_f6 = doc.add_paragraph()
    p_f6.paragraph_format.space_before = Pt(6)
    p_f6.paragraph_format.space_after = Pt(2)
    p_f6.paragraph_format.keep_with_next = True
    r_f6_title = p_f6.add_run("Figure 6: Principle of Least Privilege: Restrict Write Permissions IAM Policy")
    r_f6_title.bold = True
    r_f6_title.font.size = Pt(10)
    r_f6_title.font.color.rgb = COLOR_SECONDARY

    img4_path = os.path.join(img_dir, "media_1795373189487_38f691cc.png")
    if os.path.exists(img4_path):
        doc.add_picture(img4_path, width=Inches(6.4))
        p_cap6 = doc.add_paragraph()
        p_cap6.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap6.paragraph_format.space_before = Pt(2)
        p_cap6.paragraph_format.space_after = Pt(3)
        r_cap6 = p_cap6.add_run("AWS IAM Policy Summary: RestrictSensorWriteOnlyPolicy showing Allow PutObject and Deny DeleteObject")
        r_cap6.font.size = Pt(8)
        r_cap6.font.italic = True
        r_cap6.font.color.rgb = COLOR_MUTED

    p_f6_desc = doc.add_paragraph()
    p_f6_desc.paragraph_format.space_before = Pt(2)
    p_f6_desc.paragraph_format.space_after = Pt(8)
    p_f6_desc.paragraph_format.line_spacing = 1.15
    p_f6_desc.add_run(
        "• Specific Evidence Explanation:\n"
        "Figure 6 provides verification for Security Task 2: 'Restrict write permissions to sensor applications' (Deliverable 6). "
        "The custom policy 'RestrictSensorWriteOnlyPolicy' defines two explicit security boundaries: "
        "(1) Limited Write Allow: Permits automated sensor applications to invoke 's3:PutObject' strictly on the resource path 'sensors/*' "
        "within 'iot-sensor-vault-jeel', allowing daily telemetry ingestion. "
        "(2) Explicit Deny: Forbids 's3:DeleteObject' and 's3:DeleteObjectVersion' across the entire bucket resource. "
        "Under AWS IAM evaluation logic, an explicit Deny unconditionally overrides any Allow, preventing edge sensor nodes from "
        "overwriting historical archives or executing malicious deletion commands."
    ).font.size = Pt(8.5)

    doc.add_page_break()

    # =========================================================================
    # PAGE 7: FIGURE 7 (RBAC MODAL ACCESS CONTROL MATRIX)
    # =========================================================================
    p_f7 = doc.add_paragraph()
    p_f7.paragraph_format.space_before = Pt(8)
    p_f7.paragraph_format.space_after = Pt(3)
    p_f7.paragraph_format.keep_with_next = True
    r_f7_title = p_f7.add_run("Figure 7: Role-Based Access Control (RBAC) & Least Privilege Enforcement Matrix")
    r_f7_title.bold = True
    r_f7_title.font.size = Pt(11)
    r_f7_title.font.color.rgb = COLOR_SECONDARY

    img_rbac_path = r"D:\Gen Ai\Secure-IoT-Data-Backup-System\rbac_modal_screenshot.png"
    if os.path.exists(img_rbac_path):
        doc.add_picture(img_rbac_path, width=Inches(6.5))
        p_cap7 = doc.add_paragraph()
        p_cap7.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap7.paragraph_format.space_before = Pt(3)
        p_cap7.paragraph_format.space_after = Pt(6)
        r_cap7 = p_cap7.add_run("Live Web Application Security Center: Granular RBAC permission grid governing access across industrial sensor streams")
        r_cap7.font.size = Pt(8.5)
        r_cap7.font.italic = True
        r_cap7.font.color.rgb = COLOR_MUTED

    p_f7_desc = doc.add_paragraph()
    p_f7_desc.paragraph_format.space_before = Pt(4)
    p_f7_desc.paragraph_format.space_after = Pt(12)
    p_f7_desc.paragraph_format.line_spacing = 1.25
    p_f7_desc.add_run(
        "• Specific Evidence Explanation:\n"
        "Figure 7 illustrates the live Role-Based Access Control (RBAC) permission enforcement modal implemented in the web application gateway:\n"
        "(1) Principle of Least Privilege (PoLP): The table explicitly details the security boundaries across 5 operational roles (BackupAdmin, Sensor Application, Compliance Auditor, Field Operations Tech, External Contractor).\n"
        "(2) Strict Deletion Denial for Sensor Applications: For the 'Sensor Application' role, permissions are rigidly configured as: Read = YES, Upload = YES, Delete = NO (Restricted), Restore = NO, Admin = NO. This directly verifies Course Security Task 2 ('Restrict write permissions to sensor applications').\n"
        "(3) Comprehensive Administrative Authority: The 'BackupAdmin' identity is granted complete administrative control (Read, Upload, Delete, Restore, Admin = YES) across all sensor streams, satisfying Course Security Task 1.\n"
        "(4) Real-Time Denial & Audit Log: Attempted deletions by restricted roles automatically trigger a '403 Forbidden' denial and register immediate security incident alerts for administrative review."
    ).font.size = Pt(9.5)

    doc.add_page_break()

    # =========================================================================
    # PAGE 8: FIGURE 8 (BACKUPADMIN ROLE), CONCLUSION & SUBMISSION SIGN-OFF
    # =========================================================================

    # --- FIGURE 8: BACKUPADMIN ROLE CONFIGURATION ---
    p_f8 = doc.add_paragraph()
    p_f8.paragraph_format.space_before = Pt(4)
    p_f8.paragraph_format.space_after = Pt(2)
    p_f8.paragraph_format.keep_with_next = True
    r_f8_title = p_f8.add_run("Figure 8: BackupAdmin IAM Role Configuration & Full Administrative Authority")
    r_f8_title.bold = True
    r_f8_title.font.size = Pt(10)
    r_f8_title.font.color.rgb = COLOR_SECONDARY

    img5_path = os.path.join(img_dir, "media_1795373189490_5b30b138.png")
    if os.path.exists(img5_path):
        doc.add_picture(img5_path, width=Inches(6.4))
        p_cap8 = doc.add_paragraph()
        p_cap8.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap8.paragraph_format.space_before = Pt(2)
        p_cap8.paragraph_format.space_after = Pt(3)
        r_cap8 = p_cap8.add_run("AWS IAM Role Creation Screen: BackupAdminRole with AmazonS3FullAccess policy attached")
        r_cap8.font.size = Pt(8)
        r_cap8.font.italic = True
        r_cap8.font.color.rgb = COLOR_MUTED

    p_f8_desc = doc.add_paragraph()
    p_f8_desc.paragraph_format.space_before = Pt(2)
    p_f8_desc.paragraph_format.space_after = Pt(8)
    p_f8_desc.paragraph_format.line_spacing = 1.15
    p_f8_desc.add_run(
        "• Specific Evidence Explanation:\n"
        "Figure 8 verifies Security Task 1: 'Create BackupAdmin role' (Deliverable 3). "
        "The IAM role named 'BackupAdminRole' is configured with an EC2 service trust policy ('ec2.amazonaws.com'), "
        "enabling the cloud virtual machine hosting the backup gateway to assume credentials securely via the AWS metadata service. "
        "Attached with the managed policy 'AmazonS3FullAccess', the BackupAdmin role possesses elevated privileges required for "
        "disaster recovery operations: executing point-in-time snapshot rollbacks, managing bucket encryption keys (SSE-KMS), "
        "auditing CloudTrail access events, and maintaining bucket lifecycle automation policies."
    ).font.size = Pt(8.5)

    # Section 4: Technical Summary & Architectural Conclusion
    add_section_header("4. Technical Summary & Architectural Conclusion")
    p_conc = doc.add_paragraph()
    p_conc.paragraph_format.space_before = Pt(3)
    p_conc.paragraph_format.space_after = Pt(8)
    p_conc.paragraph_format.line_spacing = 1.2
    run_conc = p_conc.add_run(
        "The Secure IoT Data Backup System successfully bridges cloud infrastructure, edge computing reliability, and information security. "
        "By deploying on an AWS EC2 virtual machine and enforcing Amazon S3 Object Versioning, the platform provides immutable defense against data loss. "
        "By structuring granular IAM policies, the Principle of Least Privilege is rigidly upheld between administrative operators and field IoT devices. "
        "Finally, the implementation of automated storage lifecycle rules guarantees that enterprise telemetry archives remain compliant and cost-effective over long retention horizons. "
        "All evaluation deliverables assigned by the course curriculum have been constructed, validated on live AWS cloud resources, and verified."
    )
    run_conc.font.size = Pt(9)
    run_conc.font.color.rgb = COLOR_TEXT

    # Official Submission Sign-off box
    sign_table = doc.add_table(rows=1, cols=1)
    sign_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_s = sign_table.cell(0, 0)
    c_s.width = Inches(7.0)
    set_cell_shading(c_s, "EEF2FF")
    set_cell_margins(c_s, top=90, bottom=90, left=130, right=130)
    p_s = c_s.paragraphs[0]
    p_s.paragraph_format.space_after = Pt(0)
    p_s.paragraph_format.line_spacing = 1.25
    r_s = p_s.add_run(
        "Submitted by: Vasani Jeel (Reg. No: 24UG00241) | Bachelor of Computer Applications (BCA)\n"
        "Course: Cloud Computing - SA Evaluation (15 Marks) | Assignment 18: Secure IoT Data Backup System\n"
        "Live Project URL: http://3.25.136.151:5000/ (AWS EC2 i-05ce0744eaeecba10, t3.micro, State: Running)\n"
        "GitHub Repository: https://github.com/jeel190/Secure-IoT-Data-backup-System | S3 Vault: s3://iot-sensor-vault-jeel"
    )
    r_s.font.size = Pt(8.5)
    r_s.font.color.rgb = COLOR_PRIMARY
    r_s.bold = True

    # Output paths
    downloads_dir = r"C:\Users\dell\Downloads"
    docx_path = os.path.join(downloads_dir, "Secure_IoT_Data_Backup_Report_Vasani_Jeel.docx")
    
    doc.save(docx_path)
    print(f"[+] DOCX created successfully at: {docx_path}")
    return docx_path

if __name__ == "__main__":
    create_report()
