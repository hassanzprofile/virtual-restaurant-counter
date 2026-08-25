"""
Pizza Corner Restaurant POS System - Main Entry Point
Run this file to launch:  python main.py

Requirements (install once):
    pip install reportlab   (for PDF invoices & printing)

Optional for Excel export (future):
    pip install openpyxl

Usage:
    python main.py
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import database as db
from dashboard_tab import DashboardTab
from menu_tab      import MenuTab
from billing_tab   import BillingTab
from sales_tab     import SalesTab


class PizzaCornerPOS(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Pizza Corner — Restaurant POS")
        self.geometry("1150x720")
        self.minsize(950, 620)
        self.configure(bg="#8B0000")

        # Initialize database
        db.initialize_database()

        # ── Styles ──
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook",
                        background="#8B0000", borderwidth=0)
        style.configure("TNotebook.Tab",
                        background="#8B0000", foreground="white",
                        font=("Segoe UI", 11), padding=[16, 8])
        style.map("TNotebook.Tab",
                  background=[("selected", "#F5F5F0")],
                  foreground=[("selected", "#C0392B")])
        style.configure("Treeview",
                        font=("Segoe UI", 10), rowheight=26)
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 10, "bold"),
                        background="#E8E8E0", foreground="#333")
        style.configure("TScrollbar",
                        troughcolor="#F5F5F0", background="#CCCCCC")

        # ── Top bar ──
        top_bar = tk.Frame(self, bg="#8B0000", pady=6)
        top_bar.pack(fill="x")

        tk.Label(top_bar,
                 text="🍔  Pizza Corner — Restaurant POS",
                 bg="#8B0000", fg="white",
                 font=("Segoe UI", 13, "bold")).pack(side="left", padx=16)

        tk.Button(top_bar, text="Exit", command=self.quit,
                  bg="#C0392B", fg="white", font=("Segoe UI", 9),
                  relief="flat", padx=10, pady=3,
                  cursor="hand2").pack(side="right", padx=12)

        # ── Tabs ──
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True)

        self.tab_dash  = DashboardTab(self.nb)
        self.tab_menu  = MenuTab(self.nb)
        self.tab_bill  = BillingTab(self.nb)
        self.tab_sales = SalesTab(self.nb)

        self.nb.add(self.tab_dash,  text="  Dashboard  ")
        self.nb.add(self.tab_menu,  text="  Menu  ")
        self.nb.add(self.tab_bill,  text="  New Order  ")
        self.nb.add(self.tab_sales, text="  Sales Report  ")

        self.nb.bind("<<NotebookTabChanged>>", self._on_tab_change)

        # ── Status bar ──
        self.statusbar = tk.Label(
            self,
            text="Ready  |  Pizza Corner POS v1.0  |  Welcome!",
            bg="#8B0000", fg="#FFAAAA",
            font=("Segoe UI", 9), anchor="w", pady=4
        )
        self.statusbar.pack(fill="x", padx=10, side="bottom")

    def _on_tab_change(self, event):
        idx = self.nb.index(self.nb.select())
        if idx == 0:
            self.tab_dash.refresh()
        elif idx == 1:
            self.tab_menu.load_items()
        elif idx == 2:
            self.tab_bill.refresh_menu()
        elif idx == 3:
            self.tab_sales.load_report()


def main():
    app = PizzaCornerPOS()
    app.mainloop()


if __name__ == "__main__":
    main()
