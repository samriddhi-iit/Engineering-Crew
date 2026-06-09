```python
import gradio as gr
import datetime
from accounts import Account, get_share_price # Assuming accounts.py is in the same directory

# --- Global Account Instance ---
# For simplicity in this demo, we'll use a single account instance.
# In a real application, you'd manage multiple accounts, perhaps with login.
user_account = None

# --- Gradio Interface Functions ---

def create_account(account_id: str, initial_deposit: float):
    """Creates a new account."""
    global user_account
    try:
        user_account = Account(account_id, initial_deposit)
        return f"Account '{account_id}' created successfully with initial deposit of ${initial_deposit:.2f}."
    except ValueError as e:
        return f"Error creating account: {e}"

def deposit_funds(amount: float):
    """Deposits funds into the account."""
    global user_account
    if user_account is None:
        return "Error: No account created. Please create an account first."
    try:
        user_account.deposit(amount)
        return f"Successfully deposited ${amount:.2f}. Current state:\n{str(user_account)}"
    except ValueError as e:
        return f"Error depositing funds: {e}"

def withdraw_funds(amount: float):
    """Withdraws funds from the account."""
    global user_account
    if user_account is None:
        return "Error: No account created. Please create an account first."
    try:
        user_account.withdraw(amount)
        return f"Successfully withdrew ${amount:.2f}. Current state:\n{str(user_account)}"
    except ValueError as e:
        return f"Error withdrawing funds: {e}"

def buy_shares_action(symbol: str, quantity: int):
    """Buys shares for the account."""
    global user_account
    if user_account is None:
        return "Error: No account created. Please create an account first."
    try:
        user_account.buy_shares(symbol.upper(), quantity)
        return f"Successfully bought {quantity} shares of {symbol.upper()}. Current state:\n{str(user_account)}"
    except ValueError as e:
        return f"Error buying shares: {e}"

def sell_shares_action(symbol: str, quantity: int):
    """Sells shares from the account."""
    global user_account
    if user_account is None:
        return "Error: No account created. Please create an account first."
    try:
        user_account.sell_shares(symbol.upper(), quantity)
        return f"Successfully sold {quantity} shares of {symbol.upper()}. Current state:\n{str(user_account)}"
    except ValueError as e:
        return f"Error selling shares: {e}"

def get_account_summary():
    """Returns the current account summary."""
    global user_account
    if user_account is None:
        return "Error: No account created. Please create an account first."
    return str(user_account)

def get_holdings_report():
    """Returns the current holdings."""
    global user_account
    if user_account is None:
        return "Error: No account created. Please create an account first."
    holdings = user_account.get_holdings()
    if not holdings:
        return "No shares currently held."
    report = "Current Holdings:\n"
    for symbol, quantity in holdings.items():
        report += f"- {symbol}: {quantity} shares\n"
    return report

def get_transactions_report():
    """Returns the transaction history."""
    global user_account
    if user_account is None:
        return "Error: No account created. Please create an account first."
    transactions = user_account.get_transactions()
    if not transactions:
        return "No transactions recorded yet."
    report = "Transaction History:\n"
    for tx in transactions:
        report += f"- [{tx['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}] {tx['type']}: "
        if tx['type'] == 'DEPOSIT':
            report += f"${tx['amount']:.2f}. Balance after: ${tx['balance_after']:.2f}\n"
        elif tx['type'] == 'WITHDRAWAL':
            report += f"${tx['amount']:.2f}. Balance after: ${tx['balance_after']:.2f}\n"
        elif tx['type'] == 'BUY':
            report += f"{tx['quantity']} of {tx['symbol']} @ ${tx['price']:.2f} (Cost: ${tx['cost']:.2f}). Balance after: ${tx['balance_after']:.2f}\n"
        elif tx['type'] == 'SELL':
            report += f"{tx['quantity']} of {tx['symbol']} @ ${tx['price']:.2f} (Revenue: ${tx['revenue']:.2f}). Balance after: ${tx['balance_after']:.2f}\n"
    return report

def get_profit_loss_report():
    """Returns the profit/loss report."""
    global user_account
    if user_account is None:
        return "Error: No account created. Please create an account first."
    pl = user_account.get_profit_loss()
    return f"Current Profit/Loss: ${pl:.2f}"

def get_portfolio_value_report():
    """Returns the portfolio value report."""
    global user_account
    if user_account is None:
        return "Error: No account created. Please create an account first."
    portfolio_value = user_account.get_portfolio_value()
    return f"Current Portfolio Value: ${portfolio_value:.2f}"


# --- Gradio Interface Definition ---

with gr.Blocks() as demo:
    gr.Markdown("# Trading Account Simulation")

    with gr.Tab("Account Management"):
        with gr.Row():
            account_id_input = gr.Textbox(label="Account ID", placeholder="Enter a unique ID")
            initial_deposit_input = gr.Number(label="Initial Deposit ($)", value=0.0)
        create_account_btn = gr.Button("Create Account")
        create_account_output = gr.Textbox(label="Account Creation Status", interactive=False)

        gr.Markdown("---")

        with gr.Row():
            deposit_amount_input = gr.Number(label="Amount to Deposit ($)", value=0.0)
        deposit_btn = gr.Button("Deposit Funds")

        with gr.Row():
            withdraw_amount_input = gr.Number(label="Amount to Withdraw ($)", value=0.0)
        withdraw_btn = gr.Button("Withdraw Funds")

        account_status_output = gr.Textbox(label="Account Status", interactive=False, lines=10)

        def update_account_status():
            return get_account_summary()

        create_account_btn.click(
            create_account,
            inputs=[account_id_input, initial_deposit_input],
            outputs=create_account_output
        )
        deposit_btn.click(
            deposit_funds,
            inputs=[deposit_amount_input],
            outputs=[account_status_output]
        )
        withdraw_btn.click(
            withdraw_funds,
            inputs=[withdraw_amount_input],
            outputs=[account_status_output]
        )
        # Automatically update status when new account is created
        create_account_btn.click(
            update_account_status,
            inputs=[],
            outputs=[account_status_output]
        )


    with gr.Tab("Trading"):
        with gr.Row():
            trade_symbol_input = gr.Textbox(label="Stock Symbol", placeholder="e.g., AAPL")
            trade_quantity_input = gr.Number(label="Quantity", value=1)
        with gr.Row():
            buy_btn = gr.Button("Buy Shares")
            sell_btn = gr.Button("Sell Shares")
        trade_output = gr.Textbox(label="Trade Status", interactive=False, lines=5)

        buy_btn.click(
            buy_shares_action,
            inputs=[trade_symbol_input, trade_quantity_input],
            outputs=[trade_output]
        )
        sell_btn.click(
            sell_shares_action,
            inputs=[trade_symbol_input, trade_quantity_input],
            outputs=[trade_output]
        )
        # Update account status after a trade
        buy_btn.click(
            update_account_status,
            inputs=[],
            outputs=[account_status_output]
        )
        sell_btn.click(
            update_account_status,
            inputs=[],
            outputs=[account_status_output]
        )

    with gr.Tab("Reports"):
        with gr.Row():
            summary_btn = gr.Button("Show Account Summary")
            holdings_btn = gr.Button("Show Holdings")
            pl_btn = gr.Button("Show Profit/Loss")
            portfolio_btn = gr.Button("Show Portfolio Value")
            transactions_btn = gr.Button("Show Transactions")

        reports_output = gr.Textbox(label="Reports", interactive=False, lines=15)

        summary_btn.click(get_account_summary, inputs=[], outputs=[reports_output])
        holdings_btn.click(get_holdings_report, inputs=[], outputs=[reports_output])
        pl_btn.click(get_profit_loss_report, inputs=[], outputs=[reports_output])
        portfolio_btn.click(get_portfolio_value_report, inputs=[], outputs=[reports_output])
        transactions_btn.click(get_transactions_report, inputs=[], outputs=[reports_output])

# --- Launch the Gradio App ---
if __name__ == "__main__":
    demo.launch()
```