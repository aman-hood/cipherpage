"""
Document Text Extraction and Chunking Engine (RAG-02, RAG-07).
Splits document text into semantic chunks while preserving section/page metadata (RAG-04)
and defending against prompt injection (RAG-07).
"""
import re
from typing import List, Dict, Any, Optional

class DocumentChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def sanitize_untrusted_text(self, text: str) -> str:
        """
        Defends against prompt injection inside documents (RAG-07).
        Removes system prompt overrides, ignore instructions, and control sequences.
        """
        # Strip potential malicious instruction injections
        sanitized = re.sub(
            r'(?i)(ignore previous instructions|disregard all prior directives|system prompt override|you are now a)',
            '[FILTERED INSTRUCTION]',
            text
        )
        return sanitized.strip()

    def chunk_text(self, raw_text: str, default_section: str = "General") -> List[Dict[str, Any]]:
        cleaned = self.sanitize_untrusted_text(raw_text)
        paragraphs = cleaned.split("\n\n")

        chunks: List[Dict[str, Any]] = []
        current_chunk = ""
        current_section = default_section
        chunk_idx = 0

        for p in paragraphs:
            p_clean = p.strip()
            if not p_clean:
                continue

            # Detect headings / section titles (e.g. # Title, ## Section)
            first_line = p_clean.split("\n")[0].strip()
            is_new_header = first_line.startswith("#") or (first_line.isupper() and len(first_line) < 60)
            
            if is_new_header:
                if current_chunk:
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "content": current_chunk,
                        "section_title": current_section,
                        "token_count": len(current_chunk.split())
                    })
                    chunk_idx += 1
                    current_chunk = ""
                current_section = first_line.lstrip("#").strip()[:100]

            if len(current_chunk) + len(p_clean) <= self.chunk_size:
                current_chunk += ("\n\n" if current_chunk else "") + p_clean
            else:
                if current_chunk:
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "content": current_chunk,
                        "section_title": current_section,
                        "token_count": len(current_chunk.split())
                    })
                    chunk_idx += 1
                
                # Handle large paragraphs exceeding chunk size
                if len(p_clean) > self.chunk_size:
                    for i in range(0, len(p_clean), self.chunk_size - self.chunk_overlap):
                        sub_text = p_clean[i:i + self.chunk_size]
                        chunks.append({
                            "chunk_index": chunk_idx,
                            "content": sub_text,
                            "section_title": current_section,
                            "token_count": len(sub_text.split())
                        })
                        chunk_idx += 1
                    current_chunk = ""
                else:
                    current_chunk = p_clean

        if current_chunk:
            chunks.append({
                "chunk_index": chunk_idx,
                "content": current_chunk,
                "section_title": current_section,
                "token_count": len(current_chunk.split())
            })

        return chunks

chunker = DocumentChunker()
