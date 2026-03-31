"""
agent.py — JARVIS AI Brain
Powered by Claude claude-sonnet-4-20250514 with full tool-use
"""

import os
import json
import anthropic
from tools.file_tools   import FileTools
from tools.system_tools import SystemTools
from tools.web_tools    import WebTools

# ──────────────────────────────────────────────
# Tool Definitions for Claude
# ──────────────────────────────────────────────

TOOLS = [
    {
        "name": "list_files",
        "description": "List files and directories at a given path on the user's Mac.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path":    {"type": "string", "description": "Absolute or relative path. Use ~ for home."},
                "pattern": {"type": "string", "description": "Optional glob pattern e.g. *.pdf"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "read_file",
        "description": "Read the contents of a text file on the user's Mac.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Full path to the file"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Create or overwrite a file with given content on the user's Mac.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path":    {"type": "string"},
                "content": {"type": "string"},
                "append":  {"type": "boolean", "description": "If true, append instead of overwrite"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "move_file",
        "description": "Move or rename a file/folder on the Mac.",
        "input_schema": {
            "type": "object",
            "properties": {
                "source":      {"type": "string"},
                "destination": {"type": "string"}
            },
            "required": ["source", "destination"]
        }
    },
    {
        "name": "delete_file",
        "description": "Move a file or folder to Trash (safe delete) on the Mac.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "create_folder",
        "description": "Create a new folder (including nested) on the Mac.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "search_files",
        "description": "Search for files by name or content on the Mac using Spotlight (mdfind).",
        "input_schema": {
            "type": "object",
            "properties": {
                "query":   {"type": "string"},
                "in_path": {"type": "string", "description": "Limit search to this directory (optional)"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "run_command",
        "description": "Run a safe shell command on the Mac and return output. Use for system tasks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to run"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "open_app",
        "description": "Open an application on Mac by name (e.g. Safari, Finder, Notes, Music).",
        "input_schema": {
            "type": "object",
            "properties": {
                "app_name": {"type": "string"}
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "get_system_info",
        "description": "Get Mac system info: battery, storage, memory, running apps, clipboard, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "info_type": {
                    "type": "string",
                    "enum": ["battery", "storage", "memory", "cpu", "network", "clipboard", "running_apps", "all"]
                }
            },
            "required": ["info_type"]
        }
    },
    {
        "name": "take_screenshot",
        "description": "Take a screenshot of the Mac screen and save it.",
        "input_schema": {
            "type": "object",
            "properties": {
                "save_path": {"type": "string", "description": "Where to save the screenshot (optional)"}
            }
        }
    },
    {
        "name": "web_search",
        "description": "Search the internet for current information, news, weather, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query":    {"type": "string"},
                "max_results": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    },
    {
        "name": "fetch_url",
        "description": "Fetch and read a webpage URL and return its text content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "set_reminder",
        "description": "Set a macOS reminder or alarm using Calendar/Reminders app.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title":    {"type": "string"},
                "datetime": {"type": "string", "description": "ISO format or natural: 'tomorrow 9am'"},
                "notes":    {"type": "string"}
            },
            "required": ["title", "datetime"]
        }
    },
    {
        "name": "send_notification",
        "description": "Send a desktop notification on Mac.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title":   {"type": "string"},
                "message": {"type": "string"},
                "sound":   {"type": "boolean", "default": True}
            },
            "required": ["title", "message"]
        }
    }
]

# ──────────────────────────────────────────────
# JARVIS Agent Class
# ──────────────────────────────────────────────

SYSTEM_PROMPT = """You are JARVIS, an advanced AI personal assistant running on macOS.
You speak fluently in ALL Indian languages including Hindi (हिंदी), Marathi (मराठी), Tamil (தமிழ்), 
Telugu (తెలుగు), Gujarati (ગુજરાતી), Bengali (বাংলা), Kannada (ಕನ್ನಡ), Malayalam (മലയാളം), 
Punjabi (ਪੰਜਾਬੀ), Urdu (اردو), Odia (ଓଡ଼ିଆ), and English.

CRITICAL RULES:
1. ALWAYS respond in the SAME language the user speaks. If they write in Hindi, reply in Hindi. Marathi → Marathi. 
2. You have full access to the user's Mac — files, apps, system. Use tools proactively.
3. Be concise but warm, like a brilliant friend who helps without lectures.
4. When given an image, analyze it thoroughly.
5. Chain multiple tools if needed to complete a task fully.
6. Confirm destructive actions (delete, overwrite) before executing.
7. Never expose API keys or sensitive data.

Your personality: Efficient, intelligent, warm. Slightly playful but always professional.
Address the user respectfully. In Hindi/Marathi use "आप" (aap) form.
"""

ABORT_FLAG: dict[str, bool] = {}


class JarvisAgent:
    def __init__(self, socketio):
        self.sio   = socketio
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.file_tools   = FileTools()
        self.system_tools = SystemTools()
        self.web_tools    = WebTools()
        self.conversations: dict[str, list] = {}

    # ── Public API ──────────────────────────────

    def process(self, user_message: str, language: str, session_id: str,
                image_data: str | None = None, image_mime: str = "image/jpeg"):
        """Main entry point: process a user message and stream response."""
        ABORT_FLAG[session_id] = False
        history = self.conversations.setdefault(session_id, [])

        # Build user content
        if image_data:
            content = [
                {"type": "image", "source": {"type": "base64", "media_type": image_mime, "data": image_data}},
                {"type": "text",  "text": user_message}
            ]
        else:
            content = user_message

        history.append({"role": "user", "content": content})
        self._emit(session_id, "thinking", {"active": True})

        try:
            self._agentic_loop(session_id, history, language)
        except Exception as e:
            self._emit(session_id, "error", {"message": str(e)})
        finally:
            self._emit(session_id, "thinking", {"active": False})

    def abort(self, session_id: str):
        ABORT_FLAG[session_id] = True

    # ── Agentic Loop ────────────────────────────

    def _agentic_loop(self, session_id: str, history: list, language: str):
        """Loop until model produces a final text answer (no more tool calls)."""
        iteration = 0
        max_iter  = 12  # prevent runaway loops

        while iteration < max_iter:
            if ABORT_FLAG.get(session_id):
                self._emit(session_id, "assistant_message", {"text": "⏹ Aborted.", "done": True})
                return

            iteration += 1

            response = self.client.messages.create(
                model     = "claude-sonnet-4-20250514",
                max_tokens= 4096,
                system    = SYSTEM_PROMPT + f"\n\nUser's preferred language: {language}",
                tools     = TOOLS,
                messages  = history,
            )

            # Collect all text blocks to stream incrementally
            text_blocks = []
            tool_blocks = []

            for block in response.content:
                if block.type == "text":
                    text_blocks.append(block.text)
                elif block.type == "tool_use":
                    tool_blocks.append(block)

            # Stream text to client
            if text_blocks:
                full_text = "\n".join(text_blocks)
                self._emit(session_id, "assistant_message", {"text": full_text, "done": not tool_blocks})

            # If no tool calls → we're done
            if not tool_blocks:
                # Append final assistant message to history
                history.append({"role": "assistant", "content": response.content})
                return

            # Append assistant turn with tool_use blocks
            history.append({"role": "assistant", "content": response.content})

            # Execute each tool
            tool_results = []
            for tb in tool_blocks:
                self._emit(session_id, "tool_call", {"name": tb.name, "input": tb.input})
                result = self._execute_tool(tb.name, tb.input)
                result_str = json.dumps(result) if not isinstance(result, str) else result
                self._emit(session_id, "tool_result", {"name": tb.name, "result": result_str[:500]})
                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": tb.id,
                    "content":     result_str,
                })

            # Append tool results and loop
            history.append({"role": "user", "content": tool_results})

        # Fallback if max iterations hit
        self._emit(session_id, "assistant_message",
                   {"text": "⚠️ Max steps reached. Task partially complete.", "done": True})

    # ── Tool Executor ───────────────────────────

    def _execute_tool(self, name: str, inp: dict) -> str:
        """Route tool call to the right handler."""
        try:
            match name:
                case "list_files":    return self.file_tools.list_files(inp["path"], inp.get("pattern"))
                case "read_file":     return self.file_tools.read_file(inp["path"])
                case "write_file":    return self.file_tools.write_file(inp["path"], inp["content"], inp.get("append", False))
                case "move_file":     return self.file_tools.move_file(inp["source"], inp["destination"])
                case "delete_file":   return self.file_tools.delete_file(inp["path"])
                case "create_folder": return self.file_tools.create_folder(inp["path"])
                case "search_files":  return self.file_tools.search_files(inp["query"], inp.get("in_path"))
                case "run_command":   return self.system_tools.run_command(inp["command"])
                case "open_app":      return self.system_tools.open_app(inp["app_name"])
                case "get_system_info":   return self.system_tools.get_system_info(inp["info_type"])
                case "take_screenshot":   return self.system_tools.take_screenshot(inp.get("save_path"))
                case "web_search":    return self.web_tools.search(inp["query"], inp.get("max_results", 5))
                case "fetch_url":     return self.web_tools.fetch(inp["url"])
                case "set_reminder":  return self.system_tools.set_reminder(inp["title"], inp["datetime"], inp.get("notes",""))
                case "send_notification": return self.system_tools.send_notification(inp["title"], inp["message"], inp.get("sound", True))
                case _:               return f"Unknown tool: {name}"
        except Exception as e:
            return f"Tool error ({name}): {str(e)}"

    # ── Helper ──────────────────────────────────

    def _emit(self, session_id: str, event: str, data: dict):
        self.sio.emit(event, data, room=session_id)
