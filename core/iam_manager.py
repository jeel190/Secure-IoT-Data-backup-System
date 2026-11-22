import json
import time
from datetime import datetime
from config import AUDIT_DIR

AUDIT_LOG_FILE = AUDIT_DIR / "audit_trail.jsonl"

# Standard AWS IAM Policy Definitions
IAM_ROLES = {
    "BackupAdmin": {
        "RoleName": "BackupAdminRole",
        "Description": "Full cloud storage administrator role with backup, restore, lifecycle, and audit privileges.",
        "Arn": "arn:aws:iam::123456789012:role/BackupAdminRole",
        "TrustPolicy": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": ["ec2.amazonaws.com", "backup.amazonaws.com"]},
                    "Action": "sts:AssumeRole"
                }
            ]
        },
        "Policies": [
            {
                "PolicyName": "BackupAdminFullAccessPolicy",
                "PolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "AllowAllS3Operations",
                            "Effect": "Allow",
                            "Action": [
                                "s3:ListBucket",
                                "s3:GetBucketLocation",
                                "s3:GetBucketVersioning",
                                "s3:PutBucketVersioning",
                                "s3:GetLifecycleConfiguration",
                                "s3:PutLifecycleConfiguration",
                                "s3:GetObject",
                                "s3:GetObjectVersion",
                                "s3:PutObject",
                                "s3:DeleteObject",
                                "s3:DeleteObjectVersion",
                                "s3:RestoreObject"
                            ],
                            "Resource": [
                                "arn:aws:s3:::iot-secure-telemetry-vault",
                                "arn:aws:s3:::iot-secure-telemetry-vault/*"
                            ]
                        },
                        {
                            "Sid": "AllowAuditAccess",
                            "Effect": "Allow",
                            "Action": [
                                "cloudtrail:LookupEvents",
                                "cloudtrail:GetTrailStatus"
                            ],
                            "Resource": "*"
                        }
                    ]
                }
            }
        ]
    },
    "SensorDevice": {
        "RoleName": "SensorApplicationRole",
        "Description": "Least-privilege role for IoT edge devices and sensor ingestion jobs. Write-only to sensor path; strictly prohibited from deleting or modifying bucket policies.",
        "Arn": "arn:aws:iam::123456789012:role/SensorApplicationRole",
        "TrustPolicy": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "iot.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        },
        "Policies": [
            {
                "PolicyName": "SensorWriteOnlyPolicy",
                "PolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "AllowSensorDailyUploadsOnly",
                            "Effect": "Allow",
                            "Action": [
                                "s3:PutObject"
                            ],
                            "Resource": "arn:aws:s3:::iot-secure-telemetry-vault/sensors/*"
                        },
                        {
                            "Sid": "DenyObjectDeletionAndLifecycleModification",
                            "Effect": "Deny",
                            "Action": [
                                "s3:DeleteObject",
                                "s3:DeleteObjectVersion",
                                "s3:PutBucketPolicy",
                                "s3:PutLifecycleConfiguration",
                                "s3:PutBucketVersioning"
                            ],
                            "Resource": "*"
                        }
                    ]
                }
            }
        ]
    },
    "Auditor": {
        "RoleName": "ComplianceAuditorRole",
        "Description": "Read-only compliance and security role for verifying backups and examining logs without modification rights.",
        "Arn": "arn:aws:iam::123456789012:role/ComplianceAuditorRole",
        "TrustPolicy": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "audit.internal.cloud"},
                    "Action": "sts:AssumeRole"
                }
            ]
        },
        "Policies": [
            {
                "PolicyName": "AuditorReadOnlyPolicy",
                "PolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "AllowReadMetadataAndObjects",
                            "Effect": "Allow",
                            "Action": [
                                "s3:ListBucket",
                                "s3:GetBucketLocation",
                                "s3:GetBucketVersioning",
                                "s3:GetLifecycleConfiguration",
                                "s3:GetObject",
                                "s3:GetObjectVersion",
                                "cloudtrail:LookupEvents"
                            ],
                            "Resource": [
                                "arn:aws:s3:::iot-secure-telemetry-vault",
                                "arn:aws:s3:::iot-secure-telemetry-vault/*"
                            ]
                        },
                        {
                            "Sid": "ExplicitDenyAllWritesAndDeletes",
                            "Effect": "Deny",
                            "Action": [
                                "s3:PutObject",
                                "s3:DeleteObject",
                                "s3:DeleteObjectVersion"
                            ],
                            "Resource": "*"
                        }
                    ]
                }
            }
        ]
    },
    "AnonymousUser": {
        "RoleName": "PublicAnonymousUser",
        "Description": "Unauthenticated public actor representing Internet access. Strictly denied by S3 Block Public Access.",
        "Arn": "arn:aws:iam::000000000000:user/Anonymous",
        "Policies": []
    }
}

class IAMManager:
    def __init__(self):
        self.active_role = "BackupAdmin" # Default role

    def set_active_role(self, role_name: str) -> bool:
        if role_name in IAM_ROLES:
            self.active_role = role_name
            self.log_audit_event("iam:SwitchRole", "arn:aws:iam::role/" + role_name, "ALLOW", f"Active role switched to {role_name}")
            return True
        return False

    def get_active_role(self) -> str:
        return self.active_role

    def get_role_details(self, role_name: str = None) -> dict:
        r = role_name or self.active_role
        return IAM_ROLES.get(r, IAM_ROLES["AnonymousUser"])

    def evaluate_permission(self, action: str, resource_arn: str, role_name: str = None) -> tuple[bool, str]:
        """
        Evaluates AWS IAM policy logic:
        1. Explicit Deny wins over everything.
        2. Must have at least one explicit Allow.
        3. Default is Deny.
        """
        r_name = role_name or self.active_role
        role_data = IAM_ROLES.get(r_name)

        if not role_data or r_name == "AnonymousUser":
            reason = f"Access Denied: S3 Block Public Access is active. Unauthenticated or Anonymous role has 0 permissions."
            self.log_audit_event(action, resource_arn, "DENY", reason, r_name)
            return False, reason

        has_allow = False

        for policy in role_data.get("Policies", []):
            statements = policy["PolicyDocument"].get("Statement", [])
            for stmt in statements:
                effect = stmt.get("Effect")
                actions = stmt.get("Action", [])
                res = stmt.get("Resource", [])
                if isinstance(res, str):
                    res = [res]

                # Match action (support wildcards like s3:*)
                action_matched = False
                for a in actions:
                    if a == "*" or a == action:
                        action_matched = True
                        break
                    elif a.endswith("*") and action.startswith(a[:-1]):
                        action_matched = True
                        break

                # Match resource (support wildcards)
                res_matched = False
                for r in res:
                    if r == "*" or r == resource_arn:
                        res_matched = True
                        break
                    elif r.endswith("*") and resource_arn.startswith(r[:-1]):
                        res_matched = True
                        break

                if action_matched and res_matched:
                    if effect == "Deny":
                        reason = f"Explicit Deny in policy '{policy['PolicyName']}' for action '{action}' on resource '{resource_arn}'"
                        self.log_audit_event(action, resource_arn, "DENY", reason, r_name)
                        return False, reason
                    elif effect == "Allow":
                        has_allow = True

        if has_allow:
            reason = f"Authorized by policy for role '{r_name}'"
            self.log_audit_event(action, resource_arn, "ALLOW", reason, r_name)
            return True, reason
        else:
            reason = f"Implicit Deny: No policy statement grants '{action}' to role '{r_name}' on resource '{resource_arn}'"
            self.log_audit_event(action, resource_arn, "DENY", reason, r_name)
            return False, reason

    def log_audit_event(self, action: str, resource: str, status: str, details: str, role_name: str = None):
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "principal": role_name or self.active_role,
            "action": action,
            "resource": resource,
            "status": status,
            "details": details,
            "ip_address": "10.0.4.15 (EC2 Cloud VM Internal IP)",
            "userAgent": "AWS-SDK/IoT-Backup-Client-v2"
        }
        try:
            with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            print(f"Error logging audit event: {e}")

    def get_audit_logs(self, limit: int = 100) -> list:
        if not AUDIT_LOG_FILE.exists():
            return []
        logs = []
        try:
            with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        logs.append(json.loads(line.strip()))
            logs.reverse() # Most recent first
            return logs[:limit]
        except Exception as e:
            return [{"error": str(e)}]

# Global Singleton instance
iam_manager = IAMManager()
