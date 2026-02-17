# Document Analysis Skill

Analyze scanned documents to extract metadata: sender, date, document type, and categories.

## Purpose

After OCR, use AI to intelligently identify:
- **Sender** - Who sent the document (company/organization name)
- **Date** - Document date (not scan date)
- **Type** - What kind of document (invoice, statement, letter, etc.)
- **Categories** - Tags for organization (insurance, banking, rent, medical, etc.)

## How to Use

1. **Extract text from PDF** using PyPDF2 or similar
2. **Read the first 1-2 pages** (usually contains sender info)
3. **Analyze the text** to identify:
   - Letterhead/sender name
   - Document date (look for "Datum:", date in header, etc.)
   - Document type keywords
   - Subject matter for categorization

## Analysis Guidelines

### Sender Identification
- Look for company names in letterhead (top of page)
- Check sender address block
- Look for logos or brand names
- Common patterns:
  - "Cornércard" / "Cornér Bank" → Cornercard
  - "Sanitas" → Sanitas
  - "MZP Real Estate" / "MZP" → MZP
  - "SVA Zürich" → SVA_Zurich
  - "UBS" → UBS
  - "Möbel Schubiger" → Schubiger

### Date Extraction
- Look for explicit dates: "Zürich, 10.02.2026" or "10. Februar 2026"
- German months: Januar, Februar, März, April, Mai, Juni, Juli, August, September, Oktober, November, Dezember
- Prefer document date over invoice period or due date
- Format as YYYY-MM-DD

### Document Type
Common types:
- **Rechnung** - Invoice
- **Kontoauszug** - Account statement
- **Kostenvoranschlag** - Cost estimate
- **Mietzinsrechnung** - Rent invoice
- **Mitteilung** - Notice/communication
- **Verwaltungswechsel** - Management change notice
- **Fragebogen** - Questionnaire

### Categories
Tag documents for organization:
- **banking** - Bank statements, credit cards
- **insurance** - Health, dental, liability insurance
- **rent** - Rent invoices, property management
- **medical** - Doctor bills, prescriptions, health services
- **utilities** - Electricity, internet, phone
- **tax** - Tax documents, receipts
- **legal** - Contracts, official notices

## Output Format

Return structured metadata:

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

## Confidence Levels

- **high** - Sender clearly identified in letterhead, date explicit
- **medium** - Sender inferred from context, date found but ambiguous
- **low** - Multiple possible senders, date unclear
- **unknown** - Cannot determine sender or date

## When to Ask for Help

If confidence is **low** or **unknown**, return:

```json
{
  "status": "needs_identification",
  "preview_text": "First 500 chars of document...",
  "possible_senders": ["Option1", "Option2"],
  "confidence": "low"
}
```

Then wait for human input before proceeding.

## Integration with Scan Workflow

After OCR and document splitting:

1. For each document, extract text
2. Analyze using this skill's guidelines
3. If confidence >= medium, organize automatically
4. If confidence < medium, ask for identification
5. Save to: `{output_base}/{YYYY}/{Sender}/{YYYY-MM-DD}_{Sender}_{Type}.pdf`

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

**Output:**
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

## Notes

- Use AI reasoning, not regex patterns
- Context matters - read the full document if needed
- Swiss German terms are common (Rechnung, Mietzins, etc.)
- Dates can be in multiple formats - normalize to YYYY-MM-DD
- When in doubt, ask the human
