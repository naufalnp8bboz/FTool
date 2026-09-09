import re
import math
from collections import Counter
from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class NLPEngine:
    # Common positive and negative words for fast local sentiment analysis without heavy models
    POSITIVE_WORDS = {
        "good", "great", "excellent", "amazing", "wonderful", "fantastic", "positive", "love", "awesome",
        "brilliant", "outstanding", "superb", "fast", "reliable", "easy", "clean", "futuristic",
        "powerful", "best", "perfect", "helpful", "smart", "innovative", "effective", "safe", "miracle"
    }
    NEGATIVE_WORDS = {
        "bad", "terrible", "awful", "horrible", "poor", "slow", "broken", "hate", "ugly", "useless",
        "error", "bug", "difficult", "hard", "complicated", "fail", "failed", "crash", "flaw",
        "confusing", "overcomplicated", "worse", "worst", "danger", "risky"
    }

    @staticmethod
    def analyze_text(text: str) -> Dict[str, Any]:
        if not text.strip():
            return {
                "word_count": 0,
                "char_count": 0,
                "sentence_count": 0,
                "reading_ease": 100.0,
                "sentiment": "Neutral",
                "sentiment_score": 0.0,
                "top_keywords": []
            }

        # Tokenization
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        word_count = len(words)
        char_count = len(text)
        sentence_count = max(1, len(sentences))

        # Syllable approximation
        def count_syllables(w: str) -> int:
            w = w.lower()
            count = len(re.findall(r'[aeiouy]+', w))
            if w.endswith("e") and not w.endswith("le") and count > 1:
                count -= 1
            return max(1, count)

        syllable_count = sum(count_syllables(w) for w in words) if words else 1

        # Flesch Reading Ease
        # 206.835 - 1.015 * (total words / total sentences) - 84.6 * (total syllables / total words)
        words_per_sent = word_count / sentence_count if sentence_count > 0 else 1
        syllables_per_word = syllable_count / word_count if word_count > 0 else 1
        fre = 206.835 - (1.015 * words_per_sent) - (84.6 * syllables_per_word)
        fre = max(0.0, min(100.0, round(fre, 1)))

        # Sentiment
        pos_hits = sum(1 for w in words if w in NLPEngine.POSITIVE_WORDS)
        neg_hits = sum(1 for w in words if w in NLPEngine.NEGATIVE_WORDS)
        total_hits = pos_hits + neg_hits
        if total_hits > 0:
            score = (pos_hits - neg_hits) / total_hits
        else:
            score = 0.0

        if score > 0.15:
            sentiment = "Positive"
        elif score < -0.15:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        # Top keywords (excluding common stopwords)
        stopwords = {
            "the", "and", "is", "in", "to", "of", "it", "that", "you", "he", "was", "for", "on", "are",
            "as", "with", "his", "they", "at", "be", "this", "have", "from", "or", "one", "had", "by",
            "word", "but", "not", "what", "all", "were", "we", "when", "your", "can", "said", "there",
            "use", "an", "each", "which", "she", "do", "how", "their", "if", "will", "up", "other", "about"
        }
        filtered_words = [w for w in words if w not in stopwords]
        counter = Counter(filtered_words)
        top_keywords = [{"word": k, "count": v} for k, v in counter.most_common(8)]

        return {
            "word_count": word_count,
            "char_count": char_count,
            "sentence_count": sentence_count,
            "reading_ease": fre,
            "sentiment": sentiment,
            "sentiment_score": round(score, 2),
            "top_keywords": top_keywords
        }

    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        if not text1.strip() or not text2.strip():
            return 0.0
        vectorizer = TfidfVectorizer()
        try:
            tfidf = vectorizer.fit_transform([text1, text2])
            sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            return round(float(sim) * 100.0, 2)
        except Exception:
            return 0.0
