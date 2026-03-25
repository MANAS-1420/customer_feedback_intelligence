import re
import pandas as pd
from collections import Counter
import unicodedata

# Optimized Regex Patterns
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
NUM_PATTERN = re.compile(r"\d+")
# Updated to better handle Devanagari (Hindi) and standard symbols
SPECIAL_PATTERN = re.compile(r"[^\w\s\u0900-\u097F]")
SPACE_PATTERN = re.compile(r"\s+")

def normalize(text: str) -> str:
    """Enhanced cleaning for English, Hindi, and Hinglish."""
    if pd.isna(text) or str(text).strip() == "":
        return ""
    
    # Normalize unicode (handles different ways of writing the same Hindi character)
    t = unicodedata.normalize('NFKC', str(text))
    t = t.lower()
    
    # Remove URLs and Numbers
    t = URL_PATTERN.sub(" ", t)
    t = NUM_PATTERN.sub(" ", t)
    
    # Remove Special Characters but keep Hindi script
    t = SPECIAL_PATTERN.sub(" ", t)
    
    # Collapse multiple spaces
    t = SPACE_PATTERN.sub(" ", t).strip()
    return t

def any_hit(text: str, keywords: list) -> bool:
    """Fast check for keyword existence using set intersection or simple 'in'."""
    if not text:
        return False
    return any(kw in text for kw in keywords if kw)

def matched_keywords(text: str, keywords: list) -> list:
    """Returns a unique list of found keywords."""
    if not text:
        return []
    return list({kw for kw in keywords if kw and kw in text})

def best_match_id(text: str, keywords_by_label: dict, labels: list, default_id: int) -> int:
    """Scores labels based on keyword frequency."""
    if not text:
        return int(default_id)
        
    scores = Counter()
    for label in labels:
        kws = keywords_by_label.get(label, [])
        for kw in kws:
            if kw and kw in text:
                scores[label] += 1
                
    if not scores:
        return int(default_id)
    
    # Return the label with the highest count
    best_label = scores.most_common(1)[0][0]
    return int(labels.index(best_label))

def parse_global_sentiment(x) -> int:
    """Standardizes sentiment inputs to 0, 1, 2."""
    if pd.isna(x):
        return 1
    s = str(x).strip().lower()
    mapping = {
        "0": 0, "negative": 0, "neg": 0, "bad": 0, "worst": 0,
        "1": 1, "neutral": 1, "neu": 1, "avg": 1, "average": 1, "mid": 1,
        "2": 2, "positive": 2, "pos": 2, "good": 2, "best": 2
    }
    return mapping.get(s, 1)
