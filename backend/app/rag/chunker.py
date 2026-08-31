from __future__ import annotations
from typing import List, Dict, Any

try:
    from app.config import settings
except ImportError:
    from backend.app.config import settings

class TextChunker:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def split_text(self, text: str) -> List[str]:
        """
        Splits text into overlapping chunks respecting paragraph and line breaks.
        """
        if not text:
            return []

        paragraphs = text.split("\n\n")
        chunks: List[str] = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(para) > self.chunk_size:
                lines = para.split("\n")
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if len(current_chunk) + len(line) + 1 <= self.chunk_size:
                        current_chunk += ("\n" if current_chunk else "") + line
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                            overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                            current_chunk = current_chunk[overlap_start:].strip() + "\n" + line
                        else:
                            while len(line) > self.chunk_size:
                                chunks.append(line[:self.chunk_size])
                                line = line[self.chunk_size - self.chunk_overlap:]
                            current_chunk = line
            else:
                if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                    current_chunk += ("\n\n" if current_chunk else "") + para
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                        overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                        current_chunk = current_chunk[overlap_start:].strip() + "\n\n" + para
                    else:
                        current_chunk = para

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes documents with content and metadata, produces chunks with enriched metadata.
        """
        chunked_docs: List[Dict[str, Any]] = []

        for doc in documents:
            content = doc["content"]
            meta = doc["metadata"]
            chunks = self.split_text(content)

            for idx, chunk in enumerate(chunks):
                chunk_meta = {
                    **meta,
                    "chunk_id": f"{meta['source']}_chunk_{idx}",
                    "chunk_index": idx,
                    "total_chunks": len(chunks),
                    "chunk_char_length": len(chunk)
                }
                chunked_docs.append({
                    "id": f"{meta['source']}_chunk_{idx}",
                    "text": chunk,
                    "metadata": chunk_meta
                })

        return chunked_docs
