---
description: Available tools - scanline CLI, output storage paths, and the document scanner script with its commands and options.
---

# TOOLS.md - Scanner Agent

## Scanner CLI

- **Tool:** `scanline` (macOS) or SANE utilities (Linux)
- **Detection:** `scanline -list` to find available scanners
- **Settings:** Resolution, size, mode configurable per-scan

## Output Storage

- **Default:** Configured via preferences (first-run setup)
- **Fallback:** `~/Documents/Scanned` if default not accessible
- **Structure:** `YYYY/Category/YYYY-MM-DD_Description.pdf` — see [[file-organization]]

## Document Scanner Script

Located at: `skills/document-scanner/scripts/scan_and_organize.py`

Commands:
- `setup-check` - Check configuration status
- `list-scanners` - List available scanners
- `front` - Scan front sides (duplex workflow)
- `back` - Scan back sides and merge
- `single` - Single-sided scan

Options:
- `--scanner "Name"` - Override scanner
- `--output "/path"` - Override output directory
- `--front-pdf "/path"` - Front PDF for back mode

## Dependencies

- `PyPDF2` - PDF manipulation
- `ocrmypdf` - OCR text layer (optional but recommended)
- `scanline` - Scanner interface (macOS)
