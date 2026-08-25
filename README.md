<div align="center">

  <!-- Glowing Title Banner -->
  <svg width="100%" height="90" viewBox="0 0 700 90" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <!-- Neon Glow Filter -->
      <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="6" result="blur1" />
        <feGaussianBlur stdDeviation="14" result="blur2" />
        <feMerge>
          <feMergeNode in="blur2" />
          <feMergeNode in="blur1" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>

      <!-- Neon Gradient -->
      <linearGradient id="neonGradient" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#00F2FE" />
        <stop offset="50%" stop-color="#4FACFE" />
        <stop offset="100%" stop-color="#00FF87" />
      </linearGradient>
    </defs>

    <!-- Glowing Background Layer -->
    <text x="50%" y="60" text-anchor="middle" fill="url(#neonGradient)" font-family="'Segoe UI', 'Helvetica Neue', Arial, sans-serif" font-weight="900" font-size="44" letter-spacing="4" filter="url(#glow)" opacity="0.85">
      VIRTUAL COUNTER
    </text>

    <!-- Sharp Foreground Layer -->
    <text x="50%" y="60" text-anchor="middle" fill="#FFFFFF" font-family="'Segoe UI', 'Helvetica Neue', Arial, sans-serif" font-weight="900" font-size="44" letter-spacing="4">
      VIRTUAL COUNTER
    </text>
  </svg>

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
                                                                           
                        [ RESTAURANT POS SYSTEM ]


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
