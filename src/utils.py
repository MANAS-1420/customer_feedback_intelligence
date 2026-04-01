# src/utils.py
import re
import unicodedata

URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
NOISE_PATTERN = re.compile(r"[^\w\s\u0900-\u097F.,!?@+-]")
SPACE_PATTERN = re.compile(r"\s+")

# ABSA Splitter: Splits by punctuation OR contrastive words (English & Hinglish)
CLAUSE_SPLITTER = re.compile(r'[.!?;]|\b(?:but|however|although|though|lekin|par|magar|yet|still)\b', re.IGNORECASE)

def normalize(text: str) -> str:
    """Normalizes text by lowercasing, removing URLs, and preserving Hindi/English characters."""
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

def split_into_clauses(text: str) -> list:
    """Splits a full review into individual logical clauses for Aspect-Based Sentiment Analysis."""
    if not isinstance(text, str) or not text.strip(): return []
    
    raw_clauses = CLAUSE_SPLITTER.split(text)
    clauses = []
    
    # Filter out empty strings and the conjunctions themselves
    ignore_words = ['but', 'however', 'although', 'though', 'lekin', 'par', 'magar', 'yet', 'still']
    for c in raw_clauses:
        if c and len(c.strip()) > 3 and c.lower().strip() not in ignore_words:
            clauses.append(c.strip())
            
    return clauses if clauses else [text]
