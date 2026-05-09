import csv
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from common import load_contracts, send_tx

ADMIN_PASSWORD = "admin123"

COLORS = {
    "bg": "#0f172a",
    "panel": "#111c33",
    "panel2": "#16213b",
    "card": "#1e293b",
    "line": "#334155",
    "text": "#e5e7eb",
    "muted": "#94a3b8",
    "blue": "#38bdf8",
    "green": "#22c55e",
    "purple": "#a855f7",
    "orange": "#fb923c",
    "red": "#ef4444",
    "button": "#2563eb",
    "button_hover": "#1d4ed8",
}


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


class ModernButton(tk.Button):
    def __init__(self, parent, text, command=None, bg=None, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=bg or COLORS["button"],
            fg="white",
            activebackground=COLORS["button_hover"],
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            **kwargs,
        )


class ReportCardGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Permanent Report Card DApp")
        self.root.geometry("1200x760")
        self.root.minsize(1050, 680)
        self.root.configure(bg=COLORS["bg"])

        try:
            self.w3, self.report, self.coin = load_contracts()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            raise

        self.account = tk.StringVar()
        self.status = tk.StringVar(value="Connected to Ganache")
        self.live_alert_running = False
        self.last_block = self.w3.eth.block_number

        self.setup_style()
        self.build_ui()
        self.load_accounts()
        self.refresh_header()
        self.dashboard()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TCombobox",
            fieldbackground=COLORS["panel2"],
            background=COLORS["panel2"],
            foreground=COLORS["text"],
            arrowcolor=COLORS["blue"],
            bordercolor=COLORS["line"],
        )

        style.configure(
            "Treeview",
            background=COLORS["panel"],
            foreground=COLORS["text"],
            fieldbackground=COLORS["panel"],
            rowheight=28,
            borderwidth=0,
            font=("Segoe UI", 10),
        )

        style.configure(
            "Treeview.Heading",
            background=COLORS["card"],
            foreground=COLORS["blue"],
            font=("Segoe UI", 10, "bold"),
        )

        style.map("Treeview", background=[("selected", COLORS["button"])])

    def build_ui(self):
        self.sidebar = tk.Frame(self.root, bg=COLORS["panel"], width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main = tk.Frame(self.root, bg=COLORS["bg"])
        self.main.pack(side="right", fill="both", expand=True)

        self.build_sidebar()
        self.build_topbar()
        self.build_content()

    def build_sidebar(self):
        logo = tk.Label(
            self.sidebar,
            text="🎓\nReport Card",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 20, "bold"),
            justify="center",
        )
        logo.pack(pady=(25, 20))

        subtitle = tk.Label(
            self.sidebar,
            text="Blockchain Grade System",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 10),
        )
        subtitle.pack(pady=(0, 20))

        self.nav_frame = tk.Frame(self.sidebar, bg=COLORS["panel"])
        self.nav_frame.pack(fill="x", padx=14)

        nav_items = [
            ("🏠 Dashboard", self.dashboard),
            ("👤 Register User", self.show_register),
            ("📘 View Grade", self.show_view_grade),
            ("💰 Check Balance", self.show_balance),
            ("🕘 Activity History", self.show_activity),
            ("🛠 Admin Actions", self.show_admin),
            ("📊 Reports", self.show_reports),
            ("🚨 Live Alert", self.start_live_alert),
        ]

        for text, cmd in nav_items:
            btn = tk.Button(
                self.nav_frame,
                text=text,
                command=cmd,
                anchor="w",
                bg=COLORS["panel"],
                fg=COLORS["text"],
                activebackground=COLORS["panel2"],
                activeforeground=COLORS["blue"],
                relief="flat",
                bd=0,
                padx=12,
                pady=11,
                cursor="hand2",
                font=("Segoe UI", 11),
            )
            btn.pack(fill="x", pady=2)

        bottom = tk.Frame(self.sidebar, bg=COLORS["panel"])
        bottom.pack(side="bottom", fill="x", padx=14, pady=18)

        self.connection_label = tk.Label(
            bottom,
            text="● Connected to Ganache",
            bg=COLORS["panel"],
            fg=COLORS["green"],
            font=("Segoe UI", 10, "bold"),
        )
        self.connection_label.pack(anchor="w")

    def build_topbar(self):
        top = tk.Frame(self.main, bg=COLORS["bg"])
        top.pack(fill="x", padx=24, pady=(20, 12))

        left = tk.Frame(top, bg=COLORS["bg"])
        left.pack(side="left")

        tk.Label(
            left,
            text="Permanent Report Card",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            font=("Segoe UI", 24, "bold"),
        ).pack(anchor="w")

        tk.Label(
            left,
            text="Blockchain-powered student grade management system",
            bg=COLORS["bg"],
            fg=COLORS["muted"],
            font=("Segoe UI", 11),
        ).pack(anchor="w")

        right = tk.Frame(top, bg=COLORS["bg"])
        right.pack(side="right")

        tk.Label(
            right,
            text="Account",
            bg=COLORS["bg"],
            fg=COLORS["muted"],
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")

        row = tk.Frame(right, bg=COLORS["bg"])
        row.pack()

        self.account_combo = ttk.Combobox(row, textvariable=self.account, width=62, state="readonly")
        self.account_combo.pack(side="left", ipady=4)
        self.account_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_header())

        ModernButton(row, "Refresh", self.refresh_all, bg=COLORS["purple"]).pack(side="left", padx=(8, 0))

        self.header = tk.Label(
            self.main,
            text="",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            padx=16,
            pady=10,
            anchor="w",
            justify="left",
            font=("Segoe UI", 10),
        )
        self.header.pack(fill="x", padx=24, pady=(0, 14))

    def build_content(self):
        self.content = tk.Frame(self.main, bg=COLORS["bg"])
        self.content.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        self.output_panel = tk.Frame(self.main, bg=COLORS["panel"], highlightbackground=COLORS["line"], highlightthickness=1)
        self.output_panel.pack(fill="x", padx=24, pady=(0, 16))

        out_header = tk.Frame(self.output_panel, bg=COLORS["panel"])
        out_header.pack(fill="x", padx=12, pady=(10, 0))

        tk.Label(
            out_header,
            text="System Output",
            bg=COLORS["panel"],
            fg=COLORS["blue"],
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")

        ModernButton(out_header, "Clear", self.clear_output, bg=COLORS["red"]).pack(side="right")

        self.output = tk.Text(
            self.output_panel,
            height=8,
            bg="#020617",
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            bd=0,
            padx=12,
            pady=10,
            font=("Consolas", 10),
        )
        self.output.pack(fill="x", padx=12, pady=12)

        self.status_bar = tk.Label(
            self.main,
            textvariable=self.status,
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            anchor="w",
            padx=14,
            pady=6,
            font=("Segoe UI", 9),
        )
        self.status_bar.pack(fill="x")

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def card(self, parent, title, color=COLORS["blue"]):
        frame = tk.Frame(parent, bg=COLORS["panel"], highlightbackground=COLORS["line"], highlightthickness=1)
        header = tk.Label(
            frame,
            text=title,
            bg=COLORS["panel"],
            fg=color,
            font=("Segoe UI", 13, "bold"),
            anchor="w",
        )
        header.pack(fill="x", padx=14, pady=(12, 8))
        body = tk.Frame(frame, bg=COLORS["panel"])
        body.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        return frame, body

    def metric_card(self, parent, title, value, subtitle, color):
        frame = tk.Frame(parent, bg=COLORS["panel"], highlightbackground=COLORS["line"], highlightthickness=1)
        frame.pack(side="left", fill="both", expand=True, padx=6)

        tk.Label(frame, text=title, bg=COLORS["panel"], fg=COLORS["muted"], font=("Segoe UI", 10)).pack(anchor="w", padx=14, pady=(12, 0))
        tk.Label(frame, text=str(value), bg=COLORS["panel"], fg=color, font=("Segoe UI", 28, "bold")).pack(anchor="w", padx=14)
        tk.Label(frame, text=subtitle, bg=COLORS["panel"], fg=COLORS["muted"], font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(0, 12))

    def dashboard(self):
        self.clear_content()

        metrics = tk.Frame(self.content, bg=COLORS["bg"])
        metrics.pack(fill="x", pady=(0, 14))

        try:
            student_count = self.report.functions.studentCount().call()
            total_supply = self.coin.functions.totalSupply().call()
            block_number = self.w3.eth.block_number
            admin = self.report.functions.getAdmin().call()
            paused = self.report.functions.paused().call()
        except Exception:
            student_count = "?"
            total_supply = "?"
            block_number = "?"
            admin = "?"
            paused = "?"

        self.metric_card(metrics, "Students", student_count, "stored grades", COLORS["blue"])
        self.metric_card(metrics, "Grade Coin", total_supply, "total minted", COLORS["green"])
        self.metric_card(metrics, "Latest Block", block_number, "Ganache block", COLORS["orange"])
        self.metric_card(metrics, "System", "Paused" if paused else "Active", "current status", COLORS["red"] if paused else COLORS["green"])

        bottom = tk.Frame(self.content, bg=COLORS["bg"])
        bottom.pack(fill="both", expand=True)

        quick_frame, quick = self.card(bottom, "Quick Actions", COLORS["purple"])
        quick_frame.pack(side="left", fill="both", expand=True, padx=(0, 7))

        ModernButton(quick, "View Grade", self.show_view_grade).pack(fill="x", pady=5)
        ModernButton(quick, "Check Balance", self.show_balance, bg=COLORS["green"]).pack(fill="x", pady=5)
        ModernButton(quick, "Register User", self.show_register, bg=COLORS["purple"]).pack(fill="x", pady=5)
        ModernButton(quick, "Admin Dashboard", self.admin_dashboard, bg=COLORS["orange"]).pack(fill="x", pady=5)

        info_frame, info = self.card(bottom, "Current Session", COLORS["blue"])
        info_frame.pack(side="left", fill="both", expand=True, padx=(7, 0))

        tk.Label(
            info,
            text=f"Admin Wallet:\n{admin}\n\nSelected Wallet:\n{self.get_account()}\n\nThis dashboard reads live data from Ganache.",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            justify="left",
            font=("Segoe UI", 11),
        ).pack(anchor="w")

        self.log("Dashboard loaded.")

    def show_register(self):
        self.clear_content()
        frame, body = self.card(self.content, "Register User", COLORS["purple"])
        frame.pack(fill="x")

        self.add_label(body, "Display Name")
        self.name_entry = self.entry(body)
        ModernButton(body, "Register", self.register_user).pack(anchor="w", pady=10)

    def show_view_grade(self):
        self.clear_content()
        frame, body = self.card(self.content, "View Student Grade", COLORS["blue"])
        frame.pack(fill="x")

        self.add_label(body, "Student ID")
        self.grade_id_entry = self.entry(body)
        ModernButton(body, "View Grade", self.view_grade).pack(anchor="w", pady=10)

    def show_balance(self):
        self.clear_content()
        frame, body = self.card(self.content, "Check Grade Coin and ETH Balance", COLORS["green"])
        frame.pack(fill="x")

        self.add_label(body, "Wallet Address")
        self.balance_addr_entry = self.entry(body, width=70)
        self.balance_addr_entry.insert(0, self.get_account())
        ModernButton(body, "Check Balance", self.check_balance, bg=COLORS["green"]).pack(anchor="w", pady=10)

    def show_activity(self):
        self.clear_content()
        frame, body = self.card(self.content, "Personal Activity History", COLORS["orange"])
        frame.pack(fill="x")

        self.add_label(body, "Wallet Address")
        self.balance_addr_entry = self.entry(body, width=70)
        self.balance_addr_entry.insert(0, self.get_account())
        ModernButton(body, "Show Activity", self.activity_history, bg=COLORS["orange"]).pack(anchor="w", pady=10)

    def show_admin(self):
        self.clear_content()
        frame, body = self.card(self.content, "Admin Actions", COLORS["red"])
        frame.pack(fill="both", expand=True)

        grid = tk.Frame(body, bg=COLORS["panel"])
        grid.pack(fill="x")

        self.add_label(grid, "Admin Password", 0, 0)
        self.password_entry = self.entry(grid, show="*", row=1, col=0)
        self.password_entry.insert(0, ADMIN_PASSWORD)

        self.add_label(grid, "Student ID", 2, 0)
        self.admin_id_entry = self.entry(grid, row=3, col=0)

        self.add_label(grid, "Student Name", 2, 1)
        self.admin_name_entry = self.entry(grid, row=3, col=1)

        self.add_label(grid, "Subject", 4, 0)
        self.admin_subject_entry = self.entry(grid, row=5, col=0)

        self.add_label(grid, "Grade", 4, 1)
        self.admin_grade_entry = self.entry(grid, row=5, col=1)

        ModernButton(grid, "Add / Update Grade", self.add_update_grade).grid(row=6, column=0, columnspan=2, sticky="ew", pady=12, padx=6)

        self.add_label(grid, "Mint To Address", 7, 0)
        self.mint_addr_entry = self.entry(grid, row=8, col=0)
        self.mint_addr_entry.insert(0, self.get_account())

        self.add_label(grid, "Amount", 7, 1)
        self.mint_amount_entry = self.entry(grid, row=8, col=1)

        ModernButton(grid, "Mint Grade Coin", self.mint_coin, bg=COLORS["green"]).grid(row=9, column=0, columnspan=2, sticky="ew", pady=12, padx=6)

        ModernButton(grid, "Pause System", self.pause_system, bg=COLORS["red"]).grid(row=10, column=0, sticky="ew", padx=6, pady=6)
        ModernButton(grid, "Resume System", self.resume_system, bg=COLORS["purple"]).grid(row=10, column=1, sticky="ew", padx=6, pady=6)

        self.add_label(grid, "New Admin Address", 11, 0)
        self.new_admin_entry = self.entry(grid, row=12, col=0)
        ModernButton(grid, "Transfer Ownership", self.transfer_ownership, bg=COLORS["orange"]).grid(row=12, column=1, sticky="ew", padx=6, pady=6)

    def show_reports(self):
        self.clear_content()
        frame, body = self.card(self.content, "Reports and Tools", COLORS["blue"])
        frame.pack(fill="x")

        ModernButton(body, "Admin Dashboard", self.admin_dashboard, bg=COLORS["blue"]).pack(fill="x", pady=5)
        ModernButton(body, "Data History Report", self.data_history_report, bg=COLORS["purple"]).pack(fill="x", pady=5)
        ModernButton(body, "Export Balance Snapshot CSV", self.export_csv, bg=COLORS["green"]).pack(fill="x", pady=5)

    def add_label(self, parent, text, row=None, col=None):
        label = tk.Label(parent, text=text, bg=COLORS["panel"], fg=COLORS["muted"], font=("Segoe UI", 10, "bold"))
        if row is None:
            label.pack(anchor="w", pady=(4, 2))
        else:
            label.grid(row=row, column=col, sticky="w", padx=6, pady=(4, 2))

    def entry(self, parent, width=38, show=None, row=None, col=None):
        e = tk.Entry(
            parent,
            width=width,
            show=show,
            bg="#020617",
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            bd=0,
            font=("Segoe UI", 11),
        )
        if row is None:
            e.pack(anchor="w", ipady=7, pady=(0, 6))
        else:
            e.grid(row=row, column=col, sticky="ew", padx=6, pady=(0, 6), ipady=7)
            parent.grid_columnconfigure(col, weight=1)
        return e

    def load_accounts(self):
        values = [f"{i}: {acc}" for i, acc in enumerate(self.w3.eth.accounts)]
        self.account_combo["values"] = values
        if values:
            self.account_combo.current(0)
            self.account.set(values[0])

    def get_account(self):
        value = self.account.get()
        if ":" in value:
            return value.split(":", 1)[1].strip()
        return value.strip()

    def is_admin(self):
        try:
            return self.get_account().lower() == self.report.functions.getAdmin().call().lower()
        except Exception:
            return False

    def require_admin(self):
        if not self.is_admin():
            messagebox.showwarning("Access Denied", "Only the Admin wallet can use this action.")
            return False

        if not hasattr(self, "password_entry") or self.password_entry.get() != ADMIN_PASSWORD:
            messagebox.showwarning("Wrong Password", "Admin password is incorrect.")
            return False

        return True

    def refresh_header(self):
        account = self.get_account()

        try:
            admin = self.report.functions.getAdmin().call()
            name = self.report.functions.users(account).call()
            paused = self.report.functions.paused().call()
            role = "Admin" if account.lower() == admin.lower() else "Normal User"

            self.header.config(
                text=(
                    f"Current: {account}   |   "
                    f"Registered name: {name if name else 'Not registered'}   |   "
                    f"Admin: {admin}   |   "
                    f"Role: {role}   |   "
                    f"Paused: {paused}"
                )
            )

        except Exception as e:
            self.header.config(text=f"Could not load state: {clean_error(e)}")

    def refresh_all(self):
        try:
            self.w3, self.report, self.coin = load_contracts()
            self.load_accounts()
            self.refresh_header()
            self.dashboard()
            self.log("Refreshed blockchain connection.")
        except Exception as e:
            self.log("Refresh failed: " + clean_error(e))

    def log(self, message):
        self.output.insert(tk.END, str(message) + "\n\n")
        self.output.see(tk.END)
        self.status.set(str(message).replace("\n", " ")[:130])

    def clear_output(self):
        self.output.delete("1.0", tk.END)

    def register_user(self):
        if not hasattr(self, "name_entry"):
            return

        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter a display name.")
            return

        try:
            tx = self.report.functions.registerUser(name).transact({"from": self.get_account(), "gas": 200000})
            receipt = send_tx(self.w3, tx)
            self.log(f"Registered successfully. Status={receipt.status}")
            self.refresh_header()
        except Exception as e:
            self.log("Failed: " + clean_error(e))

    def view_grade(self):
        try:
            sid = int(self.grade_id_entry.get().strip())
            name, subject, grade = self.report.functions.getGrade(sid).call()
            self.log(f"Student ID {sid}\nName: {name}\nSubject: {subject}\nGrade: {grade}")
        except Exception as e:
            self.log("Could not find grade: " + clean_error(e))

    def check_balance(self):
        addr = self.balance_addr_entry.get().strip()

        try:
            coins = self.coin.functions.balanceOf(addr).call()
            eth = self.w3.from_wei(self.w3.eth.get_balance(addr), "ether")
            self.log(f"Address: {addr}\nGrade Coin: {coins}\nETH: {eth}")
        except Exception:
            self.log("Invalid address.")

    def build_method_map(self):
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

        for item in self.report.abi:
            if item.get("type") != "function":
                continue

            name = item.get("name")
            if name not in labels:
                continue

            types = [inp["type"] for inp in item.get("inputs", [])]
            signature = name + "(" + ",".join(types) + ")"
            h = self.w3.keccak(text=signature).hex()
            selector = h[:10] if h.startswith("0x") else "0x" + h[:8]
            method_map[selector] = labels[name]

        return method_map

    def activity_history(self):
        addr = self.balance_addr_entry.get().strip().lower()
        method_map = self.build_method_map()
        lines = ["Block     Action                 Value", "-" * 55]
        found = False

        for b in range(self.w3.eth.block_number + 1):
            block = self.w3.eth.get_block(b, full_transactions=True)

            for tx in block.transactions:
                frm = tx["from"].lower()
                to = tx["to"].lower() if tx["to"] else "contract creation"

                if frm == addr or to == addr:
                    found = True
                    tx_input = tx["input"]

                    if isinstance(tx_input, bytes):
                        tx_input = "0x" + tx_input.hex()

                    action = "ETH transfer" if tx_input == "0x" else method_map.get(tx_input[:10], "contract action")
                    value = self.w3.from_wei(tx["value"], "ether")
                    lines.append(f"{b:<9} {action:<22} {value} ETH")

        if not found:
            lines.append("No activity found.")

        self.log("\n".join(lines))

    def add_update_grade(self):
        if not self.require_admin():
            return

        try:
            sid = int(self.admin_id_entry.get().strip())
            name = self.admin_name_entry.get().strip()
            subject = self.admin_subject_entry.get().strip()
            grade = int(self.admin_grade_entry.get().strip())

            tx = self.report.functions.addOrUpdateGrade(sid, name, subject, grade).transact(
                {"from": self.get_account(), "gas": 300000}
            )
            receipt = send_tx(self.w3, tx)
            self.log(f"Grade saved. Status={receipt.status}")
            self.refresh_header()
        except Exception as e:
            self.log("Transaction failed: " + clean_error(e))

    def mint_coin(self):
        if not self.require_admin():
            return

        try:
            to = self.mint_addr_entry.get().strip()
            amount = int(self.mint_amount_entry.get().strip())
            tx = self.report.functions.mintGradeCoin(to, amount).transact({"from": self.get_account(), "gas": 300000})
            receipt = send_tx(self.w3, tx)
            self.log(f"Coins minted. Status={receipt.status}")
        except Exception as e:
            self.log("Transaction failed: " + clean_error(e))

    def pause_system(self):
        if not self.require_admin():
            return

        try:
            tx = self.report.functions.pause().transact({"from": self.get_account(), "gas": 100000})
            receipt = send_tx(self.w3, tx)
            self.log(f"System paused. Status={receipt.status}")
            self.refresh_header()
        except Exception as e:
            self.log("Transaction failed: " + clean_error(e))

    def resume_system(self):
        if not self.require_admin():
            return

        try:
            tx = self.report.functions.resume().transact({"from": self.get_account(), "gas": 100000})
            receipt = send_tx(self.w3, tx)
            self.log(f"System resumed. Status={receipt.status}")
            self.refresh_header()
        except Exception as e:
            self.log("Transaction failed: " + clean_error(e))

    def transfer_ownership(self):
        if not self.require_admin():
            return

        try:
            new_admin = self.new_admin_entry.get().strip()
            tx = self.report.functions.transferOwnership(new_admin).transact(
                {"from": self.get_account(), "gas": 150000}
            )
            receipt = send_tx(self.w3, tx)
            self.log(f"Ownership transferred. Status={receipt.status}")
            self.refresh_header()
        except Exception as e:
            self.log("Transaction failed: " + clean_error(e))

    def admin_dashboard(self):
        from collections import Counter

        counts = Counter()

        for b in range(self.w3.eth.block_number + 1):
            block = self.w3.eth.get_block(b, full_transactions=True)
            for tx in block.transactions:
                counts[tx["from"]] += 1

        lines = [
            "===== Admin Dashboard =====",
            f"Total student grades: {self.report.functions.studentCount().call()}",
            f"Total Grade Coin minted: {self.coin.functions.totalSupply().call()}",
            f"Total blocks: {self.w3.eth.block_number}",
            f"Total transactions scanned: {sum(counts.values())}",
            "Top 3 active users:",
        ]

        for addr, total in counts.most_common(3):
            lines.append(f"{addr} => {total} transactions")

        self.log("\n".join(lines))

    def data_history_report(self):
        count = self.report.functions.studentCount().call()
        grades = []
        lines = ["Student ID   Name                 Subject              Grade", "-" * 65]

        for sid in range(1, count + 20):
            try:
                name, subject, grade = self.report.functions.getGrade(sid).call()
                grades.append(grade)
                lines.append(f"{sid:<12} {name:<20} {subject:<20} {grade}")
            except Exception:
                pass

        lines.append("-" * 65)
        if grades:
            lines.append(f"Class average grade: {round(sum(grades) / len(grades), 2)}")
        else:
            lines.append("No grades found.")

        self.log("\n".join(lines))

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile="balance_snapshot.csv",
            filetypes=[("CSV Files", "*.csv")],
        )

        if not path:
            return

        accounts = set(self.w3.eth.accounts)

        for b in range(self.w3.eth.block_number + 1):
            block = self.w3.eth.get_block(b, full_transactions=True)
            for tx in block.transactions:
                accounts.add(tx["from"])
                if tx["to"]:
                    accounts.add(tx["to"])

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Account Address", "Grade Coin Balance", "ETH Balance"])

            for addr in sorted(accounts):
                coin_balance = self.coin.functions.balanceOf(addr).call()
                eth_balance = self.w3.from_wei(self.w3.eth.get_balance(addr), "ether")
                writer.writerow([addr, coin_balance, eth_balance])

        self.log(f"Saved CSV: {path}")

    def start_live_alert(self):
        if self.live_alert_running:
            self.log("Live alert is already running.")
            return

        self.live_alert_running = True
        self.log("Live alert started. Watching GradeChanged events only.")

        thread = threading.Thread(target=self.live_alert_loop, daemon=True)
        thread.start()

    def live_alert_loop(self):
        topic_hash = self.w3.keccak(text="GradeChanged(uint256,string,string,uint256)").hex()
        if not topic_hash.startswith("0x"):
            topic_hash = "0x" + topic_hash

        while self.live_alert_running:
            try:
                current_block = self.w3.eth.block_number

                if current_block > self.last_block:
                    for block_number in range(self.last_block + 1, current_block + 1):
                        logs = self.w3.eth.get_logs({
                            "fromBlock": block_number,
                            "toBlock": block_number,
                            "address": self.report.address,
                            "topics": [topic_hash],
                        })

                        for log in logs:
                            try:
                                event_data = self.report.events.GradeChanged().process_log(log)
                                args = event_data["args"]
                                self.log(
                                    "ALERT: A grade change just happened! "
                                    f"ID={args['studentId']}, "
                                    f"Name={args['studentName']}, "
                                    f"Subject={args['subject']}, "
                                    f"Grade={args['grade']}"
                                )
                            except Exception:
                                self.log("ALERT: A grade change just happened!")

                    self.last_block = current_block

                time.sleep(2)
            except Exception:
                self.log("Live alert check failed. Make sure Ganache is running.")
                time.sleep(2)


if __name__ == "__main__":
    root = tk.Tk()
    app = ReportCardGUI(root)
    root.mainloop()
