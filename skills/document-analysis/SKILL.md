---
description: AI-powered document metadata extraction. Entry point for sender, date, type, and category identification from OCR text.
---

# Document Analysis Skill

Analyze scanned documents to extract metadata. This is the entry point — follow links for detailed guidance on each aspect.

## Purpose

After OCR, use AI to identify:
- **Sender** — Who sent it → [[sender-identification]]
- **Date** — Document date (not scan date) → [[date-extraction]]
- **Type** — What kind of document → [[document-types]]
- **Categories** — Tags for organization → [[categories]]
- **Confidence** — How certain are we → [[confidence-levels]]

## Quick Workflow

1. **Extract text** from PDF (first 1-2 pages)
2. **Identify sender** using [[sender-identification]] guidelines
3. **Extract date** per [[date-extraction]] rules
4. **Determine type** from [[document-types]]
5. **Assess confidence** via [[confidence-levels]]
6. **Return result** or ask for help if confidence low

## Output Format

```json
{
  "sender": "Sanitas",
  "sender_normalized": "Sanitas",
  "date": "2026-01-08",
  "document_type": "Kostenvoranschlag",
  "categories": ["insurance", "medical"],
  "confidence": "high",
  "summary": "Cost estimate for dental treatment"
}
```

## When to Ask for Help

If [[confidence-levels]] is **low** or **unknown**, return:

```json
{
  "status": "needs_identification",
  "preview_text": "First 500 chars of document...",
  "possible_senders": ["Option1", "Option2"],
  "confidence": "low"
}
```

## Example Analysis

**Input text:**
```
Sanitas
Post CH AG
CH-8021 Zürich

Herr Anton Huck
Kreuzstrasse 41
8008 Zürich

Winterthur, 08.01.2026
Kunden-Nr.: 44.83584-3

Kostenvoranschlag für Zahnbehandlung
```

**Analysis:**
- Sender: "Sanitas" (letterhead) → [[sender-identification]]
- Date: "08.01.2026" (Swiss format) → [[date-extraction]]
- Type: "Kostenvoranschlag" (keyword) → [[document-types]]
- Categories: insurance + medical → [[categories]]
- Confidence: high (clear letterhead, explicit date)

**Output:**
```json
{
  "sender": "Sanitas",
  "date": "2026-01-08",
  "document_type": "Kostenvoranschlag",
  "categories": ["insurance", "medical"],
  "confidence": "high"
}
```

## Key Principles

- **Use AI reasoning**, not regex patterns
- **Context matters** — read the full document if needed
- **Swiss German terms** are common (Rechnung, Mietzins)
- **Normalize dates** to YYYY-MM-DD
- **When in doubt**, ask the human
