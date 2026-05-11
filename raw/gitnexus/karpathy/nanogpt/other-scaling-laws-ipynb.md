# Other — scaling_laws.ipynb

# Scaling Laws (scaling_laws.ipynb)

## Purpose

This notebook reproduces key results from the [Chinchilla paper](https://arxiv.org/pdf/2203.15556.pdf) (Hoffmann et al., 2022). It provides utilities for calculating parameter counts and FLOPs for transformer language models, and fits the scaling law function L(N, D) to determine compute-optimal model configurations. The numbers don't match the paper exactly but serve as a practical guide.

## Key Functions

### `gpt_params(seq_len, vocab_size, d_model, num_heads, num_layers)`

Calculates the total number of parameters in a GPT-style model. The FFN intermediate size is hardcoded to `4 * d_model` per GPT conventions.

**Parameter breakdown per component:**

| Component | Formula |
|---|---|
| Token + position embeddings | `d_model * vocab_size + d_model * seq_len` |
| QKV projections (per layer) | `3 * d_model² + 3 * d_model` |
| Output projection (per layer) | `d_model² + d_model` |
| FFN up (per layer) | `d_model * ffw_size + ffw_size` |
| FFN down (per layer) | `ffw_size * d_model + d_model` |
| Layer norms (per layer) | `2 * 2 * d_model` |
| Final layer norm | `2 * d_model` |
| Output head (no bias) | `d_model * vocab_size` |

**Important:** Embedding parameters are excluded from the total count. The function returns ~123.65M for GPT-2 small config, matching OpenAI's reported 124M.

### `chinchilla_params(seq_len, vocab_size, d_model, num_heads, num_layers, ffw_size)`

Calculates parameters for Chinchilla-family models. Unlike GPT, these use **relative positional embeddings** instead of learned position embeddings, and the FFN size is a separate argument rather than fixed at `4 * d_model`.

**Key differences from `gpt_params`:**

- No position embeddings (token embeddings only)
- Additional relative position parameters per layer: `d_model² + 2 * d_model` (relative keys, content bias, relative bias)
- `ffw_size` is configurable

The notebook validates this against all 50 Chinchilla model configurations from Table A9. The estimated counts closely match the reported values (within ~5% for most models, with larger deviations for a few).

### `chinchilla_flops(seq_len, vocab_size, d_model, num_heads, num_layers, ffw_size)`

Calculates total training FLOPs following Chinchilla Appendix F. The `key_size` is derived as `d_model // num_heads`.

**FLOP breakdown:**

| Component | Formula |
|---|---|
| Embeddings | `2 * seq_len * vocab_size * d_model` |
| QKV projections (per layer) | `2 * 3 * seq_len * d_model * (key_size * num_heads)` |
| Key × Query logits (per layer) | `2 * seq_len² * (key_size * num_heads)` |
| Softmax (per layer) | `3 * num_heads * seq_len²` |
| Softmax × Value (per layer) | `2 * seq_len² * (key_size * num_heads)` |
| Output projection (per layer) | `2 * seq_len * (key_size * num_heads) * d_model` |
| FFN (per layer) | `2 * seq_len * (d_model * ffw_size + d_model * ffw_size)` |
| Logits | `2 * seq_len * d_model * vocab_size` |

**Critical implementation detail:** Per author correspondence, there is a typo in the paper — embeddings and logits FLOPs are **not** counted when reproducing Table 4. The forward pass FLOPs are computed as:

```
forward_flops = num_layers * (attention_flops + ffn_flops)
```

Backward pass FLOPs are `2 * forward_flops` (per Kaplan et al. 2020), giving:

```
total_flops = 3 * forward_flops
```

## Approximate vs. Exact FLOPs

The notebook compares the exact FLOP calculation against the standard approximation:

```
approx_flops = 6 * D * N
```

where `D` is the dataset size (tokens) and `N` is the parameter count. Using the 6 models from Chinchilla Table A4 (with `vocab_size = 32000`, `seq_len = 2048`), the ratio of exact to approximate FLOPs ranges from ~0.99 to ~1.10, confirming the approximation is reasonable but not exact.

## Chinchilla Model Data

All 50 model configurations from Table A9 are embedded as a JSON array. Each entry is:

```
[total_params, d_model, ffw_size, kv_size, num_heads, num_layers]
```

Models range from 44M to 16.2B parameters.

## Scaling Laws: Approach 3

The notebook fits the Chinchilla Approach 3 loss function L(N, D), which approximates the final loss as a function of model size (N) and data size (D). This is the core scaling law used to determine compute-optimal allocations between model size and training data.

## Usage Notes

- The parameter count functions exclude embedding parameters from the total, consistent with the Chinchilla paper's convention.
- The FLOP calculation intentionally omits embedding and logit layers to match the paper's Table 4 reproduction.
- The `seq_len` parameter in `chinchilla_flops` effectively represents the number of tokens in a forward pass; for total training FLOPs, scale by `D / seq_len` where `D` is total training tokens.
- Validation against GPT-2 small (124M params) and Chinchilla Table A9/A4 models confirms the calculations are approximately correct, though not pixel-perfect matches to the paper.