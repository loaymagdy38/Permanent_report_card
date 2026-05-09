from common import connect, load_abi, load_bin, save_addresses, send_tx

def main():
    w3 = connect()
    accounts = w3.eth.accounts
    admin = accounts[0]

    print("Deploying ReportCard contract...")
    Contract = w3.eth.contract(abi=load_abi(), bytecode=load_bin())
    tx_hash = Contract.constructor().transact({"from": admin, "gas": 6000000})
    receipt = send_tx(w3, tx_hash)
    report = w3.eth.contract(address=receipt.contractAddress, abi=load_abi())
    coin_address = report.functions.getCoinAddress().call()
    save_addresses(receipt.contractAddress, coin_address)

    print("ReportCard deployed at:", receipt.contractAddress)
    print("GradeCoin deployed at:", coin_address)

    samples = [
        (1, "Ahmed Ali", "Math", 88),
        (2, "Mona Hassan", "Cryptography", 92),
        (3, "Omar Samir", "Blockchain", 85),
    ]
    for item in samples:
        tx = report.functions.addOrUpdateGrade(*item).transact({"from": admin, "gas": 300000})
        send_tx(w3, tx)
    print("Added 3 sample student grades.")
    print("Saved addresses in deployed_addresses.json")

if __name__ == "__main__":
    main()
