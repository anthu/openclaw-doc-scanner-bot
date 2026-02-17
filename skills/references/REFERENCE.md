# Document Scanner Reference

## Architecture

The document scanner uses a multi-stage pipeline:

```
Physical Documents
    ↓
[1] Scan (scanline + Brother MFC-L2800DW)
    ↓
[2] OCR (scanline -ocr)
    ↓
[3] Analysis (page grouping, date extraction)
    ↓
[4] Splitting (PyPDF2)
    ↓
[5] Organization (DiskStation filing)
```

## Document Identification Patterns

### Pattern Matching

The system identifies documents by searching for keywords in OCR text:

```python
PATTERNS = {
    "cornercard": ["cornercard", "comer banca", "comercard", "cornèr"],
    "sva_zurich": ["sva zürich", "familienzulagen", "familienausgleichskasse"],
    "bank": ["ubs", "credit suisse", "raiffeisen", "postfinance"],
    "insurance": ["axa", "zurich insurance", "helvetia"],
    "utility": ["ewz", "swisscom", "sunrise"],
}
```

### Page Grouping Heuristics

Documents are grouped by detecting:

1. **Page numbers** - "1/3", "2/3", "3/3" indicate a 3-page document
2. **Letterhead consistency** - Same sender across pages
3. **Content continuity** - Text flows naturally between pages
4. **Footer patterns** - Consistent footer information

### Date Extraction

Supported date formats:

- `DD.MM.YYYY` - Swiss standard (e.g., "17.02.2026")
- `DD.MM.YY` - Short year (e.g., "17.02.26")
- `YYYY-MM-DD` - ISO format (e.g., "2026-02-17")
- `Month YYYY` - Text format (e.g., "February 2026", "Feb. 2026")

Priority order:
1. Date in document header
2. Date near sender information
3. First date found in document
4. Scan date (fallback)

## File Organization

### Directory Structure

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

### Naming Convention

Format: `YYYY-MM-DD_Description.pdf`

- **Date:** Document date (not scan date)
- **Description:** Auto-generated from document type and content
- **Sanitization:** Spaces → underscores, special chars removed

Examples:
- `2026-02-02_Cornercard_Monthly_Statement.pdf`
- `2026-01-15_UBS_Account_Statement.pdf`
- `2026-02-17_Unknown_Document.pdf`

## Advanced Features

### Manual Page Reordering

If automatic reordering fails, manually specify page order:

```python
from scripts.scan_and_organize import split_and_save
from PyPDF2 import PdfReader, PdfWriter

# Reorder pages manually
reader = PdfReader("scan.pdf")
writer = PdfWriter()

# Correct order: pages 3, 1, 2, 4
for page_num in [2, 0, 1, 3]:  # 0-indexed
    writer.add_page(reader.pages[page_num])

with open("reordered.pdf", "wb") as f:
    writer.write(f)
```

### Batch Processing

Process multiple scans:

```bash
for pdf in ~/Desktop/scans/*.pdf; do
    python3 scripts/analyze_and_split.py "$pdf"
done
```

### Custom Patterns

Add organization-specific patterns in `scripts/config.py`:

```python
PATTERNS = {
    "my_company": ["my company inc", "mycompany.com"],
    "landlord": ["property management", "rent invoice"],
}
```

## Troubleshooting

### Common Issues

**Issue:** Pages out of order
**Solution:** Check for page numbers in OCR text. If missing, manually reorder.

**Issue:** Wrong document type detected
**Solution:** Add more specific patterns to `PATTERNS` dict.

**Issue:** Date not extracted
**Solution:** Check date format. Add custom regex if needed.

**Issue:** OCR quality poor
**Solution:** Increase scan resolution to 400 or 600 DPI.

### Debug Mode

Enable verbose logging:

```bash
export DEBUG=1
python3 scripts/scan_and_organize.py
```

### Manual OCR

Test OCR on a specific PDF:

```bash
scanline -ocr /path/to/document.pdf
```

## API Reference

### scan_documents()

Scans documents using scanline.

**Returns:** `Path` - Path to scanned PDF

**Raises:** `subprocess.CalledProcessError` if scan fails

### ocr_pdf(pdf_path: Path)

Extracts text from PDF using OCR.

**Parameters:**
- `pdf_path`: Path to PDF file

**Returns:** `str` - Extracted text

### analyze_pages(pdf_path: Path, ocr_text: str)

Analyzes pages and groups into documents.

**Parameters:**
- `pdf_path`: Path to PDF file
- `ocr_text`: OCR extracted text

**Returns:** `List[Dict]` - List of document metadata

### split_and_save(pdf_path: Path, documents: List[Dict])

Splits PDF and saves organized documents.

**Parameters:**
- `pdf_path`: Path to source PDF
- `documents`: List of document metadata from analyze_pages()

**Returns:** `List[Path]` - Paths to saved files

## Examples

### Example 1: Basic Scan

```bash
python3 scripts/scan_and_organize.py
```

### Example 2: Process Existing PDF

```python
from pathlib import Path
from scripts.scan_and_organize import ocr_pdf, analyze_pages, split_and_save

pdf_path = Path("~/Desktop/scan.pdf")
ocr_text = ocr_pdf(pdf_path)
documents = analyze_pages(pdf_path, ocr_text)
saved_files = split_and_save(pdf_path, documents)

print(f"Saved {len(saved_files)} documents")
```

### Example 3: Custom Output Location

```python
import sys
from pathlib import Path

# Override OUTPUT_BASE
sys.path.insert(0, str(Path(__file__).parent))
import scan_and_organize

scan_and_organize.OUTPUT_BASE = Path("~/Documents/Archive")
scan_and_organize.main()
```
