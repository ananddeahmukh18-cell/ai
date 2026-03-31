"""
JARVIS-MAC — AI Personal Assistant for macOS
Real-time Flask + SocketIO backend with Claude AI
"""

import os
import base64
import json
import threading
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from agent import JarvisAgent

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "jarvis-mac-secret-2024")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

agent = JarvisAgent(socketio=socketio)


# ──────────────────────────────────────────────
# HTTP Routes
# ──────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "version": "2.0.0"})


# ──────────────────────────────────────────────
# SocketIO Events
# ──────────────────────────────────────────────

@socketio.on("connect")
def on_connect():
    print(f"[+] Client connected: {request.sid}")
    emit("status", {"msg": "Connected to JARVIS", "ready": True})


@socketio.on("disconnect")
def on_disconnect():
    print(f"[-] Client disconnected: {request.sid}")


@socketio.on("chat_message")
def handle_chat(data):
    """Handle text/voice message from user."""
    message  = data.get("message", "").strip()
    language = data.get("language", "en")
    session_id = request.sid

    if not message:
        return

    # Run agent in background thread so SocketIO stays responsive
    def run():
        agent.process(
            user_message=message,
            language=language,
            session_id=session_id,
        )

    threading.Thread(target=run, daemon=True).start()


@socketio.on("image_message")
def handle_image(data):
    """Handle image + optional text from user."""
    image_b64  = data.get("image")          # base64 string
    mime_type  = data.get("mime", "image/jpeg")
    message    = data.get("message", "इस इमेज को analyze करो")
    language   = data.get("language", "en")
    session_id = request.sid

    def run():
        agent.process(
            user_message=message,
            language=language,
            session_id=session_id,
            image_data=image_b64,
            image_mime=mime_type,
        )

    threading.Thread(target=run, daemon=True).start()


@socketio.on("abort")
def handle_abort(data):
    agent.abort(request.sid)


# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5050))
    print(f"""
╔══════════════════════════════════════════╗
║        JARVIS-MAC  v2.0  Online          ║
║  Open → http://localhost:{port}              ║
╚══════════════════════════════════════════╝
    """)
    socketio.run(app, host="0.0.0.0", port=port, debug=False, use_reloader=False)
