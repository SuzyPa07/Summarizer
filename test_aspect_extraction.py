from app.aspect_extraction import extract_aspects

review = """
The battery life is great, the screen is bright,
but the price is expensive and the packaging is poor.
"""

print(extract_aspects(review))