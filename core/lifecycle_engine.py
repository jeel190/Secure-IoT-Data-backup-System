import json
from datetime import datetime
from core.storage_engine import storage_engine
from core.iam_manager import iam_manager

AWS_S3_PRICING_PER_GB_MONTH = {
    "STANDARD": 0.023,       # $0.023 per GB/mo
    "STANDARD_IA": 0.0125,   # $0.0125 per GB/mo (45% savings)
    "GLACIER": 0.004         # $0.004 per GB/mo (82% savings)
}

class LifecycleEngine:
    def __init__(self):
        self.rules = [
            {
                "id": "S3-Lifecycle-IoT-Telemetry-Retention",
                "status": "Enabled",
                "prefix": "sensors/",
                "transitions": [
                    {
                        "days": 30,
                        "target_class": "STANDARD_IA",
                        "description": "Transition active sensor daily backups to Standard Infrequent Access after 30 days"
                    },
                    {
                        "days": 90,
                        "target_class": "GLACIER",
                        "description": "Transition older sensor telemetry to AWS Glacier archival storage after 90 days"
                    }
                ],
                "noncurrent_version_expiration": {
                    "noncurrent_days": 365,
                    "description": "Permanently expire non-current historical versions older than 1 year (365 days)"
                },
                "abort_incomplete_multipart_upload_days": 7
            }
        ]

    def get_lifecycle_rules(self, active_role: str = None) -> dict:
        role = active_role or iam_manager.get_active_role()
        allowed, reason = iam_manager.evaluate_permission(
            "s3:GetLifecycleConfiguration",
            f"arn:aws:s3:::{storage_engine.bucket_name}",
            role
        )
        if not allowed:
            return {"success": False, "error": f"403 Forbidden - {reason}"}

        return {
            "success": True,
            "bucket_name": storage_engine.bucket_name,
            "rules": self.rules
        }

    def simulate_advance_days(self, days: int, active_role: str = None) -> dict:
        role = active_role or iam_manager.get_active_role()
        allowed, reason = iam_manager.evaluate_permission(
            "s3:PutLifecycleConfiguration",
            f"arn:aws:s3:::{storage_engine.bucket_name}",
            role
        )
        if not allowed:
            return {"success": False, "status_code": 403, "error": f"403 Forbidden - {reason}"}

        sim_res = storage_engine.advance_simulation_days(days)
        iam_manager.log_audit_event(
            "s3:LifecycleEvaluator",
            f"arn:aws:s3:::{storage_engine.bucket_name}",
            "ALLOW",
            f"Simulated {days} days time-lapse. Applied {sim_res['transitions_count']} class transitions, {sim_res['expired_count']} expired versions.",
            role
        )
        return {"success": True, "details": sim_res}

    def calculate_cost_savings(self) -> dict:
        stats = storage_engine.get_storage_stats()
        by_class = stats["by_storage_class"]

        std_gb = by_class["STANDARD_MB"] / 1024
        ia_gb = by_class["STANDARD_IA_MB"] / 1024
        glacier_gb = by_class["GLACIER_MB"] / 1024
        total_gb = std_gb + ia_gb + glacier_gb

        # Cost without lifecycle (all Standard)
        cost_all_standard = total_gb * AWS_S3_PRICING_PER_GB_MONTH["STANDARD"]

        # Cost with lifecycle tiering
        actual_cost = (
            (std_gb * AWS_S3_PRICING_PER_GB_MONTH["STANDARD"]) +
            (ia_gb * AWS_S3_PRICING_PER_GB_MONTH["STANDARD_IA"]) +
            (glacier_gb * AWS_S3_PRICING_PER_GB_MONTH["GLACIER"])
        )

        savings_usd = max(0.0, cost_all_standard - actual_cost)
        savings_pct = round((savings_usd / cost_all_standard * 100), 1) if cost_all_standard > 0 else 0.0

        return {
            "total_stored_gb": round(total_gb, 4),
            "tier_breakdown_gb": {
                "STANDARD": round(std_gb, 4),
                "STANDARD_IA": round(ia_gb, 4),
                "GLACIER": round(glacier_gb, 4)
            },
            "unoptimized_monthly_cost_usd": round(cost_all_standard, 4),
            "optimized_monthly_cost_usd": round(actual_cost, 4),
            "monthly_savings_usd": round(savings_usd, 4),
            "percentage_savings": savings_pct
        }

lifecycle_engine = LifecycleEngine()
