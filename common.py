import json
from pathlib import Path
from web3 import Web3

RPC_URL = "http://127.0.0.1:7545"
BASE = Path(__file__).resolve().parent
BUILD = BASE / "build"
ADDR_FILE = BASE / "deployed_addresses.json"

GRADE_COIN_ABI = [
    {"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"}
]

def connect():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        raise RuntimeError("Ganache is not running on http://127.0.0.1:7545")
    return w3

def load_abi():
    with open(BUILD / "ReportCard_abi.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_bin():
    text = (BUILD / "ReportCard_bin.txt").read_text(encoding="utf-8").strip()
    return text if text.startswith("0x") else "0x" + text

def save_addresses(report_card, coin):
    with open(ADDR_FILE, "w", encoding="utf-8") as f:
        json.dump({"report_card": report_card, "grade_coin": coin}, f, indent=4)

def load_contracts():
    w3 = connect()
    with open(ADDR_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    report = w3.eth.contract(address=data["report_card"], abi=load_abi())
    coin = w3.eth.contract(address=data["grade_coin"], abi=GRADE_COIN_ABI)
    return w3, report, coin

def send_tx(w3, tx_hash):
    return w3.eth.wait_for_transaction_receipt(tx_hash)
