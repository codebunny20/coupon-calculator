# Coupon Calculator

A lightweight Flask app for calculating discounts and comparing multibuy deals. It provides live price previews, a standalone basic calculator, and saved calculation history in a simple, mobile-friendly interface.

Live app: [Open Coupon Calculator](https://coupon-calculator.up.railway.app)

## Features

### Discount calculator

- Calculate percentage-off and fixed-amount discounts.
- See the amount saved and final price update as you enter values.
- Adjust the discount quickly with the `-10`, `-5`, `-1`, `+1`, `+5`, and `+10` buttons.
- Prevent negative prices and discounts; percentage discounts must be between 0% and 100%.
- Fixed discounts are capped at the original price, so the final price cannot go below zero.

### Multibuy deal calculator

Compare the regular total with the promotional total, see your savings, and calculate the effective price per item for:

- **Buy X, get Y free** (for example, buy 2, get 1 free).
- **X for Y items** (for example, 3 for 2).
- **X for a fixed price** (for example, 2 for $5).

Enter a unit price and quantity; the calculator accounts for complete deal groups and any remaining items.

### Basic calculator

A compact calculator modal supports addition, subtraction, multiplication, division, decimals, clear, and backspace. Calculations can be saved to the shared history.

### History, settings, and help

- Save discount, multibuy, and basic-calculator results.
- Review recent calculations and delete individual entries.
- History is stored in `history.json` and limited to the latest 100 entries.
- Switch between light and dark themes; the theme preference is saved in the browser.
- Use the dedicated Help guide, About, Privacy Policy, and Donate pages linked from the footer.
- Responsive interface with live previews and validation messages.

## Calculation and data details

- Python's `Decimal` is used for monetary calculations, with currency rounded to two decimal places using half-up rounding.
- History is stored as JSON on the server running the app. No account or database is required.
- The app includes API endpoints for live previews, saved calculations, and history management.

## Tech stack

- Python and Flask
- Gunicorn for production serving
- HTML templates, CSS, and JavaScript
- JSON file storage for calculation history

## Project structure

```text
app.py                       Flask routes, validation, and calculation logic
logic.js                     Front-end behavior, live previews, and calculator UI
templates/
  index.html                 Main calculator page and dialogs
  pages/
    help.html                User guide
    about.html               About page
    donate.html              Support page
    privacy policy.html      Privacy policy
static/
  styles.css                 Responsive styles and themes
history.json                 Saved calculation history
tests/
  test_multibuy.py           Multibuy calculation and page tests
requirements.txt             Python runtime dependencies
```

## Run locally

1. Clone the repository and open its directory.
2. Create and activate a virtual environment.
3. Install the app dependencies and start the Flask app:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open [http://localhost:8000](http://localhost:8000).

## Run tests

Install `pytest` if it is not already available, then run:

```powershell
python -m pytest tests/test_multibuy.py
```

## Deployment

The app is deployed on Railway. `gunicorn` is included in `requirements.txt` for production serving; `python app.py` starts the development server locally on port 8000.

## Contributing

Contributions are welcome. Please open an issue or pull request with proposed improvements, bug fixes, or additional deal types.

## Interface behavior

- Discount and multibuy previews update automatically after a short pause while entering values.
- Changing the multibuy deal type shows only the relevant inputs; switching between deal types updates the preview.
- Settings, Help, History, and Basic Calculator dialogs can be closed with their close controls, by clicking the backdrop, or by pressing `Escape`.
- The Basic Calculator supports chained arithmetic, and division by zero displays an error instead of an invalid result.
- Calculator history can be refreshed in the Basic Calculator and individual entries can be deleted from the History dialog.

## License

This project is available for personal and educational use.
