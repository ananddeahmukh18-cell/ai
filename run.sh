#!/bin/bash
# ──────────────────────────────────────────────
# JARVIS-MAC Launch Script
# ──────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Colors ──────────────────────────────
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════╗"
echo "║         JARVIS-MAC  v2.0  Boot           ║"
echo "║    AI Personal Assistant for macOS       ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# ── Check Python ──────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo -e "${RED}❌ Python 3 not found. Install from https://python.org${NC}"
  exit 1
fi
echo -e "${GREEN}✅ Python: $(python3 --version)${NC}"

# ── Check .env ────────────────────────────────
if [ ! -f ".env" ]; then
  if [ -f ".env.example" ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Created .env from .env.example"
    echo -e "   Please edit .env and add your ANTHROPIC_API_KEY${NC}"
    echo ""
    read -p "Press Enter after editing .env to continue..."
  else
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
  fi
fi

# ── Load API key check ─────────────────────────
source .env 2>/dev/null || true
if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your_anthropic_api_key_here" ]; then
  echo -e "${RED}❌ ANTHROPIC_API_KEY not set in .env${NC}"
  echo -e "   Get your key at: https://console.anthropic.com"
  exit 1
fi
echo -e "${GREEN}✅ API Key loaded${NC}"

# ── Virtual Environment ───────────────────────
if [ ! -d "venv" ]; then
  echo -e "${CYAN}📦 Creating virtual environment...${NC}"
  python3 -m venv venv
fi

source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment active${NC}"

# ── Install Dependencies ──────────────────────
echo -e "${CYAN}📦 Installing/checking dependencies...${NC}"
pip install -r requirements.txt -q --disable-pip-version-check

echo -e "${GREEN}✅ Dependencies ready${NC}"

# ── Launch ────────────────────────────────────
PORT=${PORT:-5050}
echo ""
echo -e "${CYAN}🚀 Starting JARVIS on http://localhost:${PORT}${NC}"
echo -e "${YELLOW}   Press Ctrl+C to stop${NC}"
echo ""

# Open browser after 2s delay
(sleep 2 && open "http://localhost:${PORT}") &

python3 app.py
