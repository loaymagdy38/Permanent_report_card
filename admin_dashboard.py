from collections import Counter
from common import load_contracts

w3, report, coin = load_contracts()
counts = Counter()
for b in range(w3.eth.block_number + 1):
    block = w3.eth.get_block(b, full_transactions=True)
    for tx in block.transactions:
        counts[tx["from"]] += 1

print("===== Admin Dashboard =====")
print("Total student grades:", report.functions.studentCount().call())
print("Total Grade Coin minted:", coin.functions.totalSupply().call())
print("Total blocks:", w3.eth.block_number)
print("Total transactions scanned:", sum(counts.values()))
print("Top 3 active users:")
for addr, total in counts.most_common(3):
    print(addr, "=>", total, "transactions")
