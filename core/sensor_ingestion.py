import json
import random
import time
from datetime import datetime, timedelta
import requests
from config import PUBLIC_API_URL, PUBLIC_API_SOURCE
from core.storage_engine import storage_engine
from core.iam_manager import iam_manager

DEVICE_TYPES = {
    "ENV-STATION-01": {
        "location": "North Campus - Weather Mast",
        "type": "Environmental & Air Quality",
        "metrics": ["temperature_c", "humidity_pct", "pm25_ug_m3", "co2_ppm", "uv_index"]
    },
    "TURBINE-EDGE-04": {
        "location": "Generator Hall 2 - Wind Turbine Unit 4",
        "type": "Industrial Rotary Machinery",
        "metrics": ["vibration_mms", "bearing_temp_c", "rpm", "oil_pressure_psi", "power_output_kw"]
    },
    "SMART-METER-09": {
        "location": "Substation 3B - Smart Grid Node",
        "type": "Energy Grid Telemetry",
        "metrics": ["voltage_v", "current_a", "active_power_kw", "frequency_hz", "power_factor"]
    },
    "FACTORY-HVAC-12": {
        "location": "Cleanroom 1 - HVAC Chiller Plant",
        "type": "Precision Climate Control",
        "metrics": ["chilled_water_temp_c", "airflow_cfm", "compressor_load_pct", "filter_diff_pressure_kpa"]
    }
}

class SensorIngestionEngine:
    def __init__(self):
        self.device_catalog = DEVICE_TYPES

    def fetch_live_public_weather_iot(self) -> dict:
        """
        Fetches live open environmental telemetry from Open-Meteo API
        (Public APIs GitHub showcase integration).
        """
        try:
            resp = requests.get(PUBLIC_API_URL, timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current", {})
                return {
                    "source": PUBLIC_API_SOURCE,
                    "status": "ONLINE",
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude"),
                    "elevation": data.get("elevation"),
                    "timestamp": current.get("time"),
                    "live_readings": {
                        "temperature_c": current.get("temperature_2m"),
                        "relative_humidity_pct": current.get("relative_humidity_2m"),
                        "apparent_temperature_c": current.get("apparent_temperature"),
                        "surface_pressure_hpa": current.get("surface_pressure"),
                        "wind_speed_kmh": current.get("wind_speed_10m")
                    }
                }
        except Exception as e:
            pass

        # Fallback simulated live weather if offline or network restricted
        return {
            "source": PUBLIC_API_SOURCE + " (Simulated Mode)",
            "status": "CACHED_OFFLINE",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "live_readings": {
                "temperature_c": round(random.uniform(24.5, 31.8), 2),
                "relative_humidity_pct": round(random.uniform(55.0, 78.5), 1),
                "apparent_temperature_c": round(random.uniform(26.0, 33.0), 2),
                "surface_pressure_hpa": round(random.uniform(1008.0, 1014.0), 1),
                "wind_speed_kmh": round(random.uniform(8.0, 22.5), 1)
            }
        }

    def generate_single_reading(self, device_id: str) -> dict:
        info = self.device_catalog.get(device_id, {})
        dev_type = info.get("type", "Generic IoT")
        now_str = datetime.utcnow().isoformat() + "Z"

        if device_id == "ENV-STATION-01":
            return {
                "device_id": device_id,
                "timestamp": now_str,
                "type": dev_type,
                "location": info["location"],
                "data": {
                    "temperature_c": round(random.uniform(22.0, 35.0), 2),
                    "humidity_pct": round(random.uniform(40.0, 85.0), 1),
                    "pm25_ug_m3": round(random.uniform(12.0, 68.0), 1),
                    "co2_ppm": round(random.uniform(410.0, 680.0), 1),
                    "uv_index": round(random.uniform(1.0, 9.5), 1)
                }
            }
        elif device_id == "TURBINE-EDGE-04":
            return {
                "device_id": device_id,
                "timestamp": now_str,
                "type": dev_type,
                "location": info["location"],
                "data": {
                    "vibration_mms": round(random.uniform(0.8, 3.2), 2),
                    "bearing_temp_c": round(random.uniform(52.0, 79.5), 1),
                    "rpm": round(random.uniform(1450.0, 1530.0), 0),
                    "oil_pressure_psi": round(random.uniform(45.0, 58.0), 1),
                    "power_output_kw": round(random.uniform(180.0, 240.0), 1)
                }
            }
        elif device_id == "SMART-METER-09":
            return {
                "device_id": device_id,
                "timestamp": now_str,
                "type": dev_type,
                "location": info["location"],
                "data": {
                    "voltage_v": round(random.uniform(228.0, 242.0), 1),
                    "current_a": round(random.uniform(18.0, 42.5), 2),
                    "active_power_kw": round(random.uniform(4.1, 9.8), 2),
                    "frequency_hz": round(random.uniform(49.85, 50.15), 2),
                    "power_factor": round(random.uniform(0.92, 0.99), 2)
                }
            }
        else: # FACTORY-HVAC-12
            return {
                "device_id": device_id,
                "timestamp": now_str,
                "type": dev_type,
                "location": info["location"],
                "data": {
                    "chilled_water_temp_c": round(random.uniform(5.5, 8.2), 1),
                    "airflow_cfm": round(random.uniform(3200.0, 3600.0), 0),
                    "compressor_load_pct": round(random.uniform(62.0, 88.0), 1),
                    "filter_diff_pressure_kpa": round(random.uniform(0.15, 0.45), 2)
                }
            }

    def generate_daily_csv_payload(self, target_date: str = None, hours: int = 12) -> str:
        """
        Creates sample daily sensor telemetry in CSV format (e.g. temperature_2026-11-22.csv).
        Matches AgroSense / LoRaWAN industrial temperature and humidity sensor logs.
        """
        date_str = target_date or datetime.utcnow().strftime("%Y-%m-%d")
        lines = ["timestamp,sensor_id,location,temperature_c,humidity_pct,surface_pressure_hpa,status"]
        for hour in range(hours):
            t_str = f"{date_str}T{hour+8:02d}:00:00Z"
            temp = round(random.uniform(26.5, 31.0) + (hour * 0.3), 2)
            hum = round(random.uniform(48.0, 56.5) - (hour * 0.4), 1)
            press = round(random.uniform(1011.0, 1013.5), 1)
            lines.append(f"{t_str},ENV-STATION-01,North Campus Mast,{temp},{hum},{press},OPERATIONAL")
        return "\n".join(lines)

    def generate_daily_batch_payload(self, target_date: str = None, readings_per_device: int = 24) -> dict:
        """
        Creates a structured daily IoT sensor backup payload containing
        hourly readings across all registered sensor nodes plus public meteorological feed.
        """
        date_str = target_date or datetime.utcnow().strftime("%Y-%m-%d")
        payload = {
            "backup_manifest_version": "2.0-cloud",
            "backup_date": date_str,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "cloud_vault": storage_engine.bucket_name,
            "ingestion_agent": "SensorEdgeDaemon-v1.8",
            "public_weather_reference": self.fetch_live_public_weather_iot(),
            "sensor_nodes": list(self.device_catalog.keys()),
            "total_records": readings_per_device * len(self.device_catalog),
            "telemetry_records": []
        }

        # Generate hourly readings
        base_time = datetime.strptime(date_str, "%Y-%m-%d")
        for hour in range(readings_per_device):
            reading_time = base_time + timedelta(hours=hour)
            time_iso = reading_time.isoformat() + "Z"
            for dev_id in self.device_catalog.keys():
                reading = self.generate_single_reading(dev_id)
                reading["timestamp"] = time_iso
                payload["telemetry_records"].append(reading)

        return payload

    def backup_daily_sensors(self, target_date: str = None, active_role: str = "SensorDevice") -> dict:
        """
        Executes daily backup upload to S3 object storage with versioning.
        Uses SensorDevice IAM role (least privilege).
        """
        date_str = target_date or datetime.utcnow().strftime("%Y-%m-%d")
        payload = self.generate_daily_batch_payload(date_str)
        payload_json = json.dumps(payload, indent=2)

        s3_key = f"sensors/daily_telemetry_{date_str}.json"
        metadata = {
            "backup_date": date_str,
            "sensor_type": "Multi-Sensor IoT Daily Telemetry",
            "record_count": payload["total_records"],
            "compression": "none",
            "origin_ip": "10.0.4.15"
        }

        result = storage_engine.put_backup(
            key=s3_key,
            data_content=payload_json,
            metadata=metadata,
            active_role=active_role
        )

        return result

    def seed_initial_historical_backups(self):
        """
        Pre-populates the vault with categorized daily backups and version chains
        across all 4 departments (env, turbine, grid, hvac).
        """
        if storage_engine.get_document_by_id("sensors/env/temperature_2026-11-22.csv"):
            return

        print("[*] Initializing categorized IoT sensor archives in S3 vault...")
        today = datetime.utcnow().strftime("%Y-%m-%d")

        seeds = [
            {
                "key": "sensors/env/temperature_2026-11-22.csv",
                "dept": "env",
                "device_id": "ENV-STATION-01",
                "desc": "AgroSense Air Temperature & Humidity Daily Log (LoRaWAN IoT)",
                "tags": "AgroSense, Temperature, Humidity, CSV",
                "versions": 3,
                "is_csv": True
            },
            {
                "key": "sensors/env/ambient_weather_mast.json",
                "dept": "env",
                "device_id": "ENV-STATION-01",
                "desc": "North Campus Meteorological Mast & Ambient Weather Telemetry",
                "tags": "Weather, Temperature, Ambient, IoT",
                "versions": 3
            },
            {
                "key": "sensors/env/air_quality_north.json",
                "dept": "env",
                "device_id": "ENV-STATION-01",
                "desc": "Air Quality Particle Count (PM2.5, CO2, Humidity) Daily Batch",
                "tags": "AirQuality, PM2.5, Sensors",
                "versions": 1
            },
            {
                "key": "sensors/turbine/wind_turbine_unit4.json",
                "dept": "turbine",
                "device_id": "TURBINE-EDGE-04",
                "desc": "Generator Hall 2 Wind Turbine Unit 4 RPM & Bearing Temperature",
                "tags": "Turbine, Industrial, Bearing, Energy",
                "versions": 3
            },
            {
                "key": "sensors/turbine/vibration_analysis.json",
                "dept": "turbine",
                "device_id": "TURBINE-EDGE-04",
                "desc": "High Frequency Vibration Spectrum & Harmonics Analysis",
                "tags": "Vibration, Predictive-Maintenance, FFT",
                "versions": 1
            },
            {
                "key": "sensors/grid/substation_3b_power.json",
                "dept": "grid",
                "device_id": "SMART-METER-09",
                "desc": "Substation 3B 3-Phase Grid Voltage, Current & Power Factor",
                "tags": "SmartGrid, Voltage, Substation, Power",
                "versions": 2
            },
            {
                "key": "sensors/grid/transformer_telemetry.json",
                "dept": "grid",
                "device_id": "SMART-METER-09",
                "desc": "Step-Down Transformer Thermal Load & Reactive Power Telemetry",
                "tags": "Transformer, Grid-Safety, Thermal",
                "versions": 1
            },
            {
                "key": "sensors/hvac/chiller_plant_cleanroom.json",
                "dept": "hvac",
                "device_id": "FACTORY-HVAC-12",
                "desc": "Cleanroom 1 Chiller Loop, Differential Pressure & Airflow CFM",
                "tags": "Cleanroom, Chiller, HVAC, Airflow",
                "versions": 3
            },
            {
                "key": "sensors/hvac/compressor_runtime.json",
                "dept": "hvac",
                "device_id": "FACTORY-HVAC-12",
                "desc": "Industrial Refrigerant Compressor Load & Duty Cycle Log",
                "tags": "Compressor, DutyCycle, HVAC",
                "versions": 1
            }
        ]

        for s in seeds:
            # Skip if already exists
            existing_doc = storage_engine.get_document_by_id(s["key"])
            if existing_doc and len(existing_doc.get("versions", [])) >= s["versions"]:
                continue

            for v_idx in range(s["versions"]):
                if s.get("is_csv"):
                    content_str = self.generate_daily_csv_payload(today, hours=12)
                    if v_idx > 0:
                        content_str += f"\n# Snapshot v{v_idx + 1}: Recalibrated reading offset applied."
                    rec_count = 12
                else:
                    payload = self.generate_daily_batch_payload(today, readings_per_device=24)
                    payload["device_source"] = s["device_id"]
                    payload["snapshot_revision"] = f"v{v_idx + 1}.0"
                    if v_idx > 0:
                        payload["revision_notes"] = f"Snapshot version {v_idx + 1}: Sensor recalibration applied."
                    content_str = json.dumps(payload, indent=2)
                    rec_count = payload["total_records"]

                meta = {
                    "department": s["dept"],
                    "description": s["desc"],
                    "tags": s["tags"],
                    "sensor_type": s["desc"],
                    "device_id": s["device_id"],
                    "backup_date": today,
                    "record_count": rec_count
                }
                storage_engine.put_backup(
                    key=s["key"],
                    data_content=content_str,
                    metadata=meta,
                    active_role="BackupAdmin"
                )

        print("[*] Seeded categorized IoT sensor backup archives with multiple versions.")

sensor_ingestion_engine = SensorIngestionEngine()
