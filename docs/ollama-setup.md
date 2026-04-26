# Ollama Setup Guide — Polymarket AI Arbitrage

## Your Subscription

- **Provider**: Ollama Pro
- **Current Plan**: Pro
- **Renews**: April 22, 2027
- **Model**: `kimi-k2.6:cloud` (hosted by Ollama under commercial license)

## Authentication

Ollama Pro cloud inference typically requires an API key. Local Ollama server does not.

```bash
# Add to your ~/.bashrc or run before starting the Python bridge
export OLLAMA_HOST="https://your-ollama-pro-endpoint.ollama.com"   # cloud only; omit for local
export OLLAMA_API_KEY="ollama_pro_key_xxx"                         # cloud only
export OLLAMA_MODEL="kimi-k2.6:cloud"
```

## Local Development (WSL)

For zero-latency local testing before hitting Pro credits:

```bash
# Install Ollama in WSL
curl -fsSL https://ollama.com/install.sh | sh

# Pull a fast open-weight surrogate (not kimi — local only)
ollama pull qwen2.5:14b

# Start server
ollama serve

# Then override model only for local dev
export OLLAMA_HOST="http://localhost:11434"
export OLLAMA_MODEL="qwen2.5:14b"
```

## Verify Connectivity

```bash
curl ${OLLAMA_HOST:-http://localhost:11434}/api/tags   -H "Authorization: Bearer ${OLLAMA_API_KEY}" 2>/dev/null | jq '.models[].name'
# Should list: kimi-k2.6:cloud
```

## Architecture Note

Pro plan inference runs in Ollama cloud (unknown region). If your Go engine is on AWS, measure RTT:

```bash
ping your-ollama-pro-endpoint.ollama.com
```

Target: **total round-trip + inference < 1.5s** so Go engine still has 1.2s for execution within the 2.7s arbitrage window.

If latency is too high, run **Ollama locally on a GPU box** in the same VPC as the Go engine and only use Pro for model updates/research.
