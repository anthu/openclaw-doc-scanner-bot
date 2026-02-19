---
description: Heuristics for splitting multi-document scans. Detects page numbers, letterhead changes, and content boundaries.
---

# Page Grouping

When scanning multiple documents at once, the system must detect where one document ends and another begins.

## Detection Heuristics

### 1. Page Numbers

The strongest signal. Look for patterns like:

- `1/3`, `2/3`, `3/3` → 3-page document
- `Seite 1 von 2` → German "Page 1 of 2"
- `Page 1`, `Page 2` → English pagination

### 2. Letterhead Consistency

Same sender across consecutive pages indicates one document:

- Logo position consistent
- Company name in same location
- Address block unchanged

New letterhead = new document.

### 3. Content Continuity

Text that flows naturally between pages:

- Sentences cut mid-word
- Tables spanning pages
- Numbered lists continuing

### 4. Footer Patterns

Consistent footer information suggests same document:

- Page numbers in footer
- Document reference numbers
- Company disclaimer text

## Split Points

Mark a new document when:

- Letterhead changes completely
- Page numbering resets (3/3 → 1/2)
- Clear visual break (full blank space, new header)

## Edge Cases

- **Blank pages** - Remove silently, don't use as split points
- **Attachments** - May have different formatting but belong to cover letter
- **Multi-part mailings** - Invoice + payment slip are one document
