---
name: document-scanner
description: Scan, analyze, split, and organize physical documents. Use when the user asks to scan documents, organize scanned mail, process physical letters, or digitize paperwork. Handles multi-page documents, automatic page reordering, and organized filing with AI-powered document identification.
---

# Document Scanner

Scan physical documents, intelligently split mixed documents, and organize them with AI-powered sender/date identification.

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
2. Use the **document-analysis** skill guidelines to identify:
   - **Sender** - Who sent it (e.g., "UBS", "Cornercard", "SVA_Zurich")
   - **Date** - Document date in YYYY-MM-DD format
   - **Type** - Document type (e.g., "Rechnung", "Kontoauszug", "Mitteilung")

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
| `list-scanners` | List available scanners |
| `setup-check` | Check configuration |
| `list-pending` | List documents awaiting identification |
| `organize --id ID --sender NAME [--date DATE] [--type TYPE]` | Move pending doc to final location |

## Options

- `--scanner "Name"` - Use specific scanner (overrides default)
- `--output "/path"` - Save to specific directory (overrides default)
- `--resolution 300` - Scan resolution in DPI

## Response Statuses

| Status | Meaning | Next Action |
|--------|---------|-------------|
| `awaiting_flip` | Front sides scanned | Ask user to flip stack, then run `back` |
| `needs_identification` | Documents ready for ID | Identify each document, then `organize` |
| `organized` | Document filed | Done |
| `empty` | No pages in feeder | Check scanner |
| `error` | Something failed | Check message |

## Example Session

```
Agent: Scanning your documents...
[runs: scan_and_organize.py single]

Script returns:
{
  "status": "needs_identification",
  "documents": [
    {
      "id": "20260215_143022_00",
      "text_preview": "UBS Switzerland AG\nZürich, 10.02.2026\nKontoauszug...",
      "pages": 2
    },
    {
      "id": "20260215_143022_01", 
      "text_preview": "Cornercard\nMastercard Abrechnung\nAbrechnungsdatum: 31.01.2026...",
      "pages": 3
    }
  ]
}

Agent analyzes text_preview using document-analysis skill:
- Doc 00: Sender=UBS, Date=2026-02-10, Type=Kontoauszug
- Doc 01: Sender=Cornercard, Date=2026-01-31, Type=Abrechnung

Agent organizes:
[runs: organize --id 20260215_143022_00 --sender UBS --date 2026-02-10 --type Kontoauszug]
[runs: organize --id 20260215_143022_01 --sender Cornercard --date 2026-01-31 --type Abrechnung]

Agent: Done! Saved 2 documents:
- 2026/UBS/2026-02-10_UBS_Kontoauszug.pdf
- 2026/Cornercard/2026-01-31_Cornercard_Abrechnung.pdf
```

## Configuration

Preferences stored in `memory/preferences.json`:
- `default_scanner` - Scanner to use
- `default_output` - Where to save files
- `local_fallback` - Backup location if default unavailable

## Troubleshooting

**Scanner not found:**
```bash
scanline -list
```

**Poor OCR quality:**
- Increase resolution (try 400 or 600 DPI)
- Ensure documents are clean and flat

**Output not accessible:**
- Script automatically falls back to local directory
- Check mount status of network drives
