import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from config import DATA_DIR, AUDIT_DIR

ALERTS_FILE = AUDIT_DIR / "security_alerts.json"
KMS_FILE = DATA_DIR / "storage" / "kms_key_status.json"

USERS = {
    "system_admin": {
        "username": "system_admin",
        "display_name": "BackupAdmin (System Admin)",
        "email": "admin@cloudvault.internal",
        "group": "SecurityAdmin",
        "role_arn": "arn:aws:iam::123456789012:role/BackupAdminRole",
        "avatar_badge": "BackupAdmin",
        "color": "indigo",
        "description": "Full administrative privilege, key rotation & delete authority.",
        "policy_file": "admin_backup_policy.json",
        "permissions": {
            "folders": ["all", "env", "turbine", "grid", "hvac"],
            "can_read": True,
            "can_upload": True,
            "can_delete": True,
            "can_restore": True,
            "is_admin": True
        }
    },
    "sensor_edge": {
        "username": "sensor_edge",
        "display_name": "Sensor Application (Write Only)",
        "email": "edge-daemon@devices.internal",
        "group": "SensorIngestion",
        "role_arn": "arn:aws:iam::123456789012:role/SensorApplicationRole",
        "avatar_badge": "Write-Only",
        "color": "amber",
        "description": "Least-Privilege: Ingest & upload sensor records. Delete strictly denied.",
        "policy_file": "sensor_write_only_policy.json",
        "permissions": {
            "folders": ["all", "env", "turbine", "grid", "hvac"],
            "can_read": True,
            "can_upload": True,
            "can_delete": False, # Least privilege: NO DELETE
            "can_restore": False,
            "is_admin": False
        }
    },
    "compliance_auditor": {
        "username": "compliance_auditor",
        "display_name": "Compliance Auditor (Read Only)",
        "email": "auditor@compliance.internal",
        "group": "Auditor",
        "role_arn": "arn:aws:iam::123456789012:role/ComplianceAuditorRole",
        "avatar_badge": "Auditor",
        "color": "blue",
        "description": "Read-only access for compliance audit. Cannot upload or delete.",
        "policy_file": "auditor_readonly_policy.json",
        "permissions": {
            "folders": ["all", "env", "turbine", "grid", "hvac"],
            "can_read": True,
            "can_upload": False,
            "can_delete": False,
            "can_restore": False,
            "is_admin": False
        }
    },
    "field_operator": {
        "username": "field_operator",
        "display_name": "Field Operations Tech",
        "email": "field-ops@iot.internal",
        "group": "FieldOps",
        "role_arn": "arn:aws:iam::123456789012:role/FieldOperationsRole",
        "avatar_badge": "Field Ops",
        "color": "emerald",
        "description": "Field inspections and telemetry ingestion. Delete restricted.",
        "policy_file": "field_ops_policy.json",
        "permissions": {
            "folders": ["all", "env", "turbine", "grid", "hvac"],
            "can_read": True,
            "can_upload": True,
            "can_delete": False,
            "can_restore": False,
            "is_admin": False
        }
    },
    "contractor_guest": {
        "username": "contractor_guest",
        "display_name": "External Contractor (Restricted)",
        "email": "contractor@external.internal",
        "group": "Guest",
        "role_arn": "arn:aws:iam::000000000000:user/ContractorGuest",
        "avatar_badge": "Restricted",
        "color": "rose",
        "description": "Restricted guest: Environmental stream only. Industrial streams blocked.",
        "policy_file": "contractor_restricted_policy.json",
        "permissions": {
            # Strictly restricted: Only environmental mast permitted, other industrial folders BLOCKED!
            "folders": ["all", "env"],
            "can_read": True,
            "can_upload": False,
            "can_delete": False,
            "can_restore": False,
            "is_admin": False
        }
    }
}

class SecurityCenter:
    def __init__(self):
        self.current_user = USERS["system_admin"]
        self._init_files()

    def _init_files(self):
        if not ALERTS_FILE.exists():
            with open(ALERTS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
        if not KMS_FILE.exists():
            initial_kms = {
                "key_arn": "arn:aws:kms:us-east-1:123456789012:key/mrk-iot-backup-vault-master",
                "current_version": "v1",
                "key_state": "Active",
                "algorithm": "AES-256-GCM",
                "origin": "AWS_KMS",
                "created_at": "2026-11-01 08:00:00 UTC",
                "last_rotated_at": "2026-11-01 08:00:00 UTC",
                "rotation_count": 0,
                "compliance": "NIST SP 800-57 / AWS KMS Automated Key Rotation Standard"
            }
            with open(KMS_FILE, "w", encoding="utf-8") as f:
                json.dump(initial_kms, f, indent=2)

    def get_current_user(self):
        return self.current_user

    def switch_user(self, username: str) -> dict:
        if username in USERS:
            self.current_user = USERS[username]
            return {"success": True, "user": self.current_user}
        return {"success": False, "error": f"Unknown user '{username}'"}

    def check_folder_access(self, folder: str, user: dict = None) -> tuple[bool, str]:
        u = user or self.current_user
        perms = u.get("permissions", {})
        allowed_folders = perms.get("folders", [])

        if folder == "all":
            return True, "Access granted"

        if folder in allowed_folders:
            return True, "Access granted"

        # Access denied
        reason = f"Access Denied: Role '{u['display_name']}' ({u['group']}) lacks IAM permission to access '{folder}' department storage under AWS Least-Privilege policy."
        self.log_alert(
            title="IAM Access Violation Detected",
            resource=f"sensors/{folder}/*",
            reason=reason,
            user=u,
            action="Browse"
        )
        return False, reason

    def check_action_permission(self, action: str, folder: str, user: dict = None) -> tuple[bool, str]:
        u = user or self.current_user
        perms = u.get("permissions", {})

        # First check folder access
        folder_ok, reason = self.check_folder_access(folder, u)
        if not folder_ok:
            return False, reason

        if action == "view" or action == "download":
            if perms.get("can_read", False):
                return True, "Authorized"
            reason = f"Role '{u['display_name']}' is not authorized to read files."
            self.log_alert("Unauthorized Read Attempt", f"sensors/{folder}/*", reason, u, action)
            return False, reason

        if action == "upload":
            if perms.get("can_upload", False):
                return True, "Authorized"
            reason = f"Role '{u['display_name']}' lacks s3:PutObject permission in '{folder}' folder."
            self.log_alert("Unauthorized Upload Attempt", f"sensors/{folder}/*", reason, u, action)
            return False, reason

        if action == "delete":
            if perms.get("can_delete", False):
                return True, "Authorized"
            reason = f"CRITICAL: Unauthorized Delete Rejected. Role '{u['display_name']}' is strictly denied s3:DeleteObject by least-privilege policy."
            self.log_alert("Malicious / Unauthorized Delete Blocked", f"sensors/{folder}/*", reason, u, action)
            return False, reason

        if action == "restore":
            if perms.get("can_restore", False):
                return True, "Authorized"
            reason = f"Role '{u['display_name']}' lacks s3:RestoreObject privilege."
            self.log_alert("Unauthorized Restore Attempt", f"sensors/{folder}/*", reason, u, action)
            return False, reason

        return False, "Unknown action denied"

    def log_alert(self, title: str, resource: str, reason: str, user: dict = None, action: str = "Access"):
        u = user or self.current_user
        alert_id = f"alt-{uuid.uuid4().hex[:6]}"
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        alert = {
            "alert_id": alert_id,
            "title": title,
            "resource": resource,
            "action": action,
            "reason": reason,
            "username": u["username"],
            "user_display_name": u["display_name"],
            "group": u["group"],
            "source_ip": "10.0.4.15",
            "timestamp": now_str,
            "acknowledged": False,
            "webhook_status": "Dispatched to CloudWatch / Incident Webhook (HTTP 200)"
        }

        alerts = self.get_alerts_list()
        alerts.insert(0, alert)
        try:
            with open(ALERTS_FILE, "w", encoding="utf-8") as f:
                json.dump(alerts, f, indent=2)
        except Exception as e:
            print(f"Error saving alert: {e}")

        return alert

    def get_alerts_list(self) -> list:
        if not ALERTS_FILE.exists():
            return []
        try:
            with open(ALERTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def get_admin_alerts_summary(self) -> dict:
        alerts = self.get_alerts_list()
        unread_count = sum(1 for a in alerts if not a.get("acknowledged", False))
        kms_status = self.get_kms_status()
        return {
            "is_admin": (self.current_user.get("group") == "SecurityAdmin"),
            "unread_count": unread_count,
            "alerts": alerts,
            "kms_status": kms_status,
            "metrics": {
                "total_alerts": len(alerts),
                "unread_alerts": unread_count,
                "s3_encryption": "AWS KMS (SSE-KMS / AES-256-GCM)",
                "bucket_protection": "Enforced"
            }
        }

    def acknowledge_alert(self, alert_id: str) -> bool:
        alerts = self.get_alerts_list()
        for a in alerts:
            if a.get("alert_id") == alert_id:
                a["acknowledged"] = True
                break
        with open(ALERTS_FILE, "w", encoding="utf-8") as f:
            json.dump(alerts, f, indent=2)
        return True

    def clear_all_alerts(self) -> bool:
        alerts = self.get_alerts_list()
        for a in alerts:
            a["acknowledged"] = True
        with open(ALERTS_FILE, "w", encoding="utf-8") as f:
            json.dump(alerts, f, indent=2)
        return True

    def get_kms_status(self) -> dict:
        if not KMS_FILE.exists():
            self._init_files()
        try:
            with open(KMS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"current_version": "v1", "key_state": "Active"}

    def rotate_kms_key(self) -> dict:
        status = self.get_kms_status()
        curr_ver = status.get("current_version", "v1")
        try:
            ver_num = int(curr_ver.replace("v", "")) + 1
        except Exception:
            ver_num = 2
        new_ver = f"v{ver_num}"

        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        status["current_version"] = new_ver
        status["last_rotated_at"] = now_str
        status["rotation_count"] = status.get("rotation_count", 0) + 1

        with open(KMS_FILE, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2)

        return {
            "success": True,
            "report": {
                "key_arn": status["key_arn"],
                "key_version": new_ver,
                "rotated_at": now_str,
                "compliance": status["compliance"]
            }
        }

security_center = SecurityCenter()
