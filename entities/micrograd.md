---
title: micrograd
created: 2026-04-16
updated: 2026-04-16
type: entity
tags: [repository, python, autograd, neural-network, karpathy]
sources: []
---

# micrograd

micrograd is a tiny autograd engine (with a bite!) that implements backpropagation (reverse-mode autodiff) over a dynamically built DAG, plus a small neural networks library on top with a PyTorch-like API.
 
## Key Stats
- **Stars:** 15.4k
- **Language:** Python
- **Lines:** ~100 (engine) + ~50 (nn)

## GitNexus Analysis
- **Files:** 8
- **Symbols:** 59
- **Relationships:** 122 edges
- **Clusters:** 4 functional areas
- **Processes:** 1 execution flow

## Architecture

### Engine (~100 lines)
- `Value` class - scalar with gradient
- Dynamic computational graph
- Supports: +, -, *, /, **, relu, sigmoid, etc.
 
### Neural Network Library (~50 lines)
- `Neuron`, `Layer`, `MLP` classes
- PyTorch-like API
- Supports binary classification

## Example Usage
```python
from micrograd.engine import Value
a = Value(-4.0)
b = Value(2.0)
c = a + b
d = a * b + b**3
c += c + 1
d += d * 2 + (b + a).relu()
# ... forward pass
g.backward()  # compute gradients
print(a.grad)  # dg/da
```

## Educational Purpose
Useful for understanding how autodiff works under the hood. The notebook `demo.ipynb` shows training a 2-layer MLP on the moon dataset.
 
## Related
- [[andrej-karpathy]] - Author