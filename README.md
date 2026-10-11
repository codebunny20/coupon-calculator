# Coupon Calculator

A lightweight Flask app for fast, reliable checkout math. It helps shoppers and cashiers quickly estimate discount savings, compare final prices, and evaluate bundle-style deals without relying on error-prone mental math.

Live app: [Open Coupon Calculator](https://coupon-calculator.up.railway.app)

## Overview

Coupon Calculator is designed for real-world shopping scenarios where speed and accuracy matter. Instead of manually calculating discounts in the middle of a busy checkout, users can enter price information and get clear, validated results instantly.

The app supports both standard discount calculations and multibuy savings scenarios, making it useful for everyday retail decisions as well as more complex promotional offers.

## Features

- Percentage and fixed-amount discount calculations
- Automatic validation for invalid or negative inputs
- Protection against unrealistic values such as discounts over 100%
- Money-safe calculations using Python’s Decimal type
- Rounded totals to two decimal places for currency accuracy
- Multibuy deal support for:
  - buy X get Y free
  - X for Y items
  - bundle pricing
- Recent calculation history with delete support
- Simple, mobile-friendly UI for fast use

## How it works

The app takes an original price and a discount value, validates the input, and then calculates:

- discount amount
- final price
- savings percentage
- total savings

For multibuy deals, it can also estimate:

- regular total
- deal total
- savings
- effective unit price

## Tech stack

- Flask
- Python
- Decimal for precise money handling
- HTML, CSS, and JavaScript for the front end
- JSON-based local history storage

## Project structure

- `app.py` – Flask routes and calculation logic
- `logic.js` – front-end behavior and live previews
- `templates/` – HTML templates for the main app and supporting pages
- `static/` – CSS and static assets
- `history.json` – saved calculation history

## Run locally

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies
4. Start the app

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open:

```text
http://localhost:8000
```

## Deployment

This project is deployed on Railway and is configured to run as a Flask web app in production.

## Why this project matters

This app was built around a practical everyday problem: doing quick, accurate pricing math under pressure. It reflects a simple but important software principle—solve a real problem with a tool that is clear, useful, and trustworthy.

## License

This project is available for personal and educational use.

## Contributing

Contributions are welcome. If you want to improve the calculator, add better validation, expand deal types, or improve the UI, feel free to open a pull request or suggest changes.
