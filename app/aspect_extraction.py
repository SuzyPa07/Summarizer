import re

ASPECT_KEYWORDS = {
    "battery": ["battery", "battery life", "charging"],
    "screen": ["screen", "display"],
    "performance": ["performance", "speed", "slow", "fast"],
    "camera": ["camera", "photo quality"],
    "sound": ["sound", "audio", "speaker"],
    "storage": ["storage", "memory"],
    "price": ["price", "cost", "expensive", "cheap"],
    "quality": ["quality", "build quality", "poor quality"],
    "design": ["design", "appearance", "look"],
    "durability": ["durability", "durable", "broken", "damage"],
    "packaging": ["packaging", "package", "box"],
    "delivery": ["delivery", "shipping", "arrived"],
    "size": ["size", "dimensions"],
    "comfort": ["comfort", "comfortable"],
    "ease of use": ["easy to use", "user friendly", "difficult to use"],
    "customer service": ["customer service", "support"],
    "connectivity": ["wifi", "bluetooth", "connection"],
    "value": ["value for money", "worth the price"]
}


def extract_aspects(review, domain="auto"):
    review = str(review).lower()

    found_aspects = []

    # Specific aspects that qualify as quality must take priority.
    specific_quality_contexts = [
        "camera quality",
        "screen quality",
        "display quality",
        "sound quality",
        "audio quality",
        "photo quality",
        "video quality"
    ]

    for aspect, keywords in ASPECT_KEYWORDS.items():
        for keyword in keywords:
            pattern = r"\b" + re.escape(keyword) + r"\b"

            if re.search(pattern, review):
                # Do not separately classify generic quality
                # when it describes another specific aspect.
                if aspect == "quality":
                    if any(context in review for context in specific_quality_contexts):
                        continue

                found_aspects.append(aspect)
                break

    return found_aspects