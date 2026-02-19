---
description: Common issues and solutions - page order, OCR quality, date extraction, debug mode.
---

# Troubleshooting

## Common Issues

### Pages Out of Order

**Symptom:** Document pages scrambled after duplex scan.

**Cause:** Feeder pulled pages in unexpected order.

**Solution:** 
1. Check for page numbers in OCR text
2. If page numbers exist, reorder automatically
3. If missing, manual reorder required - see [[api-reference#manual-page-reordering]]

### Wrong Document Type Detected

**Symptom:** Invoice categorized as statement, or vice versa.

**Cause:** Ambiguous keywords in document.

**Solution:** 
1. Check document text for type indicators
2. Use context (sender typically sends X type)
3. When uncertain, ask human

### Date Not Extracted

**Symptom:** Falls back to scan date instead of document date.

**Cause:** Unusual date format or position.

**Solution:**
1. Check OCR quality - is text readable?
2. Review [[date-extraction]] for supported formats
3. Look for date in different locations (header, footer, body)

### OCR Quality Poor

**Symptom:** Extracted text is garbled or incomplete.

**Cause:** Low scan resolution or document quality.

**Solution:**
1. Increase scan resolution to 400 or 600 DPI
2. Ensure documents are flat and clean
3. Check scanner glass for smudges

### Scanner Not Found

**Symptom:** `scanner_not_found` error.

**Cause:** Scanner offline, wrong name, or network issue.

**Solution:**
1. Run `scanline -list` to see available scanners
2. Check scanner is powered on and connected
3. For network scanners, verify same network segment

## Debug Mode

Enable verbose logging:

```bash
export DEBUG=1
python3 skills/document-scanner/scripts/scan_and_organize.py
```

## Manual OCR Test

Test OCR on a specific PDF:

```bash
scanline -ocr /path/to/document.pdf
```

## When to Escalate

Return `needs_identification` and wait for human input when:

- Confidence level is `low` or `unknown`
- Multiple possible senders with equal likelihood
- Date ambiguous or missing entirely
- Document type unclear
