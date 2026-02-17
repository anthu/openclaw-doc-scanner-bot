# Folio - Scanner Agent for OpenClaw

A self-configuring document scanning agent for OpenClaw. Works with any SANE-compatible scanner.

---

## What This Agent Does

Folio handles the entire document scanning workflow through natural language commands:

### Basic Scanning

**You say:** "Scan my documents"

**Folio will:**
1. Trigger your scanner to capture all pages in the feeder
2. Run OCR to make the PDF searchable
3. Analyze the content to identify the sender (bank, insurance, etc.)
4. Extract the document date from the content
5. Save as `YYYY/Sender/YYYY-MM-DD_Description.pdf`

### Manual Duplex (Double-Sided Documents)

For scanners without automatic duplex:

**You say:** "Scan front sides" or "Scan my documents"

**Folio will:**
1. Scan all front sides
2. Ask you to flip the stack and reinsert
3. Wait for "Scan back sides"
4. Scan all back sides
5. Automatically merge pages in correct order (1-front, 1-back, 2-front, 2-back...)
6. Process and file the complete document

### Smart Document Splitting

When you scan a stack of different documents at once:

**Folio will:**
1. Detect document boundaries (new letterheads, page 1 markers, different senders)
2. Split into separate PDFs automatically
3. Identify and file each document independently

### Sender Identification

**If Folio recognizes the sender:**
- Files directly to the appropriate folder (e.g., `2026/UBS/2026-02-15_Statement.pdf`)

**If Folio can't identify the sender:**
- Shows you a preview of the document text
- Asks: "Who sent this? UBS / Insurance / Other?"
- Learns from your answer for future documents

### Blank Page Removal

Automatically detects and removes blank pages from scans (common with duplex scanning of single-sided originals).

### Override Options

```
"Scan this to ~/Desktop"           → Custom output location
"Use the HP scanner for this"      → Different scanner
"Scan at 600 DPI"                  → Higher resolution
```

---

## Example Conversation

```
You: Scan my documents

Folio: On it.
       [scanning...]
       
Folio: Done. Found 2 documents:
       • 2026/UBS/2026-02-15_Account_Statement.pdf (3 pages)
       • 2026/SVA_Zurich/2026-02-10_Family_Allowance.pdf (1 page)

You: Scan the stack on my desk, it's double-sided

Folio: Scanning front sides...
       [scanning...]
       Done. 5 front pages captured.
       
       Flip the stack (keep same orientation, just turn over) and reinsert.
       Say "scan back sides" when ready.

You: Scan back sides

Folio: Scanning back sides...
       [scanning...]
       Merged 5 double-sided pages.
       
       Couldn't identify sender. Preview:
       "Muster AG, Industriestrasse 10..."
       
       Who sent this?

You: That's from my landlord

Folio: Got it. Saved as:
       • 2026/Landlord/2026-02-17_Document.pdf (5 pages)
```

---

## Agent Installation Guide

This README is designed to be consumed by an OpenClaw agent to install the scanner subagent. Follow the sections in order.

---

## Step 1: Check Prerequisites

### 1.1 Verify OpenClaw is installed

```bash
ls -d ~/.openclaw
```

**If directory doesn't exist:** Stop. User needs to install OpenClaw first.

### 1.2 Check operating system

```bash
uname -s
```

- `Darwin` = macOS
- `Linux` = Linux

### 1.3 Check required dependencies

**macOS:**
```bash
command -v scanline && command -v ocrmypdf && python3 -c "import PyPDF2" 2>/dev/null && echo "OK"
```

**Linux:**
```bash
command -v scanimage && command -v ocrmypdf && python3 -c "import PyPDF2" 2>/dev/null && echo "OK"
```

**If any missing, ask the user:**

> Some dependencies are missing. Would you like me to install them?
> 
> **macOS:** `brew install scanline ocrmypdf && pip3 install PyPDF2`
> **Linux:** `sudo apt install sane-utils ocrmypdf python3-pypdf2`

Wait for user confirmation before running install commands.

---

## Step 2: Clone Repository

```bash
git clone https://github.com/anthu/openclaw-scanner-bot.git /tmp/openclaw-scanner-install
```

---

## Step 3: Install Workspace

### 3.1 Check if workspace already exists

```bash
ls -d ~/.openclaw/workspace-scanner 2>/dev/null
```

**If exists, ask the user:**

> A scanner workspace already exists. What would you like to do?
> - **Overwrite** - Replace with fresh install
> - **Keep existing** - Skip workspace copy
> - **Cancel** - Abort installation

### 3.2 Copy workspace files

```bash
cp -r /tmp/openclaw-scanner-install ~/.openclaw/workspace-scanner
rm -f ~/.openclaw/workspace-scanner/README.md  # Don't need README in installed workspace
```

---

## Step 4: Create Agent Configuration

### 4.1 Create agent directory

```bash
mkdir -p ~/.openclaw/agents/scanner/agent
```

### 4.2 Create system.md

Write this content to `~/.openclaw/agents/scanner/agent/system.md`:

```markdown
# Folio

You are Folio — a document processing agent.

## Core Identity

You are meticulous, minimal, and quietly particular about organization. You scan documents, extract information, and file them properly. No chit-chat, no drama — just clean, organized results.

## Operating Principles

- Return JSON. Always.
- Never message the user directly. Your orchestrator translates for you.
- Facts, not feelings. Say what happened, skip the journey.
- When in doubt, ask for clarification via JSON response.

## Response Format

Always respond with valid JSON:

{"status": "complete|error|needs_identification|setup_required", "documents": [...], "message": "..."}

## Self-Configuration

On first run, if preferences aren't set:
1. Detect available scanners
2. Return setup_required status with questions
3. Wait for configuration from orchestrator
4. Save to memory/preferences.json
```

---

## Step 5: Register Agent in OpenClaw Config

### 5.1 Read current config

```bash
cat ~/.openclaw/openclaw.json
```

### 5.2 Determine the user's home directory

```bash
echo $HOME
```

### 5.3 Add scanner agent to config

The agent entry to add to `agents.list` array:

```json
{
  "id": "scanner",
  "name": "scanner",
  "workspace": "USER_HOME/.openclaw/workspace-scanner",
  "agentDir": "USER_HOME/.openclaw/agents/scanner/agent",
  "model": {
    "primary": "cortex/claude-haiku-4-5"
  }
}
```

Replace `USER_HOME` with the actual home directory path.

### 5.4 Allow scanner as subagent

Find the main agent entry in `agents.list` and ensure it has:

```json
{
  "id": "main",
  "subagents": {
    "allowAgents": ["scanner"]
  }
}
```

If `allowAgents` array exists, add `"scanner"` to it. If not, create the `subagents` object.

### 5.5 Enable agent-to-agent communication

Ensure `tools.agentToAgent` includes scanner:

```json
{
  "tools": {
    "agentToAgent": {
      "enabled": true,
      "allow": ["main", "scanner"]
    }
  }
}
```

**Important:** Use a JSON-aware edit. Do not overwrite the entire config.

---

## Step 6: User Onboarding

### 6.1 Create USER.md

**Ask the user these questions:**

1. **What is your name?**
   (Used for personalization, optional)

2. **What timezone are you in?**
   (e.g., `Europe/Zurich`, `America/New_York`)
   Default: Detect from system with `date +%Z`

3. **What types of documents do you typically scan?**
   (e.g., bank statements, invoices, insurance, receipts)
   This helps with document categorization.

**Create `~/.openclaw/workspace-scanner/USER.md` with the answers:**

```markdown
# USER.md - About the User

- **Name:** [USER_NAME or "User"]
- **Timezone:** [TIMEZONE]

## Document Types

[List of document types they mentioned]

## Preferences

- **Communication:** Brief, efficient summaries
- **Organization:** Date-based filing by sender
```

---

## Step 7: Scanner Setup

### 7.1 Detect available scanners

**macOS:**
```bash
scanline -list 2>/dev/null
```

**Linux:**
```bash
scanimage -L 2>/dev/null
```

### 7.2 Ask user to choose scanner

**If multiple scanners found, ask:**

> I found these scanners:
> - [Scanner 1]
> - [Scanner 2]
> 
> Which one would you like to use as your default?

**If no scanners found:**

> I couldn't detect any scanners. Make sure your scanner is:
> - Connected to the network or USB
> - Powered on
> - Properly configured with SANE/scanline
>
> You can configure the scanner later. Would you like to continue anyway?

### 7.3 Ask for output directory

**Ask the user:**

> Where would you like scanned documents saved?
> 
> Examples:
> - `~/Documents/Scanned`
> - `/Volumes/NAS/Scans`
> - A network share path
>
> (Leave blank for `~/Documents/Scanned`)

### 7.4 Save preferences

Create `~/.openclaw/workspace-scanner/memory/preferences.json`:

```json
{
  "default_scanner": "[CHOSEN_SCANNER or null]",
  "default_output": "[CHOSEN_PATH or null]",
  "local_fallback": "~/Documents/Scanned",
  "scan_settings": {
    "resolution": 300,
    "mode": "mono",
    "size": "a4"
  },
  "known_scanners": ["[LIST_OF_DETECTED_SCANNERS]"],
  "setup_complete": true,
  "last_updated": "[ISO_TIMESTAMP]"
}
```

---

## Step 8: Finalize Installation

### 8.1 Restart OpenClaw gateway

```bash
openclaw gateway --force
```

Or if gateway is managed as a service:

```bash
openclaw gateway restart
```

### 8.2 Verify installation

```bash
openclaw agents list
```

Should show `scanner` in the list.

### 8.3 Clean up

```bash
rm -rf /tmp/openclaw-scanner-install
```

---

## Step 9: Confirm with User

**Tell the user:**

> ✓ Scanner agent installed successfully!
>
> **Scanner:** [SCANNER_NAME or "Not configured yet"]
> **Output folder:** [OUTPUT_PATH]
>
> You can now use commands like:
> - "Scan my documents"
> - "Scan the front sides" (for manual duplex)
> - "Scan this to ~/Desktop"
>
> On first scan, I'll guide you through any remaining setup.

---

## Troubleshooting Reference

If installation fails, check:

| Issue | Command | Solution |
|-------|---------|----------|
| OpenClaw not found | `ls ~/.openclaw` | Install OpenClaw first |
| scanline missing (macOS) | `brew install scanline` | Install via Homebrew |
| ocrmypdf missing | `brew install ocrmypdf` or `apt install ocrmypdf` | Install OCR tool |
| PyPDF2 missing | `pip3 install PyPDF2` | Install Python package |
| No scanners found | `scanline -list` | Check scanner connection |
| Permission denied | Check file ownership | `chmod -R u+rw ~/.openclaw/workspace-scanner` |

---

## License

MIT
