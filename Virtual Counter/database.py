"""
Pizza Corner Restaurant POS - Database Module
SQLite database: menu items, orders, invoices
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "pizza_corner.db")


def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def initialize_database():
    with _conn() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            category    TEXT    NOT NULL DEFAULT 'Burger',
            price       REAL    NOT NULL DEFAULT 0,
            description TEXT    DEFAULT '',
            available   INTEGER NOT NULL DEFAULT 1,
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS invoices (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no     TEXT    NOT NULL UNIQUE,
            customer_name  TEXT    NOT NULL DEFAULT 'Walk-in',
            customer_phone TEXT    DEFAULT '',
            table_no       TEXT    DEFAULT '',
            order_type     TEXT    DEFAULT 'Dine In',
            subtotal       REAL    NOT NULL DEFAULT 0,
            discount       REAL    NOT NULL DEFAULT 0,
            total          REAL    NOT NULL DEFAULT 0,
            payment_method TEXT    NOT NULL DEFAULT 'Cash',
            notes          TEXT    DEFAULT '',
            created_at     TEXT    DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS invoice_items (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id   INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
            item_name    TEXT    NOT NULL,
            quantity     REAL    NOT NULL DEFAULT 1,
            unit_price   REAL    NOT NULL DEFAULT 0,
            subtotal     REAL    NOT NULL DEFAULT 0
        );
        """)
        # Seed menu if empty
        count = con.execute("SELECT COUNT(*) FROM menu_items").fetchone()[0]
        if count == 0:
            _seed_menu(con)


def _seed_menu(con):
    items = [
        # Burgers
        ("Classic Beef Burger",    "Burger",    350, "Juicy beef patty with lettuce & sauce"),
        ("Double Smash Burger",    "Burger",    550, "Double patty, cheese, special sauce"),
        ("Zinger Burger",          "Burger",    420, "Crispy fried chicken fillet"),
        ("BBQ Burger",             "Burger",    480, "Beef patty with smoky BBQ sauce"),
        ("Cheese Burger",          "Burger",    380, "Classic with extra cheese"),
        ("Veggie Burger",          "Burger",    300, "Veggie patty with fresh veggies"),
        # Deals
        ("Burger Deal (1+Drink)",  "Deal",      500, "1 Burger + Regular Drink"),
        ("Family Deal (4+Fries+Drinks)", "Deal",1799,"4 Burgers + 4 Fries + 4 Drinks"),
        ("Student Deal",           "Deal",      350, "1 Burger + Small Drink"),
        # Sides
        ("Fries (Regular)",        "Sides",     150, "Crispy golden fries"),
        ("Fries (Large)",          "Sides",     220, "Large portion crispy fries"),
        ("Onion Rings",            "Sides",     180, "Crispy battered onion rings"),
        ("Coleslaw",               "Sides",     100, "Creamy homemade coleslaw"),
        # Drinks
        ("Pepsi (Regular)",        "Drink",     80,  "330ml"),
        ("Pepsi (Large)",          "Drink",     120, "600ml"),
        ("Mineral Water",          "Drink",     60,  "500ml"),
        ("Fresh Juice",            "Drink",     150, "Seasonal fresh juice"),
        ("Milkshake",              "Drink",     250, "Chocolate / Vanilla / Strawberry"),
        # Extras
        ("Extra Cheese",           "Extra",     50,  "Add cheese slice"),
        ("Extra Sauce",            "Extra",     30,  "Ketchup / Mayo / BBQ"),
        ("Extra Patty",            "Extra",     180, "Add beef patty"),
    ]
    con.executemany(
        "INSERT INTO menu_items (name, category, price, description) VALUES (?,?,?,?)",
        items
    )


# ── Menu CRUD ─────────────────────────────────────────────────────────────────

def get_all_menu_items(search="", category="All"):
    with _conn() as con:
        q = "SELECT * FROM menu_items WHERE 1=1"
        params = []
        if search:
            q += " AND name LIKE ?"
            params.append(f"%{search}%")
        if category and category != "All":
            q += " AND category = ?"
            params.append(category)
        q += " ORDER BY category, name"
        return [dict(r) for r in con.execute(q, params).fetchall()]


def get_available_menu_items(search="", category="All"):
    with _conn() as con:
        q = "SELECT * FROM menu_items WHERE available=1"
        params = []
        if search:
            q += " AND name LIKE ?"
            params.append(f"%{search}%")
        if category and category != "All":
            q += " AND category = ?"
            params.append(category)
        q += " ORDER BY category, name"
        return [dict(r) for r in con.execute(q, params).fetchall()]


def get_menu_item_by_id(item_id):
    with _conn() as con:
        r = con.execute("SELECT * FROM menu_items WHERE id=?", (item_id,)).fetchone()
        return dict(r) if r else None


def add_menu_item(name, category, price, description=""):
    with _conn() as con:
        con.execute(
            "INSERT INTO menu_items (name, category, price, description) VALUES (?,?,?,?)",
            (name, category, price, description)
        )


def update_menu_item(item_id, name, category, price, description, available):
    with _conn() as con:
        con.execute(
            "UPDATE menu_items SET name=?, category=?, price=?, description=?, available=? WHERE id=?",
            (name, category, price, description, available, item_id)
        )


def delete_menu_item(item_id):
    with _conn() as con:
        con.execute("DELETE FROM menu_items WHERE id=?", (item_id,))


def get_menu_categories():
    with _conn() as con:
        rows = con.execute(
            "SELECT DISTINCT category FROM menu_items ORDER BY category"
        ).fetchall()
        return [r[0] for r in rows]


# ── Invoice CRUD ──────────────────────────────────────────────────────────────

def _next_invoice_no():
    with _conn() as con:
        row = con.execute(
            "SELECT invoice_no FROM invoices ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if row:
            try:
                num = int(row[0].split("-")[1]) + 1
            except Exception:
                num = 1
        else:
            num = 1
        return f"BRG-{num:05d}"


def save_invoice(customer, phone, table_no, order_type,
                 cart_items, subtotal, discount, total,
                 payment, notes=""):
    invoice_no = _next_invoice_no()
    with _conn() as con:
        cur = con.execute(
            """INSERT INTO invoices
               (invoice_no, customer_name, customer_phone, table_no, order_type,
                subtotal, discount, total, payment_method, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (invoice_no, customer, phone, table_no, order_type,
             subtotal, discount, total, payment, notes)
        )
        inv_id = cur.lastrowid
        for item in cart_items:
            con.execute(
                """INSERT INTO invoice_items
                   (invoice_id, item_name, quantity, unit_price, subtotal)
                   VALUES (?,?,?,?,?)""",
                (inv_id, item["item_name"], item["quantity"],
                 item["unit_price"], item["subtotal"])
            )
    return invoice_no, inv_id


def get_all_invoices(date_from=None, date_to=None, search=""):
    with _conn() as con:
        q = "SELECT * FROM invoices WHERE 1=1"
        params = []
        if date_from:
            q += " AND DATE(created_at) >= ?"
            params.append(date_from)
        if date_to:
            q += " AND DATE(created_at) <= ?"
            params.append(date_to)
        if search:
            q += " AND (invoice_no LIKE ? OR customer_name LIKE ?)"
            params += [f"%{search}%", f"%{search}%"]
        q += " ORDER BY id DESC"
        return [dict(r) for r in con.execute(q, params).fetchall()]


def get_invoice_by_id(inv_id):
    with _conn() as con:
        r = con.execute("SELECT * FROM invoices WHERE id=?", (inv_id,)).fetchone()
        return dict(r) if r else None


def get_invoice_items(inv_id):
    with _conn() as con:
        return [dict(r) for r in con.execute(
            "SELECT * FROM invoice_items WHERE invoice_id=?", (inv_id,)
        ).fetchall()]


def get_sales_summary(date_from=None, date_to=None):
    with _conn() as con:
        q = """SELECT
                   COALESCE(SUM(total),0)    AS revenue,
                   COALESCE(SUM(discount),0) AS discounts,
                   COUNT(*)                  AS bills
               FROM invoices WHERE 1=1"""
        params = []
        if date_from:
            q += " AND DATE(created_at) >= ?"
            params.append(date_from)
        if date_to:
            q += " AND DATE(created_at) <= ?"
            params.append(date_to)
        r = con.execute(q, params).fetchone()
        return dict(r)


def get_top_selling_items(limit=10):
    with _conn() as con:
        return [dict(r) for r in con.execute("""
            SELECT item_name,
                   SUM(quantity)          AS total_qty,
                   SUM(subtotal)          AS total_rev
            FROM invoice_items
            GROUP BY item_name
            ORDER BY total_qty DESC
            LIMIT ?
        """, (limit,)).fetchall()]


def get_sales_by_category(date_from=None, date_to=None):
    with _conn() as con:
        q = """
            SELECT m.category,
                   COALESCE(SUM(ii.subtotal),0) AS revenue,
                   COALESCE(SUM(ii.quantity),0) AS qty
            FROM invoice_items ii
            JOIN invoices i ON i.id = ii.invoice_id
            LEFT JOIN menu_items m ON m.name = ii.item_name
            WHERE 1=1
        """
        params = []
        if date_from:
            q += " AND DATE(i.created_at) >= ?"
            params.append(date_from)
        if date_to:
            q += " AND DATE(i.created_at) <= ?"
            params.append(date_to)
        q += " GROUP BY m.category ORDER BY revenue DESC"
        return [dict(r) for r in con.execute(q, params).fetchall()]
        
