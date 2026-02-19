---
description: Deep technical reference - architecture, patterns, file organization, troubleshooting, and API. Follow links for specific topics.
---

# Document Scanner Reference

Technical reference for the document scanning system. Start with [[architecture]] for system overview, then follow links based on your needs.

## Topics

- [[architecture]] — Multi-stage pipeline overview: scan → OCR → analysis → splitting → organization
- [[page-grouping]] — Heuristics for splitting multi-document scans into individual files
- [[date-extraction]] — Date format parsing for Swiss documents (DD.MM.YYYY, German months)
- [[file-organization]] — Directory structure, naming conventions, and filing rules
- [[troubleshooting]] — Common issues, debug mode, and when to escalate
- [[api-reference]] — Python function signatures and usage examples

## Quick Reference

### Pipeline Stages

1. **Scan** → 2. **OCR** → 3. **Analyze** → 4. **Split** → 5. **Organize**

### Key Decisions

| Question | Reference |
|----------|-----------|
| How do I detect document boundaries? | [[page-grouping]] |
| What date format should I use? | [[date-extraction]] |
| Where do files go? | [[file-organization]] |
| Something's not working | [[troubleshooting]] |
| How do I call these functions? | [[api-reference]] |

## Legacy Patterns

> **Note:** The original pattern matching approach is deprecated. Use AI-based analysis via [[document-analysis]] instead of hardcoded patterns.

Historical patterns for reference only:

```python
# DEPRECATED - use AI analysis instead
PATTERNS = {
    "cornercard": ["cornercard", "comer banca", "comercard", "cornèr"],
    "sva_zurich": ["sva zürich", "familienzulagen", "familienausgleichskasse"],
    ...
}
```
