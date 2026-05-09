from common import load_contracts, send_tx

w3, report, coin = load_contracts()
account = w3.eth.accounts[1]
print("Sending a sample user registration transaction from:", account)
try:
    tx = report.functions.registerUser("Test User").transact({"from": account, "gas": 200000})
    receipt = send_tx(w3, tx)
    print("Transaction status:", receipt.status)
except Exception as e:
    print("Transaction failed safely:", e)
