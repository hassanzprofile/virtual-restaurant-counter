"""
Pizza Corner Restaurant POS - Menu Management Tab
Manage menu items: add, edit, toggle availability, delete
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database as db

CATEGORIES = ["Burger", "Deal", "Sides", "Drink", "Extra", "Other"]


class MenuTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#F5F5F0")
        self._build_ui()
        self.load_items()

    def _build_ui(self):
        toolbar = tk.Frame(self, bg="#F5F5F0")
        toolbar.pack(fill="x", padx=16, pady=(14, 6))

        tk.Label(toolbar, text="Search:", bg="#F5F5F0",
                 font=("Segoe UI", 10)).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.load_items())
        tk.Entry(toolbar, textvariable=self.search_var, width=22,
                 font=("Segoe UI", 10), relief="solid", bd=1).pack(side="left", padx=(4, 16))

        tk.Label(toolbar, text="Category:", bg="#F5F5F0",
                 font=("Segoe UI", 10)).pack(side="left")
        self.cat_var = tk.StringVar(value="All")
        ttk.Combobox(toolbar, textvariable=self.cat_var,
                     values=["All"] + CATEGORIES, state="readonly",
                     width=12).pack(side="left", padx=(4, 16))
        self.cat_var.trace_add("write", lambda *a: self.load_items())

        tk.Button(toolbar, text="+ Add Item", command=self.open_add_dialog,
                  bg="#C0392B", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=14, pady=5, cursor="hand2").pack(side="right")
        tk.Button(toolbar, text="Refresh", command=self.load_items,
                  bg="#E8E8E0", fg="#333", font=("Segoe UI", 10),
                  relief="flat", padx=10, pady=5, cursor="hand2").pack(side="right", padx=6)

        cols = ("ID", "Item Name", "Category", "Price (Rs)", "Status")
        frame = tk.Frame(self, bg="#F5F5F0")
        frame.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        self.tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")
        widths = [40, 260, 100, 110, 100]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w,
                             anchor="w" if col == "Item Name" else "center")
        self.tree.tag_configure("unavail", foreground="#AAAAAA", background="#F5F5F5")
        self.tree.tag_configure("avail",   background="#FFFFFF")

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda e: self.open_edit_dialog())

        bar = tk.Frame(self, bg="#EAEAE0", pady=8)
        bar.pack(fill="x", padx=16)

        tk.Button(bar, text="✏ Edit", command=self.open_edit_dialog,
                  bg="#F0A500", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=12, pady=4, cursor="hand2").pack(side="left", padx=4)
        tk.Button(bar, text="✅/❌ Toggle Available", command=self.toggle_available,
                  bg="#1A6FBF", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=12, pady=4, cursor="hand2").pack(side="left", padx=4)
        tk.Button(bar, text="🗑 Delete", command=self.delete_selected,
                  bg="#D9534F", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=12, pady=4, cursor="hand2").pack(side="left", padx=4)

        self.status_var = tk.StringVar()
        tk.Label(bar, textvariable=self.status_var, bg="#EAEAE0",
                 font=("Segoe UI", 10), fg="#555").pack(side="right", padx=8)

    def load_items(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        items = db.get_all_menu_items(self.search_var.get(), self.cat_var.get())
        for item in items:
            avail = "Available" if item["available"] else "Unavailable"
            tag   = "avail" if item["available"] else "unavail"
            self.tree.insert("", "end", iid=item["id"], tags=(tag,), values=(
                item["id"], item["name"], item["category"],
                f"Rs. {item['price']:,.0f}", avail
            ))
        self.status_var.set(f"{len(items)} items")

    def _selected_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select an item first.")
            return None
        return db.get_menu_item_by_id(int(sel[0]))

    def toggle_available(self):
        item = self._selected_item()
        if not item:
            return
        new_val = 0 if item["available"] else 1
        db.update_menu_item(item["id"], item["name"], item["category"],
                            item["price"], item["description"], new_val)
        self.load_items()

    def delete_selected(self):
        item = self._selected_item()
        if not item:
            return
        if messagebox.askyesno("Delete", f"Delete '{item['name']}'?"):
            db.delete_menu_item(item["id"])
            self.load_items()

    def open_add_dialog(self):
        self._item_dialog(None)

    def open_edit_dialog(self):
        item = self._selected_item()
        if item:
            self._item_dialog(item["id"])

    def _item_dialog(self, item_id):
        item = db.get_menu_item_by_id(item_id) if item_id else None
        dlg = tk.Toplevel(self)
        dlg.title("Add Menu Item" if not item else f"Edit — {item['name']}")
        dlg.geometry("440x380")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(bg="#F5F5F0")

        tk.Label(dlg, text="Add Menu Item" if not item else "Edit Item",
                 bg="#F5F5F0", font=("Segoe UI", 13, "bold"),
                 fg="#C0392B").pack(padx=18, pady=(14, 8), anchor="w")

        f = tk.Frame(dlg, bg="#F5F5F0")
        f.pack(fill="both", expand=True, padx=18)
        f.columnconfigure(1, weight=1)

        def row(label, r, default="", is_combo=False, vals=None):
            tk.Label(f, text=label, bg="#F5F5F0",
                     font=("Segoe UI", 10), anchor="w").grid(
                row=r, column=0, sticky="w", pady=6)
            var = tk.StringVar(value=default)
            if is_combo:
                ttk.Combobox(f, textvariable=var, values=vals,
                             state="readonly", width=28).grid(
                    row=r, column=1, sticky="ew", padx=(8, 0), pady=6)
            else:
                tk.Entry(f, textvariable=var, width=30,
                         font=("Segoe UI", 10), relief="solid", bd=1).grid(
                    row=r, column=1, sticky="ew", padx=(8, 0), pady=6)
            return var

        v_name  = row("Item Name *",  0, item["name"]        if item else "")
        v_cat   = row("Category *",   1, item["category"]    if item else "Burger",
                      True, CATEGORIES)
        v_price = row("Price (Rs) *", 2, str(item["price"])  if item else "0")
        v_desc  = row("Description",  3, item["description"] if item else "")

        v_avail = tk.IntVar(value=item["available"] if item else 1)
        avail_f = tk.Frame(f, bg="#F5F5F0")
        avail_f.grid(row=4, column=0, columnspan=2, sticky="w", pady=6)
        tk.Checkbutton(avail_f, text="Available on menu",
                       variable=v_avail, bg="#F5F5F0",
                       font=("Segoe UI", 10)).pack(side="left")

        def save():
            name  = v_name.get().strip()
            cat   = v_cat.get().strip()
            if not name or not cat:
                messagebox.showerror("Missing", "Name and category are required.", parent=dlg)
                return
            try:
                price = float(v_price.get())
            except ValueError:
                messagebox.showerror("Invalid", "Price must be a number.", parent=dlg)
                return
            if item:
                db.update_menu_item(item["id"], name, cat, price,
                                    v_desc.get().strip(), v_avail.get())
            else:
                db.add_menu_item(name, cat, price, v_desc.get().strip())
            self.load_items()
            dlg.destroy()

        bf = tk.Frame(dlg, bg="#F5F5F0", pady=10)
        bf.pack(fill="x", padx=18)
        tk.Button(bf, text="💾 Save", command=save,
                  bg="#C0392B", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=16, pady=5, cursor="hand2").pack(side="left", padx=4)
        tk.Button(bf, text="Cancel", command=dlg.destroy,
                  bg="#E8E8E0", fg="#333", font=("Segoe UI", 10),
                  relief="flat", padx=12, pady=5, cursor="hand2").pack(side="left", padx=4)
