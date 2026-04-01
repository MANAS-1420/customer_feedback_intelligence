# src/utils.py
import re
import unicodedata

URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
NOISE_PATTERN = re.compile(r"[^\w\s\u0900-\u097F.,!?@+-]")
SPACE_PATTERN = re.compile(r"\s+")

def normalize(text: str) -> str:
    if not isinstance(text, str): return ""
    text = unicodedata.normalize('NFKC', text).lower()
    text = URL_PATTERN.sub(" ", text)
    text = NOISE_PATTERN.sub(" ", text)
    return SPACE_PATTERN.sub(" ", text).strip()

def any_hit(text: str, keywords: list) -> bool:
    for kw in keywords:
        if re.search(r'\b' + re.escape(kw) + r'\b', text): return True
    return False

def matched_keywords(text: str, keywords: list) -> list:
    matches = []
    for kw in keywords:
        if re.search(r'\b' + re.escape(kw) + r'\b', text): matches.append(kw)
    return list(set(matches))
