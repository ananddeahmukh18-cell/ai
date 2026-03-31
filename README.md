# 🤖 JARVIS-MAC — AI Personal Assistant for macOS

> A real-time Jarvis-like AI assistant for Mac supporting all Indian languages, powered by Claude AI (Anthropic). Voice input, image analysis, file management, web search, and full system control — all from a beautiful browser UI.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-3.0-green?style=flat-square)
![Claude](https://img.shields.io/badge/Claude-Sonnet--4-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🗣️ **Indian Languages** | Hindi, Marathi, Tamil, Telugu, Gujarati, Bengali, Kannada, Malayalam, Punjabi, Urdu + English |
| 🎤 **Voice Input** | Speak in any Indian language via Web Speech API |
| 📷 **Image Analysis** | Upload photos for AI analysis (identify objects, read text, describe scenes) |
| 📁 **File Management** | List, read, write, move, delete, search files across your Mac |
| 💻 **System Control** | Battery, storage, CPU, memory, running apps, clipboard, notifications, reminders |
| 🌐 **Web Search** | Real-time internet search via DuckDuckGo |
| 🚀 **App Launcher** | Open any macOS application by name |
| 📸 **Screenshots** | Take and save Mac screenshots |
| ⚡ **Real-time** | WebSocket-powered streaming responses |
| 🔒 **Safe** | Dangerous commands blocked; delete sends to Trash |

---

## 🛠️ Tech Stack

```
Frontend  →  HTML5 + CSS3 + Vanilla JS + Socket.IO client
Backend   →  Python 3.11 + Flask + Flask-SocketIO (gevent)
AI Brain  →  Anthropic Claude claude-sonnet-4-20250514 (tool use)
Voice     →  Web Speech API (browser-native, Indian language support)
TTS       →  Web Speech Synthesis API
Files     →  Python pathlib + subprocess (mdfind, osascript)
Search    →  DuckDuckGo Instant Answer API (no key needed)
```

---

## 🚀 Quick Start

### Prerequisites
- macOS 12+ (Monterey or later)
- Python 3.11+
- Anthropic API key → [Get one here](https://console.anthropic.com)

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/jarvis-mac.git
cd jarvis-mac
```

### 2. Add your API key
```bash
cp .env.example .env
# Edit .env and set your ANTHROPIC_API_KEY
nano .env
```

### 3. Launch JARVIS
```bash
chmod +x run.sh
./run.sh
```

The browser will automatically open at `http://localhost:5050` 🚀

---

## 📁 Project Structure

```
jarvis-mac/
├── app.py              # Flask + SocketIO server (main entry point)
├── agent.py            # Claude AI agent with agentic tool-use loop
├── tools/
│   ├── __init__.py
│   ├── file_tools.py   # Mac file system operations
│   ├── system_tools.py # macOS system control (battery, apps, notif...)
│   └── web_tools.py    # DuckDuckGo search + URL fetcher
├── templates/
│   └── index.html      # Full frontend (chat UI + voice + image)
├── requirements.txt
├── .env.example
├── run.sh              # One-click launch script
└── README.md
```

---

## 🗣️ Language Examples

| Language | Example Command |
|----------|----------------|
| Hindi    | `मेरे Desktop की files list करो` |
| Marathi  | `माझ्या Downloads मध्ये काय आहे?` |
| Tamil    | `என் Desktop-ல் screenshot எடு` |
| Telugu   | `నా Mac battery status చెప్పు` |
| English  | `Search the web for latest AI news` |

---

## 🔧 Available Tools (15 total)

| Tool | Description |
|------|-------------|
| `list_files` | List directory contents |
| `read_file` | Read file contents |
| `write_file` | Create/edit files |
| `move_file` | Move/rename files |
| `delete_file` | Safe delete (Trash) |
| `create_folder` | Create directories |
| `search_files` | Spotlight file search |
| `run_command` | Execute shell commands |
| `open_app` | Open macOS apps |
| `get_system_info` | Battery/CPU/memory/storage |
| `take_screenshot` | Capture screen |
| `web_search` | DuckDuckGo search |
| `fetch_url` | Read any webpage |
| `set_reminder` | Create macOS reminders |
| `send_notification` | Desktop notifications |

---

## 🔐 Security

- Dangerous shell commands (`rm -rf /`, `sudo rm`, etc.) are blocked
- File deletion uses macOS Trash (recoverable)
- API key stored locally in `.env` (never committed to git)
- No data sent to third parties except Anthropic API

---

## 🗺️ Roadmap

- [ ] Persistent conversation history (SQLite)
- [ ] Custom wake word detection
- [ ] Email integration (macOS Mail)
- [ ] Calendar event creation
- [ ] File content search (grep)
- [ ] Python script execution sandbox
- [ ] iOS Shortcut integration
- [ ] Local LLM support (Ollama)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) file.

---

## 🙏 Credits

Built with [Anthropic Claude API](https://anthropic.com) · [Flask-SocketIO](https://flask-socketio.readthedocs.io) · Web Speech API

---

*Made with ❤️ for Indian users — जय हिंद! 🇮🇳*
