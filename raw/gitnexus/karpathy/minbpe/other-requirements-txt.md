# Other — requirements.txt

# requirements.txt

## Purpose

This file declares the Python package dependencies required by the project. It serves as the single source of truth for environment setup, ensuring reproducible installations across development, CI, and deployment environments.

## Dependencies

| Package | Purpose |
|---------|---------|
| `regex` | Enhanced regular expression engine supporting advanced pattern features (e.g., Unicode properties, recursive patterns, fuzzy matching) beyond the standard `re` module |
| `tiktoken` | Fast BPE tokenization library developed by OpenAI, used for counting and encoding text tokens against specific tokenizer models |

## Installation

```bash
pip install -r requirements.txt
```

To install into an isolated environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Dependency Details

### regex

The `regex` module is a drop-in replacement for Python's built-in `re` module with extended capabilities. Within this project, it is likely used for:

- **Unicode-aware pattern matching** — full Unicode property support (e.g., `\p{L}`, `\p{N}`)
- **Best-effort fuzzy matching** — approximate string matching with configurable error thresholds
- **Recursive/balanced group patterns** — matching nested structures that `re` cannot handle

It is imported as `regex` and exposes the same API surface as `re`, so code can often substitute `import regex as re` for a seamless upgrade path.

### tiktoken

`tiktoken` provides fast byte-pair encoding (BPE) tokenization. Key characteristics:

- **Model-specific tokenizers** — supports `cl100k_base`, `p50k_base`, `r50k_base`, and other encoder models
- **Counting tokens** — `tiktoken.encoding_for_model(model_name)` returns an encoder whose `.encode()` method splits text into token IDs; `len(tokens)` yields the token count
- **Performance** — implemented in Rust, significantly faster than pure-Python tokenizers

Typical usage pattern:

```python
import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")
tokens = encoding.encode("some text to tokenize")
token_count = len(tokens)
```

## Relationship to the Codebase

This requirements file supports the project's text processing and tokenization logic. The two packages work in complementary roles:

- `regex` handles **pattern extraction and text parsing** — identifying structural elements in raw text
- `tiktoken` handles **token counting and encoding** — ensuring text conforms to model token limits

Any module in the project that performs string matching, text splitting, or token-level operations depends on one or both of these packages.

## Notes

- This file uses **unpinned versions** (`regex` and `tiktoken` without version specifiers). For production deployments, consider pinning versions (e.g., `regex==2023.12.25`, `tiktoken==0.7.0`) to guarantee reproducibility.
- No transitive dependencies are declared here; `pip` resolves them automatically from each package's own metadata.