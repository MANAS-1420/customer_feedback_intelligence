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

def flexible_match(kw: str, text: str) -> bool:
    """Smart matcher: Catches exact phrases OR stems single words (damage -> damaged)"""
    kw_lower = kw.lower()
    if len(kw_lower.split()) > 1:
        return kw_lower in text.lower()
    else:
        # Matches the core word + up to 3 trailing characters (ed, ing, s)
        return bool(re.search(r'\b' + re.escape(kw_lower) + r'[a-z]{0,3}\b', text.lower()))

def any_hit(text: str, keywords: list) -> bool:
    for kw in keywords:
        if flexible_match(kw, text): return True
    return False

def matched_keywords(text: str, keywords: list) -> list:
    matches = []
    for kw in keywords:
        if flexible_match(kw, text): matches.append(kw)
    return list(set(matches))

def split_into_clauses(text: str) -> list:
    if not isinstance(text, str) or not text.strip(): return []
    raw_clauses = CLAUSE_SPLITTER.split(text)
    clauses = []
    ignore_words = ['but', 'however', 'although', 'though', 'lekin', 'par', 'magar', 'yet', 'still', 'phir', 'bhi', 'warna', 'jabki']
    for c in raw_clauses:
        if c and len(c.strip()) > 3 and c.lower().strip() not in ignore_words:
            clauses.append(c.strip())
    return clauses if clauses else [text]
