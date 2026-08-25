<div align="center">

  <!-- Glowing Header Image -->
  <a href="https://github.com">
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=800&size=40&duration=3000&pause=1000&color=00F2FE&center=true&vCenter=true&multiline=false&width=600&height=80&lines=VIRTUAL+COUNTER" alt="Virtual Counter" />
  </a>

  <p><em>Modern, High-Performance Desktop Restaurant Management & POS Suite</em></p>

  <!-- Badges -->
  <p>
    <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
    <img src="https://img.shields.io/badge/GUI-Tkinter-38B2AC?style=for-the-badge&logo=tcl&logoColor=white" alt="Tkinter" />
    <img src="https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
    <img src="https://img.shields.io/badge/Reports-ReportLab%20PDF-E74C3C?style=for-the-badge&logo=adobeacrobatreader&logoColor=white" alt="ReportLab" />
    <img src="https://img.shields.io/badge/Analytics-Matplotlib-11557C?style=for-the-badge&logo=python&logoColor=white" alt="Matplotlib" />
    <img src="https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge" alt="License" />
  </p>

</div>


A desktop Point of Sale (POS) and restaurant management system built in Python using **Tkinter** and **SQLite**. The application streamlines order processing, menu item management, billing with automatic subtotal and discount calculations, PDF invoice generation, and sales dashboard analytics.

## Features

* **Billing & Order Processing:** Real-time item cart, automatic subtotal/discount calculations, and seamless checkout.
* **Menu Catalog Management:** Add, edit, categorize, and delete food items.
* **Sales Records & Logs:** Searchable transaction history and historical order lookup.
* **Dashboard Analytics:** Visual sales tracking and revenue metrics via embedded charts.
* **Invoice Generation:** Automatic PDF receipt formatting and generation.
* **Zero-Setup Database:** SQLite backend that initializes automatically on first run.


## Requirements & Compatibility

* **Recommended Versions:** Python `3.10.x`, `3.11.x`, or `3.12.x` (Python `3.10.11` tested for full out-of-the-box stability).
* **Python 3.14+ Note:** Tkinter variable listeners in Python 3.14+ require `.trace_add("write", ...)` instead of the legacy `.trace("w", ...)` to prevent runtime deprecation/errors.


## Dependencies

### 1. Built-in Modules (No Installation Required)

| Module | Role |
| :--- | :--- |
| `tkinter` / `ttk` | GUI components, entry fields, table views, and layout containers |
| `sqlite3` | Local relational database management |
| `datetime` | Timestamp formatting for sales records and receipts |
| `os`, `sys`, `json` | System path handling and internal configuration management |

> **Linux Users:** If Tkinter is not bundled with your Python distribution, install it via:
> ```bash
> sudo apt-get install python3-tk
> ```

### 2. External Packages

| Package | Purpose |
| :--- | :--- |
| `reportlab` | Generates PDF customer receipts and invoices |
| `matplotlib` | Generates analytical sales charts in the dashboard |
| `pillow` (`PIL`) | Handles GUI assets and image rendering |

## Installation & Setup

### 1. Open the Project Directory
```bash
cd Virtual Counter

Install Required Dependencies:
pip install reportlab matplotlib pillow

Run the Application:
python main.py


NOTE: Currently it's working properly on python 3.14, if you change version you have to download libraries according to that.
