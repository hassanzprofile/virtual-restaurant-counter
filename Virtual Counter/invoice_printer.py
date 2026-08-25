"""
Pizza Corner Restaurant POS - Invoice Printer
Features:
  - On-screen invoice preview
  - Save / Print as PDF (A4)
  - Save as thermal-printer text (58mm / 80mm receipt)
  - Windows print via SumatraPDF or PowerShell fallback
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import os
import subprocess
import tempfile

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

SHOP_NAME    = "Pizza Corner"
SHOP_TAGLINE = "Gourmet Pizzas & More"
SHOP_ADDRESS = "Main Food Street, Your City"
SHOP_PHONE   = "0300-0000000"
SHOP_COLOR   = "#C0392B"   # restaurant red


# ── Receipt text (thermal printer format) ─────────────────────────────────────

def _build_receipt_text(data: dict, width=42) -> str:
    def center(txt):  return txt.center(width)
    def divider(ch="-"): return ch * width
    def row(left, right, total=width):
        space = total - len(left) - len(right)
        return left + " " * max(1, space) + right

    lines = []
    lines.append(center(SHOP_NAME))
    lines.append(center(SHOP_TAGLINE))
    lines.append(center(SHOP_ADDRESS))
    lines.append(center(f"Tel: {SHOP_PHONE}"))
    lines.append(divider("="))
    lines.append(f"Invoice : {data['invoice_no']}")
    lines.append(f"Date    : {data['date']}")
    lines.append(f"Customer: {data['customer']}")
    if data.get("phone"):
        lines.append(f"Phone   : {data['phone']}")
    if data.get("table_no"):
        lines.append(f"Table   : {data['table_no']}")
    lines.append(f"Type    : {data.get('order_type','Dine In')}")
    lines.append(f"Payment : {data['payment']}")
    lines.append(divider("-"))
    lines.append(f"{'Item':<22}{'Qty':>4}{'Rate':>7}{'Amt':>8}")
    lines.append(divider("-"))
    for item in data["items"]:
        name = item["item_name"][:21]
        qty  = f"{item['quantity']:.0f}x"
        rate = f"{item['unit_price']:,.0f}"
        amt  = f"{item['subtotal']:,.0f}"
        lines.append(f"{name:<22}{qty:>4}{rate:>7}{amt:>8}")
    lines.append(divider("-"))
    lines.append(row("Subtotal:", f"Rs. {data['subtotal']:,.0f}"))
    if data.get("discount", 0):
        lines.append(row("Discount:", f"-Rs. {data['discount']:,.0f}"))
    lines.append(divider("="))
    lines.append(row("TOTAL:", f"Rs. {data['total']:,.0f}"))
    lines.append(divider("="))
    lines.append(center("Thank you for dining at"))
    lines.append(center(SHOP_NAME + "!"))
    lines.append(center("Please visit us again :)"))
    lines.append("")
    return "\n".join(lines)


# ── PDF Generator ──────────────────────────────────────────────────────────────

def generate_pdf(data: dict, filepath: str):
    if not PDF_AVAILABLE:
        raise RuntimeError("reportlab not installed.\nRun: pip install reportlab")

    c = pdf_canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    def line(x1, y1, x2, y2, clr="#CCCCCC", w=0.5):
        c.setStrokeColor(colors.HexColor(clr))
        c.setLineWidth(w)
        c.line(x1, y1, x2, y2)

    def text(txt, x, y_, size=10, bold=False, clr="#000000", align="left"):
        c.setFillColor(colors.HexColor(clr))
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        if align == "center":
            c.drawCentredString(x, y_, str(txt))
        elif align == "right":
            c.drawRightString(x, y_, str(txt))
        else:
            c.drawString(x, y_, str(txt))

    ML = 20*mm
    MR = width - 20*mm

    # Header band
    c.setFillColor(colors.HexColor(SHOP_COLOR))
    c.rect(0, height-40*mm, width, 40*mm, fill=1, stroke=0)

    text(SHOP_NAME,    width/2, height-12*mm, 26, True,  "#FFFFFF", "center")
    text(SHOP_TAGLINE, width/2, height-20*mm, 11, False, "#FFCCCC", "center")
    text(SHOP_ADDRESS, width/2, height-27*mm, 9,  False, "#FFAAAA", "center")
    text(f"Tel: {SHOP_PHONE}", width/2, height-33*mm, 9, False, "#FFAAAA", "center")

    # Badge
    c.setFillColor(colors.HexColor("#F39C12"))
    c.roundRect(ML, height-39*mm, 36*mm, 8*mm, 3, fill=1, stroke=0)
    text("ORDER RECEIPT", ML+18*mm, height-35*mm, 9, True, "#FFFFFF", "center")

    y = height - 46*mm

    # Info box
    c.setFillColor(colors.HexColor("#FFF5F5"))
    c.setStrokeColor(colors.HexColor("#DDDDDD"))
    c.setLineWidth(0.5)
    c.roundRect(ML, y-32*mm, width-40*mm, 32*mm, 3, fill=1, stroke=1)

    lx, rx = ML+4*mm, width/2+4*mm
    iy = y-6*mm
    def ifield(lbl, val, x, yy):
        text(lbl,  x,       yy, 9, False, "#888888")
        text(val,  x+26*mm, yy, 9, True,  "#111111")

    ifield("Invoice No:",  data["invoice_no"],              lx, iy)
    ifield("Date:",        data["date"],                    lx, iy-6*mm)
    ifield("Payment:",     data["payment"],                 lx, iy-12*mm)
    ifield("Order Type:",  data.get("order_type","Dine In"),lx, iy-18*mm)
    ifield("Customer:",    data["customer"],                rx, iy)
    if data.get("phone"):
        ifield("Phone:",   data["phone"],                   rx, iy-6*mm)
    if data.get("table_no"):
        ifield("Table No:",data["table_no"],                rx, iy-12*mm)

    y = y - 37*mm

    # Table header
    c.setFillColor(colors.HexColor(SHOP_COLOR))
    c.rect(ML, y-8*mm, width-40*mm, 8*mm, fill=1, stroke=0)
    th = y - 5*mm
    text("Item",    ML+3*mm,   th, 9, True, "#FFFFFF")
    text("Qty",     ML+88*mm,  th, 9, True, "#FFFFFF", "center")
    text("Rate",    ML+108*mm, th, 9, True, "#FFFFFF", "right")
    text("Amount",  MR-3*mm,   th, 9, True, "#FFFFFF", "right")
    y -= 8*mm

    for i, item in enumerate(data["items"]):
        rh  = 7*mm
        bg  = "#FFF5F5" if i % 2 == 0 else "#FFFFFF"
        c.setFillColor(colors.HexColor(bg))
        c.rect(ML, y-rh, width-40*mm, rh, fill=1, stroke=0)
        ry  = y - 4.5*mm
        text(item["item_name"][:38],              ML+3*mm,   ry, 9)
        text(f"x{item['quantity']:.0f}",          ML+88*mm,  ry, 9, align="center")
        text(f"Rs.{item['unit_price']:,.0f}",     ML+108*mm, ry, 9, align="right")
        text(f"Rs.{item['subtotal']:,.0f}",        MR-3*mm,   ry, 9, True, align="right")
        line(ML, y-rh, MR, y-rh, "#EEEEEE")
        y -= rh

    y -= 4*mm
    bx = width/2 + 10*mm
    text("Subtotal:", bx, y-6*mm, 10)
    text(f"Rs. {data['subtotal']:,.0f}", MR, y-6*mm, 10, align="right")
    yd = 13*mm
    if data.get("discount", 0):
        text("Discount:", bx, y-yd, 10, clr="#C0392B")
        text(f"-Rs. {data['discount']:,.0f}", MR, y-yd, 10, clr="#C0392B", align="right")
        yd += 7*mm

    c.setFillColor(colors.HexColor(SHOP_COLOR))
    c.rect(bx-2*mm, y-(yd+9*mm), MR-bx+4*mm, 9*mm, fill=1, stroke=0)
    text("TOTAL:", bx, y-(yd+5*mm), 12, True, "#FFFFFF")
    text(f"Rs. {data['total']:,.0f}", MR, y-(yd+5*mm), 12, True, "#FFFFFF", "right")

    fy = y - yd - 20*mm
    line(ML, fy, MR, fy, SHOP_COLOR, 1)
    text(f"Thank you for dining at {SHOP_NAME}!",
         width/2, fy-7*mm, 10, True, SHOP_COLOR, "center")
    text("We hope to see you again soon!",
         width/2, fy-13*mm, 9, False, "#888888", "center")

    c.setStrokeColor(colors.HexColor(SHOP_COLOR))
    c.setLineWidth(1.5)
    c.rect(10*mm, 10*mm, width-20*mm, height-20*mm, fill=0, stroke=1)
    c.save()
    return filepath


# ── Windows Print Helper ───────────────────────────────────────────────────────

def _do_windows_print(filepath, parent_win=None):
    sumatra_paths = [
        r"C:\Program Files\SumatraPDF\SumatraPDF.exe",
        r"C:\Program Files (x86)\SumatraPDF\SumatraPDF.exe",
        os.path.join(os.environ.get("USERPROFILE",""),
                     r"AppData\Local\SumatraPDF\SumatraPDF.exe"),
    ]
    for p in sumatra_paths:
        if os.path.exists(p):
            subprocess.Popen([p, "-print-to-default", "-silent", filepath])
            return "sumatra"
    try:
        ps = f'Start-Process -FilePath "{filepath}" -Verb Print -PassThru | Out-Null'
        r  = subprocess.run(["powershell","-Command",ps],
                            capture_output=True, timeout=10)
        if r.returncode == 0:
            return "powershell"
    except Exception:
        pass
    try:
        import ctypes
        ret = ctypes.windll.shell32.ShellExecuteW(None,"print",filepath,None,None,1)
        if ret > 32:
            return "shell"
    except Exception:
        pass
    return None


# ── Main print_invoice function ────────────────────────────────────────────────

def print_invoice(data: dict, parent=None):
    """
    Show invoice preview popup with Print / Save PDF / Save Receipt buttons.
    data keys: invoice_no, customer, phone, table_no, order_type,
               items, subtotal, discount, total, payment, date, notes
    """
    win = tk.Toplevel(parent)
    win.title(f"Invoice — {data['invoice_no']}")
    win.geometry("560x680")
    win.configure(bg="white")
    win.resizable(True, True)
    win.grab_set()

    # ── Button bar ──
    btn_bar = tk.Frame(win, bg="#F0F0F0", pady=8)
    btn_bar.pack(fill="x", padx=10)

    def do_print():
        if not PDF_AVAILABLE:
            messagebox.showwarning("Missing Library",
                "reportlab not installed.\nRun: pip install reportlab", parent=win)
            return
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        tmp.close()
        try:
            generate_pdf(data, tmp.name)
        except Exception as e:
            messagebox.showerror("PDF Error", str(e), parent=win)
            return
        import sys
        if sys.platform == "win32":
            method = _do_windows_print(tmp.name, win)
            if method:
                messagebox.showinfo("Printing",
                    "Sent to printer!\n(PDF → default printer)", parent=win)
            else:
                messagebox.showwarning("Print Failed",
                    "Could not auto-print.\nUse 'Save PDF' and print manually.", parent=win)
        elif sys.platform == "darwin":
            subprocess.run(["lpr", tmp.name])
            messagebox.showinfo("Printing", "Sent to printer!", parent=win)
        else:
            subprocess.run(["lpr", tmp.name])
            messagebox.showinfo("Printing", "Sent to printer (lpr)!", parent=win)

    def do_save_pdf():
        if not PDF_AVAILABLE:
            messagebox.showwarning("Missing Library",
                "reportlab not installed.\nRun: pip install reportlab", parent=win)
            return
        default = f"Invoice_{data['invoice_no'].replace('-','_')}.pdf"
        fp = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF File","*.pdf")],
            initialfile=default,
            title="Save Invoice as PDF",
            parent=win
        )
        if not fp:
            return
        try:
            generate_pdf(data, fp)
            ans = messagebox.askyesno("PDF Saved!",
                f"Saved!\n{fp}\n\nOpen now?", parent=win)
            if ans:
                try:    os.startfile(fp)
                except: subprocess.run(["open", fp])
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=win)

    def do_save_receipt():
        """Save thermal-printer-ready text receipt"""
        default = f"Receipt_{data['invoice_no'].replace('-','_')}.txt"
        fp = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Receipt","*.txt")],
            initialfile=default,
            title="Save Receipt Text (for small/thermal printer)",
            parent=win
        )
        if not fp:
            return
        try:
            receipt = _build_receipt_text(data)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(receipt)
            messagebox.showinfo("Saved!",
                f"Receipt saved!\n{fp}\n\nTip: Print this file on your thermal/small printer.",
                parent=win)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=win)

    tk.Button(btn_bar, text="🖨  Print (PDF)",
              command=do_print,
              bg="#28A745", fg="white", font=("Segoe UI",10,"bold"),
              relief="flat", padx=14, pady=5, cursor="hand2").pack(side="right", padx=4)

    tk.Button(btn_bar, text="📄 Save PDF",
              command=do_save_pdf,
              bg="#C0392B", fg="white", font=("Segoe UI",10,"bold"),
              relief="flat", padx=12, pady=5, cursor="hand2").pack(side="right", padx=4)

    tk.Button(btn_bar, text="🧾 Save Receipt",
              command=do_save_receipt,
              bg="#1A6FBF", fg="white", font=("Segoe UI",10,"bold"),
              relief="flat", padx=12, pady=5, cursor="hand2").pack(side="right", padx=4)

    # ── Preview area ──
    main_f = tk.Frame(win, bg="white")
    main_f.pack(fill="both", expand=True)

    canv = tk.Canvas(main_f, bg="white", highlightthickness=0)
    vsb  = tk.Scrollbar(main_f, orient="vertical", command=canv.yview)
    canv.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    canv.pack(side="left", fill="both", expand=True)

    inner = tk.Frame(canv, bg="white")
    wid   = canv.create_window((0,0), window=inner, anchor="nw")
    inner.bind("<Configure>", lambda e: canv.configure(scrollregion=canv.bbox("all")))
    canv.bind("<Configure>",  lambda e: canv.itemconfig(wid, width=e.width))
    canv.bind_all("<MouseWheel>",
                  lambda e: canv.yview_scroll(int(-1*(e.delta/120)),"units"))

    P = dict(padx=28)

    # Header
    tk.Frame(inner, bg=SHOP_COLOR, height=8).pack(fill="x")
    tk.Label(inner, text=SHOP_NAME, bg="white",
             font=("Courier New",18,"bold"), fg=SHOP_COLOR,
             anchor="center").pack(fill="x", pady=(12,0), **P)
    tk.Label(inner, text=SHOP_TAGLINE, bg="white",
             font=("Courier New",9), fg="#888",
             anchor="center").pack(fill="x", **P)
    tk.Label(inner, text=SHOP_ADDRESS, bg="white",
             font=("Courier New",8), fg="#888",
             anchor="center").pack(fill="x", **P)
    tk.Label(inner, text=f"Tel: {SHOP_PHONE}", bg="white",
             font=("Courier New",8), fg="#888",
             anchor="center").pack(fill="x", **P)
    tk.Frame(inner, bg=SHOP_COLOR, height=2).pack(fill="x", padx=28, pady=8)

    # Info
    info = tk.Frame(inner, bg="#FFF5F5")
    info.pack(fill="x", padx=28, pady=(0,8))

    def irow(lbl, val, r):
        tk.Label(info, text=lbl, bg="#FFF5F5",
                 font=("Courier New",9), fg="#888",
                 width=14, anchor="w").grid(row=r,column=0,sticky="w",padx=8,pady=2)
        tk.Label(info, text=": "+str(val), bg="#FFF5F5",
                 font=("Courier New",9,"bold"), fg="#111",
                 anchor="w").grid(row=r,column=1,sticky="w",pady=2)

    r = 0
    irow("Invoice No",  data["invoice_no"], r); r+=1
    irow("Date",        data["date"],       r); r+=1
    irow("Customer",    data["customer"],   r); r+=1
    if data.get("phone"):
        irow("Phone",   data["phone"],      r); r+=1
    if data.get("table_no"):
        irow("Table No",data["table_no"],   r); r+=1
    irow("Order Type",  data.get("order_type","Dine In"), r); r+=1
    irow("Payment",     data["payment"],    r)

    # Items table
    hdr = tk.Frame(inner, bg=SHOP_COLOR)
    hdr.pack(fill="x", padx=28, pady=(6,0))
    for txt, w, anc in [("Item",22,"w"),("Qty",4,"e"),("Rate",8,"e"),("Amt",8,"e")]:
        tk.Label(hdr, text=txt, bg=SHOP_COLOR, fg="white",
                 font=("Courier New",9,"bold"),
                 width=w, anchor=anc, padx=4, pady=5).pack(side="left")

    for i, item in enumerate(data["items"]):
        bg = "#FFF5F5" if i % 2 == 0 else "white"
        rf = tk.Frame(inner, bg=bg)
        rf.pack(fill="x", padx=28)
        qty = f"x{item['quantity']:.0f}"
        for t,w,a,bold in [
            (item["item_name"][:21], 22, "w", False),
            (qty,                   4,  "e", False),
            (f"{item['unit_price']:,.0f}", 8, "e", False),
            (f"{item['subtotal']:,.0f}",   8, "e", True),
        ]:
            tk.Label(rf, text=t, bg=bg,
                     font=("Courier New",9,"bold" if bold else "normal"),
                     width=w, anchor=a, padx=4, pady=4).pack(side="left")

    tk.Frame(inner, bg="#CCCCCC", height=1).pack(fill="x", padx=28, pady=4)

    def trow(lbl, val, fg="black", bold=False):
        r = tk.Frame(inner, bg="white")
        r.pack(fill="x", padx=28)
        tk.Label(r, text=lbl, bg="white",
                 font=("Courier New",10,"bold" if bold else "normal"),
                 fg=fg, anchor="w").pack(side="left")
        tk.Label(r, text=f"Rs. {val:,.0f}", bg="white",
                 font=("Courier New",10,"bold" if bold else "normal"),
                 fg=fg, anchor="e").pack(side="right")

    trow("Subtotal:", data["subtotal"])
    if data.get("discount",0):
        trow("Discount:", data["discount"], fg=SHOP_COLOR)

    grand = tk.Frame(inner, bg=SHOP_COLOR)
    grand.pack(fill="x", padx=28, pady=(4,12))
    tk.Label(grand, text="TOTAL", bg=SHOP_COLOR, fg="white",
             font=("Courier New",13,"bold"), padx=10, pady=7, anchor="w").pack(side="left")
    tk.Label(grand, text=f"Rs. {data['total']:,.0f}",
             bg=SHOP_COLOR, fg="white",
             font=("Courier New",13,"bold"), padx=10, pady=7, anchor="e").pack(side="right")

    if data.get("notes"):
        tk.Label(inner, text=f"Note: {data['notes']}", bg="white",
                 font=("Courier New",8), fg="#666",
                 anchor="center").pack(fill="x", padx=28)

    tk.Frame(inner, bg=SHOP_COLOR, height=2).pack(fill="x", padx=28, pady=(4,6))
    tk.Label(inner, text=f"*** Thank you for dining at {SHOP_NAME}! ***",
             bg="white", font=("Courier New",9,"italic"),
             fg="#555", anchor="center").pack(fill="x", padx=28)
    tk.Label(inner, text="Please visit us again  ❤",
             bg="white", font=("Courier New",9),
             fg="#999", anchor="center").pack(fill="x", pady=(0,20), padx=28)

    tk.Button(win, text="✖  Close", command=win.destroy,
              bg="#D9534F", fg="white", font=("Segoe UI",10,"bold"),
              relief="flat", padx=20, pady=6, cursor="hand2").pack(pady=8, side="bottom")

    win.update_idletasks()
    canv.configure(scrollregion=canv.bbox("all"))
    win.wait_window()
