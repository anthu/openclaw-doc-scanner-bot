---
name: document-scanner
description: Scan, analyze, split, and organize physical documents. Use when the user asks to scan documents, organize scanned mail, process physical letters, or digitize paperwork. Handles multi-page documents, automatic page reordering, date extraction, document splitting, and organized filing.
---

# Document Scanner

Scan physical documents, intelligently split mixed documents, extract dates, and organize them with proper naming.

## Quick Start

**Check setup and list scanners:**
```bash
python3 skills/document-scanner/scripts/scan_and_organize.py setup-check
python3 skills/document-scanner/scripts/scan_and_organize.py list-scanners
```

**Basic scan (front sides):**
```bash
python3 skills/document-scanner/scripts/scan_and_organize.py front
```

**Scan back sides (after flipping stack):**
```bash
python3 skills/document-scanner/scripts/scan_and_organize.py back --front-pdf /path/to/front.pdf
```

**Single-sided scan:**
```bash
python3 skills/document-scanner/scripts/scan_and_organize.py single
```

## Options

- `--scanner "Name"` - Use specific scanner (overrides default)
- `--output "/path"` - Save to specific directory (overrides default)
- `--resolution 300` - Scan resolution in DPI

## Workflow

### 1. Scan Documents

The script uses `scanline` with these settings:
- **Resolution:** 300 DPI (configurable)
- **Size:** DIN A4 (European standard)
- **Mode:** Monochrome (black & white for text documents)
- **Format:** PDF

### 2. Remove Blank Pages

Automatically detects and removes:
- Completely blank pages
- Pages with less than 50 characters
- Pages with only whitespace

### 3. Analyze & Split

The script analyzes each page for:
- **Page indicators:** "1/3", "2/3", "Page 2 of 5", "Seite 2 von 5"
- **Letterhead:** Identifies sender from header
- **Format consistency:** Groups pages with same sender/format

### 4. Reorder Pages

If pages are out of order, the script automatically reorders based on page numbers.

### 5. Extract Metadata

For each document:
- **Date:** DD.MM.YYYY, YYYY-MM-DD, or "Month YYYY" format
- **Sender:** From letterhead/footer patterns
- **Type:** Invoice, statement, letter, etc.

### 6. Organize & Save

Files are saved as: `YYYY/Category/YYYY-MM-DD_Description.pdf`

## Configuration

Preferences are stored in `memory/preferences.json` after first-run setup.

Document patterns for sender identification can be customized in the script:

```python
PATTERNS = {
    "cornercard": ["cornercard", "comer banca"],
    "sva_zurich": ["sva zürich", "familienzulagen"],
    # Add your own patterns...
}
```

## Troubleshooting

**Scanner not found:**
```bash
scanline -list
```

**Poor OCR quality:**
- Increase resolution (try 400 or 600 DPI)
- Ensure documents are clean and flat

**Output not accessible:**
- Script will automatically fall back to local directory
- Check mount status of network drives
