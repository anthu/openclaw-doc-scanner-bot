---
description: Directory structure, naming conventions, and filing rules. Where documents go and how they're named.
---

# File Organization

## Directory Structure

```
/Volumes/home/Scanned Documents/
├── 2025/
│   ├── Cornercard/
│   ├── SVA_Zurich/
│   └── Unknown/
└── 2026/
    ├── Cornercard/
    │   ├── 2026-01-05_Credit_Option_Agreement.pdf
    │   ├── 2026-01-20_Welcome_Letter.pdf
    │   └── 2026-02-02_Monthly_Statement.pdf
    ├── SVA_Zurich/
    │   └── 2026-02-02_Familienzulagen.pdf
    └── Bank/
        └── 2026-01-31_Account_Statement.pdf
```

## Naming Convention

Format: `YYYY-MM-DD_Description.pdf`

| Component | Rule |
|-----------|------|
| **Date** | Document date (not scan date) - see [[date-extraction]] |
| **Description** | Auto-generated from sender + document type |
| **Sanitization** | Spaces → underscores, special chars removed |

### Examples

- `2026-02-02_Cornercard_Monthly_Statement.pdf`
- `2026-01-15_UBS_Account_Statement.pdf`
- `2026-02-17_Unknown_Document.pdf`

## Sender Folders

Normalized sender names become folder names:

| Raw Text | Folder Name |
|----------|-------------|
| Cornércard | Cornercard |
| SVA Zürich | SVA_Zurich |
| Möbel Schubiger | Schubiger |
| UBS Switzerland AG | UBS |

## Fallback Locations

If primary storage unavailable:

1. Check `local_fallback` from preferences
2. Default to `~/Documents/Scanned`
3. Note the fallback in response, don't fail

## Unknown Documents

When sender can't be identified:

- Place in `{YEAR}/Unknown/`
- Name as `{DATE}_Unknown_Document.pdf`
- Return `needs_identification` status for human review
