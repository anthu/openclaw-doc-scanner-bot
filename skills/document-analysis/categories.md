---
description: Document categories for organization - banking, insurance, rent, medical, utilities, tax, legal.
---

# Categories

Tag documents with categories for cross-sender organization.

## Available Categories

### banking
Bank statements, credit cards, account notices.

**Triggers:** UBS, Credit Suisse, PostFinance, Raiffeisen, Cornercard, Visa, Mastercard

### insurance
Health insurance, dental, liability, household.

**Triggers:** Sanitas, CSS, Helsana, AXA, Zurich, Helvetia, Prämie, Police

### rent
Rent invoices, utility statements, property management.

**Triggers:** Mietzins, Nebenkosten, Verwaltung, Liegenschaft, Mietvertrag

### medical
Doctor bills, prescriptions, health services, dental.

**Triggers:** Arzt, Zahnarzt, Apotheke, Behandlung, Kostenvoranschlag, Rezept

### utilities
Electricity, internet, phone, water.

**Triggers:** EWZ, Swisscom, Sunrise, Salt, Strom, Wasser

### tax
Tax documents, receipts for deductions, official tax correspondence.

**Triggers:** Steuererklärung, Steueramt, Quellensteuer, Veranlagung

### legal
Contracts, official notices, legal correspondence.

**Triggers:** Vertrag, Kündigung, Anwalt, Gericht, Bescheid

## Multi-Category Documents

Documents often fit multiple categories:

- Health insurance invoice → `insurance`, `medical`
- Rent utility statement → `rent`, `utilities`
- Bank credit card statement → `banking`

Use primary category for filing, but note secondary in metadata.

## Category vs Sender

- **Sender** determines the **folder** (`2026/Sanitas/`)
- **Categories** enable **cross-cutting searches** ("show all medical documents")
