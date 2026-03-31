"""tools/system_tools.py — macOS system interactions"""

import os
import subprocess
import json
import shlex
from pathlib import Path
from datetime import datetime

# Commands that are BLOCKED for safety
BLOCKED = [
    "rm -rf /", "mkfs", "dd if=", ":(){:|:&};:", "fork bomb",
    "sudo rm", "chmod 777 /", "chown", "> /dev/",
]


def _safe(cmd: str) -> bool:
    lc = cmd.lower()
    return not any(b in lc for b in BLOCKED)


class SystemTools:

    def run_command(self, command: str) -> str:
        if not _safe(command):
            return "❌ Command blocked for safety reasons."
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True,
                text=True, timeout=30
            )
            out = result.stdout.strip()
            err = result.stderr.strip()
            if result.returncode != 0 and err:
                return f"⚠️ Exit {result.returncode}:\n{err[:1000]}"
            return out[:2000] if out else "✅ Command completed (no output)"
        except subprocess.TimeoutExpired:
            return "❌ Command timed out (30s limit)"
        except Exception as e:
            return f"❌ Error: {e}"

    def open_app(self, app_name: str) -> str:
        try:
            subprocess.Popen(["open", "-a", app_name])
            return f"✅ Opening {app_name}..."
        except Exception as e:
            return f"❌ Cannot open {app_name}: {e}"

    def get_system_info(self, info_type: str) -> str:
        info = {}
        try:
            if info_type in ("battery", "all"):
                r = subprocess.run(
                    ["pmset", "-g", "batt"], capture_output=True, text=True
                )
                info["battery"] = r.stdout.strip()

            if info_type in ("storage", "all"):
                r = subprocess.run(
                    ["df", "-h", "/"], capture_output=True, text=True
                )
                info["storage"] = r.stdout.strip()

            if info_type in ("memory", "all"):
                r = subprocess.run(
                    ["vm_stat"], capture_output=True, text=True
                )
                info["memory"] = r.stdout.strip()[:500]

            if info_type in ("cpu", "all"):
                r = subprocess.run(
                    ["top", "-l", "1", "-n", "0"],
                    capture_output=True, text=True
                )
                lines = r.stdout.strip().splitlines()[:10]
                info["cpu"] = "\n".join(lines)

            if info_type in ("network", "all"):
                r = subprocess.run(
                    ["ifconfig"], capture_output=True, text=True
                )
                info["network"] = r.stdout.strip()[:800]

            if info_type in ("clipboard", "all"):
                r = subprocess.run(
                    ["pbpaste"], capture_output=True, text=True
                )
                info["clipboard"] = r.stdout.strip()[:200]

            if info_type in ("running_apps", "all"):
                r = subprocess.run(
                    ["osascript", "-e",
                     'tell application "System Events" to get name of every application process whose background only is false'],
                    capture_output=True, text=True
                )
                info["running_apps"] = r.stdout.strip()

        except Exception as e:
            return f"❌ Info error: {e}"

        return json.dumps(info, ensure_ascii=False, indent=2)

    def take_screenshot(self, save_path: str | None = None) -> str:
        if not save_path:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = str(Path.home() / "Desktop" / f"jarvis_screenshot_{ts}.png")
        save_path = str(Path(save_path).expanduser())
        try:
            subprocess.run(["screencapture", "-x", save_path], check=True)
            return f"📸 Screenshot saved: {save_path}"
        except Exception as e:
            return f"❌ Screenshot failed: {e}"

    def set_reminder(self, title: str, datetime_str: str, notes: str = "") -> str:
        script = f'''
        tell application "Reminders"
            set newReminder to make new reminder
            set name of newReminder to "{title}"
            set body of newReminder to "{notes}"
        end tell
        '''
        try:
            subprocess.run(["osascript", "-e", script], check=True)
            return f"⏰ Reminder set: {title}"
        except Exception as e:
            return f"❌ Reminder failed: {e}"

    def send_notification(self, title: str, message: str, sound: bool = True) -> str:
        sound_line = 'sound name "Glass"' if sound else ""
        script = f'''
        display notification "{message}" with title "{title}" {sound_line}
        '''
        try:
            subprocess.run(["osascript", "-e", script], check=True)
            return f"🔔 Notification sent: {title}"
        except Exception as e:
            return f"❌ Notification failed: {e}"
