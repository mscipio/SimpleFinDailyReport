# SimpleFIN Daily Financial Report Generator

This Python project is designed to automate the process of fetching financial transactions and account balances via the **SimpleFIN Bridge** and delivering a detailed, styled **HTML summary email** directly to your inbox.

It's built for scheduled execution, making it perfect for setting up daily reports using tools like **Linux Cron** (via WSL 2) or a dedicated cloud service.

## 🚨 Security & Configuration

This project requires sensitive credentials (API key, email password) which are stored in a local **`.env`** file for security.

**🔥 CRITICAL WARNING:** **Never commit your filled-in `CONFIG.env` file to a public repository.** The included `.gitignore` file prevents this by default.

## ⚙️ Prerequisites

1. **Python 3.8+**

2. An active account with **SimpleFIN**.

3. An **App Password** for your email service (e.g., Gmail, Outlook) to allow the script to log in and send emails via SMTP.

## 🚀 Setup Guide

### Step 1: Clone the Repository & Install Dependencies

Clone the project to your local machine and install the required Python packages:

```
git clone [https://github.com/mscipio/SimpleFinDailyReport](https://github.com/mscipio/SimpleFinDailyReport)
cd SimpleFinDailyReport
pip install requests python-dotenv

```

### Step 2: Configure the SimpleFIN Access URL

The script requires a long-lived **SimpleFIN Access URL** that replaces the one-time setup token.

1. Copy the long Base64 Setup Token from the SimpleFIN website (this token is only shown once!).

2. Open the `SimpleFIN_token_exchange.py` file and replace the `SETUP_TOKEN` placeholder with your token.

3. Run the exchange script:

   ```
   python SimpleFIN_token_exchange.py
   
   ```

4. The output will be the full **SimpleFIN Access URL**. **Copy this entire URL.**

5. Create a file named **`CONFIG.env`** in the project root and paste the URL as the value for `SIMPLEFIN_ACCESS_URL`.

### Step 3: Define Email Settings in `CONFIG.env`

Fill out the following email configuration variables in your `CONFIG.env` file:

| Variable | Description | Example Value |
| :--- | :--- | :--- | 
| `SENDER_EMAIL` | The email address sending the report (From). | `reports@my-domain.com` | 
| `SENDER_PASSWORD` | The dedicated **App Password** for the sender account. | `abcd1234wxyz5678` | 
| `RECIPIENT_EMAIL` | The email address receiving the report (To). | `me@my-inbox.com` | 
| `SMTP_SERVER` | The SMTP server address. | `smtp.gmail.com` | 

### Step 4: Map and Group Your Accounts

The script relies on two JSON objects in the `CONFIG.env` file to structure the report. Use the exact account names reported by SimpleFIN as the **keys**.

#### A. `ACCOUNT_GROUPS`

Maps the raw account name to a financial category for Net Worth calculation.

| Group Types | Description |
| :--- | :--- | 
| `"Credit Cards"` | Treated as liabilities. | 
| `"Checking Accounts"` | Treated as assets. | 
| `"Savings Accounts"` | Treated as assets. | 
| `"Investments"` | Treated as assets. | 
| `"Other"` | For miscellaneous accounts. | 
| `"Ignore"` | Excludes the account from the report entirely. | 

**Example for `ACCOUNT_GROUPS` (Must be valid JSON):**

```
ACCOUNT_GROUPS={"Account Name 1": "Credit Cards", "Account Name 2": "Checking Accounts", "Ignore Account": "Ignore"}

```

#### B. `ACCOUNT_NICKNAMES`

Maps the raw account name to a clean, user-friendly nickname for display in the email report.

**Example for `ACCOUNT_NICKNAMES` (Must be valid JSON):**

```
ACCOUNT_NICKNAMES={"Account Name 1": "[Chase] Freedom Card", "Account Name 2": "[Bank] Joint Checking"}

```

## 🏃 Running and Scheduling

### Manual Test Run

To test your configuration and ensure the email sends correctly:

```
python MAIN.py

```

### Scheduling via Cron (WSL/Linux)

For daily automation, use the Linux `cron` utility.

1. Edit your user's crontab:

   ```
   crontab -e
   
   ```

2. Add a line to execute the script daily (e.g., at 7:00 AM):

   ```
   0 7 * * * /usr/bin/python3 /path/to/SimpleFinDailyReport/MAIN.py
   
   ```

   *Ensure you use the **full, absolute path** to your Python interpreter and the `MAIN.py` script.*