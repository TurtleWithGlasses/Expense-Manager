import tempfile, subprocess, sys, requests
from packaging.version import Version
from PySide6.QtWidgets import QMessageBox
from version import __version__

LATEST_URL = "http://127.0.0.1:9000/latest.json"

def _download(url: str) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".exe")
    with requests.get(url, stream=True, timeout=30) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=1<<20):
            if chunk: tmp.write(chunk)
    tmp.close()
    return tmp.name

def check_for_updates(parent=None, silent=True):
    try:
        j = requests.get(LATEST_URL, timeout=8).json()
        latest = j.get("version", "")
        url = j.get("installer_url", "")
        notes = j.get("notes", "")
        if not latest or not url:
            return
        if Version(latest) > Version(__version__):
            txt = f"A new version {latest} is available (you have {__version__})."
            if notes: txt += f"\n\n{notes}"
            if QMessageBox.question(parent, "Update available", txt,
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                path = _download(url)
                # Inno Setup silent upgrade; works per-user without admin
                subprocess.Popen([path, "/VERYSILENT", "/NORESTART"])
                from PySide6.QtWidgets import QApplication
                QApplication.instance().quit()
        elif not silent:
            QMessageBox.information(parent, "Up to date", f"You're on {__version__}.")
    except Exception as e:
        if not silent:
            QMessageBox.warning(parent, "Update check failed", str(e))