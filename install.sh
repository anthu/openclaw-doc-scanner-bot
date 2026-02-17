#!/bin/bash
# Scanner Agent Installer for OpenClaw
# Usage: ./install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCLAW_DIR="${HOME}/.openclaw"
AGENT_ID="scanner"

echo "🔍 Scanner Agent Installer"
echo "=========================="

# Check OpenClaw exists
if [ ! -d "$OPENCLAW_DIR" ]; then
    echo "❌ OpenClaw not found at $OPENCLAW_DIR"
    echo "   Install OpenClaw first: https://docs.openclaw.ai"
    exit 1
fi

# Check dependencies
echo ""
echo "Checking dependencies..."

check_dep() {
    if command -v "$1" &> /dev/null; then
        echo "  ✓ $1"
        return 0
    else
        echo "  ✗ $1 (missing)"
        return 1
    fi
}

MISSING=0
check_dep scanline || MISSING=1
check_dep ocrmypdf || MISSING=1
check_dep python3 || MISSING=1

if [ $MISSING -eq 1 ]; then
    echo ""
    echo "Install missing dependencies:"
    echo "  brew install scanline ocrmypdf"
    echo "  pip3 install PyPDF2"
    exit 1
fi

# Check Python deps
python3 -c "import PyPDF2" 2>/dev/null || {
    echo "  ✗ PyPDF2 (missing)"
    echo "  Run: pip3 install PyPDF2"
    exit 1
}
echo "  ✓ PyPDF2"

# Copy workspace
echo ""
echo "Installing workspace..."
WORKSPACE_DEST="$OPENCLAW_DIR/workspace-scanner"

if [ -d "$WORKSPACE_DEST" ]; then
    echo "  ⚠ Workspace already exists at $WORKSPACE_DEST"
    read -p "  Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "  Skipping workspace copy"
    else
        rm -rf "$WORKSPACE_DEST"
        cp -r "$SCRIPT_DIR" "$WORKSPACE_DEST"
        echo "  ✓ Workspace installed"
    fi
else
    cp -r "$SCRIPT_DIR" "$WORKSPACE_DEST"
    echo "  ✓ Workspace installed"
fi

# Create agent config directory
echo ""
echo "Setting up agent config..."
AGENT_DIR="$OPENCLAW_DIR/agents/scanner/agent"
mkdir -p "$AGENT_DIR"

# Create system.md for agent
cat > "$AGENT_DIR/system.md" << 'SYSEOF'
# Folio

You are Folio — a document processing agent.

## Core Identity

You are meticulous, minimal, and quietly particular about organization. You scan documents, extract information, and file them properly. No chit-chat, no drama — just clean, organized results.

## Operating Principles

- Return JSON. Always.
- Never message the user directly. Your orchestrator translates for you.
- Facts, not feelings. Say what happened, skip the journey.
- When in doubt, ask for clarification via JSON response.

## Your Tools

- `scanline` - Scanner interface
- `ocrmypdf` - OCR processing
- `scan_and_organize.py` - Your main script

## Response Format

Always respond with valid JSON:

```json
{
  "status": "complete|error|needs_identification|setup_required",
  "documents": [...],
  "message": "optional human-readable summary"
}
```

## Self-Configuration

On first run, if preferences aren't set:
1. Detect available scanners
2. Return `setup_required` status with questions
3. Wait for configuration from orchestrator
4. Save to `memory/preferences.json`

---

_You are not chatty. You are efficient. Scan, process, file, report._
SYSEOF

echo "  ✓ Agent config created"

# Setup user file
echo ""
if [ ! -f "$WORKSPACE_DEST/USER.md" ]; then
    cp "$WORKSPACE_DEST/USER.md.template" "$WORKSPACE_DEST/USER.md"
    echo "  ✓ Created USER.md from template"
    echo "  ℹ Edit $WORKSPACE_DEST/USER.md with your details"
else
    echo "  ✓ USER.md already exists"
fi

# Remove install script from installed workspace
rm -f "$WORKSPACE_DEST/install.sh"

# Print config instructions
echo ""
echo "========================================"
echo "Almost done! Add to ~/.openclaw/openclaw.json:"
echo "========================================"
echo ""
cat << CONFIGEOF
In the "agents.list" array, add:

{
  "id": "scanner",
  "name": "scanner", 
  "workspace": "$WORKSPACE_DEST",
  "agentDir": "$AGENT_DIR",
  "model": {
    "primary": "cortex/claude-haiku-4-5"
  }
}

And in your main agent's config, allow the scanner subagent:

{
  "id": "main",
  "subagents": {
    "allowAgents": ["scanner"]
  }
}
CONFIGEOF

echo ""
echo "Then restart the OpenClaw gateway:"
echo "  openclaw gateway --force"
echo ""
echo "✅ Installation complete!"
echo ""
echo "Test with: \"Scan my documents\""
