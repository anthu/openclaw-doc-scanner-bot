#!/usr/bin/env python3
"""
AI-based document identification using OpenClaw's model
"""
import json
import sys
import os
from pathlib import Path

def identify_document(text: str) -> dict:
    """
    Use AI to identify sender and date from document text.
    Returns: {"sender": str, "date": str, "confidence": float}
    """
    # Prepare prompt for the AI
    prompt = f"""Analyze this document text and extract:
1. The sender/company name (normalize to a simple identifier, e.g., "UBS", "Cornercard", "MoebelSchubiger")
2. The document date (YYYY-MM-DD format)

Document text (first 2000 chars):
{text[:2000]}

Respond with JSON only:
{{"sender": "CompanyName", "date": "YYYY-MM-DD", "confidence": 0.0-1.0}}

Rules:
- Use consistent sender names (e.g., "MoebelSchubiger" not "Möbel Schubiger AG")
- Pick the most relevant date (invoice date, statement date, not future dates)
- confidence: 1.0 = very sure, 0.5 = uncertain, 0.0 = unknown
"""
    
    # Call OpenClaw's model via environment
    # This assumes the scanner agent has access to exec/model tools
    # For now, we'll use a simple subprocess call to the main agent
    
    try:
        import subprocess
        import tempfile
        
        # Write prompt to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(prompt)
            prompt_file = f.name
        
        # Call via OpenClaw CLI or direct model access
        # For now, return a placeholder that triggers the agent workflow
        result = {
            "sender": None,
            "date": None,
            "confidence": 0.0,
            "needs_ai": True,
            "text_preview": text[:500]
        }
        
        os.unlink(prompt_file)
        return result
        
    except Exception as e:
        return {
            "sender": None,
            "date": None,
            "confidence": 0.0,
            "error": str(e)
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: identify_document.py <text>")
        sys.exit(1)
    
    text = sys.argv[1]
    result = identify_document(text)
    print(json.dumps(result))
