#!/usr/bin/env python3
"""
Document Scanner - Self-configuring with preference support

Dependencies (install before use):
    pip3 install PyPDF2
    brew install ocrmypdf scanline
"""
import subprocess
import sys
import re
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# Check dependencies at import time
try:
    from PyPDF2 import PdfReader, PdfWriter, PdfMerger
except ImportError:
    print(json.dumps({
        "status": "error",
        "error": "missing_dependency",
        "message": "PyPDF2 not installed. Run: pip3 install PyPDF2"
    }))
    sys.exit(1)

# Paths
SCRIPT_DIR = Path(__file__).parent
WORKSPACE_DIR = SCRIPT_DIR.parent.parent.parent  # skills/document-scanner/scripts -> workspace
MEMORY_DIR = WORKSPACE_DIR / "memory"
PREFERENCES_FILE = MEMORY_DIR / "preferences.json"
STAGING_DIR = WORKSPACE_DIR / "skills" / "scan-staging"

# Document patterns removed - AI-based identification used instead
PATTERNS = {}


def check_tools() -> List[str]:
    """Check if required tools are available"""
    missing = []
    for tool in ['scanline']:
        if shutil.which(tool) is None:
            missing.append(tool)
    return missing


def detect_scanners() -> List[str]:
    """Detect available scanners using scanline"""
    try:
        result = subprocess.run(['scanline', '-list'], capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return []
        
        scanners = []
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            # Skip headers, footers, and comments
            if line and not line.startswith('#') and line.startswith('*'):
                # Extract scanner name after the asterisk
                scanner_name = line[1:].strip()
                if scanner_name and scanner_name.lower() != 'done':
                    scanners.append(scanner_name)
        return scanners
    except Exception:
        return []


def load_preferences() -> Dict:
    """Load preferences from memory file"""
    if not PREFERENCES_FILE.exists():
        return {"setup_complete": False}
    
    try:
        with open(PREFERENCES_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"setup_complete": False}


def save_preferences(prefs: Dict) -> None:
    """Save preferences to memory file"""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    prefs['last_updated'] = datetime.now().isoformat()
    
    with open(PREFERENCES_FILE, 'w') as f:
        json.dump(prefs, f, indent=2)


def get_output_base(prefs: Dict, override: str = None) -> Path:
    """Get output directory, with fallback logic"""
    if override:
        path = Path(override).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    default_output = prefs.get('default_output')
    if default_output:
        path = Path(default_output)
        # Check if it's a mounted volume
        if path.exists() or (path.parent.exists() and path.parent.is_mount()):
            path.mkdir(parents=True, exist_ok=True)
            return path
    
    # Fallback to local directory
    fallback = prefs.get('local_fallback', '~/Documents/Scanned')
    path = Path(fallback).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path


def scan_documents(side: str, scanner: str, staging_dir: Path) -> Optional[Path]:
    """Scan documents using scanline"""
    print(f"Scanning {side} sides with {scanner}...", file=sys.stderr)
    
    staging_dir.mkdir(parents=True, exist_ok=True)
    scan_start_time = datetime.now().timestamp()
    
    result = subprocess.run([
        "scanline",
        "-verbose",
        "-scanner", scanner,
        "-resolution", "300",
        "-a4",
        "-mono",
        "-dir", str(staging_dir),
        f"{side}-scan"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        if "error" in result.stderr.lower() and "empty" not in result.stderr.lower():
            raise Exception(f"Scanner error: {result.stderr}")
    
    # Find PDFs created after scan started
    pdf_files = []
    for pdf_path in staging_dir.glob(f"{side}-scan/**/*.pdf"):
        if pdf_path.stat().st_mtime > scan_start_time:
            pdf_files.append(pdf_path)
    
    # Also check root of staging dir
    for pdf_path in staging_dir.glob(f"{side}-scan*.pdf"):
        if pdf_path.stat().st_mtime > scan_start_time:
            pdf_files.append(pdf_path)
    
    if not pdf_files:
        return None
    
    pdf_path = max(pdf_files, key=lambda p: p.stat().st_mtime)
    
    try:
        reader = PdfReader(pdf_path)
        if len(reader.pages) == 0:
            return None
        if pdf_path.stat().st_size < 10000:
            return None
        return pdf_path
    except Exception:
        return None


def merge_duplex(front_pdf: Path, back_pdf: Path, staging_dir: Path) -> Path:
    """Merge front and back sides with proper page interleaving"""
    front_reader = PdfReader(front_pdf)
    back_reader = PdfReader(back_pdf)
    
    front_pages = len(front_reader.pages)
    back_pages = len(back_reader.pages)
    
    writer = PdfWriter()
    min_pages = min(front_pages, back_pages)
    
    # Interleave: front[0], back[LAST], front[1], back[LAST-1], ...
    for i in range(min_pages):
        writer.add_page(front_reader.pages[i])
        back_index = back_pages - 1 - i
        writer.add_page(back_reader.pages[back_index])
    
    # Handle extra pages
    if front_pages > back_pages:
        for i in range(back_pages, front_pages):
            writer.add_page(front_reader.pages[i])
    elif back_pages > front_pages:
        for i in range(front_pages, back_pages):
            back_index = back_pages - 1 - i
            writer.add_page(back_reader.pages[back_index])
    
    merged_path = staging_dir / "merged-scan.pdf"
    with open(merged_path, "wb") as f:
        writer.write(f)
    
    # Try OCR if available
    if shutil.which('ocrmypdf'):
        ocr_path = staging_dir / "merged-scan-ocr.pdf"
        try:
            result = subprocess.run([
                "ocrmypdf", "--skip-text", "--optimize", "1",
                "--output-type", "pdf", str(merged_path), str(ocr_path)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return ocr_path
        except Exception:
            pass
    
    return merged_path


def is_blank_page(page) -> bool:
    """Check if a page is blank"""
    try:
        text = page.extract_text() or ""
        if len(text.strip()) >= 50:
            return False
        
        # Check for image resources
        try:
            resources = page.get('/Resources')
            if resources and '/XObject' in resources:
                xobjects = resources['/XObject'].get_object()
                if len(xobjects) > 0:
                    return False
        except (KeyError, TypeError, AttributeError):
            pass
        
        return True
    except Exception:
        return False


def extract_page_indicator(text: str) -> Tuple[Optional[int], Optional[int]]:
    """Extract page number like '2/5' from text"""
    patterns = [
        r'(\d+)\s*/\s*(\d+)',
        r'[Pp]age\s+(\d+)\s+of\s+(\d+)',
        r'[Ss]eite\s+(\d+)\s+von\s+(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return (int(match.group(1)), int(match.group(2)))
    
    return (None, None)


def analyze_page_format(page) -> Dict:
    """Analyze page formatting"""
    text = page.extract_text() or ""
    lines = text.split('\n')
    
    page_num, total_pages = extract_page_indicator(text)
    
    header_lines = lines[:max(1, len(lines) // 5)]
    header_text = '\n'.join(header_lines).lower()
    
    footer_lines = lines[-max(1, len(lines) // 10):]
    footer_text = '\n'.join(footer_lines).lower()
    
    sender = None
    for doc_type, patterns in PATTERNS.items():
        if any(pattern in header_text or pattern in footer_text for pattern in patterns):
            sender = doc_type
            break
    
    return {
        'page_indicator': (page_num, total_pages),
        'sender': sender,
        'header_text': header_text[:200],
        'footer_text': footer_text[:200],
        'full_text': text,
        'text_length': len(text),
        'line_count': len(lines)
    }


def extract_dates(text: str) -> List[str]:
    """Extract dates from text"""
    dates = []
    dates.extend(re.findall(r'\b(\d{1,2}\.\d{1,2}\.\d{2,4})\b', text))
    dates.extend(re.findall(r'\b(\d{4}-\d{2}-\d{2})\b', text))
    dates.extend(re.findall(
        r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})\b',
        text, re.IGNORECASE
    ))
    return list(set(dates))


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string"""
    german_months = {
        'januar': 'January', 'februar': 'February', 'märz': 'March', 'april': 'April',
        'mai': 'May', 'juni': 'June', 'juli': 'July', 'august': 'August',
        'september': 'September', 'oktober': 'October', 'november': 'November', 'dezember': 'December'
    }
    
    date_lower = date_str.lower()
    for de, en in german_months.items():
        if de in date_lower:
            date_str = date_str.lower().replace(de, en)
            break
    
    formats = [
        "%d.%m.%Y", "%d.%m.%y", "%Y-%m-%d",
        "%B %Y", "%b %Y", "%B. %Y", "%b. %Y",
        "%d. %B %Y", "%d. %b %Y",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def analyze_and_split(pdf_path: Path) -> List[Dict]:
    """Analyze PDF and split into documents"""
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    page_analyses = []
    non_blank_pages = []
    
    for i, page in enumerate(reader.pages):
        if is_blank_page(page):
            continue
        
        analysis = analyze_page_format(page)
        analysis['index'] = i
        page_analyses.append(analysis)
        non_blank_pages.append(i)
    
    # Group into documents
    documents = []
    current_doc = None
    
    for i, analysis in enumerate(page_analyses):
        page_num, total_pages_ind = analysis['page_indicator']
        sender = analysis['sender']
        text = analysis['full_text'][:500].lower()
        
        start_new = False
        
        if current_doc is None:
            start_new = True
        elif i % 2 == 0:
            if page_num == 1:
                start_new = True
            elif sender and current_doc.get('sender') and sender != current_doc['sender']:
                start_new = True
            elif 'sehr geehrte' in text or 'guten tag' in text:
                start_new = True
        
        if start_new:
            if current_doc:
                documents.append(current_doc)
            current_doc = {
                'pages': [analysis['index']],
                'sender': sender,
                'page_indicators': [(page_num, total_pages_ind)],
                'analyses': [analysis]
            }
        else:
            current_doc['pages'].append(analysis['index'])
            current_doc['page_indicators'].append((page_num, total_pages_ind))
            current_doc['analyses'].append(analysis)
    
    if current_doc:
        documents.append(current_doc)
    
    # Reorder and extract metadata
    for doc in documents:
        indicators = doc['page_indicators']
        if all(num is not None for num, _ in indicators):
            expected_order = sorted(range(len(indicators)), key=lambda i: indicators[i][0])
            current_order = list(range(len(indicators)))
            
            if expected_order != current_order:
                doc['pages'] = [doc['pages'][i] for i in expected_order]
                doc['page_indicators'] = [doc['page_indicators'][i] for i in expected_order]
                doc['analyses'] = [doc['analyses'][i] for i in expected_order]
        
        doc_text = '\n'.join(a['full_text'] for a in doc['analyses'])
        doc['dates'] = extract_dates(doc_text)
        doc['type'] = doc['sender'] or 'unknown'
        doc['full_text'] = doc_text
    
    return documents


def generate_filename(doc: Dict, idx: int) -> str:
    """Generate descriptive filename from document content"""
    text = doc['full_text'][:2000].lower()
    sender = doc.get('sender') or doc.get('type', 'unknown')
    
    descriptions = []
    
    if 'mietzins' in text or 'rent' in text:
        descriptions.append("Mietzinsrechnung")
    elif 'rechnung' in text or 'invoice' in text:
        descriptions.append("Rechnung")
    
    if 'familienzulagen' in text:
        descriptions.append("Familienzulagen")
    
    if 'verwaltungswechsel' in text:
        descriptions.append("Verwaltungswechsel")
    
    if 'fragebogen' in text:
        descriptions.append("Fragebogen")
    
    if 'mitteilung' in text and not descriptions:
        descriptions.append("Mitteilung")
    
    senders = []
    if 'mzp' in text:
        senders.append("MZP")
    if 'sva' in text and 'zürich' in text:
        senders.append("SVA_Zurich")
    if 'ubs' in text:
        senders.append("UBS")
    if 'cornercard' in text:
        senders.append("Cornercard")
    
    parts = []
    if senders:
        parts.extend(senders[:2])
    if descriptions:
        parts.extend(descriptions[:2])
    
    if not parts:
        parts.append(sender.replace("_", " ").title().replace(" ", "_"))
        parts.append(str(idx + 1))
    
    return "_".join(parts)


def save_documents(pdf_path: Path, documents: List[Dict], output_base: Path) -> List[Dict]:
    """Save split documents and return metadata"""
    reader = PdfReader(pdf_path)
    saved_docs = []
    
    for idx, doc in enumerate(documents):
        writer = PdfWriter()
        
        blank_count = 0
        for page_num in doc['pages']:
            page = reader.pages[page_num]
            if not is_blank_page(page):
                writer.add_page(page)
            else:
                blank_count += 1
        
        if len(writer.pages) == 0:
            continue
        
        doc_date = datetime.now()
        if doc['dates']:
            first_page_text = doc['analyses'][0]['full_text'][:1000] if doc['analyses'] else ""
            first_page_dates = extract_dates(first_page_text)
            dates_to_try = first_page_dates if first_page_dates else doc['dates']
            
            parsed_dates = []
            for date_str in dates_to_try:
                parsed = parse_date(date_str)
                if parsed:
                    today = datetime.now()
                    days_diff = (parsed - today).days
                    if -730 <= days_diff <= 90:
                        parsed_dates.append(parsed)
            
            if parsed_dates:
                doc_date = max(parsed_dates)
        
        doc_type = doc['type']
        folder_name = doc_type.replace("_", " ").title().replace(" ", "_")
        
        year_folder = output_base / str(doc_date.year)
        type_folder = year_folder / folder_name
        type_folder.mkdir(parents=True, exist_ok=True)
        
        date_str = doc_date.strftime("%Y-%m-%d")
        doc_description = generate_filename(doc, idx)
        filename = f"{date_str}_{doc_description}.pdf"
        output_path = type_folder / filename
        
        with open(output_path, "wb") as f:
            writer.write(f)
        
        saved_docs.append({
            "sender": doc['sender'],
            "type": doc['type'],
            "date": date_str,
            "pages": len(writer.pages),
            "saved_to": str(output_path)
        })
    
    return saved_docs


def cleanup(staging_dir: Path):
    """Clean up staging directory"""
    if staging_dir.exists() and staging_dir.is_dir():
        # Safety check: only delete if it's under our workspace
        try:
            staging_dir.relative_to(WORKSPACE_DIR)
            shutil.rmtree(staging_dir)
        except ValueError:
            pass  # Not under workspace, don't delete


def main():
    parser = argparse.ArgumentParser(description='Document Scanner')
    parser.add_argument('mode', nargs='?', default='front', 
                        choices=['front', 'back', 'single', 'list-scanners', 'setup-check'],
                        help='Scan mode or command')
    parser.add_argument('--front-pdf', help='Path to front PDF (for back mode)')
    parser.add_argument('--scanner', help='Scanner name override')
    parser.add_argument('--output', help='Output directory override')
    parser.add_argument('--resolution', type=int, help='Resolution override')
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.mode == 'list-scanners':
        scanners = detect_scanners()
        print(json.dumps({"status": "ok", "scanners": scanners}))
        return
    
    if args.mode == 'setup-check':
        prefs = load_preferences()
        missing_tools = check_tools()
        scanners = detect_scanners()
        
        if missing_tools:
            print(json.dumps({
                "status": "error",
                "error": "missing_tools",
                "missing": missing_tools,
                "message": f"Missing tools: {', '.join(missing_tools)}. Install with: brew install {' '.join(missing_tools)}"
            }))
            return
        
        if not prefs.get('setup_complete'):
            print(json.dumps({
                "status": "setup_required",
                "available_scanners": scanners,
                "questions": [
                    {"key": "default_scanner", "question": "Which scanner should I use by default?", "options": scanners},
                    {"key": "default_output", "question": "Where should I save scanned documents?", "default": "/Volumes/home/Scanned Documents"}
                ]
            }))
            return
        
        print(json.dumps({"status": "ok", "preferences": prefs}))
        return
    
    # Load preferences
    prefs = load_preferences()
    
    # Check tools
    missing_tools = check_tools()
    if missing_tools:
        print(json.dumps({
            "status": "error",
            "error": "missing_tools",
            "missing": missing_tools
        }))
        return
    
    # Check setup
    if not prefs.get('setup_complete') and not args.scanner:
        scanners = detect_scanners()
        print(json.dumps({
            "status": "setup_required",
            "available_scanners": scanners,
            "questions": [
                {"key": "default_scanner", "question": "Which scanner should I use by default?", "options": scanners},
                {"key": "default_output", "question": "Where should I save scanned documents?", "default": "/Volumes/home/Scanned Documents"}
            ]
        }))
        return
    
    # Get scanner
    scanner = args.scanner or prefs.get('default_scanner')
    if not scanner:
        print(json.dumps({"status": "error", "error": "no_scanner", "message": "No scanner configured"}))
        return
    
    # Verify scanner is available
    available = detect_scanners()
    if scanner not in available:
        print(json.dumps({
            "status": "error",
            "error": "scanner_not_found",
            "message": f"Scanner '{scanner}' not available",
            "available_scanners": available
        }))
        return
    
    # Get output directory
    output_base = get_output_base(prefs, args.output)
    using_fallback = args.output is None and prefs.get('default_output') and not Path(prefs['default_output']).exists()
    
    try:
        # Scan
        pdf_path = scan_documents(args.mode, scanner, STAGING_DIR)
        
        if pdf_path is None:
            print(json.dumps({"status": "empty", "message": "No documents in feeder"}))
            return
        
        # Front mode - wait for back
        if args.mode == 'front':
            page_count = len(PdfReader(pdf_path).pages)
            print(json.dumps({
                "status": "awaiting_flip",
                "pages": page_count,
                "front_pdf": str(pdf_path),
                "message": f"Scanned {page_count} pages (front sides). Please flip the entire stack and reload."
            }))
            return
        
        # Back mode - merge with front
        if args.mode == 'back':
            if not args.front_pdf:
                print(json.dumps({"status": "error", "error": "missing_front_pdf", "message": "Front PDF path required for back mode"}))
                return
            
            front_pdf = Path(args.front_pdf)
            if not front_pdf.exists():
                print(json.dumps({"status": "error", "error": "front_pdf_not_found", "message": f"Front PDF not found: {args.front_pdf}"}))
                return
            
            pdf_path = merge_duplex(front_pdf, pdf_path, STAGING_DIR)
        
        # Analyze and split
        documents = analyze_and_split(pdf_path)
        
        # Save
        saved_docs = save_documents(pdf_path, documents, output_base)
        
        # Cleanup
        cleanup(STAGING_DIR)
        
        result = {
            "status": "complete",
            "documents": saved_docs,
            "total_pages": sum(d['pages'] for d in saved_docs),
            "total_documents": len(saved_docs)
        }
        
        if using_fallback:
            result["warning"] = "Default output not accessible, saved to fallback location"
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"status": "error", "error": "scan_failed", "message": str(e)}))


if __name__ == "__main__":
    main()
