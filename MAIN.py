import requests
import json
import smtplib
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

# Load variables from the .env file
load_dotenv("./CONFIG.env")

# --- Configuration (Store these securely!) ---
SIMPLEFIN_ACCESS_URL = os.environ.get("SIMPLEFIN_ACCESS_URL")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")
SMTP_SERVER = os.environ.get("SMTP_SERVER")
SMTP_PORT = 465 # For TLS/STARTTLS
try:
    ACCOUNT_GROUPS = json.loads(os.environ.get("ACCOUNT_GROUPS", "{}"))
    ACCOUNT_NICKNAMES = json.loads(os.environ.get("ACCOUNT_NICKNAMES", "{}"))
except json.JSONDecodeError:
    print("Error parsing JSON from .env file. Using empty dicts.")
    ACCOUNT_GROUPS = {}
    ACCOUNT_NICKNAMES = {}

if not SIMPLEFIN_ACCESS_URL:
    print("Error: Required environment variables not set.")
    exit()

# A dictionary mapping group names to their respective colors.
GROUP_COLORS = {
    "Credit Cards": "#ffadad",      # Pastel red
    "Checking Accounts": "#ffd6a5", # Pastel orange
    "Savings Accounts": "#a0c4ff",  # Pastel blue
    "Investments": "#baf3a4",       # Pastel green
    "Other": "#e0e0e0"             # A light gray for the "Other" group
}

def get_simplefin_data(days=1):
    """Fetches transaction data from SimpleFIN for the last 24 hours."""
    # Calculate timestamp for 24 hours ago
    start_date = datetime.now() - timedelta(days=days)
    start_timestamp = int(start_date.timestamp())

    try:
        response = requests.get(
            f"{SIMPLEFIN_ACCESS_URL}/accounts",
            params={'start-date': start_timestamp}
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from SimpleFIN: {e}")
        return None
    
def format_email_body_html(data):
    """Formats the transaction data to show recent transactions, account balances, and Net Worth summary, with black font for group totals."""
    if not data or not data.get("accounts"):
        return "<p style='font-family: Arial, sans-serif; font-size: 14px; text-align: center;'>No new transactions found.</p>"

    # 1. Prepare Data for All Sections and Calculate Summaries
    total_assets = 0.0
    total_liabilities = 0.0
    
    group_totals = {
        "Credit Cards": 0.0,
        "Checking Accounts": 0.0,
        "Savings Accounts": 0.0,
        "Investments": 0.0,
        "Other": 0.0
    }
    
    all_grouped_accounts = {
        "Credit Cards": [],
        "Checking Accounts": [],
        "Savings Accounts": [],
        "Investments": [],
        "Other": []
    }
    transactions_by_account = {}
    all_transactions = []

    for account in data["accounts"]:
        original_name = account.get("name")
        transactions = account.get("transactions", [])
        
        display_name = ACCOUNT_NICKNAMES.get(original_name, original_name)
        group_name = ACCOUNT_GROUPS.get(original_name, "Other")
        
        if group_name == "Ignore":
            continue

        # --- Summary and Group Total Calculation ---
        try:
            balance = float(account.get("balance", 0.0))
            
            group_totals[group_name] += balance
            
            if group_name == "Credit Cards" or balance < 0:
                total_liabilities += abs(balance)
            else:
                total_assets += balance
        except (ValueError, TypeError):
            pass

        # --- Preparation for Transactions & Balances Sections ---
        if transactions:
            transactions.sort(key=lambda t: t.get("posted", 0), reverse=True)
            transactions_by_account[display_name] = transactions
            all_transactions.extend(transactions)

        account['display_name'] = display_name
        all_grouped_accounts[group_name].append(account)

    net_worth = total_assets - total_liabilities
    
    # --- HTML Structure Begins ---
    html_body = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.4; background-color: #ffffff; color: #333; margin: 0; padding: 10px; }
            .container { max-width: 600px; margin: 0 auto; }
            h1 { font-size: 20px; color: #2c3e50; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-bottom: 15px; }
            .section-header { font-size: 18px; font-weight: bold; color: #16a085; padding: 5px 0; margin-bottom: 10px; border-bottom: 2px solid #16a085; }
            .account-subheader { font-size: 14px; font-weight: bold; color: #333; margin: 10px 0 0 0; padding: 3px 0; }
            .data-table { width: 100%; border-collapse: collapse; margin-bottom: 10px; }
            .data-table th, .data-table td { text-align: left; padding: 6px 8px; border-bottom: 1px solid #eee; font-size: 13px; }
            .data-table th { background-color: #f0f0f0; color: #555; text-align: left; }
            .positive { color: #27ae60; }
            .negative { color: #e74c3c; }
            .net-worth-row { font-size: 16px; font-weight: bold; }
            .net-worth-row td { padding: 8px 10px; }
            .balance-row { background-color: #f9f9f9; }
            .balance-row td { padding: 8px 10px; } 
            /* FIXED 1: Set color to black and remove text-shadow */
            .group-total-text { color: #000; text-shadow: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Financial Report - Last 7 days</h1>
    """
    
    # ----------------------------------------------------
    # SECTION 1: TRANSACTION SUMMARY (GROUPED BY ACCOUNT)
    # ----------------------------------------------------
    html_body += '<div class="section-header">Recent Transactions</div>'
    
    if all_transactions:
        for account_name in transactions_by_account.keys():
            transactions = transactions_by_account[account_name]

            html_body += f'<div class="account-subheader">{account_name}</div>'

            html_body += """
            <table class="data-table">
                <thead>
                    <tr>
                        <th style="width: 20%;">Date</th>
                        <th style="width: 55%;">Description</th>
                        <th style="text-align:right; width: 25%;">Amount</th>
                    </tr>
                </thead>
                <tbody>
            """
            for transaction in transactions:
                date_str = datetime.fromtimestamp(transaction.get("posted", 0)).strftime("%m/%d %H:%M")
                description = transaction.get("description", "N/A")
                amount = transaction.get("amount", "N/A")
                
                try:
                    numeric_amount = float(amount)
                    amount_class = "positive" if numeric_amount >= 0 else "negative"
                    formatted_amount = f"${numeric_amount:,.2f}"
                except (ValueError, TypeError):
                    formatted_amount = amount
                    amount_class = ""

                html_body += f"""
                    <tr>
                        <td>{date_str}</td>
                        <td>{description}</td>
                        <td><span style="float:right;" class="{amount_class}">{formatted_amount}</span></td>
                    </tr>
                """
            html_body += """
                </tbody>
            </table>
            """
    else:
        html_body += '<p>No new transactions to report in the last 24 hours.</p>'

    # ----------------------------------------------------
    # SECTION 2: GROUPED ACCOUNT BALANCE OVERVIEW (ALL ACCOUNTS)
    # ----------------------------------------------------
    html_body += '<div class="section-header" style="margin-top: 25px;">Account Balances Overview</div>'
    
    for group_name, accounts in all_grouped_accounts.items():
        if not accounts:
            continue
        
        group_color = GROUP_COLORS.get(group_name, "#7f8c8d")
        
        # --- RENDER GROUP BANNER WITH TOTAL ---
        group_total_value = group_totals[group_name]
        
        total_abs_value = abs(group_total_value)
        total_sign = "-" if group_total_value < 0 else ""
        formatted_group_total = f"{total_abs_value:,.2f}"
        
        total_class = "group-total-text"
        
        # FIXED 2: Set color of table content to black. Removed redundant inline styles/class that forced white font.
        html_body += f"""
        <table style="width: 100%; background-color: {group_color}; color: #000; border-collapse: collapse; margin: 10px 0 0 0;">
            <tr>
                <td width="68%" style="font-size: 16px; font-weight: bold; padding: 5px 10px; text-align: left;">
                    {group_name} Total:
                </td>
                <td width="7%" style="font-size: 16px; font-weight: bold; text-align:right; padding: 5px 0 5px 0;"> 
                    <span>{total_sign}$</span>
                </td>
                <td width="25%" style="font-size: 16px; font-weight: bold; text-align:left; padding: 5px 10px 5px 0;">
                    <span>{formatted_group_total}</span>
                </td>
            </tr>
        </table>
        """
        # --- END RENDER GROUP BANNER ---

        html_body += """
        <table class="data-table">
            <tbody>
        """
        for account in accounts:
            balance = account.get("balance")
            display_name = account.get("display_name")
            
            # Logic for aligned dollar sign (3 cells)
            balance_content = ""
            try:
                numeric_balance = float(balance)
                
                numeric_sign = "-" if numeric_balance < 0 else ""
                formatted_numeric_abs_balance = f"{abs(numeric_balance):,.2f}"
                
                # Removed <strong> tags from balance content
                balance_content = (
                    # 2. Cell for Sign and $ (Combined)
                    f'<td width="7%" style="text-align:right; padding: 0 0 0 0;">{numeric_sign}$</td>'
                    # 3. Cell for number
                    f'<td width="25%" style="text-align:left; padding-left:0;">{formatted_numeric_abs_balance}</td>'
                )
            except (ValueError, TypeError):
                # Fallback for non-numeric - REMOVED <strong> TAGS
                balance_content = f'<td colspan="2" width="32%" style="text-align:right; padding-left:0;">{balance}</td>'

            
            html_body += f"""
                <tr class="balance-row">
                    <td width="68%">{display_name}</td>
                    {balance_content}
                </tr>
            """
        html_body += """
            </tbody>
        </table>
        """

    # ----------------------------------------------------
    # SECTION 3: NET WORTH SUMMARY (AT BOTTOM)
    # ----------------------------------------------------
    net_worth_class = "positive" if net_worth >= 0 else "negative"
    
    html_body += """
    <div class="section-header" style="margin-top: 25px;">Net Worth Summary</div>
    <table class="data-table" style="margin-bottom: 20px;">
        <tbody>
            <tr>
                <td>Total Assets</td>
                <td style="text-align:right;">""" + f'<span class="positive">${total_assets:,.2f}</span>' + """</td>
            </tr>
            <tr>
                <td>Total Liabilities</td>
                <td style="text-align:right;">""" + f'<span class="negative">${total_liabilities:,.2f}</span>' + """</td>
            </tr>
            <tr class="net-worth-row" style="background-color: #e6e6e6; border-top: 2px solid #333;">
                <td>NET WORTH</td>
                <td style="text-align:right;">""" + f'<span class="{net_worth_class}">${net_worth:,.2f}</span>' + """</td>
            </tr>
        </tbody>
    </table>
    """

    html_body += """
        </div>
    </body>
    </html>
    """
    return html_body

def send_email_html(sender, recipient, password, subject, body_html):
    """Sends an email with HTML content using SMTP_SSL."""
    msg = MIMEText(body_html, "html")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def run_report_main(days=1):
    transaction_data = get_simplefin_data(days=days)
    if transaction_data:
        email_body_html = format_email_body_html(transaction_data)
        # Get the current date and time
        today = datetime.now()
        # Subtract 7 days using timedelta
        seven_days_ago = today - timedelta(days=days)
        # Format the date as 'YYYY-MM-DD'
        # Format the dates as 'YYYY-MM-DD'
        today_str = today.strftime('%Y-%m-%d')
        seven_days_ago_str = seven_days_ago.strftime('%Y-%m-%d')
        email_subject = f"Weekly Financial Report ({seven_days_ago_str} - {today_str})"
        send_email_html(SENDER_EMAIL, RECIPIENT_EMAIL, SENDER_PASSWORD, email_subject, email_body_html)
    else:
        print("Could not retrieve transaction data. Skipping email send.")

if __name__ == "__main__":
    run_report_main(days=7)