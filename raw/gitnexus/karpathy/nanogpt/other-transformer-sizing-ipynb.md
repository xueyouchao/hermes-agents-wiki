# Other — transformer_sizing.ipynb

# Transformer Sizing Analysis

## Purpose

This notebook provides a theoretical analysis toolkit for estimating the computational and memory characteristics of a GPT-2-style Transformer. It calculates parameter counts, FLOPs, checkpoint sizes, GPU memory footprint, and training time — all from the model's architectural hyperparameters alone, without needing to instantiate the model.

Use this notebook when changing model configurations (e.g., scaling from GPT-2 to GPT-2-XL) to predict resource requirements before committing to a training run.

## Configuration

The model is defined by six global variables at the top of the notebook:

| Variable | Default (GPT-2) | Description |
|---|---|---|
| `block_size` | 1024 | Maximum sequence length (T) |
| `vocab_size` | 50257 | Vocabulary size |
| `n_layer` | 12 | Number of transformer blocks (L) |
| `n_head` | 12 | Number of attention heads (H) |
| `n_embd` | 768 | Embedding dimension |
| `bias` | False | Whether linear layers use bias (must be `False` for this notebook's formulas) |

Commented-out configurations for other GPT-2 variants are included for reference:

- **gpt2-medium**: L=24, H=16, n_embd=1024 → ~350M params
- **gpt2-large**: L=36, H=20, n_embd=1280 → ~774M params
- **gpt2-xl**: L=48, H=25, n_embd=1600 → ~1558M params

## Core Functions

### `params()` → `OrderedDict`

Estimates the total number of trainable parameters, broken down by component. Returns an ordered dictionary with keys at multiple granularity levels:

**Embedding layer:**
- `emebedding/position` — `n_embd × block_size` (positional embeddings)
- `embedding/token` — `n_embd × vocab_size` (token embeddings)
- `embedding` — sum of the above

**Per-block attention:**
- `attention/ln` — `n_embd` (LayerNorm weight, no bias)
- `attention/kqv` — `n_embd × 3×n_embd` (fused QKV projection)
- `attention/proj` — `n_embd²` (output projection)
- `attention` — sum of the above

**Per-block MLP:**
- `mlp/ln` — `n_embd` (LayerNorm weight)
- `mlp/ffw` — `n_embd × 4×n_embd` (up-projection)
- `mlp/proj` — `4×n_embd × n_embd` (down-projection)
- `mlp` — sum of the above

**Aggregated:**
- `block` — `attention + mlp` (per-layer total)
- `transformer` — `n_layer × block`
- `ln_f` — `n_embd` (final LayerNorm)
- `dense` — `0` (weight-tied with token embedding, not counted separately)
- `total` — `embedding + transformer + ln_f + dense`

For the default GPT-2 config, this yields **124,337,664** parameters, matching PyTorch's reported count exactly.

### `flops()` → `OrderedDict`

Estimates FLOPs for a single forward pass over a sequence of length `block_size`. Only matrix-multiply FLOPs are counted (LayerNorm, Softmax, etc. are considered negligible). The convention is **actual FLOPs** (not MACs): a matrix multiply `A(B×C) @ B(C×D)` costs `2×B×C×D` FLOPs.

**Per-block attention:**
- `attention/kqv` — `2 × T × (n_embd × 3×n_embd)` — QKV projections
- `attention/scores` — `2 × T × T × n_embd` — dot-product attention scores
- `attention/reduce` — `2 × H × (T × T × head_size)` — weighted value reduction
- `attention/proj` — `2 × T × (n_embd × n_embd)` — output projection

**Per-block MLP:**
- `mlp/ffw1` — `2 × T × (n_embd × 4×n_embd)` — up-projection
- `mlp/ffw2` — `2 × T × (4×n_embd × n_embd)` — down-projection

**Aggregated:**
- `block` — `attention + mlp`
- `transformer` — `n_layer × block`
- `dense` — `2 × T × (n_embd × vocab_size)` — output logits (weight-tied)
- `forward_total` — `transformer + dense`
- `backward_total` — `2 × forward_total` (standard approximation)
- `total` — `forward_total + backward_total`

### `palm_flops()` → `int`

Cross-validates the `flops()` estimate using the formula from the [PaLM paper](https://arxiv.org/abs/2204.02311):

```
N = total_params - position_embedding_params
mf_per_token = 6N + 12 × L × H × Q × T
total_flops = mf_per_token × T
```

Where `Q = n_embd // n_head` (head dimension). The two methods agree to within 0.01%, confirming the correctness of the detailed breakdown.

## Derived Calculations

### Checkpoint Size

An AdamW checkpoint stores each parameter three times in fp32:
- The parameter itself (4 bytes)
- First moment estimate (4 bytes)
- Second moment estimate (4 bytes)

```
checkpoint_bytes = params_total × 4 × 3
```

For GPT-2: ~1.49 GB estimated vs. 1.54 GB measured → ~3.4% overhead from non-parameter metadata.

### GPU Memory Ratio

On a 40 GB A100, the parameters + optimizer buffers consume only ~3.7% of GPU memory for GPT-2. The vast majority of memory is consumed by activations (forward + backward). This ratio shifts dramatically for larger models.

### Model Flops Utilization (MFU)

MFU measures what fraction of a GPU's theoretical peak FLOPs the training loop achieves:

```
flops_achieved = total_flops × (batch_size / measured_time)
MFU = flops_achieved / gpu_peak_flops
```

With batch_size=100 (20 × 5 grad_accum) and 755ms/iteration on a single A100, the measured MFU is **~37%**. The target for well-optimized training is 50%+.

### Training Time Estimation (6ND Rule)

The total training FLOPs follow the approximation:

```
total_flops = 6 × N × D
```

Where N = parameter count, D = total training tokens. Training time on an 8×A100 node at 30% MFU:

```
time = (6 × N × D) / (8 × 312 TFLOPS × 0.3)
```

For GPT-2 (124M params, 300B tokens): **~3.46 days** estimated, matching the observed ~4 days.

## Parameter Distribution

The parameter breakdown reveals where the model's capacity lives:

```
Component              Ratio
────────────────────────────
Token embedding        31.0%
Transformer blocks     68.3%
  ├─ Attention (per L)   1.9%
  └─ MLP (per L)         3.8%
Position embedding      0.6%
Final LayerNorm         ~0%
```

Key observations:
- Token embeddings dominate at ~31% of all parameters
- Each transformer block is ~2:1 MLP-to-attention ratio
- The output head (`dense`) contributes 0 additional parameters due to weight tying with the token embedding

## FLOPs Distribution

```
Component              Ratio of forward
────────────────────────────────────────
Transformer blocks     72.9%
Output logits (dense)  27.1%
  ├─ Per-block MLP       3.3%
  └─ Per-block Attn      2.8%
```

The output logits layer is the single most expensive operation (~27% of forward FLOPs) because of the large vocabulary size. Within each block, the MLP is slightly more expensive than attention.

## Limitations

- **`bias` must be `False`** — the formulas do not account for bias parameters in linear layers or LayerNorm
- **Memory bandwidth** is not estimated — FLOPs are only one constraint; LOAD/STORE costs are noted as TODO
- **Activation memory** is not computed — only parameter/optimizer memory is estimated
- The backward-pass FLOPs use the `2× forward` approximation, which is exact only for elementwise operations and slightly overestimates for some fused ops