from flask import Flask, request, jsonify, render_template, Blueprint
import yfinance as yf
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd

# Flask set up
app = Flask(__name__)
# Create a blueprint for static files
blueprint_static = Blueprint('static', __name__, static_folder='static')
app.register_blueprint(blueprint_static)

def get_stock_data(company_name):
    """
    Fetches stock data using yfinance.
    """
    try:
        stock = yf.Ticker(company_name)
        info = stock.info
        history = stock.history(period="5y")  # Adjust the period as needed
        balance_sheet = stock.balance_sheet
        cashflow = stock.cashflow
        income_statement = stock.financials
        return info, history, balance_sheet, cashflow, income_statement
    except Exception as e:
        return None, f"Error: Unable to retrieve data for '{company_name}': {e}"

def generate_price_chart(history):
    """
    Generates a line chart of stock prices.
    """
    plt.figure(figsize=(10, 5))
    plt.plot(history['Close'])
    plt.title('Stock Price History')
    plt.xlabel('Date')
    plt.ylabel('Closing Price')

    # Convert the plot to a base64 encoded image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    chart_data = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()  # Close the plot to avoid memory leaks
    return chart_data

def evaluate_stock(company_name):
    """
    Evaluates a stock's potential as a long-term investment.
    """
    info, history, balance_sheet, cashflow, income_statement = get_stock_data(company_name)

    if info is None:
        return info, history, "Error: Unable to retrieve data for this stock."  # Return an error message

    # Extract necessary financial metrics
    debt_to_equity = info.get("debtToEquity", None)
    roe = info.get("returnOnEquity", None)
    sector = info.get("sector", None)
    pe_ratio = info.get("trailingPE", None)

    # Calculate additional metrics
    revenue_growth_yoy = calculate_revenue_growth_yoy(income_statement)
    cagr = calculate_cagr(income_statement)
    net_profit_margin = calculate_net_profit_margin(income_statement)
    free_cash_flow = calculate_free_cash_flow(cashflow)
    roa = calculate_roa(income_statement, balance_sheet)
    rd_spending_percentage = calculate_rd_spending_percentage(income_statement)
    price_to_book = calculate_price_to_book(info)
    asset_turnover = calculate_asset_turnover(income_statement, balance_sheet)
    financial_leverage = calculate_financial_leverage(balance_sheet)
    debt_to_assets_ratio = calculate_debt_to_assets_ratio(balance_sheet)
    interest_coverage_ratio = calculate_interest_coverage_ratio(income_statement, balance_sheet)
    leverage_ratio = calculate_leverage_ratio(balance_sheet)
    net_debt = calculate_net_debt(balance_sheet, info)
    debt_service_coverage_ratio = calculate_debt_service_coverage_ratio(cashflow, balance_sheet)
    free_cash_flow_to_debt = calculate_free_cash_flow_to_debt(cashflow, balance_sheet)

    # Evaluate interest rate sensitivity
    interest_rate_sensitivity = evaluate_interest_rate_sensitivity(sector, debt_to_equity)

    return (
        info,
        history,
        pe_ratio,
        roe,
        debt_to_equity,
        interest_rate_sensitivity,
        revenue_growth_yoy,
        cagr,
        net_profit_margin,
        free_cash_flow,
        roa,
        rd_spending_percentage,
        price_to_book,
        asset_turnover,
        financial_leverage,
        debt_to_assets_ratio,
        interest_coverage_ratio,
        leverage_ratio,
        net_debt,
        debt_service_coverage_ratio,
        free_cash_flow_to_debt
    )

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

def generate_advisor_description(info, pe_ratio, roe, debt_to_equity, interest_rate_sensitivity, revenue_growth_yoy, cagr, net_profit_margin, free_cash_flow, roa, rd_spending_percentage, price_to_book, asset_turnover, financial_leverage, debt_to_assets_ratio, interest_coverage_ratio, leverage_ratio, net_debt, debt_service_coverage_ratio, free_cash_flow_to_debt):
    """
    Generates a financial advisor-like description based on the evaluation results.
    """
    description = ""

    # P/E Ratio
    if pe_ratio is not None:
        description += f"The company's P/E ratio is {pe_ratio:.2f}. "

    # ROE
    if roe is not None:
        description += f"The company's Return on Equity is {roe:.2f}%. "

    # Interest Rate Sensitivity
    description += f"The company's sensitivity to interest rate changes is {interest_rate_sensitivity}. "

    # Debt-to-Equity Ratio
    if debt_to_equity is not None:
        description += f"The Debt-to-Equity ratio is {debt_to_equity:.2f}. "

    # Revenue Growth
    if revenue_growth_yoy is not None:
        description += f"The company's revenue has grown {revenue_growth_yoy:.2f}% year-over-year. "
    if cagr is not None:
        description += f"The company's Compound Annual Growth Rate (CAGR) is {cagr:.2f}%. "

    # Net Profit Margin
    if net_profit_margin is not None:
        description += f"The company's Net Profit Margin is {net_profit_margin:.2f}%. This indicates its profitability relative to revenue. "

    # Free Cash Flow
    if free_cash_flow is not None:
        description += f"The company's Free Cash Flow is {free_cash_flow:.2f}. "

    # ROA
    if roa is not None:
        description += f"The company's Return on Assets is {roa:.2f}%. "

    # R&D Spending
    if rd_spending_percentage is not None:
        description += f"The company spends {rd_spending_percentage:.2f}% of its revenue on research and development. "

    # Price-to-Book
    if price_to_book is not None:
        description += f"The company's Price-to-Book ratio is {price_to_book:.2f}. "

    # Asset Turnover
    if asset_turnover is not None:
        description += f"The company's Asset Turnover ratio is {asset_turnover:.2f}. "

    # Financial Leverage
    if financial_leverage is not None:
        description += f"The company's Financial Leverage is {financial_leverage:.2f}. "

    # Debt-to-Assets Ratio
    if debt_to_assets_ratio is not None:
        description += f"The company's Debt-to-Assets Ratio is {debt_to_assets_ratio:.2f}. "

    # Interest Coverage Ratio
    if interest_coverage_ratio is not None:
        description += f"The company's Interest Coverage Ratio is {interest_coverage_ratio:.2f}. "

    # Leverage Ratio
    if leverage_ratio is not None:
        description += f"The company's Leverage Ratio is {leverage_ratio:.2f}. "

    # Net Debt
    if net_debt is not None:
        description += f"The company's Net Debt is {net_debt:.2f}. "

    # Debt Service Coverage Ratio
    if debt_service_coverage_ratio is not None:
        description += f"The company's Debt Service Coverage Ratio is {debt_service_coverage_ratio:.2f}. "

    # Free Cash Flow to Debt
    if free_cash_flow_to_debt is not None:
        description += f"The company's Free Cash Flow to Debt ratio is {free_cash_flow_to_debt:.2f}. "

    return description

def calculate_revenue_growth_yoy(income_statement):
    """
    Calculates the year-over-year revenue growth rate.
    """
    try:
        current_revenue = income_statement.iloc[-1]['Total Revenue']
        previous_revenue = income_statement.iloc[-2]['Total Revenue']
        growth_yoy = ((current_revenue - previous_revenue) / previous_revenue) * 100
        return growth_yoy
    except:
        return None

def calculate_cagr(income_statement):
    """
    Calculates the Compound Annual Growth Rate (CAGR).
    """
    try:
        start_revenue = income_statement.iloc[0]['Total Revenue']
        end_revenue = income_statement.iloc[-1]['Total Revenue']
        years = len(income_statement)
        cagr = ((end_revenue / start_revenue) ** (1 / years) - 1) * 100
        return cagr
    except:
        return None

def calculate_net_profit_margin(income_statement):
    """
    Calculates the Net Profit Margin.
    """
    try:
        net_income = income_statement.iloc[-1]['Net Income']
        revenue = income_statement.iloc[-1]['Total Revenue']
        net_profit_margin = (net_income / revenue) * 100
        return net_profit_margin
    except:
        return None

def calculate_free_cash_flow(cashflow):
    """
    Calculates the Free Cash Flow (FCF).
    """
    try:
        operating_cash_flow = cashflow.iloc[-1]['Total Cash From Operating Activities']
        capital_expenditures = cashflow.iloc[-1]['Capital Expenditures']
        free_cash_flow = operating_cash_flow - capital_expenditures
        return free_cash_flow
    except:
        return None

def calculate_roa(income_statement, balance_sheet):
    """
    Calculates the Return on Assets (ROA).
    """
    try:
        net_income = income_statement.iloc[-1]['Net Income']
        total_assets = balance_sheet.iloc[-1]['Total Assets']
        roa = (net_income / total_assets) * 100
        return roa
    except:
        return None

def calculate_rd_spending_percentage(income_statement):
    """
    Calculates R&D Spending as a Percentage of Revenue.
    """
    try:
        rd_spending = income_statement.iloc[-1]['Research Development']
        revenue = income_statement.iloc[-1]['Total Revenue']
        rd_spending_percentage = (rd_spending / revenue) * 100
        return rd_spending_percentage
    except:
        return None

def calculate_price_to_book(info):
    """
    Calculates the Price-to-Book (P/B) Ratio.
    """
    try:
        price_to_book = info.get("priceToBook", None)
        return price_to_book
    except:
        return None

def calculate_asset_turnover(income_statement, balance_sheet):
    """
    Calculates Asset Turnover (Efficiency).
    """
    try:
        revenue = income_statement.iloc[-1]['Total Revenue']
        total_assets = balance_sheet.iloc[-1]['Total Assets']
        asset_turnover = revenue / total_assets
        return asset_turnover
    except:
        return None

def calculate_financial_leverage(balance_sheet):
    """
    Calculates Financial Leverage.
    """
    try:
        total_assets = balance_sheet.iloc[-1]['Total Assets']
        shareholders_equity = balance_sheet.iloc[-1]['Total Stockholder Equity']
        financial_leverage = total_assets / shareholders_equity
        return financial_leverage
    except:
        return None

def calculate_debt_to_assets_ratio(balance_sheet):
    """
    Calculates the Debt-to-Assets Ratio.
    """
    try:
        total_debt = balance_sheet.iloc[-1]['Total Debt']
        total_assets = balance_sheet.iloc[-1]['Total Assets']
        debt_to_assets_ratio = total_debt / total_assets
        return debt_to_assets_ratio
    except:
        return None

def calculate_interest_coverage_ratio(income_statement, balance_sheet):
    """
    Calculates the Interest Coverage Ratio.
    """
    try:
        ebit = income_statement.iloc[-1]['Ebit']
        interest_expense = balance_sheet.iloc[-1]['Interest Expense']
        interest_coverage_ratio = ebit / interest_expense
        return interest_coverage_ratio
    except:
        return None

def calculate_leverage_ratio(balance_sheet):
    """
    Calculates the Leverage Ratio.
    """
    try:
        total_assets = balance_sheet.iloc[-1]['Total Assets']
        total_equity = balance_sheet.iloc[-1]['Total Stockholder Equity']
        leverage_ratio = total_assets / total_equity
        return leverage_ratio
    except:
        return None

def calculate_net_debt(balance_sheet, info):
    """
    Calculates Net Debt.
    """
    try:
        total_debt = balance_sheet.iloc[-1]['Total Debt']
        cash_and_equivalents = info.get("totalCash", None)
        net_debt = total_debt - cash_and_equivalents
        return net_debt
    except:
        return None

def calculate_debt_service_coverage_ratio(cashflow, balance_sheet):
    """
    Calculates the Debt Service Coverage Ratio (DSCR).
    """
    try:
        net_operating_income = cashflow.iloc[-1]['Total Cash From Operating Activities']
        total_debt_service = balance_sheet.iloc[-1]['Interest Expense']
        debt_service_coverage_ratio = net_operating_income / total_debt_service
        return debt_service_coverage_ratio
    except:
        return None

def calculate_free_cash_flow_to_debt(cashflow, balance_sheet):
    """
    Calculates Free Cash Flow to Debt.
    """
    try:
        free_cash_flow = calculate_free_cash_flow(cashflow)
        total_debt = balance_sheet.iloc[-1]['Total Debt']
        free_cash_flow_to_debt = free_cash_flow / total_debt
        return free_cash_flow_to_debt
    except:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        company_name = request.form['company_name']
        (
            info,
            history,
            pe_ratio,
            roe,
            debt_to_equity,
            interest_rate_sensitivity,
            revenue_growth_yoy,
            cagr,
            net_profit_margin,
            free_cash_flow,
            roa,
            rd_spending_percentage,
            price_to_book,
            asset_turnover,
            financial_leverage,
            debt_to_assets_ratio,
            interest_coverage_ratio,
            leverage_ratio,
            net_debt,
            debt_service_coverage_ratio,
            free_cash_flow_to_debt
        ) = evaluate_stock(company_name)
        # Generate the price chart
        price_chart = generate_price_chart(history)
        # Pass the data to the template
        advisor_description = generate_advisor_description(
            info,
            pe_ratio,
            roe,
            debt_to_equity,
            interest_rate_sensitivity,
            revenue_growth_yoy,
            cagr,
            net_profit_margin,
            free_cash_flow,
            roa,
            rd_spending_percentage,
            price_to_book,
            asset_turnover,
            financial_leverage,
            debt_to_assets_ratio,
            interest_coverage_ratio,
            leverage_ratio,
            net_debt,
            debt_service_coverage_ratio,
            free_cash_flow_to_debt
        )

        # You don't seem to need `evaluation_result` in your code
        return render_template(
            'index.html',
            company_name=company_name,
            price_chart=price_chart,
            info=info,
            advisor_description=advisor_description
        )
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)