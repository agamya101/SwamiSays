# Vivekananda RAG-ready corpus

Source: The Complete Works of Swami Vivekananda
Author: Swami Vivekananda
Publisher metadata: Advaita Ashrama

## Files
- `vivekananda_rag_ready.jsonl`: main embedding/retrieval corpus. One JSON object per chunk.
- `vivekananda_rag_ready.txt`: human-readable copy with source attribution before every chunk.
- `vivekananda_source_index.jsonl`: TOC/section index with exact EPUB locators.
- `vivekananda_supplemental_footnotes.jsonl`: footnote text kept separate from main retrieval corpus.

## Main corpus cleaning
- Excludes table-of-contents/navigation and front matter before Volume 1.
- Includes **Complete Works, Vol. 1–9** and **Unpublished Vol. 10** from the EPUB.
- Excludes heading-only blocks from retrieval text but keeps their labels in metadata.
- Keeps paragraph boundaries and explicit line breaks where present.
- Chunks are built within a single source section and target about 420 words, without crossing section boundaries.
- No print page numbers are fabricated; `print_page` is `null` where the EPUB does not expose them.
- Every chunk has `source.citation` plus an `epub_locator` such as `OEBPS/part0002_split_001.xhtml#anchor`.

## Recommended RAG citation flow
1. Embed only the `text` field.
2. Retrieve top-k chunks.
3. Provide the model with each chunk's `source` metadata.
4. For a quotation, quote only wording present in `text`.
5. Display `source.citation` (and optionally the EPUB locator) in the UI.
