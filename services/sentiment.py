# Placeholder for reviews sentiment analysis using NLTK or other libraries.
from nltk.sentiment import SentimentIntensityAnalyzer

_analyzer = None

def _get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentIntensityAnalyzer()
    return _analyzer

def sentiment_score(text: str) -> float:
    analyzer = _get_analyzer()
    return analyzer.polarity_scores(text)["compound"]
