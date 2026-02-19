---
description: When to auto-organize vs ask for help. High/medium/low/unknown confidence definitions.
---

# Confidence Levels

Confidence determines whether to organize automatically or ask for human input.

## Levels

### high

**Definition:** Sender clearly identified in letterhead, date explicit, document type obvious.

**Action:** Organize automatically.

**Examples:**
- UBS logo + "Kontoauszug" + "Zürich, 10.02.2026"
- Cornercard header + statement date clearly visible

### medium

**Definition:** Sender inferred from context, date found but position ambiguous, type reasonably clear.

**Action:** Organize automatically, but note uncertainty in response.

**Examples:**
- Sender name in body text, not letterhead
- Date found but multiple dates present
- Document type implied, not stated

### low

**Definition:** Multiple possible senders, date unclear, or document type ambiguous.

**Action:** Return `needs_identification`. Include preview text and suggestions.

**Examples:**
- Generic letterhead, company name only in footer
- No clear date visible
- Could be invoice or statement

### unknown

**Definition:** Cannot determine sender or date with any confidence.

**Action:** Return `needs_identification`. Require human input.

**Examples:**
- Handwritten document
- Poor OCR quality
- Fragment or partial document

## Response Format

### Auto-organize (high/medium)

```json
{
  "status": "complete",
  "sender": "UBS",
  "date": "2026-02-10",
  "document_type": "Kontoauszug",
  "confidence": "high",
  "saved_to": "/path/to/file.pdf"
}
```

### Needs help (low/unknown)

```json
{
  "status": "needs_identification",
  "preview_text": "First 500 chars...",
  "possible_senders": ["UBS", "Credit Suisse"],
  "possible_dates": ["2026-02-10", "2026-02-15"],
  "confidence": "low",
  "reason": "Multiple bank logos visible"
}
```

## Confidence Factors

| Factor | Increases Confidence | Decreases Confidence |
|--------|---------------------|---------------------|
| Letterhead | Clear logo/name | Generic or missing |
| Date | Explicit, single date | Multiple or ambiguous |
| Type | Keywords present | No clear indicators |
| OCR quality | Clean text | Garbled output |
| Sender history | Known sender | First time seeing |
