import re


# Positive words
POSITIVE_WORDS = {
    "good", "great", "love", "amazing", "excellent",
    "nice", "perfect", "smooth", "beautiful", "fast",
    "bright", "easy", "effective", "happy", "comfortable",
    "durable", "affordable", "reliable", "clear", "quick",
    "best", "wonderful", "fantastic", "impressive",
    "useful", "strong", "lightweight", "convenient"
}


# Negative words
NEGATIVE_WORDS = {
    "bad", "hate", "poor", "terrible", "awful",
    "slow", "expensive", "disappointing", "problem",
    "dry", "broken", "difficult", "worst", "weak",
    "uncomfortable", "damaged", "late", "noisy",
    "defective", "unreliable", "heavy", "cheap"
}


# Keywords associated with each e-commerce aspect
ASPECT_TERMS = {
    "battery": ["battery", "charging"],
    "screen": ["screen", "display"],
    "performance": ["performance", "speed"],
    "camera": ["camera"],
    "sound": ["sound", "audio", "speaker"],
    "storage": ["storage", "memory"],
    "price": ["price", "cost", "expensive", "affordable"],
    "quality": ["quality", "build quality"],
    "design": ["design", "appearance"],
    "durability": ["durability", "durable"],
    "packaging": ["packaging", "package", "box"],
    "delivery": ["delivery", "shipping"],
    "size": ["size", "dimensions"],
    "comfort": ["comfort", "comfortable"],
    "ease of use": ["easy to use", "user friendly"],
    "customer service": ["customer service", "support"],
    "connectivity": ["wifi", "bluetooth", "connection"],
    "value": ["value for money", "worth the price"]
}


def get_sentiment(text):

    words = re.findall(r"\b[\w']+\b", text.lower())

    positive_count = 0
    negative_count = 0

    negation_words = {"not", "never", "no", "hardly"}

    for index, word in enumerate(words):

        # Check for positive words
        if word in POSITIVE_WORDS:

            if any(
                previous in negation_words
                for previous in words[max(0, index - 3):index]
            ):
                negative_count += 1
            else:
                positive_count += 1

        # Check for negative words
        elif word in NEGATIVE_WORDS:

            if any(
                previous in negation_words
                for previous in words[max(0, index - 3):index]
            ):
                positive_count += 1
            else:
                negative_count += 1

    if positive_count > negative_count:
        return "Positive"

    elif negative_count > positive_count:
        return "Negative"

    return "Neutral"


def analyze_sentiment(review, aspect=None):

    review = str(review).lower()

    # Split review into separate opinion sections
    sentences = re.split(
        r"[.!?]+|\b(?:but|however|although|though)\b",
        review
    )

    relevant_sentences = []

    # Find sentences related to the selected aspect
    if aspect and aspect in ASPECT_TERMS:

        keywords = ASPECT_TERMS[aspect]

        for sentence in sentences:

            for keyword in keywords:

                pattern = r"\b" + re.escape(keyword) + r"\b"

                if re.search(pattern, sentence):

                    relevant_sentences.append(sentence)
                    break

    # Use only relevant sentences when available
    if relevant_sentences:

        relevant_text = " ".join(relevant_sentences)

    else:

        relevant_text = review

    return get_sentiment(relevant_text)