"""tools/web_tools.py — Web search & fetch"""

import os
import json
import urllib.request
import urllib.parse
import html
import re


class WebTools:

    def search(self, query: str, max_results: int = 5) -> str:
        """DuckDuckGo Instant Answer API (no key needed)."""
        try:
            encoded = urllib.parse.quote_plus(query)
            url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"

            req = urllib.request.Request(url, headers={"User-Agent": "JARVIS-Mac/2.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())

            results = []

            # Abstract (main answer)
            if data.get("AbstractText"):
                results.append(f"📖 {data['AbstractText'][:300]}")
                if data.get("AbstractURL"):
                    results.append(f"   🔗 {data['AbstractURL']}")

            # Answer
            if data.get("Answer"):
                results.append(f"✅ {data['Answer']}")

            # Related topics
            for topic in data.get("RelatedTopics", [])[:max_results]:
                if isinstance(topic, dict) and topic.get("Text"):
                    text = topic["Text"][:150]
                    url  = topic.get("FirstURL", "")
                    results.append(f"• {text}\n  🔗 {url}")

            if not results:
                # Fallback: Google search link
                g_url = f"https://www.google.com/search?q={encoded}"
                return f"🔍 No instant results. Try: {g_url}"

            return f"🌐 Search: {query}\n\n" + "\n\n".join(results[:max_results])

        except Exception as e:
            return f"❌ Search error: {e}"

    def fetch(self, url: str) -> str:
        """Fetch a URL and return readable text."""
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) JARVIS/2.0",
                    "Accept": "text/html,application/xhtml+xml,*/*"
                }
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                raw = r.read().decode("utf-8", errors="replace")

            # Strip HTML tags
            text = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL)
            text = re.sub(r"<style[^>]*>.*?</style>",  "", text, flags=re.DOTALL)
            text = re.sub(r"<[^>]+>", " ", text)
            text = html.unescape(text)
            text = re.sub(r"\s+", " ", text).strip()

            return text[:3000] + ("…" if len(text) > 3000 else "")
        except Exception as e:
            return f"❌ Fetch error: {e}"
