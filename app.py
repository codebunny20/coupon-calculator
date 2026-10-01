from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from datetime import datetime, timezone
import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request

# Initialize the Flask application
app = Flask(__name__, template_folder="templates", static_folder="static")
HISTORY_PATH = Path(__file__).with_name("history.json")

# Helper function to parse a string into a Decimal number
def parse_decimal(value):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return None

# Helper function to format a Decimal number as money
def money(value):
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def load_history_entries():
    if not HISTORY_PATH.exists():
        return []

    try:
        raw_text = HISTORY_PATH.read_text(encoding="utf-8").strip()
        if not raw_text:
            return []

        data = json.loads(raw_text)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and isinstance(data.get("history"), list):
            return data["history"]
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return []

    return []


def build_equation(form, result):
    original_price = result["original_price"]
    final_price = result["final_price"]
    discount_amount = result["discount_amount"]
    requested_discount = result["requested_discount"]

    if form["discount_type"] == "percent":
        return (
            f"${original_price} - {requested_discount}% "
            f"(${discount_amount}) = ${final_price}"
        )

    return f"${original_price} - ${requested_discount} = ${final_price}"


def save_history_entry(form, result):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "discount_type": form["discount_type"],
        "original_price": str(result["original_price"]),
        "discount_value": str(result["requested_discount"]),
        "discount_amount": str(result["discount_amount"]),
        "final_price": str(result["final_price"]),
        "equation": build_equation(form, result),
    }

    entries = load_history_entries()
    entries.append(entry)
    entries = entries[-100:]

    payload = {"history": entries}
    HISTORY_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def calculate_discount(form):
    original_price = parse_decimal(form["original_price"])
    discount_value = parse_decimal(form["discount_value"])

    if original_price is None or discount_value is None:
        return None, "Enter valid numbers for price and discount."
    if original_price < 0 or discount_value < 0:
        return None, "Price and discount cannot be negative."
    if form["discount_type"] == "percent" and discount_value > 100:
        return None, "Percentage discount cannot be greater than 100."

    if form["discount_type"] == "percent":
        discount_amount = original_price * discount_value / Decimal("100")
    else:
        discount_amount = discount_value

    discount_amount = min(discount_amount, original_price)
    final_price = original_price - discount_amount
    discount_percent = (discount_amount / original_price * Decimal("100")) if original_price else Decimal("0")
    final_percent = Decimal("100") - discount_percent if original_price else Decimal("0")

    result = {
        "original_price": money(original_price),
        "discount_amount": money(discount_amount),
        "money_taken_off": money(discount_amount),
        "final_price": money(final_price),
        "savings_percent": money(discount_percent),
        "discount_percent": money(discount_percent),
        "final_percent": money(final_percent),
        "requested_discount": money(discount_value),
        "input_discount_value": money(discount_value),
        "discount_label": "Percentage" if form["discount_type"] == "percent" else "Fixed amount",
    }
    return result, None

# Route for the main page of the application
@app.route("/", methods=["GET", "POST"])
def index():
    defaults = {
        "original_price": "",
        "discount_type": "percent",
        "discount_value": "",
    }
    result = None
    error = None

    # Initialize the form with default values
    if request.method == "POST":
        form = {
            "original_price": request.form.get("original_price", "").strip(),
            "discount_type": request.form.get("discount_type", "percent"),
            "discount_value": request.form.get("discount_value", "").strip(),
        }

        defaults.update(form)
        result, error = calculate_discount(form)
        if result is not None and error is None:
            try:
                save_history_entry(form, result)
            except OSError:
                pass
# Render the template with the form, result, and error messages
    return render_template("index.html", form=defaults, result=result, error=error)


@app.route("/calculate", methods=["POST"])
def calculate():
    form = {
        "original_price": request.form.get("original_price", "").strip(),
        "discount_type": request.form.get("discount_type", "percent"),
        "discount_value": request.form.get("discount_value", "").strip(),
    }
    result, error = calculate_discount(form)

    if error:
        return jsonify({"ok": False, "error": error}), 400

    if result is None:
        return jsonify({"ok": False, "error": "Calculation failed."}), 500

    try:
        save_history_entry(form, result)
    except OSError:
        pass

    return jsonify(
        {
            "ok": True,
            "discount_amount": f"${result['discount_amount']}",
            "final_price": f"${result['final_price']}",
        }
    )


@app.route("/preview", methods=["POST"])
def preview():
    form = {
        "original_price": request.form.get("original_price", "").strip(),
        "discount_type": request.form.get("discount_type", "percent"),
        "discount_value": request.form.get("discount_value", "").strip(),
    }
    result, error = calculate_discount(form)

    if error:
        return jsonify({"ok": False, "error": error}), 400

    if result is None:
        return jsonify({"ok": False, "error": "Calculation failed."}), 500

    return jsonify(
        {
            "ok": True,
            "discount_amount": f"${result['discount_amount']}",
            "final_price": f"${result['final_price']}",
        }
    )


@app.route("/history", methods=["GET"])
def history():
    entries = load_history_entries()
    if not isinstance(entries, list):
        entries = []

    return jsonify({"ok": True, "history": list(reversed(entries))})

## bellow is the logic that saves the calculation results and equation to the history.json file

# Run the application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

