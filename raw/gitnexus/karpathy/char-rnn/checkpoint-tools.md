# Checkpoint Tools

# Checkpoint Tools

Two standalone command-line utilities for inspecting and converting model checkpoint files. These scripts operate on `.t7` serialized checkpoints produced during training.

## Overview

| Script | Purpose |
|--------|---------|
| `convert_gpu_cpu_checkpoint.lua` | Converts a GPU-trained checkpoint to a CPU-compatible format |
| `inspect_checkpoint.lua` | Prints the training options and validation losses stored in a checkpoint |

Both scripts are run directly from the command line and share a common pattern: initialize the appropriate backend (CUDA, OpenCL, or CPU), load the checkpoint file, then perform their respective operation.

## Checkpoint File Structure

The scripts expect checkpoints serialized with `torch.save` containing at minimum these fields:

- **`protos`** — table of `nn.Module` networks (e.g., the language model components). Each key is a network name, each value is an `nn` module instance.
- **`opt`** — table of training options/hyperparameters that were saved alongside the model.
- **`val_losses`** — array of validation loss values recorded across training iterations.

---

## convert_gpu_cpu_checkpoint.lua

Converts a GPU checkpoint into a CPU-compatible checkpoint by deserializing on the target GPU backend, then casting every network in `protos` to double-precision CPU tensors.

### Usage

```bash
th convert_gpu_cpu_checkpoint.lua -model /path/to/model.t7 [-gpuid 0] [-opencl 0]
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `-model` | Yes | — | Path to the GPU checkpoint file to convert |
| `-gpuid` | No | `0` | GPU device index. Set to `-1` to force CPU-only loading |
| `-opencl` | No | `0` | Set to `1` to use OpenCL instead of CUDA |

### How It Works

```mermaid
flowchart LR
    A[Load checkpoint] --> B[Iterate protos]
    B --> C["net:double()"]
    C --> D["Save as model_cpu.t7"]
```

1. **Backend initialization** — If `gpuid >= 0`, the script initializes the requested GPU backend (CUDA or OpenCL). This is necessary because the checkpoint's serialized tensors live on the GPU; the backend must be available to deserialize them. The script exits if the required packages (`cunn`/`cutorch` or `clnn`/`cltorch`) are not found.

2. **Load checkpoint** — `torch.load(opt.model)` deserializes the full checkpoint, including all GPU-resident networks.

3. **Convert networks** — Iterates over every entry in `checkpoint.protos` and calls `:double()` on each network. This recursively casts all parameters and gradients from GPU tensors to CPU double-precision tensors.

4. **Save** — Writes the modified checkpoint to the same path with `_cpu.t7` appended. For example, `models/lm.t7` becomes `models/lm.t7_cpu.t7`.

### Output

The converted file preserves the full checkpoint structure (`opt`, `val_losses`, `protos`) with all networks converted to CPU doubles. Use this file for inference on machines without a GPU or for further CPU-based training.

> **Note:** This is described in the source as a temporary patch ("until I implement a more long-term solution"). The output filename convention appends `_cpu.t7` rather than replacing the `.t7` extension, resulting in names like `model.t7_cpu.t7`.

---

## inspect_checkpoint.lua

Loads a checkpoint and prints its `opt` and `val_losses` fields. Useful for verifying training configuration or monitoring validation loss history without loading the full model into a training pipeline.

### Usage

```bash
th inspect_checkpoint.lua -model /path/to/model.t7 [-gpuid 0] [-opencl 0]
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `-model` | Yes | — | Path to the checkpoint file to inspect |
| `-gpuid` | No | `0` | GPU device index. Set to `-1` for CPU-only |
| `-opencl` | No | `0` | Set to `1` to use OpenCL instead of CUDA |

### How It Works

1. **Backend initialization** — Same GPU backend detection as the converter, but uses hard `require` calls rather than `pcall`. If `gpuid >= 0`, the corresponding backend packages must be installed; the script will error if they are missing.

2. **Load and print** — Deserializes the checkpoint and prints two fields:
   - `model.opt` — the full options table used during training
   - `model.val_losses` — the recorded validation loss values

### Output Example

```
opt:
{
  model : lstm
  rnn_size : 128
  num_layers : 2
  ...
}
val losses:
{
  1 : 3.2145
  2 : 2.9871
  ...
}
```

---

## GPU Backend Selection

Both scripts support three execution modes controlled by the `-gpuid` and `-opencl` flags:

| `-gpuid` | `-opencl` | Backend | Required Packages |
|----------|-----------|---------|-------------------|
| `-1` | any | CPU only | None (beyond base Torch) |
| `≥ 0` | `0` | CUDA | `cunn`, `cutorch` |
| `≥ 0` | `1` | OpenCL | `clnn`, `cltorch` |

The device index uses Lua's 1-based indexing internally (`gpuid + 1`), matching the convention used throughout the codebase.

> **Important:** Even if you only want to inspect or convert a checkpoint for CPU use, you must have the original GPU backend available if the checkpoint was saved with GPU tensors. The backend is needed at load time to deserialize the tensor data. Once loaded, `convert_gpu_cpu_checkpoint.lua` casts everything to CPU, and the resulting `_cpu.t7` file no longer requires any GPU backend.

## Dependencies

Both scripts depend on:

- `torch`, `nn`, `nngraph` — core Torch packages
- `util.OneHot`, `util.misc` — project utility modules (required for deserialization of checkpoints that reference these modules)
- `lfs` — Lua file system library (converter only, though not actively used in the current code)