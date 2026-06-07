---
name: binary-doc-cache
description: "Trigger: leer PDF, leer DOCX, documento binario, extraer texto. Cachea versiones legibles en docs/extracted/."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Leer documentos binarios citados por el usuario"
    - "Extraer y cachear texto legible dentro del repo antes de leer un .docx o .pdf"
---

## Activation Contract

Load this skill when the user asks to read, summarize, cite, or inspect a `.pdf`, `.docx`, or other binary document.

## Hard Rules

- Check for an existing extracted text file before converting again.
- Persist readable extracts under `docs/extracted/` before reading large binary content.
- Mirror repo-relative source paths in the extracted path and keep the original extension in the filename.
- For external files, use a sanitized path under `docs/extracted/external/`.
- If no extractor is available, report the blocker instead of pretending the binary was read.

## Decision Gates

| Case | Action |
|---|---|
| Extract exists | Read the cached `.txt`. |
| Missing `.docx` extract on macOS | Use `textutil`. |
| Missing `.pdf` extract with `pdftotext` | Use `pdftotext -layout`. |
| Missing `.pdf` extract with `pypdf` only | Use a Python extraction script. |
| No extractor | Ask before installing/enabling tooling. |

## Execution Steps

1. Resolve the cited document path.
2. Derive the expected `docs/extracted/...` path.
3. Read the cached text if present.
4. Otherwise create parent directories, extract, persist, then read the text.
5. Keep the extracted text in the repo for future sessions.

## Output Contract

Return source path, cached text path, extractor used, and any extraction limitations.

## References

- `../../docs/extracted/README.md` — cache convention when present.
