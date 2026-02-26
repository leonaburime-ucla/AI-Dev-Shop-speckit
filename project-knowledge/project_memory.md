# Project Memory

Use for stable project-specific nuances and conventions.

> **Routing authority:** Before writing any new entry to this file, read `<SHOP_ROOT>/project-knowledge/knowledge-routing.md`. That file determines which memory file is the correct destination for any given content type. Only content classified as a stable convention, gotcha, constraint, or project-wide pattern belongs here.

## Entries

- YYYY-MM-DD: <fact/convention/gotcha>

- 2026-02-23: [CONVENTION] Inline documentation is required on all newly created functions, methods, classes, and modules — including nested functions, local helpers, and callbacks. Every parameter, return type, and thrown error must be documented. Functions with non-obvious behavior must include an explanation of intent. Use the language's idiomatic format: TypeDoc/JSDoc for TypeScript/JavaScript, docstrings for Python, Rustdoc for Rust, Javadoc for Java, XML doc comments for C#, etc. There are no exceptions for "small" or "obvious" functions.
