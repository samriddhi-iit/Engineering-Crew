```python
import unittest
import datetime
from unittest.mock import patch

# Assuming accounts.py is in the same directory and importable
# If running this test file directly, ensure accounts.py is in the same directory
# or accessible via PYTHONPATH.
try:
    from accounts import Account, get_share_price
except ModuleNotFoundError:
    # Fallback for self-contained execution or if accounts.py is not directly importable
    # This part is for demonstrating the test content, not for the final output file itself.
    # In a real test_accounts.py, you'd rely on the import.
    print("Warning: 'accounts' module not found. Defining Account and get_share_price locally for test generation.")
    
    # --- Mock Share Price Function (for local fallback) ---
    def get_share_price(symbol: str) -> float:
        """
        Retrieves the current market price for a given share symbol.
        """
        mock_prices = {
            "AAPL": 150.0, "TSLA": 700.0, "GOOGL": 2500.0,
            "MSFT": 280.0, "AMZN": 3000.0
        }
        return mock_prices.get(symbol, 0.0)

    # --- Account Class (for local fallback) ---
    class Account:
        """
        Represents a user account for the trading simulation platform.
        """
        def __init__(self, account_id: str, initial_deposit: float = 0.0):
            if initial_deposit < 0:
                raise ValueError("Initial deposit cannot be negative.")
            self.account_id: str = account_id
            self._balance: float = initial_deposit
            self._initial_deposit: float = initial_deposit
            self._holdings: dict[str, int] = {}
            self._transactions: list[dict] = []

            if initial_deposit > 0:
                self._record_transaction("DEPOSIT", amount=initial_deposit, timestamp=datetime.datetime.now())

        def deposit(self, amount: float) -> None:
            if amount <= 0:
                raise ValueError("Deposit amount must be positive.")
            self._balance += amount
            self._record_transaction("DEPOSIT", amount=amount, timestamp=datetime.datetime.now())

        def withdraw(self, amount: float) -> None:
            if amount <= 0:
                raise ValueError("Withdrawal amount must be positive.")
            if self._balance < amount:
                raise ValueError("Insufficient funds for withdrawal.")
            self._balance -= amount
            self._record_transaction("WITHDRAWAL", amount=amount, timestamp=datetime.datetime.now())

        def buy_shares(self, symbol: str, quantity: int) -> None:
            if quantity <= 0:
                raise ValueError("Quantity must be positive.")
            current_price = get_share_price(symbol)
            if current_price == 0.0:
                raise ValueError(f"Could not fetch price for symbol: {symbol}")
            cost = current_price * quantity
            if self._balance < cost:
                raise ValueError(f"Insufficient funds to buy {quantity} shares of {symbol}.")
            self._balance -= cost
            self._holdings[symbol] = self._holdings.get(symbol, 0) + quantity
            self._record_transaction("BUY", symbol=symbol, quantity=quantity, price=current_price, cost=cost, timestamp=datetime.datetime.now())

        def sell_shares(self, symbol: str, quantity: int) -> None:
            if quantity <= 0:
                raise ValueError("Quantity must be positive.")
            if symbol not in self._holdings or self._holdings[symbol] < quantity:
                current_holding = self._holdings.get(symbol, 0)
                raise ValueError(f"Insufficient shares of {symbol} to sell. You have {current_holding}, but are trying to sell {quantity}.")
            current_price = get_share_price(symbol)
            if current_price == 0.0:
                raise ValueError(f"Could not fetch price for symbol: {symbol}")
            revenue = current_price * quantity
            self._balance += revenue
            self._holdings[symbol] -= quantity
            if self._holdings[symbol] == 0:
                del self._holdings[symbol]
            self._record_transaction("SELL", symbol=symbol, quantity=quantity, price=current_price, revenue=revenue, timestamp=datetime.datetime.now())

        def get_holdings(self) -> dict[str, int]:
            return self._holdings.copy()

        def get_portfolio_value(self) -> float:
            total_portfolio_value = 0.0
            for symbol, quantity in self._holdings.items():
                price = get_share_price(symbol)
                if price > 0:
                    total_portfolio_value += price * quantity
            return total_portfolio_value

        def get_total_account_value(self) -> float:
            return self._balance + self.get_portfolio_value()

        def get_profit_loss(self) -> float:
            current_total_value = self.get_total_account_value()
            return current_total_value - self._initial_deposit

        def get_transactions(self) -> list[dict]:
            return self._transactions.copy()

        def _record_transaction(self, transaction_type: str, **kwargs) -> None:
            transaction_record = {
                "type": transaction_type,
                "timestamp": kwargs.get("timestamp", datetime.datetime.now()),
                "amount": kwargs.get("amount"),
                "symbol": kwargs.get("symbol"),
                "quantity": kwargs.get("quantity"),
                "price": kwargs.get("price"),
                "cost": kwargs.get("cost"),
                "revenue": kwargs.get("revenue"),
                "balance_after": self._balance
            }
            transaction_record = {k: v for k, v in transaction_record.items() if v is not None}
            self._transactions.append(transaction_record)

        def __str__(self) -> str:
            holdings_str = ", ".join([f"{symbol}: {qty}" for symbol, qty in self._holdings.items()])
            if not holdings_str:
                holdings_str = "None"
            return (
                f"Account ID: {self.account_id}\n"
                f"Current Balance: ${self._balance:.2f}\n"
                f"Portfolio Value: ${self.get_portfolio_value():.2f}\n"
                f"Total Account Value: ${self.get_total_account_value():.2f}\n"
                f"Profit/Loss: ${self.get_profit_loss():.2f}\n"
                f"Holdings: {holdings_str}"
            )


# --- Unit Tests ---
class TestAccount(unittest.TestCase):

    def setUp(self):
        # This method is called before each test method
        # We will mock get_share_price for consistent test results
        # The target of the patch should be where the function is looked up.
        # If 'accounts' module is imported as 'from accounts import ...', the target is 'accounts.get_share_price'.
        # If 'accounts' is imported as 'import accounts', the target is 'accounts.get_share_price'.
        # If running this file stand-alone with fallback definitions, the target needs to be '__main__.get_share_price'.
        # We assume the standard import 'from accounts import ...'
        self.mock_get_share_price_patcher = patch('accounts.get_share_price')
        self.mock_get_share_price = self.mock_get_share_price_patcher.start()

        # Define mock return values for get_share_price
        self.mock_prices = {
            "AAPL": 150.0,
            "TSLA": 700.0,
            "GOOGL": 2500.0,
            "MSFT": 280.0,
            "AMZN": 3000.0
        }
        self.mock_get_share_price.side_effect = lambda symbol: self.mock_prices.get(symbol, 0.0)

    def tearDown(self):
        # This method is called after each test method
        self.mock_get_share_price_patcher.stop()

    def test_initialization_valid(self):
        account = Account("user1", 1000.0)
        self.assertEqual(account.account_id, "user1")
        self.assertEqual(account._balance, 1000.0)
        self.assertEqual(account._initial_deposit, 1000.0)
        self.assertEqual(account.get_holdings(), {})
        self.assertEqual(len(account.get_transactions()), 1)
        self.assertEqual(account.get_transactions()[0]["type"], "DEPOSIT")
        self.assertEqual(account.get_transactions()[0]["amount"], 1000.0)

    def test_initialization_zero_deposit(self):
        account = Account("user2", 0.0)
        self.assertEqual(account._balance, 0.0)
        self.assertEqual(account._initial_deposit, 0.0)
        self.assertEqual(account.get_holdings(), {})
        self.assertEqual(len(account.get_transactions()), 0)

    def test_initialization_negative_deposit(self):
        with self.assertRaisesRegex(ValueError, "Initial deposit cannot be negative."):
            Account("user3", -500.0)

    def test_deposit_valid(self):
        account = Account("user4", 500.0)
        account.deposit(200.0)
        self.assertEqual(account._balance, 700.0)
        self.assertEqual(len(account.get_transactions()), 2)
        self.assertEqual(account.get_transactions()[1]["type"], "DEPOSIT")
        self.assertEqual(account.get_transactions()[1]["amount"], 200.0)
        self.assertEqual(account.get_transactions()[1]["balance_after"], 700.0)

    def test_deposit_non_positive(self):
        account = Account("user5", 500.0)
        with self.assertRaisesRegex(ValueError, "Deposit amount must be positive."):
            account.deposit(0.0)
        with self.assertRaisesRegex(ValueError, "Deposit amount must be positive."):
            account.deposit(-100.0)
        self.assertEqual(account._balance, 500.0) # Balance should not change

    def test_withdraw_valid(self):
        account = Account("user6", 1000.0)
        account.withdraw(300.0)
        self.assertEqual(account._balance, 700.0)
        self.assertEqual(len(account.get_transactions()), 2)
        self.assertEqual(account.get_transactions()[1]["type"], "WITHDRAWAL")
        self.assertEqual(account.get_transactions()[1]["amount"], 300.0)
        self.assertEqual(account.get_transactions()[1]["balance_after"], 700.0)

    def test_withdraw_insufficient_funds(self):
        account = Account("user7", 500.0)
        with self.assertRaisesRegex(ValueError, "Insufficient funds for withdrawal."):
            account.withdraw(600.0)
        self.assertEqual(account._balance, 500.0) # Balance should not change

    def test_withdraw_non_positive(self):
        account = Account("user8", 500.0)
        with self.assertRaisesRegex(ValueError, "Withdrawal amount must be positive."):
            account.withdraw(0.0)
        with self.assertRaisesRegex(ValueError, "Withdrawal amount must be positive."):
            account.withdraw(-100.0)
        self.assertEqual(account._balance, 500.0) # Balance should not change

    def test_buy_shares_valid(self):
        account = Account("user9", 10000.0)
        account.buy_shares("AAPL", 10) # Cost: 10 * 150.0 = 1500.0
        self.assertEqual(account._balance, 8500.0)
        self.assertEqual(account.get_holdings(), {"AAPL": 10})
        self.assertEqual(len(account.get_transactions()), 2)
        buy_tx = account.get_transactions()[1]
        self.assertEqual(buy_tx["type"], "BUY")
        self.assertEqual(buy_tx["symbol"], "AAPL")
        self.assertEqual(buy_tx["quantity"], 10)
        self.assertEqual(buy_tx["price"], 150.0)
        self.assertEqual(buy_tx["cost"], 1500.0)
        self.assertEqual(buy_tx["balance_after"], 8500.0)

    def test_buy_shares_multiple_holdings(self):
        account = Account("user10", 20000.0)
        account.buy_shares("AAPL", 10) # Cost: 1500.0
        account.buy_shares("TSLA", 5)  # Cost: 5 * 700.0 = 3500.0
        self.assertEqual(account._balance, 20000.0 - 1500.0 - 3500.0)
        self.assertEqual(account.get_holdings(), {"AAPL": 10, "TSLA": 5})

    def test_buy_shares_add_to_existing_holding(self):
        account = Account("user11", 10000.0)
        account.buy_shares("AAPL", 5) # Cost: 750.0
        account.buy_shares("AAPL", 10) # Cost: 1500.0
        self.assertEqual(account._balance, 10000.0 - 750.0 - 1500.0)
        self.assertEqual(account.get_holdings(), {"AAPL": 15})

    def test_buy_shares_insufficient_funds(self):
        account = Account("user12", 1000.0)
        with self.assertRaisesRegex(ValueError, "Insufficient funds to buy.*"):\n            account.buy_shares("TSLA", 2) # Cost: 2 * 700.0 = 1400.0
        self.assertEqual(account._balance, 1000.0) # Balance should not change
        self.assertEqual(account.get_holdings(), {})

    def test_buy_shares_invalid_quantity(self):
        account = Account("user13", 10000.0)
        with self.assertRaisesRegex(ValueError, "Quantity must be positive."):
            account.buy_shares("AAPL", 0)
        with self.assertRaisesRegex(ValueError, "Quantity must be positive."):
            account.buy_shares("AAPL", -5)
        self.assertEqual(account._balance, 10000.0)
        self.assertEqual(account.get_holdings(), {})

    def test_buy_shares_unknown_symbol(self):
        account = Account("user14", 10000.0)
        # Mock get_share_price to return 0.0 for "UNKNOWN"
        self.mock_get_share_price.side_effect = lambda symbol: self.mock_prices.get(symbol, 0.0)
        with self.assertRaisesRegex(ValueError, "Could not fetch price for symbol: UNKNOWN"):\n            account.buy_shares("UNKNOWN", 10)
        self.assertEqual(account._balance, 10000.0)
        self.assertEqual(account.get_holdings(), {})

    def test_sell_shares_valid(self):
        account = Account("user15", 10000.0)
        account.buy_shares("AAPL", 10) # Cost: 1500.0, Balance: 8500.0, Holdings: {"AAPL": 10}
        account.sell_shares("AAPL", 5)  # Revenue: 5 * 150.0 = 750.0
        self.assertEqual(account._balance, 8500.0 + 750.0)
        self.assertEqual(account.get_holdings(), {"AAPL": 5})
        self.assertEqual(len(account.get_transactions()), 3)
        sell_tx = account.get_transactions()[2]
        self.assertEqual(sell_tx["type"], "SELL")
        self.assertEqual(sell_tx["symbol"], "AAPL")
        self.assertEqual(sell_tx["quantity"], 5)
        self.assertEqual(sell_tx["price"], 150.0)
        self.assertEqual(sell_tx["revenue"], 750.0)
        self.assertEqual(sell_tx["balance_after"], 8500.0 + 750.0)

    def test_sell_shares_all(self):
        account = Account("user16", 10000.0)
        account.buy_shares("TSLA", 2) # Cost: 1400.0, Balance: 8600.0, Holdings: {"TSLA": 2}
        account.sell_shares("TSLA", 2) # Revenue: 2 * 700.0 = 1400.0
        self.assertEqual(account._balance, 8600.0 + 1400.0)
        self.assertEqual(account.get_holdings(), {})

    def test_sell_shares_insufficient_quantity(self):
        account = Account("user17", 10000.0)
        account.buy_shares("AAPL", 5) # Holdings: {"AAPL": 5}
        with self.assertRaisesRegex(ValueError, "Insufficient shares of AAPL to sell.*"):\n            account.sell_shares("AAPL", 10)
        self.assertEqual(account._balance, 10000.0 - (5 * 150.0))
        self.assertEqual(account.get_holdings(), {"AAPL": 5})

    def test_sell_shares_not_held(self):
        account = Account("user18", 10000.0)
        with self.assertRaisesRegex(ValueError, "Insufficient shares of GOOGL to sell.*"):\n            account.sell_shares("GOOGL", 1)
        self.assertEqual(account._balance, 10000.0)
        self.assertEqual(account.get_holdings(), {})

    def test_sell_shares_invalid_quantity(self):
        account = Account("user19", 10000.0)
        account.buy_shares("AAPL", 5)
        with self.assertRaisesRegex(ValueError, "Quantity must be positive."):\n            account.sell_shares("AAPL", 0)
        with self.assertRaisesRegex(ValueError, "Quantity must be positive."):\n            account.sell_shares("AAPL", -2)
        self.assertEqual(account.get_holdings(), {"AAPL": 5})

    def test_sell_shares_unknown_symbol(self):
        account = Account("user20", 10000.0)
        account.buy_shares("AAPL", 5)
        # Mock get_share_price to return 0.0 for "UNKNOWN"
        self.mock_get_share_price.side_effect = lambda symbol: self.mock_prices.get(symbol, 0.0)
        with self.assertRaisesRegex(ValueError, "Could not fetch price for symbol: UNKNOWN"):\n            account.sell_shares("UNKNOWN", 1)
        self.assertEqual(account.get_holdings(), {"AAPL": 5})

    def test_get_holdings(self):
        account = Account("user21", 10000.0)
        account.buy_shares("AAPL", 10)
        account.buy_shares("TSLA", 2)
        holdings = account.get_holdings()
        self.assertEqual(holdings, {"AAPL": 10, "TSLA": 2})
        # Ensure it returns a copy
        holdings["AAPL"] = 999
        self.assertEqual(account.get_holdings(), {"AAPL": 10, "TSLA": 2})

    def test_get_portfolio_value(self):
        account = Account("user22", 10000.0)
        account.buy_shares("AAPL", 10) # Value: 10 * 150.0 = 1500.0
        account.buy_shares("TSLA", 2)  # Value: 2 * 700.0 = 1400.0
        # Total portfolio value = 1500.0 + 1400.0 = 2900.0
        self.assertEqual(account.get_portfolio_value(), 2900.0)

    def test_get_portfolio_value_with_zero_price_symbol(self):
        account = Account("user23", 10000.0)
        account.buy_shares("AAPL", 10)
        # Add a holding for a symbol not in mock_prices (get_share_price returns 0.0)
        account._holdings["XYZ"] = 5
        self.assertEqual(account.get_portfolio_value(), 1500.0) # Only AAPL should count

    def test_get_total_account_value(self):
        account = Account("user24", 5000.0)
        account.buy_shares("AAPL", 10) # Cost: 1500.0, Balance: 3500.0, Portfolio: 1500.0
        # Total Account Value = Balance + Portfolio Value = 3500.0 + 1500.0 = 5000.0
        self.assertEqual(account.get_total_account_value(), 5000.0)

        account.deposit(1000.0) # Balance: 4500.0
        # Total Account Value = 4500.0 + 1500.0 = 6000.0
        self.assertEqual(account.get_total_account_value(), 6000.0)

    def test_get_profit_loss_positive(self):
        account = Account("user25", 10000.0)
        account.buy_shares("AAPL", 10) # Cost: 1500.0, Balance: 8500.0, Portfolio: 1500.0
        # Total value = 8500.0 + 1500.0 = 10000.0
        # P/L = 10000.0 - 10000.0 = 0.0
        self.assertEqual(account.get_profit_loss(), 0.0)

        account.sell_shares("AAPL", 5) # Revenue: 750.0, Balance: 8500.0 + 750.0 = 9250.0
        # Holdings: {"AAPL": 5}, Portfolio: 5 * 150.0 = 750.0
        # Total value = 9250.0 + 750.0 = 10000.0
        # P/L = 10000.0 - 10000.0 = 0.0
        self.assertEqual(account.get_profit_loss(), 0.0)

        # Let's simulate a price change to test P/L more effectively
        # Temporarily change mock price for AAPL to 200 for calculation
        original_aapl_price = self.mock_prices.get("AAPL")
        self.mock_prices["AAPL"] = 200.0
        # Account state: Balance: 9250.0, Holdings: {"AAPL": 5}
        # New portfolio value: 5 * 200.0 = 1000.0
        # New total value = 9250.0 + 1000.0 = 10250.0
        # P/L = 10250.0 - 10000.0 = 250.0
        self.assertEqual(account.get_profit_loss(), 250.0)
        self.mock_prices["AAPL"] = original_aapl_price # Restore price

    def test_get_profit_loss_negative(self):
        account = Account("user26", 10000.0)
        # Buy shares with a price that will likely drop for P/L calculation
        account.buy_shares("TSLA", 2) # Cost: 1400.0, Balance: 8600.0, Holdings: {"TSLA": 2}, Portfolio: 1400.0
        # Total value = 8600.0 + 1400.0 = 10000.0
        # P/L = 10000.0 - 10000.0 = 0.0
        self.assertEqual(account.get_profit_loss(), 0.0)

        # Temporarily change mock price for TSLA to 500 for calculation
        original_tsla_price = self.mock_prices.get("TSLA")
        self.mock_prices["TSLA"] = 500.0
        # Account state: Balance: 8600.0, Holdings: {"TSLA": 2}
        # New portfolio value: 2 * 500.0 = 1000.0
        # New total value = 8600.0 + 1000.0 = 9600.0
        # P/L = 9600.0 - 10000.0 = -400.0
        self.assertEqual(account.get_profit_loss(), -400.0)
        self.mock_prices["TSLA"] = original_tsla_price # Restore price

    def test_get_transactions(self):
        account = Account("user27", 1000.0)
        account.deposit(500.0)
        account.buy_shares("AAPL", 5)
        transactions = account.get_transactions()
        self.assertEqual(len(transactions), 3)
        self.assertEqual(transactions[0]["type"], "DEPOSIT")
        self.assertEqual(transactions[0]["amount"], 1000.0)
        self.assertEqual(transactions[1]["type"], "DEPOSIT")
        self.assertEqual(transactions[1]["amount"], 500.0)
        self.assertEqual(transactions[2]["type"], "BUY")
        self.assertEqual(transactions[2]["symbol"], "AAPL")
        # Ensure it returns a copy
        transactions.append({"type": "MALICIOUS"})
        self.assertEqual(len(account.get_transactions()), 3)

    def test_str_representation(self):
        account = Account("user28", 10000.0)
        account.buy_shares("AAPL", 10)
        account.buy_shares("TSLA", 2)
        account.withdraw(1000.0)
        # Expected string format needs to be checked carefully
        # Bal: 10000 - 1500 - 1400 - 1000 = 6100
        # Port: 10*150 + 2*700 = 1500 + 1400 = 2900
        # Total: 6100 + 2900 = 9000
        # P/L: 9000 - 10000 = -1000
        expected_str_part_1 = "Account ID: user28"
        expected_str_part_2 = "Current Balance: $6100.00"
        expected_str_part_3 = "Portfolio Value: $2900.00"
        expected_str_part_4 = "Total Account Value: $9000.00"
        expected_str_part_5 = "Profit/Loss: $-1000.00"
        expected_str_part_6 = "Holdings: AAPL: 10, TSLA: 2"

        account_str = str(account)

        self.assertIn(expected_str_part_1, account_str)
        self.assertIn(expected_str_part_2, account_str)
        self.assertIn(expected_str_part_3, account_str)
        self.assertIn(expected_str_part_4, account_str)
        self.assertIn(expected_str_part_5, account_str)
        self.assertIn(expected_str_part_6, account_str)

    def test_str_representation_no_holdings(self):
        account = Account("user29", 5000.0)
        expected_str_part_1 = "Account ID: user29"
        expected_str_part_2 = "Current Balance: $5000.00"
        expected_str_part_3 = "Portfolio Value: $0.00"
        expected_str_part_4 = "Total Account Value: $5000.00"
        expected_str_part_5 = "Profit/Loss: $0.00"
        expected_str_part_6 = "Holdings: None"

        account_str = str(account)

        self.assertIn(expected_str_part_1, account_str)
        self.assertIn(expected_str_part_2, account_str)
        self.assertIn(expected_str_part_3, account_str)
        self.assertIn(expected_str_part_4, account_str)
        self.assertIn(expected_str_part_5, account_str)
        self.assertIn(expected_str_part_6, account_str)

if __name__ == '__main__':
    unittest.main()
```