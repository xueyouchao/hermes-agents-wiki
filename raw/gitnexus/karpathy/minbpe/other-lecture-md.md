# Other — lecture.md

# LLM Tokenization — Lecture Notes

## Overview

This document is a lecture transcript covering **tokenization in Large Language Models**. It progresses from a naive character-level approach to Byte Pair Encoding (BPE), motivates why tokenization matters, and previews the visual behavior of modern tokenizers. It is not an executable module — it serves as conceptual background for understanding the tokenization pipeline that feeds into Transformer-based LLMs.

## Topics Covered

### 1. Character-Level Tokenization (Baseline)

The simplest tokenization strategy maps each individual character to a unique integer. The lecture references the approach from the *Let's build GPT from scratch* video, which operates on the Shakespeare dataset.

**Vocabulary construction:**

```python
chars = sorted(list(set(text)))
vocab_size = len(chars)  # 65 for the Shakespeare text
```

**Encoding/decoding via lookup dictionaries:**

```python
stoi = { ch:i for i,ch in enumerate(chars) }
itos = { i:ch for i,ch in enumerate(chars) }

encode = lambda s: [stoi[c] for c in s]
decode = lambda l: ''.join([itos[i] for i in l])
```

- `encode("hii there")` → `[46, 47, 47, 1, 58, 46, 43, 56, 43]`
- `decode(encode("hii there"))` → `"hii there"`

**Embedding lookup in the model:**

```python
class BigramLanguageModel(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        self.token_embedding_table = nn.Embedding(vocab_size, n_embd)

    def forward(self, idx, targets=None):
        tok_emb = self.token_embedding_table(idx)  # (B,T,C)
```

Each integer index "plucks out" a row from `token_embedding_table`, producing the vector representation for that token. The vocabulary size (65) directly determines the number of rows in the embedding table.

### 2. Byte Pair Encoding (BPE)

Character-level tokenization is impractical for state-of-the-art LLMs. Instead, modern models tokenize at the **character-chunk level** using the BPE algorithm.

**Key reference:** The GPT-2 paper (*"Language Models are Unsupervised Multitask Learners"*, OpenAI 2019), Section 2.2 ("Input Representation"), popularized byte-level BPE for language model tokenization.

Notable parameters from that paper:
- Vocabulary expanded to **50,257** tokens
- Context length increased from 512 to **1,024** tokens

Tokens are the fundamental "atoms" at the Transformer's input. Tokenization is the bidirectional conversion between raw Python strings and lists of token integers.

### 3. Why Tokenization Matters

The lecture emphasizes that many seemingly mysterious LLM failures trace back to tokenization, not the neural network itself:

| Symptom | Root Cause |
|---|---|
| Inability to spell words | Tokens may represent multi-character chunks, hiding individual letters |
| Failure at simple string processing (e.g., reversing) | Operations on token IDs don't correspond to character-level manipulation |
| Poor performance on non-English languages (e.g., Japanese) | Non-ASCII text fragments into many tokens, reducing effective context length |
| Difficulty with arithmetic | Numbers are split inconsistently (e.g., `127` is one token, `677` becomes two) |
| Python coding issues in GPT-2 | Inconsistent tokenization of indentation and whitespace |
| Abrupt halting on specific strings (e.g., `"`)| Special tokens in the vocabulary trigger unintended behavior |
| Trailing whitespace warnings | Whitespace is tokenized but often invisible in UI |
| "SolidGoldMagikarp" anomalies | Rare tokens in the vocabulary that never appeared in training data |
| YAML preferred over JSON | YAML's syntax tokenizes more efficiently than JSON's structural characters |
| Not truly end-to-end language modeling | The model operates on token sequences, not raw text |

### 4. Visual Preview (tiktokenizer)

The [tiktokenizer webapp](https://tiktokenizer.vercel.app) demonstrates live tokenization. Key observations:

- **Whitespace is significant**: The token `" is"` (index 318) includes the leading space. Whitespace must be tokenized but is often hidden in visualizations.
- **Inconsistent number splitting**:
  - `127` → single token
  - `677` → two tokens (`" 6"` + `"77"`)
  - `1275` → `"12"` + `"75"`
  - `6773` → `" 6"` + `"773"`
  - `8041` → `" 8"` + `"041"`
- The LLM must learn these arbitrary splits during training and emit multi-token numbers across multiple time steps.

## Architecture Context

```mermaid
flowchart LR
    A[Raw Text String] --> B[Tokenizer encode]
    B --> C[Token ID Sequence]
    C --> D[nn.Embedding Lookup]
    D --> E[Transformer Forward Pass]
    E --> F[Logits]
    F --> G[Tokenizer decode]
    G --> H[Output Text String]
```

The tokenization pipeline sits entirely outside the neural network. The model never sees raw text — it only operates on integer token IDs and their corresponding embedding vectors. This separation is the source of both the pipeline's flexibility and its failure modes.

## Status

This document is marked as incomplete (`to be continued...`). The BPE algorithm implementation details, merging rules, and further examples are expected in a continuation.