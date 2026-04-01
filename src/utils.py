# src/utils.py
import re
import unicodedata

URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
NOISE_PATTERN = re.compile(r"[^\w\s\u0900-\u097F.,!?@+-]")
SPACE_PATTERN = re.compile(r"\s+")

CLAUSE_SPLITTER = re.compile(r'[.!?;]|\b(?:but|however|although|though|lekin|par|magar|yet|still|phir bhi|warna|jabki)\b', re.IGNORECASE)

def normalize(text: str) -> str:
    if not isinstance(text, str): return ""
    text = unicodedata.normalize('NFKC', text).lower()
    text = URL_PATTERN.sub(" ", text)
    text = NOISE_PATTERN.sub(" ", text)
    return SPACE_PATTERN.sub(" ", text).strip()

def any_hit(text: str, keywords: list) -> bool:
    text_padded = f" {text.lower()} "
    for kw in keywords:
        kw_lower = kw.lower()
        if len(kw_lower.split()) > 1:
            if kw_lower in text.lower(): return True
        else:
            if f" {kw_lower} " in text_padded: return True
    return False

def matched_keywords(text: str, keywords: list) -> list:
    text_padded = f" {text.lower()} "
    matches = []
    for kw in keywords:
        kw_lower = kw.lower()
        if len(kw_lower.split()) > 1:
            if kw_lower in text.lower(): matches.append(kw)
        else:
            if f" {kw_lower} " in text_padded: matches.append(kw)
    return list(set(matches))

def split_into_clauses(text: str) -> list:
    if not isinstance(text, str) or not text.strip(): return []
    raw_clauses = CLAUSE_SPLITTER.split(text)
    clauses = []
    ignore_words = ['but', 'however', 'although', 'though', 'lekin', 'par', 'magar', 'yet', 'still', 'phir bhi', 'warna', 'jabki']
    for c in raw_clauses:
        if c and len(c.strip()) > 3 and c.lower().strip() not in ignore_words:
            clauses.append(c.strip())
    return clauses if clauses else [text]
