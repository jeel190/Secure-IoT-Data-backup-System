import hashlib
import json
from pathlib import Path
from core.storage_engine import storage_engine
from core.iam_manager import iam_manager

class IntegrityVerifier:
    def verify_backup_integrity(self, key: str, version_id: str = None) -> dict:
        """
        Reads object from storage, computes SHA-256, and compares with recorded manifest hash.
        """
        res = storage_engine.get_backup_content(key, version_id, active_role="BackupAdmin")
        if not res["success"]:
            return res

        expected_hash = res["sha256"]
        actual_hash = res["verified_hash"]
        is_valid = (expected_hash == actual_hash)

        return {
            "key": key,
            "version_id": res["version_id"],
            "expected_sha256": expected_hash,
            "calculated_sha256": actual_hash,
            "integrity_passed": is_valid,
            "status": "SECURE_VERIFIED" if is_valid else "TAMPER_DETECTED",
            "encryption": res.get("encryption", "AES256"),
            "storage_class": res.get("storage_class", "STANDARD")
        }

    def simulate_tamper_attack(self, key: str, version_id: str = None) -> dict:
        """
        Simulates an unauthorized bit-flip or ransomware tampering attack on the underlying storage file.
        Used to demonstrate how cryptographic SHA-256 verification catches unauthorized mutations.
        """
        versions = storage_engine.manifest.get("objects", {}).get(key, [])
        target = None
        for v in versions:
            if not version_id or v["version_id"] == version_id:
                target = v
                break

        if not target:
            return {"success": False, "error": "Object not found"}

        file_path = Path(target["file_path"])
        if not file_path.exists():
            return {"success": False, "error": "Storage file not found"}

        with open(file_path, "a", encoding="utf-8") as f:
            f.write("\n<!-- UNAUTHORIZED_MALICIOUS_INJECTION_DETECTED -->")

        iam_manager.log_audit_event(
            "security:TamperSimulation",
            f"arn:aws:s3:::{storage_engine.bucket_name}/{key}",
            "ALERT",
            f"Tamper simulation injected into version {target['version_id']}. Hash will now mismatch!"
        )

        return {
            "success": True,
            "message": f"Tampered with version {target['version_id']} successfully. Re-verify integrity to see detection!"
        }

integrity_verifier = IntegrityVerifier()
