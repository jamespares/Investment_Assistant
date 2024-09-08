const form = document.getElementById('stock-form');
const resultsDiv = document.getElementById('results');

form.addEventListener('submit', (event) => {
    event.preventDefault(); // Prevent default form submission

    const companyName = document.getElementById('company-name').value;

    // Send the company name to your Python code (you'll need to implement this part)
    fetch('/evaluate', {  // Adjust the URL to match your server setup
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ company_name: companyName })
    })
    .then(response => response.json())
    .then(data => {
        // Display the results in the resultsDiv
        resultsDiv.innerHTML = `<pre>${data.evaluation}</pre>`; // Assuming your Python code returns the evaluation in a 'evaluation' key
    })
    .catch(error => {
        console.error('Error:', error);
        resultsDiv.innerHTML = 'An error occurred while evaluating the stock.';
    });
});