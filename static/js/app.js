// Global Client Logic for Secure IoT Data Backup System

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;

    // Reset classes
    toast.className = 'fixed bottom-5 right-5 z-50 transform transition-all duration-300 flex items-center gap-3 px-4 py-3 rounded-xl shadow-2xl border max-w-md text-xs font-mono';

    if (type === 'success') {
        toast.classList.add('bg-emerald-950', 'border-emerald-700', 'text-emerald-200');
        toast.innerHTML = `<i class="fa-solid fa-circle-check text-emerald-400 text-base"></i><span>${message}</span>`;
    } else if (type === 'error') {
        toast.classList.add('bg-rose-950', 'border-rose-700', 'text-rose-200');
        toast.innerHTML = `<i class="fa-solid fa-circle-xmark text-rose-400 text-base"></i><span>${message}</span>`;
    } else {
        toast.classList.add('bg-sky-950', 'border-sky-700', 'text-sky-200');
        toast.innerHTML = `<i class="fa-solid fa-circle-info text-sky-400 text-base"></i><span>${message}</span>`;
    }

    // Show
    toast.classList.remove('translate-y-20', 'opacity-0');
    toast.classList.add('translate-y-0', 'opacity-100');

    setTimeout(() => {
        toast.classList.remove('translate-y-0', 'opacity-100');
        toast.classList.add('translate-y-20', 'opacity-0');
    }, 4500);
}

function switchRole(newRole) {
    fetch('/api/role/switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: newRole })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showToast(`Assumed IAM Role: ${newRole}`, 'success');
            const badge = document.getElementById('headerRoleBadge');
            if (badge) badge.innerText = newRole;
            const cardBadge = document.getElementById('activeRoleCardName');
            if (cardBadge) cardBadge.innerText = newRole;
            setTimeout(() => window.location.reload(), 600);
        } else {
            showToast(data.error || 'Failed to switch role', 'error');
        }
    })
    .catch(err => showToast('Error communicating with IAM service', 'error'));
}

function triggerDailyBackup() {
    const today = new Date().toISOString().split('T')[0];
    const targetDate = prompt("Enter target date for IoT Sensor Daily Ingestion (YYYY-MM-DD):", today);
    if (!targetDate) return;

    showToast("Ingesting multi-sensor batch & computing SHA-256...", "info");

    fetch('/api/backups/daily', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date: targetDate })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showToast(`Daily backup ingested! S3 Version ID: ${data.version_id}`, 'success');
            setTimeout(() => window.location.reload(), 1200);
        } else {
            showToast(data.error || 'Backup upload failed', 'error');
        }
    })
    .catch(err => showToast('Network error during daily backup', 'error'));
}

function verifyIntegrity(key, versionId) {
    showToast(`Computing cryptographic SHA-256 for ${key}...`, 'info');
    fetch('/api/backups/verify-integrity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: key, version_id: versionId })
    })
    .then(r => r.json())
    .then(data => {
        if (data.integrity_passed) {
            alert(`✅ INTEGRITY VERIFICATION PASSED!\n\nObject Key: ${data.key}\nVersion ID: ${data.version_id}\n\nSHA-256 Calculated: ${data.calculated_sha256}\nSHA-256 Expected:   ${data.expected_sha256}\n\nStatus: Tamper-Free & Bit-Perfect Authentic.`);
            showToast("SHA-256 Verified: Bit-perfect integrity confirmed", "success");
        } else {
            alert(`🚨 CRITICAL INTEGRITY ALARM: TAMPERING DETECTED!\n\nObject Key: ${data.key}\nVersion ID: ${data.version_id}\n\nSHA-256 Calculated: ${data.calculated_sha256}\nSHA-256 Expected:   ${data.expected_sha256}\n\nStatus: CORRUPTED OR TAMPERED! File rejected.`);
            showToast("TAMPER DETECTED! SHA-256 Checksum mismatch", "error");
        }
    })
    .catch(err => showToast('Verification failed', 'error'));
}

function simulateTamper(key, versionId) {
    if (!confirm(`Simulate unauthorized bit-flip attack on version: ${versionId}?\nThis injects unauthorized data to prove SHA-256 tamper detection works.`)) return;

    fetch('/api/backups/tamper-simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: key, version_id: versionId })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            alert(`⚠️ Tamper simulation injected successfully!\n\nNow click 'Verify Integrity' on this version to witness the cryptographic alarm.`);
            showToast("Tamper injected. Re-verify integrity now!", "info");
        } else {
            showToast(data.error || 'Tamper simulation failed', 'error');
        }
    });
}

function downloadPresigned(key, versionId) {
    let url = `/api/presigned-url?key=${encodeURIComponent(key)}`;
    if (versionId) url += `&version_id=${encodeURIComponent(versionId)}`;

    fetch(url)
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            const fullUrl = window.location.origin + data.presigned_download_url;
            const openDownload = confirm(`Generated AWS S3 Pre-Signed URL:\n\n${fullUrl}\n\nExpires in: ${data.expires_in_seconds} seconds.\n\nClick OK to initiate secure signed download.`);
            if (openDownload) {
                window.location.href = data.presigned_download_url;
            }
        } else {
            showToast(data.error || 'Access Denied: Cannot generate Pre-Signed URL', 'error');
        }
    })
    .catch(err => showToast('Failed to generate pre-signed URL', 'error'));
}

function restoreVersion(key, versionId) {
    if (!confirm(`Restore historical snapshot version ${versionId}?\nThis safely creates a new latest version with this exact point-in-time state.`)) return;

    fetch('/api/backups/restore', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: key, version_id: versionId })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            alert(`✅ POINT-IN-TIME RESTORE COMPLETED!\n\nRestored from: ${data.restored_source_version}\nPromoted to New Version ID: ${data.version_id}\nStatus: Verified and Active.`);
            showToast("Version restored successfully!", "success");
            setTimeout(() => window.location.reload(), 1000);
        } else {
            alert(`❌ RESTORE OPERATION FAILED:\n\n${data.error || 'Unauthorized or Corrupted'}`);
            showToast(data.error || 'Restore failed', 'error');
        }
    });
}

function deleteBackup(key) {
    if (!confirm(`Delete object backup ${key}?\nNote: S3 Versioning will place a DeleteMarker unless you hold BackupAdmin privileges.`)) return;

    fetch('/api/backups/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: key })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showToast(data.message || 'Object deleted', 'success');
            setTimeout(() => window.location.reload(), 1000);
        } else {
            alert(`🚫 IAM ACCESS DENIED:\n\n${data.error}\n\nNotice that if your active role is 'SensorDevice' or 'Auditor', IAM strictly prevents deleting backup records! Switch to 'BackupAdmin' to perform administrative tasks.`);
            showToast(data.error || 'Delete access denied', 'error');
        }
    });
}

function deleteVersion(key, versionId) {
    if (!confirm(`Permanently purge version ${versionId}?\nThis action requires BackupAdmin role.`)) return;

    fetch('/api/backups/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: key, version_id: versionId })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showToast(data.message || 'Version permanently purged', 'success');
            setTimeout(() => window.location.reload(), 1000);
        } else {
            alert(`🚫 IAM ACCESS DENIED:\n\n${data.error}`);
            showToast(data.error || 'Delete version denied', 'error');
        }
    });
}

function refreshLiveSensors() {
    fetch('/api/sensor/live')
    .then(r => r.json())
    .then(data => {
        showToast("Polled live public & edge telemetry", "info");
        setTimeout(() => window.location.reload(), 500);
    });
}

// ----------------- CHARTS INITIALIZATION ----------------- //

document.addEventListener('DOMContentLoaded', () => {
    // 1. Storage Tier Doughnut Chart
    const tierCanvas = document.getElementById('storageTierChart');
    if (tierCanvas) {
        fetch('/api/stats')
        .then(r => r.json())
        .then(stats => {
            const b = stats.by_storage_class;
            new Chart(tierCanvas, {
                type: 'doughnut',
                data: {
                    labels: ['Standard', 'Standard-IA', 'Glacier'],
                    datasets: [{
                        data: [b.STANDARD_MB, b.STANDARD_IA_MB, b.GLACIER_MB],
                        backgroundColor: ['#0ea5e9', '#f59e0b', '#a855f7'],
                        borderWidth: 2,
                        borderColor: '#0f172a'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { color: '#94a3b8', boxWidth: 12, font: { size: 10 } } }
                    },
                    cutout: '65%'
                }
            });
        });
    }

    // 2. Real-Time Telemetry Line Chart
    const telemetryCanvas = document.getElementById('telemetryChart');
    if (telemetryCanvas) {
        const labels = ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'];
        const tempVals = [24.2, 23.8, 25.1, 28.6, 31.4, 30.2, 27.8, 25.5];
        const vibVals = [1.2, 1.4, 1.3, 1.8, 2.1, 1.9, 1.6, 1.3];
        const powerVals = [190, 185, 210, 235, 240, 225, 215, 198];

        const chart = new Chart(telemetryCanvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Turbine Power (kW)',
                        data: powerVals,
                        borderColor: '#38bdf8',
                        backgroundColor: 'rgba(56, 189, 248, 0.1)',
                        fill: true,
                        tension: 0.35,
                        yAxisID: 'y1'
                    },
                    {
                        label: 'Ambient Temp (°C)',
                        data: tempVals,
                        borderColor: '#f43f5e',
                        backgroundColor: 'transparent',
                        tension: 0.35,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Turbine Vibration (x10 mm/s)',
                        data: vibVals.map(v => v * 10),
                        borderColor: '#10b981',
                        borderDash: [5, 5],
                        backgroundColor: 'transparent',
                        tension: 0.35,
                        yAxisID: 'y'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { grid: { color: '#1e293b' }, ticks: { color: '#64748b', font: { size: 10 } } },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        grid: { color: '#1e293b' },
                        ticks: { color: '#64748b', font: { size: 10 } }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: { drawOnChartArea: false },
                        ticks: { color: '#38bdf8', font: { size: 10 } }
                    }
                },
                plugins: {
                    legend: { labels: { color: '#94a3b8', font: { size: 11 }, boxWidth: 12 } }
                }
            }
        });
    }
});
