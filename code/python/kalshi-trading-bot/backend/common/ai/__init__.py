"""AI module for enhanced signal analysis and market intelligence.

Primary providers:
  - Ollama (glm-5.1:cloud for analysis, minimax-m2.7:cloud for classification)
  - Claude (legacy, kept for backward compatibility)
  - Groq (legacy, kept for backward compatibility)
"""
from .base import AIAnalysis, AIProvider, AnomalyReport, TradeRecommendation, BaseAIClient, create_signal_prompt, create_classification_prompt
from .ollama import OllamaClient, ollama_client, analyze_signal_with_ollama, classify_market_with_ollama
from .claude import ClaudeAnalyzer
from .groq import GroqClassifier
from .logger import AICallLogger

__all__ = [
    'AIAnalysis',
    'AIProvider',
    'AnomalyReport',
    'TradeRecommendation',
    'BaseAIClient',
    'OllamaClient',
    'ClaudeAnalyzer',
    'GroqClassifier',
    'AICallLogger',
    'analyze_signal_with_ollama',
    'classify_market_with_ollama',
    'create_signal_prompt',
    'create_classification_prompt',
]