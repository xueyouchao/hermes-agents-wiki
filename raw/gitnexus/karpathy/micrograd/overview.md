# micrograd — Wiki

# micrograd

Welcome to micrograd — a minimal autograd engine and neural network library built for clarity and education. In roughly 150 lines of code, it implements reverse-mode automatic differentiation over a dynamically constructed DAG and layers a PyTorch-style neural network API on top. Every computation is scalar-level, meaning each neuron is decomposed into individual additions and multiplications. Despite this simplicity, it's capable of training deep networks on real classification tasks.

## Architecture

```mermaid
flowchart TD
    subgraph NN ["micrograd.nn"]
        MLP[MLP]
        Layer[Layer]
        Neuron[Neuron]
    end
    subgraph Engine ["micrograd.engine"]
        Value[Value]
    end
    Neuron -->|weights, biases, activations are| Value
    Layer -->|composed of| Neuron
    MLP -->|composed of| Layer
    Value -->|backward\(\) propagates| Grad[gradients]
    Grad -->|used by| Optim[Parameter Update]
    Optim -->|zero_grad resets| Neuron
```

The system has two layers. The [Autograd Engine](autograd-engine.md) defines `Value`, a scalar node that tracks its operation and children to form a computational DAG. Calling `backward()` on any `Value` traverses that DAG in reverse, accumulating gradients via the chain rule.

The [Neural Network Module](neural-network.md) builds a classic hierarchy — `Neuron` → `Layer` → `MLP` — where every parameter is a `Value` object. This means the entire forward pass is traceable and gradients flow through the network automatically, no special handling required.

Supporting infrastructure including the demo notebook, graph visualization, and tests is documented in [Other](other.md).

## End-to-End Flow

A typical training loop looks like this:

1. **Reset gradients** — Call `model.zero_grad()` to clear accumulated gradients on all parameters.
2. **Forward pass** — Feed inputs through the `MLP`. Each `Neuron` computes a weighted sum and applies an activation (e.g., ReLU), all as differentiable `Value` operations.
3. **Compute loss** — The output `Value`(s) are combined into a scalar loss.
4. **Backward pass** — Call `loss.backward()`. The engine traverses the DAG in reverse, computing `∂loss/∂param` for every parameter.
5. **Update parameters** — Adjust each parameter's data by a small step in the negative gradient direction.

This loop is demonstrated end-to-end in the [demo notebook](other.md), which trains a binary classifier on the two-moons dataset.

## Getting Started

Install the package:

```bash
pip install micrograd
```

Then create and differentiate computations:

```python
from micrograd.engine import Value

a = Value(-4.0)
b = Value(2.0)
c = a + b
d = a * b + b**3
d += (b - a).relu()
d.backward()

print(a.grad, b.grad)  # gradients of d w.r.t. a and b
```

To build and train a neural network, see the [Neural Network Module](neural-network.md) documentation or run the demo notebook directly.