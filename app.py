from flask import Flask, render_template, request
import yfinance as yf
import requests
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Load API keys from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
COMPANIES_HOUSE_API_KEY = os.getenv('COMPANIES_HOUSE_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')  # Optional if you continue using News API

# Initialize the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# Custom filter to handle newlines in templates
def nl2br(value):
    if value is None:
        return ''
    return value.replace('\n', '<br>\n')

app.jinja_env.filters['nl2br'] = nl2br

# Formatting filters for currency and numbers
def format_currency(value):
    if value is None or value == 'N/A':
        return 'N/A'
    try:
        value = float(value)
        return f"${value:,.2f}"
    except (ValueError, TypeError):
        return value

def format_number(value):
    if value is None or value == 'N/A':
        return 'N/A'
    try:
        return f"{float(value):,.2f}"
    except (ValueError, TypeError):
        return value

app.jinja_env.filters['currency'] = format_currency
app.jinja_env.filters['number'] = format_number

def get_financial_data(ticker):
    try:
        print(f"Fetching data for ticker: {ticker}")
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info:
            print("No data found for the ticker.")
            return {}
        financial_data = {
            'company_name': info.get('longName', 'N/A'),
            'summary': info.get('longBusinessSummary', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A'),
            'beta': info.get('beta', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'eps': info.get('trailingEps', 'N/A'),
            'dividend_yield': info.get('dividendYield', 'N/A'),
        }
        return financial_data
    except Exception as e:
        print(f"Exception in get_financial_data: {e}")
        return {}

def retrieve_legal_info(company_name, company_number, api_keys):
    # Fetch legal filings from Companies House
    legal_summary_ch = retrieve_legal_info_from_companies_house(company_number, api_keys['companies_house'])
    # Optionally, fetch recent legal news
    # legal_summary_news = get_recent_news(company_name, api_keys['news_api'])
    
    # Combine summaries
    legal_summary = f"**Companies House Legal Filings:**\n{legal_summary_ch}"
    # If using News API:
    # legal_summary = f"**Companies House Legal Filings:**\n{legal_summary_ch}\n\n**Recent Legal News:**\n{legal_summary_news}"
    return legal_summary

def retrieve_legal_info_from_companies_house(company_number, api_key):
    base_url = f'https://api.company-information.service.gov.uk/company/{company_number}/filing-history'
    response = requests.get(base_url, auth=(api_key, ''))
    
    if response.status_code == 200:
        filings = response.json().get('items', [])
        legal_issues = []
        
        for filing in filings:
            description = filing.get('description', '')
            if 'legal' in description.lower() or 'court' in description.lower() or 'settlement' in description.lower():
                legal_issues.append(description)
        
        if legal_issues:
            legal_summary = "\n".join(legal_issues)
        else:
            legal_summary = "No significant legal filings found."
    else:
        legal_summary = "Unable to retrieve legal information from Companies House."
    
    return legal_summary

def generate_ai_summary(financial_data, legal_summary):
    # Replace None values with 'N/A'
    for key, value in financial_data.items():
        if value is None:
            financial_data[key] = 'N/A'

    messages = [
        {"role": "system", "content": "You are a financial analyst assistant specializing in UK company data."},
        {"role": "user", "content": f"""
Provide a concise and professional summary for the following UK company, focusing on financial health and key information from Companies House filings:

**Company Name**: {financial_data.get('company_name')}
**Sector**: {financial_data.get('sector')}
**Industry**: {financial_data.get('industry')}

**Financial Summary**:
{financial_data.get('summary')}

**Key Financial Metrics**:
- Market Cap: {financial_data.get('market_cap')}
- Beta: {financial_data.get('beta')}
- P/E Ratio: {financial_data.get('pe_ratio')}
- EPS: {financial_data.get('eps')}
- Dividend Yield: {financial_data.get('dividend_yield')}

**Legal Issues**:
{legal_summary}

**Instructions**: Summarize the financial health of the company and highlight the key information from Companies House filings, discussing any potential impacts on the company's operations, revenue, and profit.
"""}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Or "gpt-4" if you have access
            messages=messages,
            max_tokens=500,
            temperature=0.5,
        )

        ai_summary = response.choices[0].message.content.strip()
        return ai_summary
    except Exception as e:
        print(f"Exception in generate_ai_summary: {e}")
        return "Error generating AI summary."

def get_tickers_by_sector(sector):
    # This function should return a list of ticker symbols in the same sector
    # For demonstration purposes, we'll use a static list
    # In a real application, you might query an API or database
    sector_tickers = {
        'Technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'],
        'Financial Services': ['JPM', 'BAC', 'WFC', 'C', 'GS'],
        # Add more sectors and their tickers as needed
    }
    return sector_tickers.get(sector, [])

def get_sector_averages(sector):
    # Fetch data for multiple companies in the same sector
    sector_tickers = get_tickers_by_sector(sector)
    
    if not sector_tickers:
        print(f"No tickers found for sector: {sector}")
        # Initialize all metrics to 'N/A'
        return {
            'market_cap': 'N/A',
            'beta': 'N/A',
            'pe_ratio': 'N/A',
            'eps': 'N/A',
            'dividend_yield': 'N/A'
        }

    metrics = {
        'market_cap': [],
        'beta': [],
        'pe_ratio': [],
        'eps': [],
        'dividend_yield': []
    }

    for ticker in sector_tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            metrics['market_cap'].append(info.get('marketCap', 0) or 0)
            metrics['beta'].append(info.get('beta', 0) or 0)
            metrics['pe_ratio'].append(info.get('trailingPE', 0) or 0)
            metrics['eps'].append(info.get('trailingEps', 0) or 0)
            metrics['dividend_yield'].append(info.get('dividendYield', 0) or 0)
        except Exception as e:
            print(f"Error retrieving data for {ticker}: {e}")
            continue

    sector_averages = {}
    for key, values in metrics.items():
        # Filter out None or zero values to avoid skewed averages
        valid_values = [v for v in values if v > 0]
        if valid_values:
            sector_averages[key] = sum(valid_values) / len(valid_values)
        else:
            sector_averages[key] = 'N/A'

    # Ensure all keys are present
    for key in ['market_cap', 'beta', 'pe_ratio', 'eps', 'dividend_yield']:
        if key not in sector_averages:
            sector_averages[key] = 'N/A'

    return sector_averages

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        company_ticker = request.form.get('ticker', '').upper().strip()
        company_number = request.form.get('company_number', '').strip()

        print(f"Received form data: {request.form}")
        print(f"Received ticker: {company_ticker}")
        print(f"Received company number: {company_number}")

        if not company_ticker or not company_number:
            error = "Please provide both the company ticker and company number."
            return render_template('index.html', error=error)

        api_keys = {
            'companies_house': COMPANIES_HOUSE_API_KEY,
            'news_api': NEWS_API_KEY,  # Optional
            'openai': OPENAI_API_KEY
        }

        financial_data = get_financial_data(company_ticker)
        if not financial_data.get('company_name') or financial_data.get('company_name') == 'N/A':
            error = "Error retrieving financial data. Please check the ticker symbol."
            return render_template('index.html', error=error)

        legal_summary = retrieve_legal_info(financial_data['company_name'], company_number, api_keys)
        ai_summary = generate_ai_summary(financial_data, legal_summary)

        # Get sector averages
        sector = financial_data.get('sector')
        if sector and sector != 'N/A':
            sector_averages = get_sector_averages(sector)
        else:
            sector_averages = {
                'market_cap': 'N/A',
                'beta': 'N/A',
                'pe_ratio': 'N/A',
                'eps': 'N/A',
                'dividend_yield': 'N/A'
            }

        return render_template(
            'report.html',
            summary=ai_summary,
            financial_data=financial_data,
            sector_averages=sector_averages,
            legal_summary=legal_summary  # Ensure this is passed
        )
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5002)
