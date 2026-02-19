---
description: Date format parsing for Swiss documents. Handles DD.MM.YYYY, German months, ISO format, and priority rules.
---

# Date Extraction

Extract the document's actual date (not the scan date).

## Supported Formats

| Format | Example | Notes |
|--------|---------|-------|
| `DD.MM.YYYY` | 17.02.2026 | Swiss standard |
| `DD.MM.YY` | 17.02.26 | Short year |
| `YYYY-MM-DD` | 2026-02-17 | ISO format |
| `D. Month YYYY` | 17. Februar 2026 | German text |
| `Month YYYY` | February 2026 | English text |

## German Months

Januar, Februar, März, April, Mai, Juni, Juli, August, September, Oktober, November, Dezember

## Priority Order

When multiple dates appear in a document:

1. **Date in document header** - Usually near letterhead, e.g., "Zürich, 10.02.2026"
2. **Date near sender information** - Often in the address block
3. **First date found** - Fallback if location unclear
4. **Scan date** - Last resort (avoid if possible)

## Common Patterns

- `Datum:` followed by date
- City name + comma + date: "Winterthur, 08.01.2026"
- `Rechnungsdatum:` for invoices
- `Abrechnungsdatum:` for statements

## Output Format

Always normalize to `YYYY-MM-DD` for consistent filing.

## Edge Cases

- **Future dates** - Likely due dates, not document dates. Look for earlier date.
- **Multiple dates** - Invoice date vs due date vs period. Prefer invoice/statement date.
- **Ambiguous format** - 01.02.2026 could be Jan 2 or Feb 1. Swiss convention is DD.MM.YYYY.
