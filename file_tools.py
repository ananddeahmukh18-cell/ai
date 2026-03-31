"""tools/file_tools.py — Mac file-system operations"""

import os
import glob
import shutil
import subprocess
from pathlib import Path


def _expand(path: str) -> str:
    return str(Path(path).expanduser().resolve())


class FileTools:

    def list_files(self, path: str, pattern: str | None = None) -> str:
        p = _expand(path)
        if not os.path.exists(p):
            return f"❌ Path not found: {p}"
        if pattern:
            items = glob.glob(os.path.join(p, pattern))
        else:
            try:
                items = [os.path.join(p, i) for i in os.listdir(p)]
            except PermissionError:
                return f"❌ Permission denied: {p}"

        if not items:
            return f"📂 Empty directory (or no matches): {p}"

        lines = []
        for item in sorted(items)[:100]:
            name = os.path.basename(item)
            if os.path.isdir(item):
                lines.append(f"📁 {name}/")
            elif os.path.isfile(item):
                size = os.path.getsize(item)
                lines.append(f"📄 {name}  ({self._human_size(size)})")
        return f"Contents of {p}:\n" + "\n".join(lines)

    def read_file(self, path: str) -> str:
        p = _expand(path)
        if not os.path.isfile(p):
            return f"❌ File not found: {p}"
        size = os.path.getsize(p)
        if size > 500_000:
            return f"❌ File too large ({self._human_size(size)}). Use a text editor."
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception as e:
            return f"❌ Cannot read: {e}"

    def write_file(self, path: str, content: str, append: bool = False) -> str:
        p = _expand(path)
        os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
        mode = "a" if append else "w"
        try:
            with open(p, mode, encoding="utf-8") as f:
                f.write(content)
            action = "Appended to" if append else "Written to"
            return f"✅ {action}: {p}"
        except Exception as e:
            return f"❌ Write failed: {e}"

    def move_file(self, source: str, destination: str) -> str:
        s, d = _expand(source), _expand(destination)
        if not os.path.exists(s):
            return f"❌ Source not found: {s}"
        try:
            shutil.move(s, d)
            return f"✅ Moved: {s} → {d}"
        except Exception as e:
            return f"❌ Move failed: {e}"

    def delete_file(self, path: str) -> str:
        """Move to Trash instead of permanent delete (safe)."""
        p = _expand(path)
        if not os.path.exists(p):
            return f"❌ Not found: {p}"
        try:
            # macOS: use AppleScript to move to Trash
            script = f'tell application "Finder" to delete POSIX file "{p}"'
            subprocess.run(["osascript", "-e", script], check=True)
            return f"🗑️ Moved to Trash: {p}"
        except Exception as e:
            return f"❌ Delete failed: {e}"

    def create_folder(self, path: str) -> str:
        p = _expand(path)
        try:
            os.makedirs(p, exist_ok=True)
            return f"✅ Folder created: {p}"
        except Exception as e:
            return f"❌ Folder creation failed: {e}"

    def search_files(self, query: str, in_path: str | None = None) -> str:
        """Use macOS Spotlight (mdfind) for fast file search."""
        cmd = ["mdfind", query]
        if in_path:
            cmd += ["-onlyin", _expand(in_path)]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            lines = result.stdout.strip().splitlines()[:30]
            if not lines:
                return f"🔍 No files found for: {query}"
            return f"🔍 Found {len(lines)} results:\n" + "\n".join(lines)
        except Exception as e:
            return f"❌ Search failed: {e}"

    @staticmethod
    def _human_size(b: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} TB"
