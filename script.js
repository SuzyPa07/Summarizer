async function analyzeReview() {

    let review = document.getElementById("review").value;
    let product = document.getElementById("product").value;

    if (review.trim() === "") {
        alert("Please enter a review");
        return;
    }

    document.getElementById("loading").style.display = "block";
    document.getElementById("result").style.display = "none";

    try {

        let response = await fetch("http://127.0.0.1:8000/predict", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                product: product,
                review: review,
                domain: "electronics"
            })
        });

        if (!response.ok) {
            throw new Error("API request failed");
        }

        let data = await response.json();

        document.getElementById("loading").style.display = "none";
        document.getElementById("result").style.display = "block";

        let output = "";

        for (let aspect in data.aspects) {

            output += `
                <div class="aspect">
                    <b>${aspect}</b><br>
                    ${data.aspects[aspect]}
                </div>
            `;
        }

        output += `
            <div class="aspect">
                <b>Overall Summary</b><br>
                ${data.summary}
            </div>
        `;

        document.getElementById("output").innerHTML = output;

    } catch (error) {

        document.getElementById("loading").style.display = "none";

        alert("Could not connect to the FastAPI server.");

        console.log(error);
    }
}