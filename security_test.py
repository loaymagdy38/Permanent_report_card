from common import load_contracts, send_tx

w3, report, coin = load_contracts()
admin = w3.eth.accounts[0]
normal_user = w3.eth.accounts[1]

print("Testing: normal user cannot add/update grades")
try:
    tx = report.functions.addOrUpdateGrade(99, "Bad User", "Math", 100).transact({"from": normal_user, "gas": 300000})
    receipt = send_tx(w3, tx)
    if receipt.status == 0:
        print("PASS: Transaction reverted for non-admin.")
    else:
        print("FAIL: Normal user was able to do admin action.")
except Exception:
    print("PASS: Normal user got an error.")
