# Other — tests

# Tests Module

## Overview

The `tests` module provides test coverage for the minbpe tokenizer library. It validates encoding/decoding correctness, GPT-4 tiktoken parity, special token handling, and tokenizer serialization (save/load). A large real-world text fixture (`taylorswift.txt`) serves as the training corpus for tokenizer tests.

## Structure

```
tests/
├── __init__.py          # Empty; marks directory as Python package
├── taylorswift.txt      # Test fixture — Wikipedia article on Taylor Swift
└── test_tokenizer.py     # Test cases (referenced by call graph)
```

## Test Fixture: `taylorswift.txt`

A snapshot of the Wikipedia article on Taylor Swift (as of February 16, 2024), used as a realistic, multi-kilobyte text corpus. It provides:

- **Diverse character content**: Unicode symbols, punctuation, varied sentence structures, and mixed formatting (tables, lists, references).
- **Sufficient length**: Large enough to exercise BPE merge training meaningfully.
- **Reproducibility**: A fixed corpus ensures deterministic test outcomes across runs.

## Test Functions

### `test_encode_decode_identity`

Validates that encoding followed by decoding produces the original input unchanged.

```python
# Pseudocode flow:
original_text = unpack(...)          # Load fixture data
encoded = tokenizer.encode(original_text)
decoded = tokenizer.decode(encoded)
assert decoded == original_text
```

**What it catches**: Broken merge tables, incorrect byte-level handling, or decode logic that drops or mutates tokens.

### `test_gpt4_tiktoken_equality`

Asserts that the minbpe `RegexTokenizer` produces byte-level encodings identical to OpenAI's `tiktoken` library with the GPT-4 `cl100k_base` encoding.

```python
# Pseudocode flow:
text = unpack(...)                   # Load fixture data
minbpe_tokens = tokenizer.encode(text)
tiktoken_tokens = tiktoken_reference.encode(text)
assert minbpe_tokens == tiktoken_tokens
```

**What it catches**: Divergence in regex pattern matching, merge order, or special token handling between minbpe and the reference implementation.

### `test_gpt4_tiktoken_equality_special_tokens`

Extends the GPT-4 parity check to cover **special tokens** (e.g., `<|endoftext