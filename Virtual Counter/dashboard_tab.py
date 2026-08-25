"""
Pizza Corner Restaurant POS - Dashboard Tab
Shows today's stats and quick overview
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import database as db


class DashboardTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#F5F5F0")
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # Title
        tk.Label(self, text="🍔  Pizza Corner — Daily Overview",
                 bg="#F5F5F0", font=("Segoe UI", 14, "bold"),
                 fg="#C0392B").pack(padx=20, pady=(16, 4), anchor="w")
        self.lbl_date = tk.Label(self, text="", bg="#F5F5F0",
                                  font=("Segoe UI", 10), fg="#888")
        self.lbl_date.pack(anchor="w", padx=20)

        # Cards row
        cards = tk.Frame(self, bg="#F5F5F0")
        cards.pack(fill="x", padx=20, pady=14)
        self.card_rev   = self._card(cards, "Today's Revenue",  "Rs. 0", "#C0392B")
        self.card_bills = self._card(cards, "Orders Today",     "0",     "#28A745")
        self.card_avg   = self._card(cards, "Avg Order Value",  "Rs. 0", "#F0A500")
        self.card_disc  = self._card(cards, "Discount Given",   "Rs. 0", "#1A6FBF")

        # Bottom row: top items + recent orders
        bot = tk.Frame(self, bg="#F5F5F0")
        bot.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        bot.columnconfigure(0, weight=1)
        bot.columnconfigure(1, weight=1)
        bot.rowconfigure(0, weight=1)

        top_f = tk.LabelFrame(bot, text=" 🏆 Top Items Today ",
                              bg="#F5F5F0", font=("Segoe UI", 10, "bold"),
                              fg="#C0392B", relief="groove", bd=1)
        top_f.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        top_cols = ("Item", "Qty", "Revenue")
        self.top_tree = ttk.Treeview(top_f, columns=top_cols, show="headings")
        self.top_tree.heading("Item",    text="Item")
        self.top_tree.heading("Qty",     text="Qty Sold")
        self.top_tree.heading("Revenue", text="Revenue")
        self.top_tree.column("Item",    width=160, anchor="w")
        self.top_tree.column("Qty",     width=70,  anchor="center")
        self.top_tree.column("Revenue", width=90,  anchor="center")
        self.top_tree.pack(fill="both", expand=True, padx=6, pady=6)

        rec_f = tk.LabelFrame(bot, text=" 🕐 Recent Orders ",
                              bg="#F5F5F0", font=("Segoe UI", 10, "bold"),
                              fg="#C0392B", relief="groove", bd=1)
        rec_f.grid(row=0, column=1, sticky="nsew")

        rec_cols = ("Invoice", "Customer", "Total", "Time")
        self.rec_tree = ttk.Treeview(rec_f, columns=rec_cols, show="headings")
        self.rec_tree.heading("Invoice",  text="Invoice No")
        self.rec_tree.heading("Customer", text="Customer")
        self.rec_tree.heading("Total",    text="Total")
        self.rec_tree.heading("Time",     text="Time")
        self.rec_tree.column("Invoice",  width=90,  anchor="center")
        self.rec_tree.column("Customer", width=110, anchor="w")
        self.rec_tree.column("Total",    width=80,  anchor="center")
        self.rec_tree.column("Time",     width=70,  anchor="center")
        self.rec_tree.pack(fill="both", expand=True, padx=6, pady=6)

        tk.Button(self, text="🔄  Refresh Dashboard", command=self.refresh,
                  bg="#C0392B", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=14, pady=5, cursor="hand2").pack(pady=8)

    def _card(self, parent, label, value, color):
        f = tk.Frame(parent, bg=color, padx=20, pady=14)
        f.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(f, text=label, bg=color, fg="white",
                 font=("Segoe UI", 9)).pack(anchor="w")
        lbl = tk.Label(f, text=value, bg=color, fg="white",
                       font=("Segoe UI", 17, "bold"))
        lbl.pack(anchor="w")
        return lbl

    def refresh(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.lbl_date.config(text=datetime.now().strftime("%A, %d %B %Y  |  %I:%M %p"))

        summary = db.get_sales_summary(today, today)
        rev  = summary["revenue"]   or 0
        cnt  = summary["bills"]     or 0
        disc = summary["discounts"] or 0
        avg  = rev / cnt if cnt else 0

        self.card_rev.config(text=f"Rs. {rev:,.0f}")
        self.card_bills.config(text=str(cnt))
        self.card_avg.config(text=f"Rs. {avg:,.0f}")
        self.card_disc.config(text=f"Rs. {disc:,.0f}")

        for r in self.top_tree.get_children():
            self.top_tree.delete(r)
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        for i, item in enumerate(db.get_top_selling_items(5), 1):
            self.top_tree.insert("", "end", values=(
                f"{medals.get(i,'')} {item['item_name']}",
                f"{item['total_qty']:.0f}",
                f"Rs. {item['total_rev']:,.0f}"
            ))

        for r in self.rec_tree.get_children():
            self.rec_tree.delete(r)
        for inv in db.get_all_invoices(today, today)[:10]:
            self.rec_tree.insert("", "end", values=(
                inv["invoice_no"],
                inv["customer_name"],
                f"Rs. {inv['total']:,.0f}",
                inv["created_at"][11:16]
            ))
