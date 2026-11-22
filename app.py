import os
import io
import csv
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, Response, make_response

from config import (
    APP_NAME, APP_VERSION, STUDENT_NAME, REGISTER_NO, ASSIGNMENT_NO,
    PROJECT_DOMAIN, BUCKET_NAME, DEFAULT_ENCRYPTION, VERSIONING_ENABLED,
    BLOCK_PUBLIC_ACCESS, PRE_SIGNED_URL_EXPIRY_SECONDS
)
from core.storage_engine import storage_engine
from core.iam_manager import iam_manager, IAM_ROLES
from core.sensor_ingestion import sensor_ingestion_engine, DEVICE_TYPES
from core.lifecycle_engine import lifecycle_engine
from core.integrity_verifier import integrity_verifier
from core.security_center import security_center, USERS

app = Flask(__name__)
app.config["SECRET_KEY"] = "iot-cloud-security-secret-key-24UG00241"

# Initialize seed data for fresh environments or cloud deployments
try:
    sensor_ingestion_engine.seed_initial_historical_backups()
except Exception as e:
    print(f"[*] Note: Seed initialization notice: {e}")

# Inject template context
@app.context_processor
def inject_global_context():
    return {
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "student_name": STUDENT_NAME,
        "register_no": REGISTER_NO,
        "assignment_no": ASSIGNMENT_NO,
        "project_domain": PROJECT_DOMAIN,
        "bucket_name": storage_engine.bucket_name,
        "current_user": security_center.get_current_user(),
        "users": USERS,
        "kms_status": security_center.get_kms_status(),
        "versioning_enabled": VERSIONING_ENABLED,
        "block_public_access": BLOCK_PUBLIC_ACCESS,
        "default_encryption": DEFAULT_ENCRYPTION,
        "current_year": datetime.utcnow().year
    }

# ----------------- MAIN UI ROUTE ----------------- #

@app.route("/")
def index():
    stats = storage_engine.get_storage_stats()
    live_weather = sensor_ingestion_engine.fetch_live_public_weather_iot()
    kms_status = security_center.get_kms_status()
    current_user = security_center.get_current_user()
    cost_data = lifecycle_engine.calculate_cost_savings()
    return render_template(
        "index.html",
        stats=stats,
        live_weather=live_weather,
        kms_status=kms_status,
        current_user=current_user,
        users=USERS,
        cost_data=cost_data
    )

# ----------------- DOCVAULT COMPATIBLE API ROUTES ----------------- #

@app.route("/api/documents", methods=["GET"])
def api_list_documents():
    dept = request.args.get("dept", "all").strip().lower()
    query = request.args.get("q", "").strip()
    user = security_center.get_current_user()

    # Check folder boundary access
    allowed, reason = security_center.check_folder_access(dept, user)
    if not allowed:
        return jsonify({
            "success": False,
            "error": "Access Denied by AWS IAM Policy",
            "reason": reason,
            "requires_admin_elevate": True,
            "documents": [],
            "counts": {"all": 0, "env": 0, "turbine": 0, "grid": 0, "hvac": 0}
        }), 403

    docs = storage_engine.list_documents(department=dept, query=query, user=user)

    # Compute category counts for badge indicators
    all_docs = storage_engine.list_documents(department="all", query="", user=user)
    counts = {
        "all": len(all_docs),
        "env": sum(1 for d in all_docs if d["department"] == "env"),
        "turbine": sum(1 for d in all_docs if d["department"] == "turbine"),
        "grid": sum(1 for d in all_docs if d["department"] == "grid"),
        "hvac": sum(1 for d in all_docs if d["department"] == "hvac")
    }

    return jsonify({
        "success": True,
        "department": dept,
        "documents": docs,
        "total": len(docs),
        "counts": counts
    })

@app.route("/api/auth/switch-user", methods=["POST"])
def api_switch_user():
    data = request.get_json(silent=True) or request.form
    username = data.get("user_id") or data.get("username") or data.get("role")
    if not username:
        return jsonify({"success": False, "error": "Missing user_id parameter"}), 400

    res = security_center.switch_user(username)
    if not res["success"]:
        return jsonify(res), 400

    # Sync with iam_manager for backend IAM compatibility
    role_map = {
        "system_admin": "BackupAdmin",
        "sensor_edge": "SensorDevice",
        "compliance_auditor": "Auditor",
        "field_operator": "BackupAdmin",
        "contractor_guest": "Auditor"
    }
    iam_role = role_map.get(username, "BackupAdmin")
    iam_manager.set_active_role(iam_role)

    return jsonify({
        "success": True,
        "user": res["user"],
        "iam_role": iam_role
    })

@app.route("/api/documents/upload", methods=["POST"])
def api_upload_document():
    user = security_center.get_current_user()
    dept = request.form.get("department") or "env"
    description = request.form.get("description", "IoT Sensor Archive Telemetry")
    tags = request.form.get("tags", "Sensor, S3-Vault, SSE-KMS")

    # If JSON payload
    if request.is_json:
        data = request.get_json()
        dept = data.get("department", dept)
        description = data.get("description", description)
        tags = data.get("tags", tags)

    # Check upload permission
    allowed, reason = security_center.check_action_permission("upload", dept, user)
    if not allowed:
        return jsonify({"success": False, "error": reason}), 403

    # Check if physical file uploaded or generate sample
    file = request.files.get("file")
    if file and file.filename != "":
        filename = file.filename
        content_bytes = file.read()
        try:
            content_str = content_bytes.decode("utf-8")
        except Exception:
            content_str = content_bytes.hex()
    else:
        # Check if user requested CSV or JSON synthetic sensor log
        fmt = request.form.get("format") or (request.json.get("format") if request.is_json else "csv")
        now_date = datetime.utcnow().strftime("%Y-%m-%d")
        now_ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        if fmt == "csv":
            filename = f"{dept}_sensor_{now_date}_{now_ts[-4:]}.csv"
            content_str = sensor_ingestion_engine.generate_daily_csv_payload(now_date, hours=24)
        else:
            filename = f"{dept}_telemetry_{now_ts}.json"
            live_w = sensor_ingestion_engine.fetch_live_public_weather_iot()
            sample_payload = {
                "metadata": {
                    "department": dept,
                    "ingested_by": user["display_name"],
                    "role_arn": user["role_arn"],
                    "ingested_at": datetime.utcnow().isoformat() + "Z",
                    "encryption": "aws:kms",
                    "s3_bucket": storage_engine.bucket_name
                },
                "sensor_readings": {
                    "station_id": f"{dept.upper()}-NODE-01",
                    "status": "OPERATIONAL",
                    "live_weather_sync": live_w.get("live_readings", {}),
                    "samples_count": 240,
                    "frequency": "60s"
                }
            }
            content_str = json.dumps(sample_payload, indent=2)

    # Store in S3 Vault
    key = f"sensors/{dept}/{filename}"
    meta = {
        "department": dept,
        "description": description,
        "tags": tags,
        "uploaded_by": user["display_name"],
        "role": user["username"]
    }
    put_res = storage_engine.put_backup(key, content_str, metadata=meta, active_role=iam_manager.get_active_role())
    if not put_res["success"]:
        return jsonify(put_res), 500

    doc = storage_engine.get_document_by_id(key)
    return jsonify({
        "success": True,
        "message": f"Successfully backed up {filename} to AWS S3 Vault.",
        "key": key,
        "version_id": put_res["version_id"],
        "document": doc
    })

def _resolve_key(dept: str, doc_id: str) -> str:
    """Helper to convert safe doc_id or raw doc_id to canonical S3 key"""
    if "/" in doc_id or "\\" in doc_id:
        return doc_id.replace("\\", "/")
    # Try finding in manifest
    manifest_objs = storage_engine.manifest.get("objects", {})
    for k in manifest_objs.keys():
        safe = k.replace("/", "_").replace("\\", "_")
        if safe == doc_id or k.endswith(doc_id):
            return k
    return f"sensors/{dept}/{doc_id}"

@app.route("/api/documents/view/<dept>/<path:doc_id>", methods=["GET"])
def api_view_document(dept, doc_id):
    user = security_center.get_current_user()
    key = _resolve_key(dept, doc_id)

    # Check view permission
    allowed, reason = security_center.check_action_permission("view", dept, user)
    if not allowed:
        return jsonify({"success": False, "error": reason}), 403

    version_id = request.args.get("version_id")
    content_res = storage_engine.get_backup_content(key, version_id=version_id, active_role=iam_manager.get_active_role())
    if not content_res["success"]:
        return jsonify(content_res), 404

    versions_res = storage_engine.get_backup_versions(key, active_role=iam_manager.get_active_role())
    versions = versions_res.get("versions", []) if versions_res.get("success") else []

    filename = key.split("/")[-1]
    return jsonify({
        "success": True,
        "key": key,
        "filename": filename,
        "department": dept,
        "version_id": content_res["version_id"],
        "content": content_res["content"],
        "sha256": content_res["sha256"],
        "storage_class": content_res.get("storage_class", "STANDARD"),
        "encryption": content_res.get("encryption", "AES256"),
        "created_at": content_res["created_at"],
        "metadata": content_res.get("metadata", {}),
        "versions": versions
    })

@app.route("/api/documents/download/<dept>/<path:doc_id>", methods=["GET"])
def api_download_document(dept, doc_id):
    user = security_center.get_current_user()
    key = _resolve_key(dept, doc_id)

    # Check download permission
    allowed, reason = security_center.check_action_permission("download", dept, user)
    if not allowed:
        return jsonify({"success": False, "error": reason}), 403

    version_id = request.args.get("version_id")
    content_res = storage_engine.get_backup_content(key, version_id=version_id, active_role=iam_manager.get_active_role())
    if not content_res["success"]:
        return jsonify(content_res), 404

    filename = key.split("/")[-1]
    response = make_response(content_res["content"])
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "application/json"
    return response

@app.route("/api/documents/delete/<dept>/<path:doc_id>", methods=["DELETE", "POST"])
def api_delete_document(dept, doc_id):
    user = security_center.get_current_user()
    key = _resolve_key(dept, doc_id)

    # Check delete permission (PoLP)
    allowed, reason = security_center.check_action_permission("delete", dept, user)
    if not allowed:
        return jsonify({"success": False, "error": reason}), 403

    del_res = storage_engine.delete_backup(key, active_role=iam_manager.get_active_role())
    if not del_res["success"]:
        return jsonify(del_res), 500

    return jsonify({
        "success": True,
        "message": f"Object {key} deleted (S3 DeleteMarker recorded).",
        "delete_marker_id": del_res.get("delete_marker_id")
    })

@app.route("/api/documents/restore/<dept>/<path:doc_id>", methods=["POST"])
def api_restore_document(dept, doc_id):
    user = security_center.get_current_user()
    key = _resolve_key(dept, doc_id)

    # Check restore permission
    allowed, reason = security_center.check_action_permission("restore", dept, user)
    if not allowed:
        return jsonify({"success": False, "error": reason}), 403

    data = request.get_json(silent=True) or {}
    version_id = data.get("version_id")
    if not version_id:
        return jsonify({"success": False, "error": "version_id is required for point-in-time restore"}), 400

    restore_res = storage_engine.restore_version(key, version_id, active_role=iam_manager.get_active_role())
    if not restore_res["success"]:
        return jsonify(restore_res), 400

    return jsonify({
        "success": True,
        "message": f"Successfully restored snapshot {version_id[:12]}... to active latest state.",
        "version_id": restore_res.get("version_id"),
        "key": key
    })

@app.route("/api/security/report-violation", methods=["POST"])
def api_report_violation():
    data = request.get_json(silent=True) or {}
    user = security_center.get_current_user()
    action = data.get("action", "Access")
    folder = data.get("folder", "unknown")
    reason = data.get("reason", "Unauthorized action attempted.")
    resource = data.get("resource", f"sensors/{folder}/*")

    alert = security_center.log_alert(
        title=data.get("title", "IAM Security Policy Violation"),
        resource=resource,
        reason=reason,
        user=user,
        action=action
    )
    return jsonify({"success": True, "alert": alert})

# ----------------- ADMIN SECURITY CENTER API ROUTES ----------------- #

@app.route("/api/admin/alerts", methods=["GET"])
def api_admin_alerts():
    summary = security_center.get_admin_alerts_summary()
    return jsonify({
        "success": True,
        **summary
    })

@app.route("/api/admin/alerts/acknowledge", methods=["POST"])
def api_acknowledge_alert():
    data = request.get_json(silent=True) or {}
    alert_id = data.get("alert_id")
    if not alert_id:
        return jsonify({"success": False, "error": "Missing alert_id"}), 400
    security_center.acknowledge_alert(alert_id)
    return jsonify({"success": True})

@app.route("/api/admin/alerts/clear-all", methods=["POST"])
def api_clear_all_alerts():
    security_center.clear_all_alerts()
    return jsonify({"success": True})

@app.route("/api/admin/kms/rotate", methods=["POST"])
def api_rotate_kms_key():
    user = security_center.get_current_user()
    if not user.get("permissions", {}).get("is_admin", False):
        return jsonify({"success": False, "error": "Permission Denied: Only BackupAdmin role can rotate KMS master key."}), 403

    res = security_center.rotate_kms_key()
    return jsonify(res)

@app.route("/api/admin/audit/export-csv", methods=["GET"])
def api_export_audit_csv():
    user = security_center.get_current_user()
    if not user.get("permissions", {}).get("is_admin", False):
        return jsonify({"success": False, "error": "Only SecurityAdmin can export audit logs."}), 403

    logs = iam_manager.get_audit_logs(limit=300)
    alerts = security_center.get_alerts_list()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Event ID", "Timestamp UTC", "Principal/User", "Role/Group", "Action", "Resource ARN", "Status", "Details"])

    for l in logs:
        writer.writerow([
            l.get("event_id", ""),
            l.get("timestamp", ""),
            l.get("user", l.get("principal", "")),
            l.get("role", ""),
            l.get("action", ""),
            l.get("resource", ""),
            "ALLOWED" if l.get("allowed") else "DENIED",
            l.get("details", "")
        ])

    for a in alerts:
        writer.writerow([
            a.get("alert_id", ""),
            a.get("timestamp", ""),
            a.get("username", ""),
            a.get("group", ""),
            a.get("action", ""),
            a.get("resource", ""),
            "SECURITY_INCIDENT",
            f"{a.get('title')}: {a.get('reason')}"
        ])

    csv_data = output.getvalue()
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=iot_vault_security_trail.csv"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    return response

# ----------------- SENSOR & LIFECYCLE ROUTES ----------------- #

@app.route("/api/sensor/live", methods=["GET"])
def api_sensor_live():
    res = sensor_ingestion_engine.fetch_live_public_weather_iot()
    return jsonify(res)

@app.route("/api/lifecycle/advance", methods=["POST"])
def api_lifecycle_advance():
    data = request.get_json(silent=True) or {}
    days = data.get("days", 30)
    res = lifecycle_engine.simulate_days_advancement(days=days, active_role=iam_manager.get_active_role())
    return jsonify(res)

# ----------------- BACKWARDS COMPATIBLE / TEST SUITE ROUTES ----------------- #

@app.route("/api/backups/daily", methods=["POST"])
def api_backup_daily():
    data = request.get_json(silent=True) or {}
    target_date = data.get("date")
    res = sensor_ingestion_engine.backup_daily_sensors(target_date, active_role=iam_manager.get_active_role())
    if not res.get("success"):
        return jsonify(res), 403 if "403" in res.get("error", "") else 500

    return jsonify(res)

@app.route("/api/backups/delete", methods=["POST"])
def api_delete_backup_compat():
    data = request.get_json(silent=True) or {}
    key = data.get("key")
    if not key:
        return jsonify({"success": False, "error": "Missing key"}), 400

    res = storage_engine.delete_backup(key, active_role=iam_manager.get_active_role())
    if not res["success"]:
        # Log to security center if forbidden
        if "403" in res.get("error", ""):
            security_center.log_alert(
                title="Unauthorized Delete Attempt",
                resource=key,
                reason=res.get("error", ""),
                user=security_center.get_current_user(),
                action="s3:DeleteObject"
            )
            return jsonify(res), 403
        return jsonify(res), 500
    return jsonify(res)

@app.route("/api/role/test-permission", methods=["POST"])
def api_test_permission():
    data = request.get_json(silent=True) or {}
    action = data.get("action")
    resource = data.get("resource")
    role = data.get("role") or iam_manager.get_active_role()

    allowed, reason = iam_manager.evaluate_permission(action, resource, role)
    return jsonify({
        "role": role,
        "action": action,
        "resource": resource,
        "allowed": allowed,
        "reason": reason
    })

@app.route("/api/backups/verify-integrity", methods=["POST"])
def api_verify_integrity():
    data = request.get_json(silent=True) or {}
    key = data.get("key")
    if not key:
        return jsonify({"success": False, "error": "Missing key"}), 400

    version_id = data.get("version_id")
    res = integrity_verifier.verify_backup_integrity(key, version_id=version_id)
    return jsonify(res)

@app.route("/api/backups/restore", methods=["POST"])
def api_restore_backup_compat():
    data = request.get_json(silent=True) or {}
    key = data.get("key")
    version_id = data.get("version_id")
    if not key or not version_id:
        return jsonify({"success": False, "error": "Missing key or version_id"}), 400

    res = storage_engine.restore_version(key, version_id, active_role=iam_manager.get_active_role())
    status_code = res.get("status_code", 200)
    if not res["success"]:
        return jsonify(res), status_code
    return jsonify(res)

@app.route("/api/presigned-url", methods=["GET"])
def api_get_presigned_url():
    key = request.args.get("key")
    if not key:
        return jsonify({"success": False, "error": "Missing key"}), 400
    url = storage_engine.generate_presigned_url(key)
    return jsonify({"success": True, "key": key, "presigned_download_url": url})

@app.route("/api/download/presigned", methods=["GET"])
@app.route("/api/download", methods=["GET"])
def api_download_presigned():
    bucket = request.args.get("bucket", storage_engine.bucket_name)
    key = request.args.get("key")
    version_id = request.args.get("versionId")
    expires = request.args.get("expires", type=int)
    signature = request.args.get("signature")

    if not key:
        return jsonify({"error": "Missing key parameter"}), 400

    # If signature and expires are provided, verify presigned signature
    if signature and expires:
        is_valid = storage_engine.verify_presigned_signature(bucket, key, version_id, expires, signature)
        if not is_valid:
            return jsonify({"error": "Invalid or expired pre-signed URL"}), 403

    read_res = storage_engine.get_backup_content(key, version_id=version_id, active_role="BackupAdmin")
    if not read_res.get("success"):
        return jsonify(read_res), 404

    filename = key.split("/")[-1]
    response = make_response(read_res["content"])
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "application/json"
    return response

@app.route("/api/role/switch", methods=["POST"])
def api_switch_role_compat():
    data = request.get_json(silent=True) or {}
    role = data.get("role")
    res = iam_manager.set_active_role(role)
    return jsonify(res)

@app.route("/api/stats", methods=["GET"])
def api_get_stats():
    stats = storage_engine.get_storage_stats()
    return jsonify(stats)

@app.route("/api/backups/versions", methods=["GET"])
def api_get_backup_versions():
    key = request.args.get("key")
    if not key:
        return jsonify({"success": False, "error": "Missing key"}), 400
    res = storage_engine.get_backup_versions(key, active_role=iam_manager.get_active_role())
    return jsonify(res)

if __name__ == "__main__":
    print(f"Starting {APP_NAME} v{APP_VERSION} on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
