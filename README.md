```text
 __      ___      _               _    _____                 _            
 \ \    / (_)    | |             | |  / ____|               | |           
  \ \  / / _ _ __| |_ _   _  __ _| | | |     ___  _   _ _ __ | |_ ___ _ __ 
   \ \/ / | | '__| __| | | |/ _` | | | |    / _ \| | | | '_ \| __/ _ \ '__|
    \  /  | | |  | |_| |_| | (_| | | | |___| (_) | |_| | | | | ||  __/ |   
     \/   |_|_|   \__|\__,_|\__,_|_|  \_____\___/ \__,_|_| |_|\__\___|_|   
                                                                           
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
