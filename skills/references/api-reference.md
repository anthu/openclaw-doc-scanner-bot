---
description: Python API - scan_documents(), ocr_pdf(), analyze_pages(), split_and_save(). Function signatures and examples.
---

# API Reference

## Core Functions

### scan_documents()

Scans documents using scanline.

```python
def scan_documents() -> Path
```

**Returns:** `Path` - Path to scanned PDF

**Raises:** `subprocess.CalledProcessError` if scan fails

### ocr_pdf(pdf_path)

Extracts text from PDF using OCR.

```python
def ocr_pdf(pdf_path: Path) -> str
```

**Parameters:**
- `pdf_path`: Path to PDF file

**Returns:** `str` - Extracted text

### analyze_pages(pdf_path, ocr_text)

Analyzes pages and groups into documents using [[page-grouping]] heuristics.

```python
def analyze_pages(pdf_path: Path, ocr_text: str) -> List[Dict]
```

**Parameters:**
- `pdf_path`: Path to PDF file
- `ocr_text`: OCR extracted text

**Returns:** `List[Dict]` - List of document metadata

### split_and_save(pdf_path, documents)

Splits PDF and saves organized documents per [[file-organization]] rules.

```python
def split_and_save(pdf_path: Path, documents: List[Dict]) -> List[Path]
```

**Parameters:**
- `pdf_path`: Path to source PDF
- `documents`: List of document metadata from analyze_pages()

**Returns:** `List[Path]` - Paths to saved files

## Usage Examples

### Basic Scan

```bash
python3 skills/document-scanner/scripts/scan_and_organize.py
```

### Process Existing PDF

```python
from pathlib import Path
from scripts.scan_and_organize import ocr_pdf, analyze_pages, split_and_save

pdf_path = Path("~/Desktop/scan.pdf")
ocr_text = ocr_pdf(pdf_path)
documents = analyze_pages(pdf_path, ocr_text)
saved_files = split_and_save(pdf_path, documents)

print(f"Saved {len(saved_files)} documents")
```

### Custom Output Location

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import scan_and_organize

scan_and_organize.OUTPUT_BASE = Path("~/Documents/Archive")
scan_and_organize.main()
```

### Batch Processing

```bash
for pdf in ~/Desktop/scans/*.pdf; do
    python3 scripts/analyze_and_split.py "$pdf"
done
```

## Manual Page Reordering

If automatic reordering fails:

```python
from PyPDF2 import PdfReader, PdfWriter

reader = PdfReader("scan.pdf")
writer = PdfWriter()

# Correct order: pages 3, 1, 2, 4
for page_num in [2, 0, 1, 3]:  # 0-indexed
    writer.add_page(reader.pages[page_num])

with open("reordered.pdf", "wb") as f:
    writer.write(f)
```
