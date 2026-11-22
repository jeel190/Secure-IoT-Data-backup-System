import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
if os.getenv("VERCEL") == "1":
    DATA_DIR = Path("/tmp/data")
else:
    DATA_DIR = BASE_DIR / "data"
STORAGE_DIR = DATA_DIR / "storage"
BACKUP_DIR = DATA_DIR / "backups"
AUDIT_DIR = DATA_DIR / "audit"

for directory in [DATA_DIR, STORAGE_DIR, BACKUP_DIR, AUDIT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Application Settings
APP_NAME = "Secure IoT Cloud Backup System"
APP_VERSION = "2.4.0"
STUDENT_NAME = "Vasani Jeel"
REGISTER_NO = "24UG00241"
ASSIGNMENT_NO = "18"
PROJECT_DOMAIN = "IoT Data Backup & Cloud Object Storage Security"

# Cloud Object Storage Configuration
BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "iot-secure-telemetry-vault")
STORAGE_PROVIDER = os.getenv("STORAGE_PROVIDER", "LOCAL_S3_SIMULATOR") # Options: LOCAL_S3_SIMULATOR, AWS_S3, AZURE_BLOB
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")

# Security & Object Versioning Defaults
VERSIONING_ENABLED = True
BLOCK_PUBLIC_ACCESS = True
DEFAULT_ENCRYPTION = "AES256" # Server-Side Encryption (SSE-S3)
PRE_SIGNED_URL_EXPIRY_SECONDS = 900 # 15 minutes

# Default Simulated Public Weather / IoT API
PUBLIC_API_URL = "https://api.open-meteo.com/v1/forecast?latitude=12.9716&longitude=77.5946&current=temperature_2m,relative_humidity_2m,apparent_temperature,surface_pressure,wind_speed_10m"
PUBLIC_API_SOURCE = "Open-Meteo Real-time Sensor Weather API (Open Public API)"
