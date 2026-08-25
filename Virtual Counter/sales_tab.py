"""
Pizza Corner Restaurant POS - Sales & Reports Tab
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import os
import database as db


class SalesTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#F5F5F0")
        self._build_ui()
        self.load_report()

    def _build_ui(self):
        # ── Filter bar ──
        bar = tk.Frame(self, bg="#F5F5F0")
        bar.pack(fill="x", padx=16, pady=10)

        tk.Label(bar, text="From:", bg="#F5F5F0", font=("Segoe UI", 10)).pack(side="left")
        self.date_from = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(bar, textvariable=self.date_from, width=12,
                 font=("Segoe UI", 10), relief="solid", bd=1).pack(side="left", padx=4)

        tk.Label(bar, text="To:", bg="#F5F5F0", font=("Segoe UI", 10)).pack(side="left", padx=(8, 0))
        self.date_to = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(bar, textvariable=self.date_to, width=12,
                 font=("Segoe UI", 10), relief="solid", bd=1).pack(side="left", padx=4)

        tk.Button(bar, text="Search", command=self.load_report,
                  bg="#C0392B", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=12, pady=4, cursor="hand2").pack(side="left", padx=8)

        for label, days in [("Today", 0), ("Last 7 Days", 7), ("This Month", 30), ("All Time", -1)]:
            tk.Button(bar, text=label, command=lambda d=days: self._quick_filter(d),
                      bg="#E8E8E0", fg="#333", font=("Segoe UI", 9),
                      relief="flat", padx=8, pady=4, cursor="hand2").pack(side="left", padx=2)

        # ── Summary cards ──
        cards = tk.Frame(self, bg="#F5F5F0")
        cards.pack(fill="x", padx=16, pady=(0, 8))
        self.lbl_revenue = self._card(cards, "Total Revenue",   "Rs. 0", "#C0392B")
        self.lbl_bills   = self._card(cards, "Total Orders",    "0",     "#28A745")
        self.lbl_avg     = self._card(cards, "Average Order",   "Rs. 0", "#F0A500")
        self.lbl_disc    = self._card(cards, "Total Discount",  "Rs. 0", "#1A6FBF")

        # ── Bottom: Invoices + Top Items ──
        bottom = tk.Frame(self, bg="#F5F5F0")
        bottom.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        bottom.columnconfigure(0, weight=2)
        bottom.columnconfigure(1, weight=1)
        bottom.rowconfigure(0, weight=1)

        # Invoice list
        inv_frame = tk.LabelFrame(bottom, text=" All Orders ",
                                  bg="#F5F5F0", font=("Segoe UI", 10, "bold"),
                                  fg="#C0392B", relief="groove", bd=1)
        inv_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        sf = tk.Frame(inv_frame, bg="#F5F5F0")
        sf.pack(fill="x", padx=8, pady=6)
        tk.Label(sf, text="Search:", bg="#F5F5F0", font=("Segoe UI", 9)).pack(side="left")
        self.inv_search = tk.StringVar()
        self.inv_search.trace_add("write", lambda *a: self.load_report())
        tk.Entry(sf, textvariable=self.inv_search, width=18,
                 font=("Segoe UI", 9), relief="solid", bd=1).pack(side="left", padx=4)

        cols = ("Invoice No", "Customer", "Type", "Items", "Discount", "Total", "Payment", "Date")
        ilist = tk.Frame(inv_frame, bg="#F5F5F0")
        ilist.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        self.inv_tree = ttk.Treeview(ilist, columns=cols, show="headings")
        widths = [90, 110, 70, 40, 75, 85, 75, 120]
        for col, w in zip(cols, widths):
            self.inv_tree.heading(col, text=col)
            self.inv_tree.column(col, width=w, anchor="center")
        self.inv_tree.column("Customer", anchor="w")
        self.inv_tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(ilist, orient="vertical", command=self.inv_tree.yview)
        self.inv_tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.inv_tree.bind("<Double-1>", self._view_invoice_detail)

        # Top items
        top_frame = tk.LabelFrame(bottom, text=" 🏆 Top Items ",
                                  bg="#F5F5F0", font=("Segoe UI", 10, "bold"),
                                  fg="#C0392B", relief="groove", bd=1)
        top_frame.grid(row=0, column=1, sticky="nsew")

        top_cols = ("Item", "Qty Sold", "Revenue")
        self.top_tree = ttk.Treeview(top_frame, columns=top_cols, show="headings")
        self.top_tree.heading("Item",     text="Item Name")
        self.top_tree.heading("Qty Sold", text="Qty Sold")
        self.top_tree.heading("Revenue",  text="Revenue")
        self.top_tree.column("Item",     width=150, anchor="w")
        self.top_tree.column("Qty Sold", width=70,  anchor="center")
        self.top_tree.column("Revenue",  width=90,  anchor="center")
        self.top_tree.pack(fill="both", expand=True, padx=6, pady=6)

    def _card(self, parent, label, value, color):
        f = tk.Frame(parent, bg=color, padx=16, pady=10)
        f.pack(side="left", fill="both", expand=True, padx=4)
        tk.Label(f, text=label, bg=color, fg="white", font=("Segoe UI", 9)).pack(anchor="w")
        lbl = tk.Label(f, text=value, bg=color, fg="white", font=("Segoe UI", 15, "bold"))
        lbl.pack(anchor="w")
        return lbl

    def _quick_filter(self, days):
        today = datetime.now()
        self.date_to.set(today.strftime("%Y-%m-%d"))
        if days == 0:
            self.date_from.set(today.strftime("%Y-%m-%d"))
        elif days == -1:
            self.date_from.set("2000-01-01")
        else:
            self.date_from.set((today - timedelta(days=days)).strftime("%Y-%m-%d"))
        self.load_report()

    def load_report(self):
        df = self.date_from.get()
        dt = self.date_to.get()
        q  = self.inv_search.get()

        summary = db.get_sales_summary(df, dt)
        rev  = summary["revenue"]   or 0
        cnt  = summary["bills"]     or 0
        disc = summary["discounts"] or 0
        avg  = rev / cnt if cnt else 0

        self.lbl_revenue.config(text=f"Rs. {rev:,.0f}")
        self.lbl_bills.config(text=str(cnt))
        self.lbl_avg.config(text=f"Rs. {avg:,.0f}")
        self.lbl_disc.config(text=f"Rs. {disc:,.0f}")

        for row in self.inv_tree.get_children():
            self.inv_tree.delete(row)
        invoices = db.get_all_invoices(df, dt, q)
        for inv in invoices:
            items = db.get_invoice_items(inv["id"])
            self.inv_tree.insert("", "end", iid=inv["id"], values=(
                inv["invoice_no"], inv["customer_name"],
                inv["order_type"],
                len(items),
                f"Rs. {inv['discount']:,.0f}",
                f"Rs. {inv['total']:,.0f}",
                inv["payment_method"],
                inv["created_at"][:16]
            ))

        for row in self.top_tree.get_children():
            self.top_tree.delete(row)
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        for i, item in enumerate(db.get_top_selling_items(), 1):
            prefix = medals.get(i, f"{i}.")
            self.top_tree.insert("", "end", values=(
                f"{prefix} {item['item_name']}",
                f"{item['total_qty']:.0f}",
                f"Rs. {item['total_rev']:,.0f}"
            ))

    def _view_invoice_detail(self, event):
        sel = self.inv_tree.selection()
        if not sel:
            return
        invoice_id = int(sel[0])
        inv   = db.get_invoice_by_id(invoice_id)
        items = db.get_invoice_items(invoice_id)

        dlg = tk.Toplevel(self)
        dlg.title(f"Order — {inv['invoice_no']}")
        dlg.geometry("500x440")
        dlg.configure(bg="white")
        dlg.grab_set()

        tk.Label(dlg, text=inv["invoice_no"], bg="white",
                 font=("Segoe UI", 13, "bold"), fg="#C0392B").pack(pady=(12, 0))
        tk.Label(dlg,
                 text=f"{inv['customer_name']}  |  {inv['order_type']}  |  {inv['created_at'][:16]}",
                 bg="white", font=("Segoe UI", 9), fg="#666").pack()

        cols = ("Item", "Qty", "Unit Price", "Subtotal")
        tree = ttk.Treeview(dlg, columns=cols, show="headings", height=10)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=110, anchor="center")
        tree.column("Item", width=200, anchor="w")
        tree.pack(fill="both", expand=True, padx=12, pady=8)

        for item in items:
            tree.insert("", "end", values=(
                item["item_name"],
                f"x{item['quantity']:.0f}",
                f"Rs. {item['unit_price']:,.0f}",
                f"Rs. {item['subtotal']:,.0f}"
            ))

        bot = tk.Frame(dlg, bg="#F0F0F0", pady=8)
        bot.pack(fill="x", padx=12)
        tk.Label(bot, text=f"Total: Rs. {inv['total']:,.0f}",
                 bg="#F0F0F0", font=("Segoe UI", 11, "bold"), fg="#C0392B").pack(side="right", padx=10)
        tk.Label(bot,
                 text=f"Discount: Rs. {inv['discount']:,.0f}  |  {inv['payment_method']}",
                 bg="#F0F0F0", font=("Segoe UI", 9), fg="#555").pack(side="left", padx=10)
        if inv.get("notes"):
            tk.Label(dlg, text=f"Note: {inv['notes']}", bg="white",
                     font=("Segoe UI", 9), fg="#888").pack(pady=(0, 4))
