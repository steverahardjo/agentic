# Chatbot-Based Expense Tracker Bot via Telegram

## Overview
This project utilizes the Telegram Bot API connected to a chatbot functionality implemented using Langchain to incorporate advanced Language Model (LLM) chatting features. It is designed for intelligent data extraction, tracking user expenses, and generating detailed reports.

## Features
- **Staging Interaction/Init Storage**: 
    - Allows tracking per month or per week.
    - Name of user
    - Email
- **Accepted Data Input**: 
  - Category
  - Expenses
- **Reporting Requests**:
  - Generate an Excel file of expenses
  - Show current remaining amount in the daily budget
  - Show current remaining amount in the monthly budget
  - Create visualizations using Matplotlib
- **Automated Outputs**:
  - Alert every 6 hours after a new data entry
  - Monthly CSV report
  - Immediate alert after data input
- **Stored Data**:
  - ID (unique generated key)
  - Name
  - Categories
  - Amount
  - Month
  - Date
  - Year
  - Photos of transactions
- **Possible Categories**:
  - Food
  - Medical
  - Transport
  - Clothing

## Setup
Here are the steps to run and contribute to this project:

1. **Clone this repository**
    ```bash
    git clone https://github.com/your-username/expense-tracker-bot.git
    ```

2. **Installing dependencies and virtual environment**:
    You can set up the virtual environment in two ways:
    
    - **Using `venv`**:
      ```bash 
      python -m venv venv
      source venv/bin/activate  # for Unix-based systems
      venv\Scripts\activate     # for Windows
      ```

    - **Using `uv`**:
      First, ensure `uv` is installed. More info at [UV Documentation](https://docs.astral.sh/uv/).

      Then run:
      ```bash
      uv venv
      uv sync
      ```

      After this, you can manually load the `venv` or use `uv` to run scripts. See more info at [UV Guide](https://docs.astral.sh/uv/guides/scripts/).

## Tech Stack
1. **Frontend**: Telegram Bot API
2. **Backend**: REST API using Django
3. **Chatbot Feature**: Langchain
4. **Language Model**: Locally run Mistral AI
5. **Database**: PostgreSQL
6. **Data Processing**: Pandas and Matplotlib
7. **Programming Language**: Python 3.10

## Future Enhancements
1. Customizable categories
2. Accepting receipts as input
3. Extending LLM capabilities in suggestion/written persuasion
