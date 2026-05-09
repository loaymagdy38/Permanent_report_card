import csv
from common import load_contracts

w3, report, coin = load_contracts()
accounts = set(w3.eth.accounts)
for b in range(w3.eth.block_number + 1):
    block = w3.eth.get_block(b, full_transactions=True)
    for tx in block.transactions:
        accounts.add(tx["from"])
        if tx["to"]:
            accounts.add(tx["to"])

with open("balance_snapshot.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Account Address", "Grade Coin Balance", "ETH Balance"])
    for addr in sorted(accounts):
        coin_balance = coin.functions.balanceOf(addr).call()
        eth_balance = w3.from_wei(w3.eth.get_balance(addr), "ether")
        writer.writerow([addr, coin_balance, eth_balance])
print("Saved balance_snapshot.csv")
