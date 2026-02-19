---
description: Sender identification from OCR text. Letterhead patterns, address blocks, and normalization rules.
---

# Sender Identification

Identify who sent the document by analyzing OCR text.

## Where to Look

1. **Letterhead** (top of page) — Most reliable. Company name, logo text
2. **Sender address block** — Usually top-left or top-right
3. **Footer** — Company registration info, website
4. **Body text** — References to "we" + company name

## Common Patterns

Swiss documents often have sender info in this format:

```
Company Name AG
Street Address
CH-8000 City
```

## Normalization Rules

Convert raw text to consistent folder names:

| Raw Text | Normalized |
|----------|------------|
| Cornércard / Cornér Bank | Cornercard |
| SVA Zürich | SVA_Zurich |
| Möbel Schubiger AG | Schubiger |
| UBS Switzerland AG | UBS |
| Sanitas Grundversicherungen AG | Sanitas |
| MZP Real Estate AG | MZP |
| Bellevue Liegenschaften | BellevueLiegenschaften |

## Normalization Guidelines

- Remove legal suffixes: AG, GmbH, SA
- Remove location qualifiers: "Switzerland", "Zürich"
- Use CamelCase for multi-word names: `MoebelSchubiger`
- Replace umlauts: ü→u, ö→o, ä→a (or keep if consistent)
- No spaces or special characters

## When Multiple Senders Appear

- **Invoice from service via bank** → Use the service provider, not the bank
- **Letter with reply address** → Use the letterhead sender
- **Forwarded documents** → Use original sender

## Unknown Senders

If sender cannot be determined:

1. Set confidence to `low` or `unknown`
2. Include `preview_text` in response
3. Suggest possible matches if any
4. Return `needs_identification` status
