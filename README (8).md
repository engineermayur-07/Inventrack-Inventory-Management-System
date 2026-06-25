# 📦 Inventrack — Inventory Management System

> A full-stack, multi-user inventory management web application built with **Python Flask** and **SQLite**, featuring intelligent batch tracking, expiry-date alerting, and a Min-Heap powered FEFO (First Expired, First Out) selling algorithm.

---

## 🚀 Live Demo

**[https://inventrack.pythonanywhere.com/](https://inventrack.pythonanywhere.com/)**

> Try it live — register with your email, add some batches, and watch the FEFO algorithm in action.
> Hosted on [PythonAnywhere](https://www.pythonanywhere.com/).

---

## 📌 Table of Contents

- [About the Project](#about-the-project)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Data Structure Design — The Min-Heap](#data-structure-design--the-min-heap)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Usage](#usage)
- [API / Routes Reference](#api--routes-reference)
- [Database Schema](#database-schema)
- [Future Improvements](#future-improvements)

---

## About the Project

**Inventrack** solves a real-world problem faced by pharmacies, grocery stores, and warehouses: managing product batches with expiry dates so that the oldest stock is always sold first — minimising waste and financial loss.

The system supports multiple independent users. Each user gets their own isolated inventory, managed through a private in-memory **Min-Heap** that enables O(log n) identification of the nearest-expiry batch at sell time — no full table scans required.

---

## Key Features

- **Secure User Registration with OTP Verification** — new accounts are confirmed via a one-time password sent to the user's email before being persisted to the database.
- **Email Notification on Successful Registration** — users receive a welcome alert once their account is activated.
- **Batch-Level Inventory Management** — stock is tracked at the individual batch level, including batch number, quantity, and expiry date.
- **FEFO Sell Algorithm** — when a product is sold, Inventrack automatically deducts from the earliest-expiring batch first, cascading across multiple batches if needed.
- **Expired Batch Auto-Removal** — batches past their expiry date are skipped and removed automatically during the sell flow.
- **Expiry Alerts Dashboard** — the dashboard flags items expiring within **10 days** (critical) and **30 days** (caution) with colour-coded warnings.
- **Multi-User Isolation** — each logged-in user has a private inventory and a dedicated Min-Heap in server memory; no data bleeds between accounts.
- **Cache-Control Headers** — every response prevents stale page caching, ensuring users always see live inventory data.
- **Session-Based Authentication** — protected routes redirect unauthenticated users to the login page.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask 3.0 |
| Database | SQLite 3 (via Python's built-in `sqlite3` module) |
| Frontend | HTML5, Jinja2 templating |
| Data Structure | Python `heapq` Min-Heap (custom per-user in-memory cache) |
| Auth / OTP | Custom OTP generation + SMTP email delivery |
| SMS Alerts | `sms.py` module (configurable) |
| Config | `python-dotenv` for environment variable management |

---

## System Architecture

```
┌────────────────────────────────────────────────────┐
│                    Flask App (app.py)               │
│  Routes: /, /register, /login, /add_batch,         │
│          /sell_product, /get_expiring_stock,        │
│          /verify-otp, /logout                       │
└────────────┬───────────────────────────────────────┘
             │
    ┌────────▼─────────┐      ┌──────────────────────┐
    │  auth.py         │      │  sms.py              │
    │  - login()       │      │  - send_otp_email()  │
    │  - generate_otp()│      │  - registration      │
    └──────────────────┘      │    alert()           │
                              └──────────────────────┘
             │
    ┌────────▼─────────────────────────────────────┐
    │  inventory_management.py                      │
    │  - add_batch()      → INSERT + heap push      │
    │  - sell_product()   → FEFO loop via heap      │
    │  - get_all_inventory()                        │
    │  - get_expiring_stocks()                      │
    └────────┬─────────────────────────────────────┘
             │
    ┌────────▼──────────────────────────────────┐
    │  heap.py  (In-Memory Min-Heap Cache)       │
    │  user_heaps = { email: [min-heap] }        │
    │  - push_batch()                            │
    │  - get_nearest_expiry(email, product)      │
    │  - load_from_db(email)                     │
    │  - clear_heap(email)                       │
    └────────┬──────────────────────────────────┘
             │
    ┌────────▼──────────────────┐
    │  SQLite — database.db     │
    │  Tables: user, inventory  │
    └───────────────────────────┘
```

---

## Data Structure Design — The Min-Heap

The most technically significant design choice in Inventrack is the **per-user Min-Heap** implemented in `heap.py`.

### Why a Heap?

At sell time, the system must find the batch of a given product with the **earliest expiry date** — this is the FEFO (First Expired, First Out) principle. A naïve approach would query the database and sort results every time. Instead, Inventrack loads each user's inventory into an in-memory Min-Heap on login, enabling:

- **O(log n)** batch insertions (on `add_batch`)
- **O(k)** nearest-expiry lookup where k = number of batches for that product
- **Zero redundant DB reads** during the sell loop

### How it works

```python
# Each heap element is a tuple: (expiry_date, item_id, product_name, batch_no, quantity)
# Python's heapq always pops the smallest element — i.e., the earliest expiry date.

heap_element = (expiry_date, item_id, product_name, batch_no, quantity)
heapq.heappush(user_heaps[email], heap_element)
```

Each user (`email`) has an isolated heap. When a batch is added or sold, the user's heap is rebuilt from the database (`load_from_db`) to maintain consistency.

### FEFO Sell Loop

```
sell_product(email, product_name, quantity=10)
  └── while remaining > 0:
        batch = get_nearest_expiry(email, product_name)   # O(k) scan
        if batch is expired:
            DELETE from DB → reload heap → continue
        if batch.quantity <= remaining:
            DELETE batch from DB → reload heap → remaining -= batch.quantity
        else:
            UPDATE quantity in DB → remaining = 0
```

This ensures **no expired stock is ever sold**, and deductions always begin with the oldest batch.

---

## Project Structure

```
Inventrack-Inventory-Management-System/
│
├── app.py                  # Flask application, route handlers
├── auth.py                 # User authentication, OTP generation & email
├── database_setup.py       # SQLite schema initialisation (run once on startup)
├── heap.py                 # Per-user Min-Heap cache (in-memory, FEFO engine)
├── inventory_management.py # Core inventory logic (add, sell, query)
├── sms.py                  # Email/SMS alert utilities
├── requirements.txt        # Python dependencies
├── .gitignore
└── templates/              # Jinja2 HTML templates
    ├── landing_page.html
    ├── login.html
    ├── register.html
    ├── verify_otp.html
    ├── dashboard.html
    ├── add.html
    ├── sell.html
    ├── error_add.html
    └── error_sell.html
```

---

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/engineermayur-07/Inventrack-Inventory-Management-System.git
cd Inventrack-Inventory-Management-System

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables (see section below)
cp .env.example .env            # or create .env manually

# 5. Run the application
python app.py
```

The app will be available at `http://127.0.0.1:5000`.

The database (`database.db`) is created automatically on first run via `init_db()` in `database_setup.py`.

---

## Environment Variables

Create a `.env` file in the project root with the following keys:

```env
SECRET_KEY=your-secret-key-here

# Email configuration for OTP delivery
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Optional: SMS/alert configuration
SMS_API_KEY=your-sms-api-key
```

> **Note:** For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) rather than your account password.

---

## Usage

### 1. Register
Navigate to `/register`, fill in your name, email, and mobile number. An OTP will be sent to your email — enter it to complete registration.

### 2. Login
Go to `/login` with your registered credentials. On success you are redirected to your personal dashboard.

### 3. Add a Batch
Click **Add Batch** and provide:
- Product Name (auto-uppercased)
- Batch Number (must be unique across all users)
- Quantity
- Expiry Date

### 4. Sell a Product
Click **Sell**, enter the product name and quantity. Inventrack will automatically deduct from the earliest-expiring batch first (FEFO), spanning multiple batches if needed and skipping/removing any expired ones automatically.

### 5. Dashboard
Your home dashboard shows:
- All inventory sorted by expiry date
- Expiring-soon alerts (🟡 within 30 days, 🔴 within 10 days)

---

## API / Routes Reference

| Method | Route | Description | Auth Required |
|---|---|---|---|
| GET | `/` | Dashboard (or landing page if not logged in) | No |
| GET/POST | `/register` | New user registration | No |
| GET/POST | `/verify-otp` | OTP verification to complete registration | No |
| GET/POST | `/login` | User login | No |
| GET | `/logout` | Clears session and redirects to home | Yes |
| GET/POST | `/add_batch` | Add a new product batch | Yes |
| GET/POST | `/sell_product` | Sell a quantity of a product (FEFO) | Yes |
| GET | `/get_expiring_stock` | View items expiring within 30 days | Yes |

---

## Database Schema

### `user`
| Column | Type | Notes |
|---|---|---|
| id | INTEGER | Primary key, auto-increment |
| email | TEXT | Unique identifier |
| password | TEXT | User's password |
| name | TEXT | Display name |
| mobile | TEXT | Mobile number |

### `inventory`
| Column | Type | Notes |
|---|---|---|
| id | INTEGER | Primary key, auto-increment |
| user_email | TEXT | Foreign key → user.email |
| product_name | TEXT | Stored uppercase |
| batch_no | TEXT | Unique per batch |
| quantity | INTEGER | Units in stock |
| expiry_date | TEXT | Format: `YYYY-MM-DD` |

---

## Future Improvements

- **Password Hashing** — currently passwords are stored in plain text; integrating `bcrypt` or `werkzeug.security` would make this production-ready.
- **Forgot Password / OTP Reset** — allow users to reset credentials via email OTP.
- **Low Stock Alerts** — notify users when a product's total quantity falls below a configurable threshold.
- **CSV / Excel Export** — allow users to download their inventory as a spreadsheet.
- **Product Categories** — group products and filter dashboard by category.
- **Docker / CI-CD** — containerise with Docker and add a CI/CD pipeline for automated deployments.
- **REST API** — expose inventory endpoints as a JSON API for mobile or third-party integrations.

---

## 👨‍💻 Author

**Mayur B Gund**
SY B.Tech Computer Science & Engineering

[![GitHub](https://img.shields.io/badge/GitHub-engineermayur--07-181717?logo=github)](https://github.com/engineermayur-07)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-mgund1920-0A66C2?logo=linkedin)](https://linkedin.com/in/mgund1920)
[![Email](https://img.shields.io/badge/Email-mgund1920%40gmail.com-D14836?logo=gmail)](mailto:mgund1920@gmail.com)

---

> *Built with Flask, SQLite, and a carefully placed Min-Heap.*
