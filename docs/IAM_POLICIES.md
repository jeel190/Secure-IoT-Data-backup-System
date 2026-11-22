# Deliverable 3: BackupAdmin Role Configuration & IAM Policies
## Assignment 18: Secure IoT Data Backup System
**Student:** Vasani Jeel | **Reg. No:** 24UG00241

---

### 1. BackupAdmin Role Configuration (Security Task 1)
* **Role Name:** `BackupAdminRole`
* **ARN:** `arn:aws:iam::123456789012:role/BackupAdminRole`
* **Trust Relationship (Trust Policy):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": [
          "ec2.amazonaws.com",
          "backup.amazonaws.com"
        ]
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

* **Attached Permissions Policy (`BackupAdminFullAccessPolicy`):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAllS3BackupOperations",
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
```

---

### 2. Sensor Application Role Configuration (Security Task 2 - Least Privilege)
* **Role Name:** `SensorApplicationRole`
* **ARN:** `arn:aws:iam::123456789012:role/SensorApplicationRole`
* **Trust Relationship:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "iot.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

* **Attached Permissions Policy (`SensorWriteOnlyPolicy`):**
```json
{
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
```

---

### 3. S3 Block Public Access Configuration (Security Task 4)
Applied to bucket `iot-secure-telemetry-vault`:
```json
{
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": true,
    "IgnorePublicAcls": true,
    "BlockPublicPolicy": true,
    "RestrictPublicBuckets": true
  }
}
```

---

### 4. S3 Storage Lifecycle Configuration (Deliverable 5)
```json
{
  "Rules": [
    {
      "ID": "IoTTelemetryArchiveRule",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "sensors/"
      },
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ],
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 365
      },
      "AbortIncompleteMultipartUpload": {
        "DaysAfterInitiation": 7
      }
    }
  ]
}
```
