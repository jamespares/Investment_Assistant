document.querySelector("button").addEventListener("click", function() {
    const companyName = document.querySelector("input").value;

    fetch("/evaluate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ company_name: companyName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.evaluation) {
            alert(data.evaluation);
        } else {
            alert(data.error || "An error occurred");
        }
    })
    .catch(error => console.error("Error:", error));
});
