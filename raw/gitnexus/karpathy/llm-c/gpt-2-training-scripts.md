# GPT-2 Training — scripts

# GPT-2 Training Scripts

Shell scripts that reproduce GPT-2 and GPT-3 training runs using llm.c or PyTorch. Each script encodes the exact hyperparameters, data paths, and hardware configuration needed to train a specific model size to Chinchilla-optimal compute.

## Script Inventory

| Script | Backend | Model | Params | Tokens | Dataset | Hardware Estimate |
|---|---|---|---|---|---|---|
| `run_gpt2_124M.sh` | llm.c | GPT-2 124M | 124M | 10B | FineWeb 10B | 8×A100, ~94 min, ~$20 |
| `run_gpt2_350M.sh` | llm.c | GPT-2 350M | 350M | ~30B | FineWeb 100B | 8×A100, ~13.7 hr, ~$200 |
| `run_gpt2_774M.sh` | llm.c | GPT-2 774M | 774M | ~150B | FineWeb 100B | 8×A100, ~135 hr, ~$2000 |
| `run_gpt2_1558M.sh` | llm.c | GPT-2 1558M | 1558M | 32B | FineWeb-EDU 100B | 8×H100, ~24 hr, ~$672 |
| `run_gpt3_125M.sh` | llm.c | GPT-3 125M | 125M | 300B | FineWeb 100B | 8×A100, ~24 hr, ~$336 |
| `pyrun_gpt2_124M.sh` | PyTorch | GPT-2 124M | 124M | 10B | FineWeb 10B | 8×GPU |

The compute budget for each run follows the Chinchilla scaling law: `6 × params × tokens`. For example, the 124M run targets `6 × 124e6 × 10e9 ≈ 7e18` FLOPs.

## Two Training Backends

### llm.c (`train_gpt2cu`)

The C/CUDA implementation, launched via `mpirun`:

```bash
make train_gpt2cu USE_CUDNN=1
mpirun -np 8 ./train_gpt2cu -i ... -j ... -o log_gpt2_124M ...
```

Built with `USE_CUDNN=1` to enable cuDNN acceleration. Supports checkpointing, HellaSwag evaluation, and automatic crash recovery.

### PyTorch (`train_gpt2.py`)

The Python reference implementation, launched via `torchrun`:

```bash
torchrun --standalone --nproc_per_node=8 train_gpt2.py \
    --input_bin "..." --input_val_bin "..." --output_dir pylog_gpt2_124M ...
```

Current limitations compared to llm.c:
- No checkpoint writes — only train/val loss logs
- No HellaSwag accuracy evaluation
- No resume-from-checkpoint support

## Crash Recovery Loop

All llm.c scripts wrap the training invocation in a `while true` loop that checks for a completion marker file before each iteration:

```bash
out_dir="log_gpt2_124M"
done_file="$out_dir/DONE_00018865"

while true; do
    if [ -f "$done_file" ]; then
        echo "File $done_file exists. Exiting the loop."
        break
    fi

    mpirun -np 8 ./train_gpt2cu ... -y 1 ...

    sleep 1
done
```

The DONE file is named `DONE_XXXXXXXXX` where the number matches the total iteration count (e.g., `DONE_00018865` for 18,865 steps). The `-y 1` flag tells `train_gpt2cu` to resume from the latest checkpoint on startup. If the process crashes or stalls, the loop re-launches it and training continues from where it left off.

## Flag Reference

### llm.c Flags (`train_gpt2cu`)

| Flag | Example | Description |
|---|---|---|
| `-i` | `fineweb_train_*.bin` | Training data glob pattern |
| `-j` | `fineweb_val_*.bin` | Validation data glob pattern |
| `-o` | `log_gpt2_124M` | Output directory for logs/checkpoints |
| `-v` | `250` | Validate every N steps |
| `-s` | `20000` | Sample/generate every N steps |
| `-g` | `144` | HellaSwag evaluation every N steps |
| `-h` | `1` | Enable HellaSwag evaluation |
| `-b` | `64` | Micro batch size per GPU |
| `-t` | `1024` | Maximum sequence length |
| `-d` | `524288` | Total batch size in tokens (across all GPUs + grad accumulation) |
| `-r` | `0` | Recompute flag (0=none, 1=recompute GeLU) |
| `-z` | `1` | ZeRO stage (1=shard optimizer states) |
| `-c` | `0.1` | Weight decay |
| `-l` | `0.0006` | Peak learning rate |
| `-q` | `0.0` | Learning rate decay fraction (0.0=no decay, 0.1=cosine) |
| `-k` | `cosine` | LR schedule type (used in 1558M) |
| `-u` | `700` | Warmup iterations |
| `-n` | `5000` | Number of iterations (0=infinite, used with `-x`) |
| `-x` | `60000` | Maximum total iterations |
| `-e` | `d12` | Model architecture spec |
| `-y` | `1` | Resume from checkpoint on startup |
| `-ge` | `1` | Gradient clipping enabled |
| `-sl` | `7.0` | Gradient clip low threshold |
| `-sg` | `7.0` | Gradient clip high threshold |
| `-nk` | `5` | Number of evaluation runs |
| `-nm` | `50000` | Max evaluation samples |

### PyTorch Flags (`train_gpt2.py`)

| Flag | Example | Description |
|---|---|---|
| `--input_bin` | `fineweb_train_*.bin` | Training data glob |
| `--input_val_bin` | `fineweb_val_*.bin` | Validation data glob |
| `--output_dir` | `pylog_gpt2_124M` | Output directory |
| `--val_loss_every` | `250` | Validate every N steps |
| `--sample_every` | `0` | Sample every N steps |
| `--write_tensors` | `0` | Write tensor logs |
| `--model` | `d12` | Model architecture spec |
| `--batch_size` | `32` | Micro batch size per GPU |
| `--sequence_length` | `1024` | Maximum sequence length |
| `--total_batch_size` | `524288` | Total batch size in tokens |
| `--dtype` | `bfloat16` | Training precision |
| `--compile` | `1` | Use `torch.compile` |
| `--tensorcores` | `1` | Enable TensorCore usage |
| `--flash` | `1` | Use Flash Attention |
| `--num_iterations` | `18865` | Total training iterations |
| `--weight_decay` | `0.1` | Weight decay |
| `--zero_stage` | `1` | ZeRO stage |
| `--learning_rate` | `0.0006` | Peak learning rate |
| `--warmup_iters` | `700` | Warmup iterations |
| `--learning_rate_decay_frac` | `0.0` | LR decay fraction |
| `--overfit_single_batch` | `0` | Debug: overfit single batch |

## Model Architecture Specs

The `-e` / `--model` flag selects the transformer configuration:

| Spec | Model | Layers | Hidden | Heads | Context |
|---|---|---|---|---|---|
| `d12` | GPT-2 124M | 12 | 768 | 12 | 1024 |
| `d24` | GPT-2 350M | 24 | 1024 | 16 | 1024 |
| `d36` | GPT-2 774M | 36 | 1280 | 20 | 1024 |
| `d48` | GPT-2 1558M | 48 | 1600 | 25 | 1024 |
| `gpt3:c768` | GPT-3 125M | 12 | 768 | 12 | 2048 |

The GPT-3 125M model shares the same width as GPT-2 124M but doubles the context length to 2048 and trains on 300B tokens instead of 10B.

## Data Prerequisites

Each script expects preprocessed `.bin` files in `dev/data/`. Generate them before running:

```bash
# For FineWeb 10B (124M model)
python dev/data/fineweb.py --version 10B

# For FineWeb 100B (350M, 774M, GPT-3 125M)
python dev/data/fineweb.py --version 100B

# For FineWeb-EDU 100B (1558M model)
python dev/data/edu_fineweb.py --version 100B

# For HellaSwag evaluation (llm.c scripts only)
python dev/data/hellaswag.py
```

## Memory Optimization

If you hit OOM on smaller GPUs, adjust these flags in order of priority:

1. **Enable recompute** (`-r 1`): Discards GeLU activations during forward pass and recomputes them in backward. Trades compute for memory.

2. **Reduce micro batch size** (`-b`): Halve it repeatedly (64 → 32 → 16 → 8) until the model fits. The gradient accumulation loop automatically compensates to maintain the same total batch size.

3. **Reduce sequence length** (`-t`): If your task tolerates shorter context, lower from 1024 or 2048. This is linear in memory.

After getting things to fit, try dialing recompute back to `-r 0` to recover speed.

## Single-GPU and Multi-Node

### Single GPU

Drop the multi-process launcher — the binary/script auto-detects available GPUs and adjusts gradient accumulation accordingly. Results are identical up to floating-point precision.

```bash
# llm.c: replace mpirun invocation
./train_gpt2cu -i ... -j ... [all other flags same]

# PyTorch: replace torchrun invocation
python train_gpt2.py --input_bin ... --input_val_bin ... [all other flags same]
```

### Multi-Node

For llm.c, pass a host specification to `mpirun`:

```bash
mpirun -np 16 --host node1:8,node2:8 ./train_gpt2cu ...
```

For PyTorch, consult the [torchrun documentation](https://pytorch.org/docs/stable/elastic/run.html) for multi-node configuration. See also [PR #426](https://github.com/karpathy/llm.c/pull/426) for multi-node llm.c support.

## Training Hyperparameter Summary

| Model | LR | Warmup | Decay | Weight Decay | Batch (tokens) | Schedule |
|---|---|---|---|---|---|---|
| 124M | 6e-4 | 700 | 0.0 | 0.1 | 524,288 | Constant |
| 350M | 3e-4 | 700 | 0.0 | 0.1 | 524,288 | Constant |
| 774M | 2.5e-4 | 700 | 0.0 | 0.1 | 524,288 | Constant |
| 1558M | 6e-4 | 700 | 0.1 (cosine) | 0.1 | 1,048,576 | Cosine |
| GPT-3 125M | 6e-4 | 700 | 0.1 | 0.1 | 524,288 | Cosine |

The smaller models use constant LR (no decay). The 1558M and GPT-3 125M runs use cosine decay with a decay fraction of 0.1.