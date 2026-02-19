---
description: Multi-stage pipeline overview - scan → OCR → analysis → splitting → organization. Start here for system understanding.
---

# Architecture

The document scanner uses a multi-stage pipeline:

```
Physical Documents
    ↓
[1] Scan (scanline + Brother MFC-L2800DW)
    ↓
[2] OCR (scanline -ocr)
    ↓
[3] Analysis (page grouping, date extraction)
    ↓
[4] Splitting (PyPDF2)
    ↓
[5] Organization (DiskStation filing)
```

## Stage Details

1. **Scan** - Physical documents feed through the scanner. See [[scanner-discovery]] for setup.
2. **OCR** - Text layer added to enable searching and analysis.
3. **Analysis** - Documents grouped by [[page-grouping]] heuristics, dates extracted via [[date-extraction]].
4. **Splitting** - PyPDF2 separates multi-document scans into individual files.
5. **Organization** - Files moved to final locations per [[file-organization]] rules.
