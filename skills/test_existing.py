#!/usr/bin/env python3
"""
Test the document scanner on existing PDF
"""
import sys
from pathlib import Path

# Add script directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from scan_and_organize import ocr_pdf, analyze_pages, split_and_save

def main():
    pdf_path = Path("/Users/antonhuck/.openclaw/workspace/scan-staging/documents/2026/scan_085244.pdf")
    
    print("Testing document scanner on existing scan...")
    print(f"Input: {pdf_path}\n")
    
    # OCR
    print("Step 1: OCR")
    ocr_text = ocr_pdf(pdf_path)
    print()
    
    # Analyze
    print("Step 2: Analyze & Group")
    documents = analyze_pages(pdf_path, ocr_text)
    print()
    
    # Split and save
    print("Step 3: Split & Save")
    saved_files = split_and_save(pdf_path, documents)
    print()
    
    print("=" * 60)
    print(f"✅ SUCCESS - Saved {len(saved_files)} document(s)")
    print("=" * 60)
    for f in saved_files:
        print(f"   {f}")

if __name__ == "__main__":
    main()
