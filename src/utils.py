import re
import pandas as pd
from collections import Counter

URL_PATTERN = re.compile(r"http\S+|www\S+")
NUM_PATTERN = re.compile(r"\d+")
SPECIAL_PATTERN = re.compile(r"[^\w\s\u0900-\u097F]")
SPACE_PATTERN = re.compile(r"\s+")

def normalize(text: str) -> str:
    if pd.isna(text):
        return ""
    t = str(text).lower()
    t = URL_PATTERN.sub(" ", t)
    t = NUM_PATTERN.sub(" ", t)
    t = SPECIAL_PATTERN.sub(" ", t)
    t = SPACE_PATTERN.sub(" ", t).strip()
    return t

def any_hit(text: str, keywords: list) -> bool:
    for kw in keywords:
        if kw and kw in text:
            return True
    return False

def matched_keywords(text: str, keywords: list) -> list:
    hits = []
    for kw in keywords:
        if kw and kw in text:
            hits.append(kw)
    return list(dict.fromkeys(hits))

def best_match_id(text: str, keywords_by_label: dict, labels: list, default_id: int) -> int:
    scores = Counter()
    for label in labels:
        for kw in keywords_by_label.get(label, []):
            if kw and kw in text:
                scores[label] += 1
    if not scores:
        return int(default_id)
    best_label = scores.most_common(1)[0][0]
    return int(labels.index(best_label))

def parse_global_sentiment(x) -> int:
    if pd.isna(x):
        return 1
    s = str(x).strip().lower()
    if s in ["0", "1", "2"]:
        return int(s)
    if s in ["negative", "neg", "bad"]:
        return 0
    if s in ["neutral", "neu", "avg", "average", "mid"]:
        return 1
    if s in ["positive", "pos", "good"]:
        return 2
    return 1
