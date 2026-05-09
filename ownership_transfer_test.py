from common import load_contracts, send_tx

w3, report, coin = load_contracts()
old_admin = report.functions.getAdmin().call()
new_admin = w3.eth.accounts[1]
print("Old admin:", old_admin)
print("New admin:", new_admin)

print("Step 1: old admin does admin action")
tx = report.functions.addOrUpdateGrade(50, "Before Transfer", "Math", 70).transact({"from": old_admin, "gas": 300000})
print("Status:", send_tx(w3, tx).status)

print("Step 2: transfer ownership")
tx = report.functions.transferOwnership(new_admin).transact({"from": old_admin, "gas": 200000})
print("Status:", send_tx(w3, tx).status)

print("Step 3: old admin should fail")
tx = report.functions.addOrUpdateGrade(51, "Old Admin", "Math", 70).transact({"from": old_admin, "gas": 300000})
receipt = send_tx(w3, tx)
print("PASS" if receipt.status == 0 else "FAIL")

print("Step 4: new admin should succeed")
tx = report.functions.addOrUpdateGrade(52, "New Admin", "Math", 95).transact({"from": new_admin, "gas": 300000})
receipt = send_tx(w3, tx)
print("PASS" if receipt.status == 1 else "FAIL")
