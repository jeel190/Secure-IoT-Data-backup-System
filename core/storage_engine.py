import os
import json
import hashlib
import time
import uuid
import hmac
from datetime import datetime, timedelta
from pathlib import Path
from config import STORAGE_DIR, BUCKET_NAME, DEFAULT_ENCRYPTION, VERSIONING_ENABLED, BLOCK_PUBLIC_ACCESS, PRE_SIGNED_URL_EXPIRY_SECONDS
from core.iam_manager import iam_manager

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

MANIFEST_FILE = STORAGE_DIR / "s3_bucket_manifest.json"
PRESIGNED_SECRET_KEY = "iot-cloud-super-secret-hmac-key-24UG00241"

class StorageEngine:
    def __init__(self):
        self.bucket_name = BUCKET_NAME
        self.versioning_enabled = VERSIONING_ENABLED
        self.block_public_access = BLOCK_PUBLIC_ACCESS
        self.default_encryption = DEFAULT_ENCRYPTION
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> dict:
        if MANIFEST_FILE.exists():
            try:
                with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Initial bucket metadata
        initial_manifest = {
            "bucket_name": self.bucket_name,
            "created_at": "2026-11-01T08:00:00Z",
            "region": "us-east-1",
            "versioning": {
                "status": "Enabled",
                "mfa_delete": "Disabled"
            },
            "public_access_block": {
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True
            },
            "server_side_encryption": {
                "rules": [
                    {
                        "apply_server_side_encryption_by_default": {
                            "sse_algorithm": "AES256"
                        }
                    }
                ]
            },
            "lifecycle_configuration": {
                "rules": [
                    {
                        "id": "IoTTelemetryArchiveRule",
                        "status": "Enabled",
                        "filter": {"prefix": "sensors/"},
                        "transitions": [
                            {"days": 30, "storage_class": "STANDARD_IA"},
                            {"days": 90, "storage_class": "GLACIER"}
                        ],
                        "noncurrent_version_expiration": {
                            "noncurrent_days": 365
                        }
                    }
                ]
            },
            "objects": {} # key -> list of versions (newest first)
        }
        self._save_manifest(initial_manifest)
        return initial_manifest

    def _save_manifest(self, manifest_data: dict = None):
        if manifest_data is not None:
            self.manifest = manifest_data
        with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
            json.dump(self.manifest, f, indent=2)

    def calculate_sha256(self, content_str: str) -> str:
        return hashlib.sha256(content_str.encode("utf-8")).hexdigest()

    def put_backup(self, key: str, data_content: str, metadata: dict = None, active_role: str = None) -> dict:
        role = active_role or iam_manager.get_active_role()
        resource_arn = f"arn:aws:s3:::{self.bucket_name}/{key}"

        # Evaluate IAM
        allowed, reason = iam_manager.evaluate_permission("s3:PutObject", resource_arn, role)
        if not allowed:
            return {"success": False, "status_code": 403, "error": f"403 Forbidden - {reason}"}

        # Calculate Hash and Size
        content_hash = self.calculate_sha256(data_content)
        content_bytes = data_content.encode("utf-8")
        size_bytes = len(content_bytes)

        # Generate unique Version ID
        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        version_id = f"v_{timestamp_str}_{uuid.uuid4().hex[:8]}"

        # Storage Path
        safe_key = key.replace("/", "_").replace("\\", "_")
        version_file_name = f"{safe_key}_{version_id}.dat"
        file_path = STORAGE_DIR / version_file_name
        with open(file_path, "wb") as f:
            f.write(content_bytes)

        # Prepare Version Record
        version_record = {
            "version_id": version_id,
            "key": key,
            "size_bytes": size_bytes,
            "size_kb": round(size_bytes / 1024, 2),
            "sha256": content_hash,
            "encryption": self.default_encryption,
            "storage_class": "STANDARD",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "age_days": 0,
            "uploaded_by_role": role,
            "file_path": str(file_path),
            "is_latest": True,
            "metadata": metadata or {}
        }

        # Update manifest
        if key not in self.manifest["objects"]:
            self.manifest["objects"][key] = []
        else:
            # Mark previous versions as not latest
            for v in self.manifest["objects"][key]:
                v["is_latest"] = False

        self.manifest["objects"][key].insert(0, version_record)
        self._save_manifest()

        return {
            "success": True,
            "key": key,
            "version_id": version_id,
            "sha256": content_hash,
            "size_bytes": size_bytes,
            "storage_class": "STANDARD",
            "encryption": self.default_encryption,
            "message": "Backup uploaded successfully with S3 object versioning and SSE-S3 encryption."
        }

    def list_backups(self, prefix: str = "", active_role: str = None) -> list:
        from core.iam_manager import iam_manager
        role = active_role or iam_manager.get_active_role()
        allowed, reason = iam_manager.evaluate_permission("s3:ListBucket", f"arn:aws:s3:::{self.bucket_name}", role)
        if not allowed:
            return []

        backups = []
        for key, versions in self.manifest.get("objects", {}).items():
            if prefix and not key.startswith(prefix):
                continue
            if not versions:
                continue
            latest = versions[0]
            if latest.get("is_delete_marker"):
                continue

            backups.append({
                "key": key,
                "latest_version_id": latest["version_id"],
                "total_versions": len(versions),
                "size_bytes": latest.get("size_bytes", 0),
                "size_kb": latest.get("size_kb", round(latest.get("size_bytes", 0)/1024, 2)),
                "storage_class": latest.get("storage_class", "STANDARD"),
                "encryption": latest.get("encryption", "AES256"),
                "created_at": latest.get("created_at"),
                "sha256": latest.get("sha256"),
                "metadata": latest.get("metadata", {})
            })
        return backups

    def get_document_by_id(self, doc_id: str) -> dict:
        for key, versions in self.manifest.get("objects", {}).items():
            safe_id = key.replace("/", "_").replace("\\", "_")
            if safe_id == doc_id or key == doc_id:
                return {"key": key, "versions": versions}
        return None

    def list_documents(self, department: str = "all", query: str = "", user: dict = None) -> list:
        from core.security_center import security_center
        u = user or security_center.get_current_user()
        results = []

        for key, versions in self.manifest.get("objects", {}).items():
            if not versions:
                continue

            latest = versions[0]
            if latest.get("is_delete_marker"):
                continue

            meta = latest.get("metadata", {})
            dept = meta.get("department")
            if not dept:
                k_lower = key.lower()
                if "env" in k_lower or "weather" in k_lower:
                    dept = "env"
                elif "turbine" in k_lower:
                    dept = "turbine"
                elif "grid" in k_lower or "meter" in k_lower:
                    dept = "grid"
                elif "hvac" in k_lower or "chiller" in k_lower:
                    dept = "hvac"
                else:
                    dept = "env"

            # Filter by department
            if department != "all" and dept != department:
                continue

            filename = key.split("/")[-1]
            desc = meta.get("description", meta.get("sensor_type", "IoT Telemetry Batch"))
            tags = meta.get("tags", "Sensor, S3-Vault, Encrypted")

            # Filter by search query
            if query:
                q_lower = query.lower()
                match = (q_lower in filename.lower() or 
                         q_lower in key.lower() or 
                         q_lower in desc.lower() or 
                         q_lower in tags.lower() or 
                         q_lower in dept.lower())
                if not match:
                    continue

            # Check permissions for current user
            can_read, _ = security_center.check_action_permission("view", dept, u)
            can_delete, _ = security_center.check_action_permission("delete", dept, u)
            can_restore, _ = security_center.check_action_permission("restore", dept, u)

            safe_id = key.replace("/", "_").replace("\\", "_")
            results.append({
                "object_id": safe_id,
                "key": key,
                "filename": filename,
                "department": dept,
                "description": desc,
                "tags": tags,
                "size_bytes": latest.get("size_bytes", 0),
                "size_kb": latest.get("size_kb", round(latest.get("size_bytes", 0)/1024, 2)),
                "storage_class": latest.get("storage_class", "STANDARD"),
                "encryption": latest.get("encryption", "AES256"),
                "uploaded_at": latest.get("created_at", "").replace("T", " ")[:19] + " UTC",
                "latest_version_id": latest.get("version_id"),
                "versions_count": len(versions),
                "sha256": latest.get("sha256"),
                "user_can_read": can_read,
                "user_can_delete": can_delete,
                "user_can_restore": can_restore
            })

        results.sort(key=lambda x: x["uploaded_at"], reverse=True)
        return results

    def get_backup_versions(self, key: str, active_role: str = None) -> dict:
        role = active_role or iam_manager.get_active_role()
        allowed, reason = iam_manager.evaluate_permission("s3:GetObjectVersion", f"arn:aws:s3:::{self.bucket_name}/{key}", role)
        if not allowed:
            return {"success": False, "error": f"403 Forbidden - {reason}"}

        versions = self.manifest.get("objects", {}).get(key, [])
        return {
            "success": True,
            "key": key,
            "bucket": self.bucket_name,
            "versioning_status": self.manifest["versioning"]["status"],
            "versions": versions
        }

    def get_backup_content(self, key: str, version_id: str = None, active_role: str = None) -> dict:
        role = active_role or iam_manager.get_active_role()
        action = "s3:GetObjectVersion" if version_id else "s3:GetObject"
        allowed, reason = iam_manager.evaluate_permission(action, f"arn:aws:s3:::{self.bucket_name}/{key}", role)
        if not allowed:
            return {"success": False, "error": f"403 Forbidden - {reason}"}

        versions = self.manifest.get("objects", {}).get(key, [])
        if not versions:
            return {"success": False, "error": "Object not found"}

        target_version = None
        if version_id:
            for v in versions:
                if v["version_id"] == version_id:
                    target_version = v
                    break
        else:
            target_version = versions[0]

        if not target_version:
            return {"success": False, "error": f"Version {version_id} not found"}

        file_path = Path(target_version["file_path"])
        if not file_path.exists():
            return {"success": False, "error": "Underlying storage object missing"}

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Compute verify hash
        current_hash = self.calculate_sha256(content)
        is_tamper_free = (current_hash == target_version["sha256"])

        return {
            "success": True,
            "key": key,
            "version_id": target_version["version_id"],
            "content": content,
            "sha256": target_version["sha256"],
            "verified_hash": current_hash,
            "integrity_valid": is_tamper_free,
            "storage_class": target_version.get("storage_class", "STANDARD"),
            "encryption": target_version.get("encryption", "AES256"),
            "created_at": target_version["created_at"],
            "metadata": target_version.get("metadata", {})
        }

    def restore_version(self, key: str, version_id: str, active_role: str = None) -> dict:
        """
        Restores a historical version by copying its state as the newest latest version.
        Guarantees non-destructive point-in-time recovery without deleting intermediate versions.
        """
        role = active_role or iam_manager.get_active_role()
        allowed, reason = iam_manager.evaluate_permission("s3:RestoreObject", f"arn:aws:s3:::{self.bucket_name}/{key}", role)
        if not allowed:
            return {"success": False, "status_code": 403, "error": f"403 Forbidden - {reason}"}

        # Fetch historical version
        read_res = self.get_backup_content(key, version_id, active_role=role)
        if not read_res["success"]:
            return read_res

        # Verify integrity before restore
        if not read_res["integrity_valid"]:
            return {
                "success": False,
                "error": "CRITICAL: Integrity verification failed! SHA-256 checksum mismatch. Restore aborted."
            }

        # Put as newest version
        restore_meta = dict(read_res.get("metadata", {}))
        restore_meta["restored_from_version"] = version_id
        restore_meta["restored_at"] = datetime.utcnow().isoformat() + "Z"
        restore_meta["restored_by"] = role

        res = self.put_backup(key, read_res["content"], metadata=restore_meta, active_role=role)
        iam_manager.log_audit_event(
            "s3:RestoreObject",
            f"arn:aws:s3:::{self.bucket_name}/{key}",
            "ALLOW",
            f"Restored historical version {version_id} into new active version {res.get('version_id')}",
            role
        )
        res["restored_source_version"] = version_id
        return res

    def delete_backup(self, key: str, version_id: str = None, active_role: str = None) -> dict:
        role = active_role or iam_manager.get_active_role()
        action = "s3:DeleteObjectVersion" if version_id else "s3:DeleteObject"
        resource_arn = f"arn:aws:s3:::{self.bucket_name}/{key}"

        allowed, reason = iam_manager.evaluate_permission(action, resource_arn, role)
        if not allowed:
            return {"success": False, "status_code": 403, "error": f"403 Forbidden - {reason}"}

        versions = self.manifest.get("objects", {}).get(key, [])
        if not versions:
            return {"success": False, "error": "Object not found"}

        if version_id:
            # Delete specific version
            found_idx = -1
            for idx, v in enumerate(versions):
                if v["version_id"] == version_id:
                    found_idx = idx
                    break
            if found_idx == -1:
                return {"success": False, "error": "Version not found"}

            deleted_v = versions.pop(found_idx)
            try:
                Path(deleted_v["file_path"]).unlink(missing_ok=True)
            except Exception:
                pass

            if versions:
                versions[0]["is_latest"] = True
            else:
                del self.manifest["objects"][key]

            self._save_manifest()
            iam_manager.log_audit_event(action, resource_arn, "ALLOW", f"Permanently deleted object version {version_id}", role)
            return {"success": True, "message": f"Version {version_id} deleted permanently."}
        else:
            # In versioned S3, deleting without versionId creates a DeleteMarker
            delete_marker_id = f"del_{int(time.time())}_{uuid.uuid4().hex[:6]}"
            for v in versions:
                v["is_latest"] = False
            # Insert a delete marker entry
            del_marker = {
                "version_id": delete_marker_id,
                "key": key,
                "is_delete_marker": True,
                "is_latest": True,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "deleted_by": role
            }
            versions.insert(0, del_marker)
            self._save_manifest()
            iam_manager.log_audit_event(action, resource_arn, "ALLOW", f"Placed S3 DeleteMarker {delete_marker_id} on object {key}", role)
            return {"success": True, "delete_marker_id": delete_marker_id, "message": "S3 Delete Marker placed. Object hidden from standard listing."}

    def generate_presigned_url(self, key: str, version_id: str = None, expires_in: int = PRE_SIGNED_URL_EXPIRY_SECONDS) -> str:
        """
        Generates S3 Pre-signed URL token allowing secure, time-limited, signed access.
        """
        expiration_timestamp = int(time.time()) + expires_in
        v_param = f"&versionId={version_id}" if version_id else ""
        signature_base = f"{self.bucket_name}:{key}:{v_param}:{expiration_timestamp}"
        signature = hmac.new(PRESIGNED_SECRET_KEY.encode(), signature_base.encode(), hashlib.sha256).hexdigest()
        
        url = f"/api/download/presigned?bucket={self.bucket_name}&key={key}{v_param}&expires={expiration_timestamp}&signature={signature}"
        return url

    def verify_presigned_signature(self, bucket: str, key: str, version_id: str, expires: int, signature: str) -> bool:
        if int(time.time()) > expires:
            return False # Expired
        v_param = f"&versionId={version_id}" if version_id else ""
        signature_base = f"{bucket}:{key}:{v_param}:{expires}"
        expected = hmac.new(PRESIGNED_SECRET_KEY.encode(), signature_base.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected)

    def advance_simulation_days(self, days_to_add: int) -> dict:
        """
        Simulates time passing for demonstration of S3 Lifecycle Transitions:
        Objects > 30 days -> STANDARD_IA
        Objects > 90 days -> GLACIER
        Noncurrent versions > 365 days -> EXPIRED
        """
        transitions_made = []
        expired_versions = []

        for key, versions in list(self.manifest.get("objects", {}).items()):
            for v in versions:
                if v.get("is_delete_marker"):
                    continue
                current_age = v.get("age_days", 0) + days_to_add
                v["age_days"] = current_age

                old_class = v.get("storage_class", "STANDARD")
                # Evaluate transition
                if current_age >= 90 and old_class != "GLACIER":
                    v["storage_class"] = "GLACIER"
                    transitions_made.append(f"{key} (v: {v['version_id'][:8]}) -> GLACIER (Age: {current_age} days)")
                elif current_age >= 30 and current_age < 90 and old_class == "STANDARD":
                    v["storage_class"] = "STANDARD_IA"
                    transitions_made.append(f"{key} (v: {v['version_id'][:8]}) -> STANDARD_IA (Age: {current_age} days)")

            # Check expiration of non-current versions > 365 days
            surviving = []
            for v in versions:
                if not v.get("is_latest", False) and v.get("age_days", 0) >= 365:
                    expired_versions.append(f"{key} (v: {v['version_id'][:8]}, Age: {v.get('age_days')} days)")
                    try:
                        Path(v["file_path"]).unlink(missing_ok=True)
                    except Exception:
                        pass
                else:
                    surviving.append(v)
            self.manifest["objects"][key] = surviving

        self._save_manifest()
        return {
            "days_advanced": days_to_add,
            "transitions_count": len(transitions_made),
            "transitions": transitions_made,
            "expired_count": len(expired_versions),
            "expired": expired_versions
        }

    def get_storage_stats(self) -> dict:
        total_objects = 0
        total_versions = 0
        total_bytes = 0
        by_class = {"STANDARD": 0, "STANDARD_IA": 0, "GLACIER": 0}

        for key, versions in self.manifest.get("objects", {}).items():
            if versions:
                total_objects += 1
            for v in versions:
                if v.get("is_delete_marker"):
                    continue
                total_versions += 1
                b = v.get("size_bytes", 0)
                total_bytes += b
                s_class = v.get("storage_class", "STANDARD")
                by_class[s_class] = by_class.get(s_class, 0) + b

        return {
            "bucket_name": self.bucket_name,
            "total_objects": total_objects,
            "total_versions": total_versions,
            "total_size_bytes": total_bytes,
            "total_size_mb": round(total_bytes / (1024 * 1024), 3),
            "by_storage_class": {
                "STANDARD_MB": round(by_class.get("STANDARD", 0) / (1024 * 1024), 3),
                "STANDARD_IA_MB": round(by_class.get("STANDARD_IA", 0) / (1024 * 1024), 3),
                "GLACIER_MB": round(by_class.get("GLACIER", 0) / (1024 * 1024), 3),
            },
            "versioning_status": self.manifest["versioning"]["status"],
            "encryption": self.default_encryption,
            "block_public_access": "All 4 settings ENABLED (Private Bucket)"
        }

# Global Singleton instance
storage_engine = StorageEngine()
