# Other — shakespeare_char

# shakespeare_char

Character-level tokenization of the Tiny Shakespeare dataset, producing binary training and validation splits for language modeling.

## Overview

This module prepares the classic **Tiny Shakespeare** corpus — a condensed collection of Shakespeare's works commonly used in character-level language modeling (dating back to the char-rnn era). It processes raw text into memory-mappable binary files where each token is a single UTF-8 character encoded as a byte-level integer.

## Dataset

The source text is a concatenation of Shakespeare's plays, stripped down to plain text. After tokenization:

| Split | File | Tokens |
|-------|------|--------|
| Train | `train.bin` | 1,003,854 |
| Val | `val.bin` | 111,540 |

The train/val split is approximately 90/10. At the character level, "tokens" correspond to individual characters in the source text.

## Usage

Run the preparation script to generate the binary files:

```bash
python prepare.py
```

This reads the raw Shakespeare text, encodes each character as a single byte (vocabulary size ≤ 256), and writes the resulting token sequences to `train.bin` and `val.bin` as raw `uint8` arrays — one byte per token.

## Output Format

Both `.bin` files are flat binary buffers of `uint8` values. They can be loaded efficiently with NumPy or memory-mapped directly:

```python
import numpy as np

# Load entirely into memory
data = np.fromfile("train.bin", dtype=np.uint8)

# Or memory-map for large-scale or lazy access
data = np.memmap("train.bin", dtype=np.uint8, mode="r")
```

Each integer value maps directly to a character via Python's `chr()` (or the equivalent in your framework's decoder). The vocabulary is the set of unique characters present in the source text — no special tokens, no BPE, no merging.

## Integration with Training

This module is a **data preparation step only**. It has no runtime dependencies on other modules and no downstream code calls into it during training. The generated `.bin` files are consumed by training scripts (typically in a `nanogpt`-style pipeline) that:

1. Memory-map or load the binary files.
2. Sample random chunks of a fixed context length.
3. Feed `(input, target)` pairs — shifted by one position — into a character-level transformer or RNN.

Because the tokenization is trivial (one character = one token), no decoder or detokenization logic is needed beyond casting `uint8` → `chr`.

## Design Notes

- **Why character-level?** Simplicity and interpretability. Every prediction is a single character, making it easy to inspect model output and debug generation. The small vocabulary (≤ 256) also keeps the output projection layer tiny.
- **Why raw binary?** Avoids the overhead of JSON/CSV parsing and enables memory-mapped training for arbitrarily large corpora. The `uint8` dtype is sufficient since the vocabulary fits in a single byte.
- **No special tokens.** There are no `<BOS>`, `<EOS>`, or `<PAD>` tokens injected by this module. If your training loop requires them, add them downstream after loading.