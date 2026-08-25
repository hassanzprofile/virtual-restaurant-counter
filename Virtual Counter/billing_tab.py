"""
Pizza Corner POS - Billing / Order Tab
Take orders from menu, apply discounts, finalize & print invoice
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import database as db
from invoice_printer import print_invoice

ORDER_TYPES = ["Dine In", "Take Away", "Delivery"]
PAYMENT_METHODS = ["Cash", "Card", "EasyPaisa", "JazzCash", "Bank Transfer"]


class BillingTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#F5F5F0")
        self.cart_items = []
        self.all_items = []
        self._build_ui()
        self.refresh_menu()

    def _build_ui(self):
        main = tk.Frame(self, bg="#F5F5F0")
        main.pack(fill="both", expand=True, padx=10, pady=8)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)
        self._build_left(main)
        self._build_right(main)

    # ── LEFT: Order / Bill ────────────────────────────────────────────────────

    def _build_left(self, parent):
        left = tk.LabelFrame(parent, text=" 🧾 Current Order ",
                             bg="#F5F5F0", font=("Segoe UI", 11, "bold"),
                             fg="#C0392B", relief="groove", bd=1)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        # Customer / Table row
        info = tk.Frame(left, bg="#F5F5F0")
        info.pack(fill="x", padx=8, pady=(4, 2))

        tk.Label(info, text="Customer:", bg="#F5F5F0",
                 font=("Segoe UI", 9)).pack(side="left")
        self.cust_name = tk.StringVar()
        tk.Entry(info, textvariable=self.cust_name, width=13,
                 font=("Segoe UI", 9), relief="solid", bd=1).pack(side="left", padx=3)

        tk.Label(info, text="Phone:", bg="#F5F5F0",
                 font=("Segoe UI", 9)).pack(side="left", padx=(4, 0))
        self.cust_phone = tk.StringVar()
        tk.Entry(info, textvariable=self.cust_phone, width=11,
                 font=("Segoe UI", 9), relief="solid", bd=1).pack(side="left", padx=3)

        tk.Label(info, text="Table:", bg="#F5F5F0",
                 font=("Segoe UI", 9)).pack(side="left", padx=(4, 0))
        self.table_no = tk.StringVar()
        tk.Entry(info, textvariable=self.table_no, width=4,
                 font=("Segoe UI", 9), relief="solid", bd=1).pack(side="left", padx=3)

        # Order type
        otype = tk.Frame(left, bg="#F5F5F0")
        otype.pack(fill="x", padx=8, pady=(2, 4))
        tk.Label(otype, text="Order Type:", bg="#F5F5F0",
                 font=("Segoe UI", 9)).pack(side="left")
        self.order_type = tk.StringVar(value="Dine In")
        for ot in ORDER_TYPES:
            tk.Radiobutton(otype, text=ot, variable=self.order_type, value=ot,
                           bg="#F5F5F0", font=("Segoe UI", 9),
                           activebackground="#F5F5F0").pack(side="left", padx=4)

        # Cart table (Height adjusted to fit on standard screen resolutions)
        cols = ("#", "Item", "Qty", "Unit Price", "Subtotal", "✕")
        cart_frame = tk.Frame(left, bg="#F5F5F0")
        cart_frame.pack(fill="both", expand=True, padx=8)

        self.cart_tree = ttk.Treeview(cart_frame, columns=cols,
                                      show="headings", height=6)
        for col, w, anc in zip(cols,
                               [25, 180, 45, 90, 90, 25],
                               ["c", "w", "c", "c", "c", "c"]):
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=w, anchor=anc)

        self.cart_tree.tag_configure("odd",  background="#FFF5F5")
        self.cart_tree.tag_configure("even", background="#FFFFFF")

        sb = ttk.Scrollbar(cart_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=sb.set)
        self.cart_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.cart_tree.bind("<Double-1>", lambda e: self._remove_selected_cart_item())

        tk.Label(left, text="Double-click a row to remove it",
                 bg="#F5F5F0", font=("Segoe UI", 8), fg="#999").pack(anchor="w", padx=10, pady=(1, 2))

        # Totals Panel
        tot = tk.Frame(left, bg="#EAEAE0", pady=5)
        tot.pack(fill="x", padx=8, pady=(2, 4))
        tot.columnconfigure(1, weight=1)

        tk.Label(tot, text="Subtotal:", bg="#EAEAE0",
                 font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", padx=8)
        self.lbl_sub = tk.Label(tot, text="Rs. 0", bg="#EAEAE0",
                                font=("Segoe UI", 9, "bold"))
        self.lbl_sub.grid(row=0, column=1, sticky="e", padx=8)

        tk.Label(tot, text="Discount (Rs):", bg="#EAEAE0",
                 font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", padx=8, pady=1)
        self.disc_var = tk.StringVar(value="0")
        tk.Entry(tot, textvariable=self.disc_var, width=10,
                 font=("Segoe UI", 9), relief="solid", bd=1).grid(
            row=1, column=1, sticky="e", padx=8, pady=1)
        self.disc_var.trace_add("write", lambda *a: self._update_total())

        tk.Label(tot, text="Payment:", bg="#EAEAE0",
                 font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", padx=8)
        self.pay_var = tk.StringVar(value="Cash")
        ttk.Combobox(tot, textvariable=self.pay_var,
                     values=PAYMENT_METHODS,
                     state="readonly", width=14).grid(
            row=2, column=1, sticky="e", padx=8, pady=1)

        tk.Label(tot, text="Notes:", bg="#EAEAE0",
                 font=("Segoe UI", 9)).grid(row=3, column=0, sticky="w", padx=8)
        self.notes_var = tk.StringVar()
        tk.Entry(tot, textvariable=self.notes_var, width=22,
                 font=("Segoe UI", 9), relief="solid", bd=1).grid(
            row=3, column=1, sticky="e", padx=8, pady=1)

        tk.Label(tot, text="TOTAL:", bg="#EAEAE0",
                 font=("Segoe UI", 12, "bold")).grid(row=4, column=0, sticky="w", padx=8, pady=3)
        self.lbl_total = tk.Label(tot, text="Rs. 0", bg="#EAEAE0",
                                  font=("Segoe UI", 13, "bold"), fg="#C0392B")
        self.lbl_total.grid(row=4, column=1, sticky="e", padx=8)

        # Buttons (Visible and fully packed)
        bf = tk.Frame(left, bg="#F5F5F0", pady=4)
        bf.pack(fill="x", padx=8, pady=(0, 4))
        
        tk.Button(bf, text="✅ Place Order & Print",
                  command=self.finalize_invoice,
                  bg="#28A745", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=10, pady=5, cursor="hand2").pack(side="left", padx=4)
                  
        tk.Button(bf, text="🗑 Clear Order", command=self.clear_bill,
                  bg="#D9534F", fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=8, pady=5, cursor="hand2").pack(side="left", padx=4)

    # ── RIGHT: Menu Picker ─────────────────────────────────────────────────────

    def _build_right(self, parent):
        right = tk.Frame(parent, bg="#F5F5F0")
        right.grid(row=0, column=1, sticky="nsew")

        menu_frame = tk.LabelFrame(right, text=" 🍔 Menu ",
                                   bg="#F5F5F0", font=("Segoe UI", 10, "bold"),
                                   fg="#C0392B", relief="groove", bd=1)
        menu_frame.pack(fill="both", expand=True)

        # Search & category filter
        sf = tk.Frame(menu_frame, bg="#F5F5F0")
        sf.pack(fill="x", padx=8, pady=4)
        tk.Label(sf, text="Search:", bg="#F5F5F0",
                 font=("Segoe UI", 9)).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._filter_menu())
        tk.Entry(sf, textvariable=self.search_var, width=12,
                 font=("Segoe UI", 9), relief="solid", bd=1).pack(side="left", padx=3)

        self.cat_filter = tk.StringVar(value="All")
        cat_cb = ttk.Combobox(sf, textvariable=self.cat_filter,
                              values=["All", "Burger", "Deal", "Sides", "Drink", "Extra", "Other"],
                              state="readonly", width=8)
        cat_cb.pack(side="left", padx=3)
        self.cat_filter.trace_add("write", lambda *a: self._filter_menu())

        # Menu item list
        ilist = tk.Frame(menu_frame, bg="#F5F5F0")
        ilist.pack(fill="both", expand=True, padx=8, pady=(0, 4))

        cols = ("Item", "Category", "Price")
        self.menu_tree = ttk.Treeview(ilist, columns=cols, show="headings", height=10)
        self.menu_tree.heading("Item",     text="Item Name")
        self.menu_tree.heading("Category", text="Category")
        self.menu_tree.heading("Price",    text="Price")
        self.menu_tree.column("Item",     width=160, anchor="w")
        self.menu_tree.column("Category", width=70,  anchor="center")
        self.menu_tree.column("Price",    width=80,  anchor="center")
        self.menu_tree.pack(side="left", fill="both", expand=True)

        sb2 = ttk.Scrollbar(ilist, orient="vertical", command=self.menu_tree.yview)
        self.menu_tree.configure(yscrollcommand=sb2.set)
        sb2.pack(side="right", fill="y")

        # Category color tags
        tag_colors = {
            "Burger": "#FFE4E4",
            "Deal":   "#FFF3CD",
            "Sides":  "#E8F5E9",
            "Drink":  "#E3F2FD",
            "Extra":  "#F3E5F5",
            "Other":  "#F5F5F5",
        }
        for cat, bg in tag_colors.items():
            self.menu_tree.tag_configure(cat, background=bg)

        self.menu_tree.bind("<Double-1>", lambda e: self._add_selected_to_cart())

        # Qty + Add button
        qr = tk.Frame(menu_frame, bg="#F5F5F0")
        qr.pack(fill="x", padx=8, pady=(0, 6))

        tk.Label(qr, text="Qty:", bg="#F5F5F0",
                 font=("Segoe UI", 9)).pack(side="left")
        self.qty_var = tk.StringVar(value="1")
        tk.Spinbox(qr, from_=1, to=99, textvariable=self.qty_var, width=4,
                   font=("Segoe UI", 9), relief="solid").pack(side="left", padx=3)

        tk.Button(qr, text="➕ Add to Order",
                  command=self._add_selected_to_cart,
                  bg="#C0392B", fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=10, pady=3, cursor="hand2").pack(side="left", padx=5)

    # ── Menu Data ──────────────────────────────────────────────────────────────

    def refresh_menu(self):
        self.all_items = db.get_available_menu_items()
        self._filter_menu()

    def _filter_menu(self):
        search = self.search_var.get().lower()
        cat    = self.cat_filter.get()
        for r in self.menu_tree.get_children():
            self.menu_tree.delete(r)
        for item in self.all_items:
            if search and search not in item["name"].lower():
                continue
            if cat != "All" and item["category"] != cat:
                continue
            self.menu_tree.insert("", "end", iid=item["id"],
                                  tags=(item["category"],),
                                  values=(
                                      item["name"],
                                      item["category"],
                                      f"Rs. {item['price']:,.0f}"
                                  ))

    # ── Cart ──────────────────────────────────────────────────────────────────

    def _add_selected_to_cart(self):
        sel = self.menu_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a menu item first.")
            return
        item_id = int(sel[0])
        item    = db.get_menu_item_by_id(item_id)
        if not item:
            return
        try:
            qty = int(self.qty_var.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid", "Quantity must be a positive number.")
            return

        existing = next((x for x in self.cart_items if x["item_id"] == item_id), None)
        if existing:
            existing["quantity"] += qty
            existing["subtotal"]  = existing["quantity"] * existing["unit_price"]
        else:
            self.cart_items.append({
                "item_id":    item_id,
                "item_name":  item["name"],
                "quantity":   qty,
                "unit_price": item["price"],
                "subtotal":   qty * item["price"],
            })

        self.qty_var.set("1")
        self._render_cart()

    def _remove_selected_cart_item(self):
        sel = self.cart_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        del self.cart_items[idx]
        self._render_cart()

    def _render_cart(self):
        for r in self.cart_tree.get_children():
            self.cart_tree.delete(r)
        for i, x in enumerate(self.cart_items):
            tag = "odd" if i % 2 else "even"
            self.cart_tree.insert("", "end", iid=i, tags=(tag,), values=(
                i + 1,
                x["item_name"],
                x["quantity"],
                f"Rs. {x['unit_price']:,.0f}",
                f"Rs. {x['subtotal']:,.0f}",
                "✕"
            ))
        self._update_total()

    def _update_total(self):
        sub = sum(x["subtotal"] for x in self.cart_items)
        try:
            disc = float(self.disc_var.get() or 0)
        except Exception:
            disc = 0
        total = max(0, sub - disc)
        self.lbl_sub.config(text=f"Rs. {sub:,.0f}")
        self.lbl_total.config(text=f"Rs. {total:,.0f}")

    def clear_bill(self):
        if self.cart_items and not messagebox.askyesno("Clear", "Clear entire order?"):
            return
        self.cart_items = []
        self.cust_name.set("")
        self.cust_phone.set("")
        self.table_no.set("")
        self.disc_var.set("0")
        self.notes_var.set("")
        self._render_cart()

    # ── Finalize ──────────────────────────────────────────────────────────────

    def finalize_invoice(self):
        if not self.cart_items:
            messagebox.showwarning("Empty Order", "Add items to the order first.")
            return

        sub  = sum(x["subtotal"] for x in self.cart_items)
        try:
            disc = float(self.disc_var.get() or 0)
        except Exception:
            disc = 0
        total    = max(0, sub - disc)
        customer = self.cust_name.get().strip() or "Walk-in"
        phone    = self.cust_phone.get().strip()
        table    = self.table_no.get().strip()
        otype    = self.order_type.get()
        payment  = self.pay_var.get()
        notes    = self.notes_var.get().strip()

        try:
            invoice_no, _ = db.save_invoice(
                customer, phone, table, otype,
                self.cart_items, sub, disc, total, payment, notes
            )

            print_invoice({
                "invoice_no":  invoice_no,
                "customer":    customer,
                "phone":       phone,
                "table_no":    table,
                "order_type":  otype,
                "items":       self.cart_items,
                "subtotal":    sub,
                "discount":    disc,
                "total":       total,
                "payment":     payment,
                "notes":       notes,
                "date":        datetime.now().strftime("%d-%b-%Y %I:%M %p")
            }, parent=self)

            self.clear_bill()
            messagebox.showinfo("Order Saved!",
                                f"Invoice #{invoice_no} saved successfully!\nTotal: Rs. {total:,.0f}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to finalize invoice: {e}")