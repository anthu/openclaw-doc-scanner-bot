---
name: document-scanner
description: Scan, analyze, split, and organize physical documents. Entry point skill graph for the scanner agent.
---

# Document Scanner

Scan physical documents, intelligently split mixed documents, and organize them with AI-powered sender/date identification.

This is a **skill graph** — follow wikilinks to traverse relevant knowledge based on your current task.

## Graph Structure

```
                    ┌─────────────────┐
                    │  SKILL.md (you) │
                    └────────┬────────┘
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
┌─────────────────┐ ┌───────────────┐ ┌─────────────────┐
│ scanner-discovery│ │document-scanner│ │ document-analysis│
└─────────────────┘ └───────────────┘ └────────┬────────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    ▼              ▼           ▼           ▼              ▼
             ┌──────────┐  ┌────────────┐ ┌─────────┐ ┌──────────┐ ┌───────────┐
             │ sender-  │  │ date-      │ │document-│ │categories│ │confidence-│
             │ identif. │  │ extraction │ │ types   │ │          │ │ levels    │
             └──────────┘  └────────────┘ └─────────┘ └──────────┘ └───────────┘

                              ┌─────────────────┐
                              │   references/   │
                              └────────┬────────┘
         ┌──────────────────┬─────────┼─────────┬──────────────────┐
         ▼                  ▼         ▼         ▼                  ▼
┌──────────────┐ ┌───────────────┐ ┌──────┐ ┌────────────┐ ┌──────────────┐
│ architecture │ │page-grouping  │ │ file-│ │troubleshoot│ │ api-reference│
│              │ │               │ │ org. │ │            │ │              │
└──────────────┘ └───────────────┘ └──────┘ └────────────┘ └──────────────┘
```

## Entry Points by Task

| I need to... | Start here |
|--------------|------------|
| Scan documents | [[document-scanner]] (this file's Quick Start below) |
| Find available scanners | [[scanner-discovery]] |
| Identify a document | [[document-analysis]] |
| Understand date formats | [[date-extraction]] |
| Know document types | [[document-types]] |
| File naming rules | [[file-organization]] |
| Debug an issue | [[troubleshooting]] |
| Understand the pipeline | [[architecture]] |

## Quick Start

**Check setup and list scanners:**
```bash
python3 skills/document-scanner/scripts/scan_and_organize.py setup-check
python3 skills/document-scanner/scripts/scan_and_organize.py list-scanners
```

**Single-sided scan:**
```bash
python3 skills/document-scanner/scripts/scan_and_organize.py single
```

**Duplex scan (front then back):**
```bash
python3 skills/document-scanner/scripts/scan_and_organize.py front
# Wait for response, flip stack, then:
python3 skills/document-scanner/scripts/scan_and_organize.py back --front-pdf /path/from/response.pdf
```

## Complete Workflow

### Step 1: Scan
Run the scan command. The script returns `status: "needs_identification"` with documents in a pending folder.

### Step 2: Identify (YOU do this)
For each document in the response:
1. Read the `text_preview` field
2. Use [[document-analysis]] to identify:
   - **Sender** → [[sender-identification]]
   - **Date** → [[date-extraction]]
   - **Type** → [[document-types]]

### Step 3: Organize
For each identified document, call:
```bash
python3 skills/document-scanner/scripts/scan_and_organize.py organize \
  --id "DOCUMENT_ID" \
  --sender "SenderName" \
  --date "2026-01-15" \
  --type "Rechnung"
```

## Commands

| Command | Description |
|---------|-------------|
| `front` | Scan front sides only (for duplex) |
| `back --front-pdf PATH` | Scan back sides and merge with fronts |
| `single` | Single-sided scan |
| `list-scanners` | List available scanners — see [[scanner-discovery]] |
| `setup-check` | Check configuration |
| `list-pending` | List documents awaiting identification |
| `organize --id ID --sender NAME [--date DATE] [--type TYPE]` | Move pending doc to final location |

## Response Statuses

| Status | Meaning | Next Action |
|--------|---------|-------------|
| `awaiting_flip` | Front sides scanned | Ask user to flip stack, then run `back` |
| `needs_identification` | Documents ready for ID | Use [[document-analysis]], then `organize` |
| `organized` | Document filed | Done |
| `empty` | No pages in feeder | Check scanner |
| `error` | Something failed | See [[troubleshooting]] |

## Configuration

Preferences stored in `memory/preferences.json`:
- `default_scanner` - Scanner to use
- `default_output` - Where to save files (see [[file-organization]])
- `local_fallback` - Backup location if default unavailable

## Troubleshooting

See [[troubleshooting]] for common issues. Quick checks:

**Scanner not found:**
```bash
scanline -list
```

**Poor OCR quality:**
- Increase resolution (try 400 or 600 DPI)
- Ensure documents are clean and flat
