---  title: char-rnn
created: 2026-04-16
updated: 2026-04-16
type: entity
tags: [repository, lua, rnn, lstm, language-model, karpathy]
sources: []---# char-rnn
char-rnn is a multi-layer RNN (LSTM/GRU) implementation for character-level language modeling, written in Lua/Torch. It's one of Karpathy's classic projects.
## Key Stats- **Stars:** 12k
- **Language:** Lua (Torch)
- **Status:** Legacy (archived)
## GitNexus Analysis
- **Files:** 12
- **Symbols:** 27
- **Relationships:** 20 edges- **Clusters:** 0## OverviewThis was Karpathy's popular character-level language model that could generate text character-by-character. It was the basis for his famous blog post "The Unreasonable Effectiveness of Recurrent Neural Networks".## Architecture- Multi-layer RNN/LSTM/GRU- Character-level tokenization- Bidirectional option
- Dropout support## Historical SignificanceThis project was instrumental in demonstrating that RNNs could:- Learn to generate Shakespeare-like text
- Generate Linux kernel source code
- Model other structured text formatsIt helped popularize the idea of character-level language modeling.## Related
- [[andrej-karpathy]] - Author
- [[nanoGPT]] - Modern successor (Transformer-based)