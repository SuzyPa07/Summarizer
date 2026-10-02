# Aspect Extraction for different e-commerce domains

ASPECTS = {
    "electronics": [
        "battery",
        "screen",
        "display",
        "performance",
        "camera",
        "price",
        "quality",
        "design",
        "sound",
        "storage"
    ],

    "skincare": [
        "texture",
        "scent",
        "formula",
        "hydration",
        "packaging",
        "skin",
        "price",
        "quality",
        "color",
        "application"
    ]
}


def extract_aspects(review, domain="electronics"):
    review = str(review).lower()

    # Use electronics if an unknown domain is provided
    aspect_list = ASPECTS.get(domain, ASPECTS["electronics"])

    found_aspects = []

    for aspect in aspect_list:
        if aspect in review:
            found_aspects.append(aspect)

    return found_aspects