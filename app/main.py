from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.pipeline import analyze_review


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReviewRequest(BaseModel):
    product: str
    review: str
    domain: str = "auto"


@app.get("/")
def home():
    return {
        "message": "Aspect-Based E-Commerce Product Feedback Summarizer API is running!"
    }


@app.post("/predict")
def predict(request: ReviewRequest):

    result = analyze_review(
        request.review,
        request.domain
    )

    return {
        "product": request.product,
        "aspects": result["aspects"],
        "summary": result["summary"]
    }