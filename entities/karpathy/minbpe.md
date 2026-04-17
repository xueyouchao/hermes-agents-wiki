---
title: minbpe
created: 2026-04-16
updated: 2026-04-16
type: entity
tags: [repository, python, tokenization, bpe, karpathy]
sources: []
---

# minbpe

minbpe is a clean, minimal implementation of Byte Pair Encoding (BPE) - the standard tokenization method for modern LLMs (GPT-4, Llama, Mistral).

## Key Stats
- **Stars:** 10.4k
- **Language:** Python
- **Lines:** Minimal (~hundreds)

## GitNexus Analysis
- **Files:** 13
- **Symbols:** 116
- **Relationships:** 264 edges
- **Clusters:** 6 functional areas
- **Processes:** 14 execution flows

## Four Implementation Tiers

1. **base.py** - Tokenizer base class (stubs for train/encode/decode)
2. **basic.py** - Simple BPE on raw text
3. **regex.py** - Regex-based splitting (GPT-2 to GPT-4 style)
4. **gpt4.py** - Exact OpenAI tiktoken parity

## Key Features
- Operates on UTF-8 encoded strings
- Prevents merges across category boundaries (regex splitting)
- Handles special tokens for security
- Achieves exact parity with OpenAI's tiktoken

## Quick Start

```python
from minbpe import BasicTokenizer
tokenizer = BasicTokenizer()
text = "aaabdaaabac"
tokenizer.train(text, 256 + 3)  # 256 byte + 3 merges
print(tokenizer.encode(text))  # [258, 100, 258, 97, 99]
```

## Related
- [[andrej-karpathy]] - Author
- [[nanoGPT]] - Uses minbpe-style tokenization