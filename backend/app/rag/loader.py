from __future__ import annotations
import os
from pathlib import Path
from typing import List, Dict, Any

try:
    from app.config import settings
except ImportError:
    from backend.app.config import settings

class DocumentLoader:
    def __init__(self, documents_dir: str = None):
        self.documents_dir = Path(documents_dir or settings.DOCUMENTS_DIR)

    def load_documents(self) -> List[Dict[str, Any]]:
        """
        Loads all markdown and text documents from the configured directory.
        Returns a list of dictionaries with content and metadata.
        """
        documents = []
        if not self.documents_dir.exists():
            return documents

        for file_path in sorted(self.documents_dir.glob("*.md")) + sorted(self.documents_dir.glob("*.txt")):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract title from the first heading if present
                first_line = content.strip().split("\n")[0] if content else ""
                title = first_line.lstrip("#").strip() if first_line.startswith("#") else file_path.stem

                doc_meta = {
                    "source": file_path.name,
                    "file_path": str(file_path),
                    "title": title,
                    "category": file_path.stem.split("_", 1)[1] if "_" in file_path.stem else file_path.stem,
                    "char_count": len(content)
                }

                documents.append({
                    "content": content,
                    "metadata": doc_meta
                })
            except Exception as e:
                print(f"[DocumentLoader] Error reading {file_path}: {e}")

        return documents
