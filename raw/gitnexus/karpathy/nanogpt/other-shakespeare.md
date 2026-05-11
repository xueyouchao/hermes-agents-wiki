# Other — shakespeare

# Tiny Shakespeare

A minimal dataset module providing the classic **tiny shakespeare** text corpus, commonly used for training and benchmarking character-level language models.

## Overview

Tiny Shakespeare is a compact excerpt of Shakespeare's works, originating from Andrej Karpathy's char-rnn experiments. It serves as a lightweight, fast-iteration dataset for developing and testing language model architectures without the overhead of large-scale corpora.

## Dataset Statistics

| Split | File | Tokens |
|-------|------|--------|
| Train | `train.bin` | 301,966 |
| Val | `val.bin` | 36,059 |

The train/val split is approximately 89%/11%.

## Data Preparation

Run the preparation script to generate the binary token files:

```bash
python prepare.py
```

This reads the raw Shakespeare text, tokenizes it at the character level, and writes two binary files:

- **`train.bin`** — training split
- **`val.bin`** — validation split

The `.bin` files contain token IDs stored as raw binary data (typically `uint16` or `int32` depending on the vocabulary size), ready to be memory-mapped or loaded directly during training.

## Usage

The generated binary files are consumed by training loops elsewhere in the codebase. A typical pattern:

```python
import numpy as np

train_data = np.memmap("train.bin", dtype=np.uint16, mode="r")
val_data = np.memmap("val.bin", dtype=np.uint16, mode="r")
```

From there, chunks are sampled to form training batches for autoregressive language modeling.

## File Inventory

| File | Purpose |
|------|---------|
| `prepare.py` | Tokenizes raw text and produces `train.bin` / `val.bin` |
| `train.bin` | Tokenized training split (generated) |
| `val.bin` | Tokenized validation split (generated) |

## Notes

- The module is self-contained with no runtime dependencies on other modules in the codebase. It serves purely as a **data source**.
- Re-run `prepare.py` if the binary files are missing or corrupted.
- The small size of this dataset makes it ideal for debugging, overfitting tests, and rapid prototyping — not for production-scale evaluation.