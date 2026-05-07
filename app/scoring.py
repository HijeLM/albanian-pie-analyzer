import random
from typing import List
from app.models import Entry


def compute_authenticity_score(entries: List[Entry]) -> dict:
    """
    score = (agreement_ratio * 0.4 + avg_source_weight * 0.4 + avg_confidence * 0.2) * 100
    """
    if not entries:
        raw_score = random.uniform(10, 30)
        return {
            "score": round(raw_score, 1),
            "label": _score_label(raw_score),
            "source_count": 0,
        }

    # Agreement ratio: proportion of entries sharing the same root
    roots = [e.root for e in entries if e.root]
    if roots:
        most_common_root = max(set(roots), key=roots.count)
        agreement_ratio = roots.count(most_common_root) / len(roots)
    else:
        agreement_ratio = 0.0

    # Average source reliability weight
    weights = [e.source.reliability_weight for e in entries if e.source]
    avg_source_weight = sum(weights) / len(weights) if weights else 0.5

    # Confidence boost from entry-level confidence scores
    confidences = [e.confidence for e in entries if e.confidence is not None]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

    # Final score: weighted formula
    raw_score = (agreement_ratio * 0.4 + avg_source_weight * 0.4 + avg_confidence * 0.2) * 100

    return {
        "score": round(min(raw_score, 100), 1),
        "label": _score_label(raw_score),
        "source_count": len(entries),
        "agreement_ratio": round(agreement_ratio, 2),
    }


def _score_label(score: float) -> str:
    if score >= 90:
        return "Highly reliable"
    elif score >= 70:
        return "Likely"
    elif score >= 40:
        return "Uncertain"
    else:
        return "Probably incorrect"
