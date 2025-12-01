# zs_bias_model.py
from transformers import pipeline
import torch
from typing import Dict
import hashlib

# Global pipeline — loaded once at startup
device = 0 if torch.cuda.is_available() else -1  # GPU if available

# DeBERTa-v3-large-mnli
zs_classifier = pipeline(
    "zero-shot-classification",
    model="MoritzLaurer/deberta-v3-large-zeroshot-v2.0",
    device=device,
    torch_dtype=torch.float16 if device == 0 else None,
)

# Zero-shot template
template = "This text expresses a {} political ideology."

labels = [
    "left-wing or progressive",
    "centrist or moderate",
    "right-wing or conservative",
]

short = {
    "left-wing or progressive": "Left",
    "centrist or moderate": "Center",
    "right-wing or conservative": "Right",
}

# Simple in-memory cache (replace with Redis in production)
cache: Dict[str, dict] = {}


def _cache_key(text: str) -> str:
    return hashlib.sha256(text.strip().lower().encode()).hexdigest()


def analyse_bias(text: str, max_chars: int = 8000) -> dict:
    """
    Political bias detection function.
    """
    # 1. Cache hit - instant result
    key = _cache_key(text)
    if key in cache:
        return cache[key]

    # 2. Truncation (keep beginning + end)
    if len(text) > max_chars:
        half = max_chars // 2
        text = text[:half] + "\n...\n" + text[-half:]

    result = zs_classifier(
        text,
        candidate_labels=labels,
        hypothesis_template=template,
        multi_label=False,  # single-label is enough and faster
    )

    scores = {
        short[label]: score for label, score in zip(result["labels"], result["scores"])
    }
    top = max(scores, key=scores.get)

    output = {
        "input": text[:500] + "..." if len(text) > 500 else text,
        "predicted_bias": top,
        "confidence": scores[top],
        "scores": scores,
    }

    # Cache forever (or add TTL if you prefer)
    cache[key] = output
    return output
