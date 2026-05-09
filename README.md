
# Permanent Report Card DApp

A blockchain-based report card system that stores student grades on a local Ethereum blockchain using Ganache. The project separates users into two roles:

- **Admin**: can manage grades, mint Grade Coin, pause/resume the system, and transfer ownership.
- **Normal User**: can register, view grades, check balances, and view activity history.

This project uses:

- Solidity Smart Contracts
- Ganache local blockchain
- Python
- web3.py
- Terminal App
- Bonus GUI App

---

## Project Idea

**Permanent Report Card**

The goal is to create a digital report card where student grade actions are recorded on the blockchain. The current grade can be updated by the Admin, but every update transaction remains recorded in blockchain history.

---

## Main Features

### Admin Features

- Add or update a student grade.
- Add or update multiple grades in one batch.
- Mint Grade Coin to any wallet address.
- Pause the system.
- Resume the system.
- Transfer admin ownership to another wallet.
- View dashboard summary.

### Normal User Features

- Register a display name once.
- View student grades by ID.
- Check Grade Coin and ETH balances.
- View personal activity history.

### System Features

- Security test for admin-only functions.
- Live alert system for `GradeChanged` events.
- Data history report showing class average.
- CSV balance snapshot exporter.
- README documentation.
- Bonus GUI app.

---

## Requirements

- Ganache running on:

```text
http://127.0.0.1:7545
```

- Python 3
- web3.py

Install dependency:

```bash
pip install web3
```

If you are using Anaconda:

```bash
conda activate crypto311
pip install web3
```

---

## Important Files

| File | Purpose |
|---|---|
| `contracts/ReportCard.sol` | Solidity smart contract and Grade Coin |
| `build/ReportCard_abi.json` | Contract ABI from Remix |
| `build/ReportCard_bin.txt` | Contract bytecode from Remix |
| `setup.py` | Deploys the contract and inserts sample grades |
| `common.py` | Shared helper functions for web3 connection and contract loading |
| `terminal_app.py` | Main terminal app |
| `gui_app.py` | Bonus graphical interface |
| `security_test.py` | Tests that normal users cannot perform admin actions |
| `admin_dashboard.py` | Prints admin summary from blockchain data |
| `data_history_report.py` | Prints stored grades and class average |
| `balance_snapshot_exporter.py` | Exports Grade Coin and ETH balances to CSV |
| `live_alert.py` | Watches only `GradeChanged` events and prints live alerts |
| `ownership_transfer_test.py` | Tests ownership transfer logic |
| `transaction_sender.py` | Sends a sample user transaction |

---

## How to Start From Zero

1. Open **Ganache**.
2. Press **Quickstart**.
3. Make sure the RPC server is:

```text
http://127.0.0.1:7545
```

4. Open **Anaconda Prompt** or PowerShell.
5. Go to the project folder:

```bash
cd "C:\Users\LOL\Desktop\project crypto\permanent_report_card_full"
```

6. Activate the environment:

```bash
conda activate crypto311
```

7. Deploy the smart contract:

```bash
python setup.py
```

Expected output:

```text
Deploying ReportCard contract...
ReportCard deployed at: 0x...
GradeCoin deployed at: 0x...
Added 3 sample student grades.
Saved addresses in deployed_addresses.json
```

---

## Run the Terminal App

```bash
python terminal_app.py
```

Choose an account index.

Usually:

```text
0
```

is the Admin after running `setup.py`.

Admin password:

```text
admin123
```

---

## Run the Bonus GUI App

```bash
python gui_app.py
```

The GUI includes:

- Account selector
- Role display
- Register user
- View grade
- Check balances
- Activity history
- Admin actions
- Live GradeChanged event watcher

---

## Run the Live Alert System

Open a second terminal:

```bash
conda activate crypto311
cd "C:\Users\LOL\Desktop\project crypto\permanent_report_card_full"
python live_alert.py
```

Then use the terminal app or GUI to add/update a grade.

Expected output:

```text
ALERT: A grade change just happened! ID=..., Name=..., Subject=..., Grade=...
```

The alert script watches the real `GradeChanged` event only.

---

## Run Testing Scripts

After `setup.py`, run:

```bash
python security_test.py
python admin_dashboard.py
python data_history_report.py
python balance_snapshot_exporter.py
```

Run ownership transfer test last because it changes the Admin:

```bash
python ownership_transfer_test.py
```

If ownership changes and you want account `0` to become Admin again, either transfer ownership back or run:

```bash
python setup.py
```

---

## Testing Checklist

- [ ] Ganache is running.
- [ ] `python setup.py` deploys successfully.
- [ ] Account `0` appears as Admin.
- [ ] User can register once.
- [ ] Duplicate registration fails with `Already registered`.
- [ ] Admin can add/update grade.
- [ ] Normal user cannot add/update grade.
- [ ] Batch add/update works.
- [ ] Mint Grade Coin works.
- [ ] Coin and ETH balance checker works.
- [ ] Activity history shows actions.
- [ ] Pause blocks user-facing actions.
- [ ] Resume allows actions again.
- [ ] Live alert prints only on grade changes.
- [ ] CSV snapshot is created.
- [ ] Ownership transfer test passes.

---

## Key Concepts for Discussion

### Blockchain

A blockchain is a distributed ledger where transactions are recorded in blocks. In this project, Ganache provides a local Ethereum blockchain.

### Smart Contract

A smart contract is code deployed on the blockchain. It stores grades, users, admin rights, and Grade Coin logic.

### ETH

ETH is the native currency of Ethereum. In Ganache, accounts receive fake ETH for testing.

### Gas

Gas is the execution fee for transactions. Even if `Value = 0 ETH`, the sender still pays a small gas fee.

### Grade Coin

Grade Coin is the custom token for this project. It is different from ETH. ETH is used for gas, while Grade Coin is a project-specific token.

### ABI

The ABI is the interface that lets Python call Solidity functions.

### Bytecode

Bytecode is the compiled contract code deployed to the blockchain.

### onlyOwner

`onlyOwner` is the access control modifier that blocks normal users from admin functions.

### Events

Events record important actions like grade changes. `live_alert.py` listens for the `GradeChanged` event.

---

## Strong Defense Answer

If asked whether grades are truly permanent:

> The current grade state can be updated by the Admin, but every update transaction is permanently recorded in the blockchain history, so grade changes can be tracked.

---

## Project Status

The project satisfies the required core tasks:

- Core smart contract
- Custom Grade Coin
- Setup script
- Access control
- Admin dashboard
- Batch operations
- Transaction sender
- Terminal app
- User registration
- Activity history
- Balance checker
- Security test
- Live alert
- Data report
- Documentation
- CSV exporter
- Pause/resume
- Ownership transfer
- Bonus GUI
