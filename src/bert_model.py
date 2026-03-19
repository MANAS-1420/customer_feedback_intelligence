from transformers import pipeline

_sentiment_model = None

def get_sentiment_model():
    global _sentiment_model
    if _sentiment_model is None:
        _sentiment_model = pipeline(
            "sentiment-analysis",
            model="nlptown/bert-base-multilingual-uncased-sentiment"
        )
    return _sentiment_model

def bert_sentiment(text: str):
    try:
        model = get_sentiment_model()
        result = model(text[:512])[0]
        label = result["label"]
        score = float(result["score"])

        if "1" in label or "2" in label:
            return 0, score
        elif "3" in label:
            return 1, score
        else:
            return 2, score
    except Exception:
        return 1, 0.50
