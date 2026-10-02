POSITIVE_WORDS = [
    "good",
    "great",
    "love",
    "amazing",
    "excellent",
    "nice",
    "perfect",
    "smooth",
    "beautiful",
    "fast",
    "bright",
    "easy",
    "effective",
    "happy"
]

NEGATIVE_WORDS = [
    "bad",
    "hate",
    "poor",
    "terrible",
    "awful",
    "slow",
    "expensive",
    "disappointing",
    "problem",
    "dry",
    "broken",
    "difficult"
]


def analyze_sentiment(review):
    review = str(review).lower()

    positive_count = 0
    negative_count = 0

    for word in POSITIVE_WORDS:
        if word in review:
            positive_count += 1

    for word in NEGATIVE_WORDS:
        if word in review:
            negative_count += 1

    if positive_count > negative_count:
        return "Positive"

    elif negative_count > positive_count:
        return "Negative"

    else:
        return "Neutral"