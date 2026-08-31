#!/usr/bin/env python3
"""
Convenience entry point for Gastroteacher PDF Exporter.
Usage:
    python export_pdf.py
    python export_pdf.py --docs
    python export_pdf.py --chats
    python export_pdf.py --out my_exports
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from backend.scripts.export_pdf import main

if __name__ == "__main__":
    main()
