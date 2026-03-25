import re
import pandas as pd
import unicodedata
from collections import Counter

URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
SPECIAL_PATTERN = re.compile(r"[^\w\s\u0900-\u097F]")
SPACE_PATTERN = re.compile(r"\s+")

def normalize(text: str) -> str:
    if pd.isna(text) or str(text).strip() == "": return ""
    t = unicodedata.normalize('NFKC', str(text)).lower()
    t = URL_PATTERN.sub(" ", t)
    t = SPECIAL_PATTERN.sub(" ", t)
    return SPACE_PATTERN.sub(" ", t).strip()

def any_hit(text: str, keywords: list) -> bool:
    return any(kw in text for kw in keywords if kw)

def matched_keywords(text: str, keywords: list) -> list:
    return list({kw for kw in keywords if kw and kw in text})

def best_match_id(text: str, keywords_by_label: dict, labels: list, default_id: int) -> int:
    scores = Counter()
    for label in labels:
        for kw in keywords_by_label.get(label, []):
            if kw in text: scores[label] += 1
    if not scores: return int(default_id)
    return labels.index(scores.most_common(1)[0][0])
