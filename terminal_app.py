from common import load_contracts, send_tx

ADMIN_PASSWORD = "admin123"

def clean_error(error):
    text = str(error)

    known_messages = [
        "Already registered",
        "Only admin allowed",
        "System is paused",
        "Student not found",
        "Grade must be 0 to 100",
        "Student name required",
        "Subject required",
        "Array length mismatch",
        "Bad address",
        "Amount must be positive",
        "Not enough coins",
    ]

    for msg in known_messages:
        if msg in text:
            return msg

    if "revert" in text:
        return "Transaction reverted"

    return "Something went wrong"

def choose_account(w3):
    print("Available accounts:")
    for i, acc in enumerate(w3.eth.accounts):
        print(f"{i}: {acc}")
    idx = int(input("Choose account index: "))
    return w3.eth.accounts[idx]

def show_header(report, account):
    try:
        name = report.functions.users(account).call()
    except Exception:
        name = ""

    admin = report.functions.getAdmin().call()

    print("\n===== Permanent Report Card =====")
    print("Current account:", account)
    print("Registered name:", name if name else "Not registered")
    print("Admin:", admin)

    if account.lower() == admin.lower():
        print("Role: Admin")
    else:
        print("Role: Normal User")

    print("=================================\n")

def view_grade(report):
    sid = int(input("Student ID: "))
    try:
        name, subject, grade = report.functions.getGrade(sid).call()
        print(f"Student: {name} | Subject: {subject} | Grade: {grade}")
    except Exception as e:
        print("Could not find grade:", clean_error(e))

def balance_checker(w3, coin):
    addr = input("Address: ").strip()
    try:
        coins = coin.functions.balanceOf(addr).call()
        eth = w3.from_wei(w3.eth.get_balance(addr), "ether")
        print("\nAddress                                 Grade Coin      ETH")
        print("-" * 70)
        print(f"{addr}   {coins:<15} {eth}")
    except Exception:
        print("Invalid address")

def method_selector(w3, signature):
    h = w3.keccak(text=signature).hex()
    if h.startswith("0x"):
        return h[:10]
    return "0x" + h[:8]

def build_method_map(w3, report):
    labels = {
        "registerUser": "register user",
        "addOrUpdateGrade": "add/update grade",
        "batchAddOrUpdateGrades": "batch grades",
        "mintGradeCoin": "mint coin",
        "pause": "pause system",
        "resume": "resume system",
        "transferOwnership": "transfer ownership",
    }

    method_map = {}

    for item in report.abi:
        if item.get("type") != "function":
            continue

        name = item.get("name")
        if name not in labels:
            continue

        types = []
        for inp in item.get("inputs", []):
            types.append(inp["type"])

        signature = name + "(" + ",".join(types) + ")"
        selector = method_selector(w3, signature)
        method_map[selector] = labels[name]

    return method_map

def get_action_name(tx_input, method_map):
    if tx_input in ("0x", b""):
        return "ETH transfer"

    if isinstance(tx_input, bytes):
        tx_input = "0x" + tx_input.hex()

    method_id = tx_input[:10]
    return method_map.get(method_id, "contract action")

def activity_history(w3, report, address):
    address = address.lower()
    method_map = build_method_map(w3, report)

    print("\nBlock     Action                 Value")
    print("-" * 55)

    found = False

    for b in range(w3.eth.block_number + 1):
        block = w3.eth.get_block(b, full_transactions=True)

        for tx in block.transactions:
            frm = tx["from"].lower()
            to = tx["to"].lower() if tx["to"] else "contract creation"

            if frm == address or to == address:
                found = True
                action = get_action_name(tx["input"], method_map)
                value = w3.from_wei(tx["value"], "ether")
                print(f"{b:<9} {action:<22} {value} ETH")

    if not found:
        print("No activity found.")

def admin_menu(w3, report, account):
    admin = report.functions.getAdmin().call()

    if account.lower() != admin.lower():
        print("Access denied: only the Admin wallet can open this menu.")
        return

    password = input("Admin password: ")
    if password != ADMIN_PASSWORD:
        print("Wrong password")
        return

    while True:
        print("\n--- Admin Menu ---")
        print("1. Add/update grade")
        print("2. Batch add/update grades")
        print("3. Mint Grade Coin")
        print("4. Pause")
        print("5. Resume")
        print("6. Transfer ownership")
        print("0. Back")

        choice = input("Choice: ")

        try:
            if choice == "1":
                sid = int(input("Student ID: "))
                name = input("Student name: ")
                subject = input("Subject: ")
                grade = int(input("Grade 0-100: "))

                tx = report.functions.addOrUpdateGrade(
                    sid, name, subject, grade
                ).transact({"from": account, "gas": 300000})

                send_tx(w3, tx)
                print("Grade saved.")

            elif choice == "2":
                n = int(input("How many students? "))

                ids = []
                names = []
                subjects = []
                grades = []

                for _ in range(n):
                    ids.append(int(input("ID: ")))
                    names.append(input("Name: "))
                    subjects.append(input("Subject: "))
                    grades.append(int(input("Grade: ")))

                tx = report.functions.batchAddOrUpdateGrades(
                    ids, names, subjects, grades
                ).transact({"from": account, "gas": 800000})

                send_tx(w3, tx)
                print("Batch saved.")

            elif choice == "3":
                to = input("Send coins to address: ").strip()
                amount = int(input("Amount: "))

                tx = report.functions.mintGradeCoin(
                    to, amount
                ).transact({"from": account, "gas": 300000})

                send_tx(w3, tx)
                print("Coins minted.")

            elif choice == "4":
                tx = report.functions.pause().transact({"from": account, "gas": 100000})
                send_tx(w3, tx)
                print("System paused.")

            elif choice == "5":
                tx = report.functions.resume().transact({"from": account, "gas": 100000})
                send_tx(w3, tx)
                print("System resumed.")

            elif choice == "6":
                new_admin = input("New admin address: ").strip()

                tx = report.functions.transferOwnership(
                    new_admin
                ).transact({"from": account, "gas": 150000})

                send_tx(w3, tx)
                print("Ownership transferred.")

            elif choice == "0":
                return

            else:
                print("Invalid choice")

        except Exception as e:
            print("Transaction failed:", clean_error(e))

def main():
    w3, report, coin = load_contracts()
    account = choose_account(w3)

    while True:
        show_header(report, account)

        print("1. Register user")
        print("2. View grade")
        print("3. Check coin and ETH balance")
        print("4. Personal activity history")
        print("9. Hidden admin menu")
        print("0. Exit")

        choice = input("Choice: ")

        if choice == "1":
            name = input("Your display name: ")

            try:
                tx = report.functions.registerUser(name).transact({"from": account, "gas": 200000})
                send_tx(w3, tx)
                print("Registered.")
            except Exception as e:
                print("Failed:", clean_error(e))

        elif choice == "2":
            view_grade(report)

        elif choice == "3":
            balance_checker(w3, coin)

        elif choice == "4":
            addr = input("Address: ").strip()
            activity_history(w3, report, addr)

        elif choice == "9":
            admin_menu(w3, report, account)

        elif choice == "0":
            break

        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
