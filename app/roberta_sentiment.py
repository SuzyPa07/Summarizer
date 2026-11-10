from transformers import pipeline

# Load the pretrained RoBERTa sentiment model
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model=MODEL_NAME,
    tokenizer=MODEL_NAME
)


def analyze_with_roberta(text):
    if not text or not text.strip():
        return "Neutral"

    result = sentiment_pipeline(
        text[:512],
        truncation=True
    )[0]

    label = result["label"].lower()

    if "positive" in label:
        return "Positive"
    elif "negative" in label:
        return "Negative"
    else:
        return "Neutral"