MODEL_VERSION = "rule-based-v0"


def predict_quality(sleep_duration_hours: float, heart_rate: float, is_deep_sleep: bool) -> dict:
    """
    Placeholder scoring logic.
    Later replaced by a trained scikit-learn model loaded from disk —
    the signature and return shape stay identical.
    """
    score = 50.0

    if 7 <= sleep_duration_hours <= 9:
        score += 25
    elif sleep_duration_hours < 6:
        score -= 20

    if heart_rate < 60:
        score += 15
    elif heart_rate > 80:
        score -= 15

    if is_deep_sleep:
        score += 10

    score = max(0.0, min(100.0, score))

    if score >= 75:
        label = "good"
    elif score >= 50:
        label = "fair"
    else:
        label = "poor"

    return {"quality_score": round(score, 1), "quality_label": label}