# Other — openwebtext

# OpenWebText Dataset Module

## Overview

The `data/openwebtext` module provides preprocessing tooling for the [OpenWebText](https://skylion007.github.io/OpenWebTextCorpus/) corpus — an open-source reproduction of OpenAI's WebText dataset, which was introduced in the [GPT-2 paper](https://d4mucfpksywv.cloudfront.net/better-language-models/language_models_are_unsupervised_multitask_learners.pdf). The module converts raw documents into tokenized binary files suitable for training language models.

## Preparation

Run the preprocessing script to tokenize and split the raw corpus:

```bash
python data/openwebtext/prepare.py
```

This reads the raw OpenWebText documents, tokenizes them, and writes the output splits to disk.

## Output Files

After `prepare.py` completes, two binary files are produced in the module directory:

| File | Size | Token Count |
|------|------|-------------|
| `train.bin` | ~17 GB | 9,035,582,198 |
| `val.bin` | ~8.5 MB | 4,434,897 |

The dataset is derived from **8,013,769 documents** in total. The validation split is intentionally small relative to training, reflecting the scale imbalance typical in large-scale language model training.

## Token Format

The `.bin` files contain token IDs stored as packed binary data. Consumers of these files should read the token sequences and feed them into the model's input pipeline. The tokenization scheme matches the GPT-2 byte-level BPE vocabulary.

## Integration

This module is a standalone data preparation step — it has no runtime dependencies on other modules in the codebase and is not invoked by any other module. It is run once offline to produce the training and validation binaries, which are then consumed by the training loop.

## References

- **GPT-2 Paper**: [Language Models are Unsupervised Multitask Learners](https://d4mucfpksywv.cloudfront.net/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)
- **OpenWebText Corpus**: [https://skylion007.github.io/OpenWebTextCorpus/](https://skylion007.github.io/OpenWebTextCorpus/)