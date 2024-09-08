import yfinance as yf
import openai

def get_stock_symbol(company_name):
    """
    Translates a company name to its corresponding stock symbol using an LLM.
    """

    # Set up OpenAI API key (replace with your actual key)
    openai.api_key = "YOUR_API_KEY"

    # Craft a prompt to ask the LLM for the stock ticker
    prompt = f"What is the stock ticker symbol for the company '{company_name}'?"

    # Call the OpenAI API
    response = openai.Completion.create(
        engine="text-davinci-003",  # Or another suitable model
        prompt=prompt,
        max_tokens=10,  # Adjust as needed
        temperature=0.0,  # Keep the response focused
    )

    # Parse the response and extract the stock ticker
    stock_symbol = response.choices[0].text.strip()

    return stock_symbol

def evaluate_stock(company_name):
    """
    Evaluates a stock's potential as a long-term investment based on financial metrics,
    fetching data automatically using yfinance after translating the company name to its symbol using an LLM.
    """

    # Translate company name to stock symbol using the LLM
    stock_symbol = get_stock_symbol(company_name)

    if stock_symbol is None:
        print(f"Error: Unable to find stock symbol for '{company_name}'.")
        return

    # Fetch data from yfinance using the retrieved symbol
    stock = yf.Ticker(stock_symbol)
    info = stock.info

    # Extract necessary financial metrics
    debt_to_equity = info.get("debtToEquity", None)
    roe = info.get("returnOnEquity", None)
    sector = info.get("sector", None)
    pe_ratio = info.get("trailingPE", None)

    if any(metric is None for metric in [debt_to_equity, roe, sector, pe_ratio]):
        print("Error: Unable to retrieve all necessary financial data for this stock.")
        return

    # Evaluate P/E ratio
    if pe_ratio is not None and pe_ratio < 20:
        print(f"Positive: The P/E ratio of {pe_ratio} suggests the stock is fairly valued or undervalued.")
    else:
        print(f"Consideration: The P/E ratio of {pe_ratio} suggests the stock might be overvalued.")

    # Evaluate ROE
    if roe is not None and roe > 0.15:  # Example: An ROE above 15% is considered good
        print("Positive: The company has a strong Return on Equity.")
    elif roe is not None:
        print(f"Consideration: The Return on Equity of {roe} is relatively low.")

    # Evaluate interest rate sensitivity
    interest_rate_sensitivity = evaluate_interest_rate_sensitivity(sector, debt_to_equity)
    print(f"Interest Rate Sensitivity: {interest_rate_sensitivity}")

    # Display overall debt-to-equity ratio
    print(f"Debt-to-Equity Ratio: {debt_to_equity}")

    # Final suggestion
    print("\nOverall evaluation based on the financial metrics provided.")


def evaluate_interest_rate_sensitivity(sector, debt_to_equity):
    """
  Estimates a company's sensitivity to interest rate changes based on sector and debt-to-equity ratio.
  """
    # Basic sector-based sensitivity (adjust as needed)
    high_sensitivity_sectors = ["Real Estate", "Utilities", "Telecommunications Services"]
    moderate_sensitivity_sectors = ["Energy", "Financials"]

    if sector in high_sensitivity_sectors:
        base_sensitivity = "High"
    elif sector in moderate_sensitivity_sectors:
        base_sensitivity = "Moderate"
    else:
        base_sensitivity = "Low"

    # Factor in debt-to-equity ratio (adjust as needed)
    if debt_to_equity is not None and debt_to_equity > 1.0:  # Example: Debt-to-equity ratio above 1.0 increases sensitivity
        if base_sensitivity == "High":
            return "Very High"
        else:
            return "High"
    else:
        return base_sensitivity


# Example usage
evaluate_stock(input("Which company are you considering investing in? "))  # Replace with the stock symbol of interest
