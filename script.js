const API_URL = "http://127.0.0.1:8000";

let selectedProduct = null;
let searchTimer = null;
let searchRequestNumber = 0;
let activeSuggestionIndex = -1;

let currentReviews = [];
let displayedReviewCount = 0;
let currentRatingFilter = "all";

let analysisRunNumber = 0;

const REVIEWS_PER_PAGE = 20;


// ==========================================
// 1. PRODUCT SEARCH
// ==========================================

let searchAbortController = null;

async function searchProducts() {
    const input = document.getElementById("product");
    const suggestions = document.getElementById("suggestions");

    if (!input || !suggestions) return;

    const query = input.value.trim();

    if (searchAbortController) {
        searchAbortController.abort();
    }

    selectedProduct = null;
    activeSuggestionIndex = -1;
    currentReviews = [];
    displayedReviewCount = 0;
    currentRatingFilter = "all";

    document.getElementById("selectedProduct").textContent =
        "Select a product to continue.";

    document.getElementById("individualSection").style.display = "none";
    document.getElementById("overallSection").style.display = "none";
    document.getElementById("customerReviewsSection").style.display = "none";

    document.getElementById("output").innerHTML = "";
    document.getElementById("overallResults").innerHTML = "";
    document.getElementById("overallSummary").innerHTML = "";
    document.getElementById("customerReviewsList").innerHTML = "";

    clearTimeout(searchTimer);

    if (query.length < 2) {
        suggestions.innerHTML = "";
        return;
    }

    suggestions.innerHTML =
        '<div class="suggestion-message">Searching products...</div>';

    const requestNumber = ++searchRequestNumber;

    searchTimer = setTimeout(async () => {
        searchAbortController = new AbortController();

        try {
            const response = await fetch(
                `${API_URL}/products/search?q=${encodeURIComponent(query)}`,
                { signal: searchAbortController.signal }
            );

            if (!response.ok) {
                throw new Error("Product search failed.");
            }

            const data = await response.json();

            if (requestNumber !== searchRequestNumber) return;
            if (input.value.trim() !== query) return;

            showSuggestions(data.products || []);

        } catch (error) {
            if (error.name === "AbortError") return;

            if (requestNumber === searchRequestNumber) {
                suggestions.innerHTML =
                    '<div class="suggestion-message error-message">' +
                    'Unable to search products. Please check the backend server.' +
                    '</div>';
            }

            console.error("Product search error:", error);
        }
    }, 250);
}


// ==========================================
// 2. DISPLAY PRODUCT SUGGESTIONS
// ==========================================

function showSuggestions(products) {
    const suggestions = document.getElementById("suggestions");

    suggestions.innerHTML = "";
    activeSuggestionIndex = -1;

    if (!products.length) {
        suggestions.innerHTML =
            '<div class="suggestion-message">No matching products found.</div>';
        return;
    }

    products.forEach((product, index) => {
        const option = document.createElement("button");

        option.type = "button";
        option.className = "suggestion-item";
        option.setAttribute("role", "option");
        option.setAttribute("aria-selected", "false");
        option.dataset.index = index;

        const name = document.createElement("span");
        name.className = "suggestion-name";
        name.textContent = product.product_name || "Unnamed product";

        const details = document.createElement("small");
        details.className = "suggestion-details";

        const brand = product.brand ? `${product.brand} · ` : "";

        details.textContent =
            `${brand}${product.review_count ?? 0} customer reviews`;

        option.appendChild(name);
        option.appendChild(details);

        option.addEventListener("click", () => {
            selectProduct(product);
        });

        suggestions.appendChild(option);
    });
}


// ==========================================
// 3. KEYBOARD NAVIGATION
// ==========================================

function handleSearchKeyboard(event) {
    const suggestions = document.getElementById("suggestions");

    if (!suggestions) return;

    const options = Array.from(
        suggestions.querySelectorAll(".suggestion-item")
    );

    if (!options.length) {
        if (event.key === "Escape") {
            suggestions.innerHTML = "";
        }
        return;
    }

    if (event.key === "ArrowDown") {
        event.preventDefault();

        activeSuggestionIndex++;

        if (activeSuggestionIndex >= options.length) {
            activeSuggestionIndex = 0;
        }

        updateActiveSuggestion(options);
    }

    else if (event.key === "ArrowUp") {
        event.preventDefault();

        activeSuggestionIndex--;

        if (activeSuggestionIndex < 0) {
            activeSuggestionIndex = options.length - 1;
        }

        updateActiveSuggestion(options);
    }

    else if (event.key === "Enter") {
        if (activeSuggestionIndex >= 0) {
            event.preventDefault();
            options[activeSuggestionIndex].click();
        }
    }

    else if (event.key === "Escape") {
        suggestions.innerHTML = "";
        activeSuggestionIndex = -1;
    }
}


function updateActiveSuggestion(options) {
    options.forEach((option, index) => {
        const isActive = index === activeSuggestionIndex;

        option.classList.toggle("active", isActive);

        option.setAttribute(
            "aria-selected",
            isActive ? "true" : "false"
        );
    });

    if (activeSuggestionIndex >= 0) {
        options[activeSuggestionIndex].scrollIntoView({
            block: "nearest"
        });
    }
}


// ==========================================
// 4. SELECT A PRODUCT
// ==========================================

function selectProduct(product) {
    selectedProduct = product;

    currentReviews = [];
    displayedReviewCount = 0;
    currentRatingFilter = "all";

    const input = document.getElementById("product");

    input.value = product.product_name;

    document.getElementById("suggestions").innerHTML = "";
    activeSuggestionIndex = -1;

    document.getElementById("selectedProduct").textContent =
        `Selected: ${product.product_name} | ${product.review_count ?? 0} customer reviews`;

    document.getElementById("individualSection").style.display = "none";
    document.getElementById("output").innerHTML = "";

    document.getElementById("overallSection").style.display = "none";
    document.getElementById("overallResults").innerHTML = "";
    document.getElementById("overallSummary").innerHTML = "";

    document.getElementById("customerReviewsSection").style.display = "none";

    const reviewList = document.getElementById("customerReviewsList");

    reviewList.innerHTML = "";
    reviewList.style.display = "none";

    document.getElementById("reviewsToggleButton").textContent =
        "Read Customer Reviews";

    document.getElementById("customerReviewsCount").textContent = "";

    document.getElementById("review").value = "";

    analysisRunNumber++;
}


// ==========================================
// 5. MAIN ANALYSIS BUTTON
// ==========================================

async function analyzeProductAndReview() {
    if (!selectedProduct) {
        alert("Please search for and select a product first.");
        return;
    }

    const product = selectedProduct;
    const runNumber = ++analysisRunNumber;

    const review = document.getElementById("review").value.trim();

    const loading = document.getElementById("loading");
    const analyzeButton = document.getElementById("analyzeButton");

    loading.style.display = "block";
    analyzeButton.disabled = true;

    document.getElementById("individualSection").style.display = "none";
    document.getElementById("overallSection").style.display = "none";
    document.getElementById("customerReviewsSection").style.display = "none";

    try {
        const tasks = [
            loadOverallAnalysis(product, runNumber)
        ];

        if (review) {
            tasks.push(
                analyzeIndividualReview(review, product, runNumber)
            );
        }

        await Promise.all(tasks);

        if (
            runNumber !== analysisRunNumber ||
            !selectedProduct ||
            selectedProduct.product_id !== product.product_id
        ) {
            return;
        }

        document.getElementById("customerReviewsSection").style.display =
            "block";

        document.getElementById("customerReviewsCount").textContent =
            "Explore reviews from other customers who purchased this product.";

    } catch (error) {
        console.error("Analysis error:", error);

        if (runNumber === analysisRunNumber) {
            alert(error.message || "Something went wrong during analysis.");
        }

    } finally {
        if (runNumber === analysisRunNumber) {
            loading.style.display = "none";
            analyzeButton.disabled = false;
        }
    }
}


// ==========================================
// 6. ANALYZE INDIVIDUAL REVIEW
// ==========================================

async function analyzeIndividualReview(review, product, runNumber) {
    const response = await fetch(`${API_URL}/predict`, {
        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            product: product.product_name,
            review: review,
            domain: "electronics"
        })
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || "Individual review analysis failed."
        );
    }

    if (runNumber !== analysisRunNumber) return;

    displayIndividualResult(data);
}


// ==========================================
// 7. DISPLAY INDIVIDUAL REVIEW RESULTS
// ==========================================

function displayIndividualResult(data) {
    const section = document.getElementById("individualSection");
    const output = document.getElementById("output");

    output.innerHTML = "";

    const summaryHeading = document.createElement("h3");
    summaryHeading.textContent = "Review Summary";

    const summary = document.createElement("p");
    summary.textContent = data.summary;

    output.appendChild(summaryHeading);
    output.appendChild(summary);

    const aspectHeading = document.createElement("h3");
    aspectHeading.textContent = "Aspect-wise Sentiment";

    output.appendChild(aspectHeading);

    Object.entries(data.aspects || {}).forEach(([aspect, sentiment]) => {
        const card = document.createElement("div");
        card.className = "aspect-card";

        const name = document.createElement("strong");
        name.textContent = aspect;

        const label = document.createElement("span");
        label.className =
            "sentiment-label " + String(sentiment).toLowerCase();

        label.textContent = sentiment;

        card.appendChild(name);
        card.appendChild(label);

        output.appendChild(card);
    });

    section.style.display = "block";
}


// ==========================================
// 8. LOAD OVERALL PRODUCT ANALYSIS
// ==========================================

async function loadOverallAnalysis(product, runNumber) {
    const productId = product.product_id;

    const response = await fetch(
        `${API_URL}/products/${encodeURIComponent(productId)}/analysis`
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || "Overall product analysis failed."
        );
    }

    if (runNumber !== analysisRunNumber) return;

    document.getElementById("overallProductName").textContent =
        product.product_name;

    document.getElementById("reviewCount").textContent =
        `Total customer reviews: ${data.total_reviews} | Reviews analyzed: ${data.analyzed_reviews}`;

    displayOverallAnalysis(data.aspect_analysis || {});

    document.getElementById("overallSection").style.display = "block";
}


// ==========================================
// 9. DISPLAY OVERALL SENTIMENT ANALYSIS
// ==========================================

function displayOverallAnalysis(aspects) {
    const results = document.getElementById("overallResults");
    const summary = document.getElementById("overallSummary");

    results.innerHTML = "";
    summary.innerHTML = "";

    // Sort by mentions, positive mentions, then positive percentage.
    const aspectNames = Object.keys(aspects).sort((a, b) => {
        const aspectA = aspects[a];
        const aspectB = aspects[b];

        const mentionsA = Number(aspectA.total_mentions) || 0;
        const mentionsB = Number(aspectB.total_mentions) || 0;

        if (mentionsA !== mentionsB) {
            return mentionsB - mentionsA;
        }

        const positiveA =
            Number(aspectA.sentiment_counts?.Positive) || 0;

        const positiveB =
            Number(aspectB.sentiment_counts?.Positive) || 0;

        if (positiveA !== positiveB) {
            return positiveB - positiveA;
        }

        const percentageA =
            Number(aspectA.sentiment_percentages?.Positive) || 0;

        const percentageB =
            Number(aspectB.sentiment_percentages?.Positive) || 0;

        return percentageB - percentageA;
    });

    if (!aspectNames.length) {
        results.textContent =
            "No specific product aspects were identified.";
        return;
    }

    const positiveAspects = [];
    const negativeAspects = [];
    const mixedAspects = [];

    aspectNames.forEach(aspect => {
        const sentiment = aspects[aspect].overall_sentiment;

        if (sentiment === "Positive") {
            positiveAspects.push(aspect);
        } else if (sentiment === "Negative") {
            negativeAspects.push(aspect);
        } else {
            mixedAspects.push(aspect);
        }
    });

    const summaryParts = [];

    if (positiveAspects.length) {
        summaryParts.push(
            "Mostly positive feedback on " + positiveAspects.join(", ")
        );
    }

    if (negativeAspects.length) {
        summaryParts.push(
            "Mostly negative feedback on " + negativeAspects.join(", ")
        );
    }

    if (mixedAspects.length) {
        summaryParts.push(
            "Mixed feedback on " + mixedAspects.join(", ")
        );
    }

    const summaryHeading = document.createElement("h3");
    summaryHeading.textContent = "Overall Feedback Summary";

    const summaryText = document.createElement("p");
    summaryText.textContent = summaryParts.join(". ") + ".";

    summary.appendChild(summaryHeading);
    summary.appendChild(summaryText);

    aspectNames.forEach(aspect => {
        const item = aspects[aspect];

        const counts = item.sentiment_counts;
        const percentages = item.sentiment_percentages;

        const card = document.createElement("div");
        card.className = "aspect-card";

        const heading = document.createElement("h3");
        heading.textContent = aspect.toUpperCase();

        const sentiment = document.createElement("p");
        sentiment.textContent =
            "Overall sentiment: " + item.overall_sentiment;

        const mentions = document.createElement("p");
        mentions.textContent =
            "Total mentions: " + item.total_mentions;

        const countText = document.createElement("p");
        countText.textContent =
            `Positive: ${counts.Positive} | Negative: ${counts.Negative} | Neutral: ${counts.Neutral}`;

        const percentageText = document.createElement("p");
        percentageText.textContent =
            `Positive: ${percentages.Positive}% | Negative: ${percentages.Negative}% | Neutral: ${percentages.Neutral}%`;

        const bar = document.createElement("div");
        bar.className = "sentiment-bar";

        const positive = document.createElement("div");
        positive.className = "bar-positive";
        positive.style.width = percentages.Positive + "%";

        const negative = document.createElement("div");
        negative.className = "bar-negative";
        negative.style.width = percentages.Negative + "%";

        const neutral = document.createElement("div");
        neutral.className = "bar-neutral";
        neutral.style.width = percentages.Neutral + "%";

        bar.appendChild(positive);
        bar.appendChild(negative);
        bar.appendChild(neutral);

        card.appendChild(heading);
        card.appendChild(sentiment);
        card.appendChild(mentions);
        card.appendChild(countText);
        card.appendChild(percentageText);
        card.appendChild(bar);

        results.appendChild(card);
    });
}


// ==========================================
// 10. LOAD ACTUAL CUSTOMER REVIEWS
// ==========================================

async function loadCustomerReviews() {
    if (!selectedProduct) return;

    const product = selectedProduct;
    const loading = document.getElementById("reviewsLoading");
    const list = document.getElementById("customerReviewsList");

    loading.style.display = "block";

    try {
        const response = await fetch(
            `${API_URL}/products/${encodeURIComponent(product.product_id)}/reviews`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Unable to load customer reviews."
            );
        }

        if (
            !selectedProduct ||
            selectedProduct.product_id !== product.product_id
        ) {
            return;
        }

        currentReviews = Array.isArray(data)
            ? data
            : (data.reviews || []);

        // Highest ratings first; unrated reviews last.
        currentReviews.sort((a, b) => {
            const ratingA = Number(a.rating);
            const ratingB = Number(b.rating);

            const validA =
                a.rating !== null &&
                a.rating !== undefined &&
                a.rating !== "" &&
                Number.isFinite(ratingA);

            const validB =
                b.rating !== null &&
                b.rating !== undefined &&
                b.rating !== "" &&
                Number.isFinite(ratingB);

            if (!validA && !validB) return 0;
            if (!validA) return 1;
            if (!validB) return -1;

            return ratingB - ratingA;
        });

        displayedReviewCount = 0;
        currentRatingFilter = "all";

        renderCustomerReviews();

        document.getElementById("customerReviewsCount").textContent =
            `${currentReviews.length} customer reviews available`;

    } catch (error) {
        list.textContent = error.message;
        console.error("Customer reviews error:", error);

    } finally {
        loading.style.display = "none";
    }
}


// ==========================================
// 11. FILTER CUSTOMER REVIEWS
// ==========================================

function getFilteredReviews() {
    if (currentRatingFilter === "all") {
        return currentReviews;
    }

    return currentReviews.filter(item => {
        const rating = Number(item.rating);

        return (
            item.rating !== null &&
            item.rating !== undefined &&
            item.rating !== "" &&
            Number.isFinite(rating) &&
            rating === Number(currentRatingFilter)
        );
    });
}


// ==========================================
// 12. CREATE STAR RATING FILTERS
// ==========================================

function createReviewFilters() {
    const filterBar = document.createElement("div");
    filterBar.className = "review-filter-bar";

    const filters = [
        { label: "All", value: "all" },
        { label: "5 ★", value: "5" },
        { label: "4 ★", value: "4" },
        { label: "3 ★", value: "3" },
        { label: "2 ★", value: "2" },
        { label: "1 ★", value: "1" }
    ];

    filters.forEach(filter => {
        const button = document.createElement("button");

        button.type = "button";
        button.className = "review-filter-button";

        if (currentRatingFilter === filter.value) {
            button.classList.add("active");
        }

        button.textContent = filter.label;

        button.addEventListener("click", () => {
            currentRatingFilter = filter.value;
            displayedReviewCount = 0;

            renderCustomerReviews();
        });

        filterBar.appendChild(button);
    });

    return filterBar;
}


// ==========================================
// 13. DISPLAY CUSTOMER REVIEWS
// ==========================================

function renderCustomerReviews() {
    const list = document.getElementById("customerReviewsList");

    list.innerHTML = "";

    list.appendChild(createReviewFilters());

    const filteredReviews = getFilteredReviews();

    const filterHeading = document.createElement("p");
    filterHeading.className = "filtered-review-count";

    filterHeading.textContent =
        currentRatingFilter === "all"
            ? `Showing ${filteredReviews.length} customer reviews`
            : `Showing ${filteredReviews.length} ${currentRatingFilter}-star reviews`;

    list.appendChild(filterHeading);

    if (!filteredReviews.length) {
        const emptyMessage = document.createElement("p");

        emptyMessage.textContent =
            "No reviews are available for this star rating.";

        list.appendChild(emptyMessage);

        displayedReviewCount = 0;
        return;
    }

    const nextReviews = filteredReviews.slice(
        0,
        displayedReviewCount + REVIEWS_PER_PAGE
    );

    nextReviews.forEach(item => {
        const card = document.createElement("div");
        card.className = "customer-review-card";

        const ratingElement = document.createElement("p");
        ratingElement.className = "review-rating";

        const rating = item.rating;

        if (rating !== null && rating !== undefined && rating !== "") {
            const numericRating = Number(rating);

            ratingElement.textContent = Number.isFinite(numericRating)
                ? `★ ${numericRating}/5`
                : `Rating: ${rating}`;
        } else {
            ratingElement.textContent = "Rating not available";
        }

        const reviewText = document.createElement("p");
        reviewText.className = "customer-review-text";
        reviewText.textContent =
            item.review || "No review text available.";

        card.appendChild(ratingElement);
        card.appendChild(reviewText);

        // Measure after the browser applies the two-line clamp.
        requestAnimationFrame(() => {
            if (!card.isConnected) return;

            reviewText.classList.add("collapsed");

            const isLongReview =
                reviewText.scrollHeight > reviewText.clientHeight + 2;

            if (isLongReview) {
                const readMoreButton = document.createElement("button");

                readMoreButton.type = "button";
                readMoreButton.className = "review-expand-button";
                readMoreButton.textContent = "Read more";

                readMoreButton.addEventListener("click", () => {
                    const isExpanded =
                        reviewText.classList.toggle("expanded");

                    reviewText.classList.toggle(
                        "collapsed",
                        !isExpanded
                    );

                    readMoreButton.textContent =
                        isExpanded ? "Read less" : "Read more";
                });

                card.appendChild(readMoreButton);
            }
        });

        list.appendChild(card);
    });

    displayedReviewCount = nextReviews.length;

    if (displayedReviewCount < filteredReviews.length) {
        const moreButton = document.createElement("button");

        moreButton.id = "showMoreReviews";
        moreButton.className = "secondary-button";
        moreButton.textContent = "Show More Reviews";

        moreButton.addEventListener("click", () => {
            renderCustomerReviews();
        });

        list.appendChild(moreButton);
    }
}


// ==========================================
// 14. SHOW / HIDE CUSTOMER REVIEWS
// ==========================================

async function toggleCustomerReviews() {
    const list = document.getElementById("customerReviewsList");
    const button = document.getElementById("reviewsToggleButton");

    if (!selectedProduct) return;

    const isHidden = list.style.display === "none";

    if (isHidden) {
        list.style.display = "block";
        button.textContent = "Hide Customer Reviews";

        if (!currentReviews.length) {
            await loadCustomerReviews();
        }

    } else {
        list.style.display = "none";
        button.textContent = "Read Customer Reviews";
    }
}


// ==========================================
// 15. CLOSE SUGGESTIONS WHEN CLICKING OUTSIDE
// ==========================================

document.addEventListener("click", function(event) {
    const suggestions = document.getElementById("suggestions");
    const input = document.getElementById("product");

    if (!suggestions || !input) return;

    if (
        !suggestions.contains(event.target) &&
        event.target !== input
    ) {
        suggestions.innerHTML = "";
        activeSuggestionIndex = -1;
    }
});


// ==========================================
// 16. INITIALIZE KEYBOARD CONTROLS
// ==========================================

document.addEventListener("DOMContentLoaded", function() {
    const input = document.getElementById("product");

    if (input) {
        input.addEventListener("keydown", handleSearchKeyboard);
    }
});