from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from datetime import datetime, timezone
import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file

# Initialize the Flask application
app = Flask(__name__, template_folder="templates", static_folder="static")
HISTORY_PATH = Path(__file__).with_name("history.json")

# Helper function to parse a string into a Decimal number
def parse_decimal(value):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return None


def parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
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


def delete_history_entry(timestamp):
    entries = load_history_entries()
    if not isinstance(entries, list):
        entries = []

    filtered_entries = [
        entry for entry in entries
        if str(entry.get("timestamp")) != str(timestamp)
    ]
    HISTORY_PATH.write_text(
        json.dumps({"history": filtered_entries}, indent=2),
        encoding="utf-8",
    )
    return filtered_entries


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


def build_multibuy_equation(form, result):
    unit_price = result["unit_price"]
    quantity = result["quantity"]
    regular_total = result["regular_total"]
    deal_total = result["deal_total"]

    if form["deal_type"] == "buy_x_get_y_free":
        return (
            f"Buy {form['buy_qty']} get {form['free_qty']} free: "
            f"{quantity} @ ${unit_price} -> ${regular_total} to ${deal_total}"
        )

    if form["deal_type"] == "x_for_y_items":
        return (
            f"{form['bundle_size']} for {form['pay_for_qty']}: "
            f"{quantity} @ ${unit_price} -> ${regular_total} to ${deal_total}"
        )

    return (
        f"{form['bundle_size']} for ${result['bundle_price']}: "
        f"{quantity} @ ${unit_price} -> ${regular_total} to ${deal_total}"
    )


def save_multibuy_history_entry(form, result):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "calculator": "multibuy",
        "deal_type": form["deal_type"],
        "quantity": str(result["quantity"]),
        "unit_price": str(result["unit_price"]),
        "regular_total": str(result["regular_total"]),
        "deal_total": str(result["deal_total"]),
        "savings": str(result["savings"]),
        "equation": build_multibuy_equation(form, result),
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


def calculate_multibuy(form):
    unit_price = parse_decimal(form["unit_price"])
    quantity = parse_int(form["quantity"])

    if unit_price is None or quantity is None:
        return None, "Enter valid numbers for unit price and quantity."
    if unit_price < 0:
        return None, "Unit price cannot be negative."
    if quantity <= 0:
        return None, "Quantity must be at least 1."

    deal_type = form.get("deal_type", "buy_x_get_y_free")
    regular_total = unit_price * Decimal(quantity)

    paid_units = Decimal(quantity)
    free_units = Decimal("0")
    bundle_price = None

    if deal_type == "buy_x_get_y_free":
        buy_qty = parse_int(form.get("buy_qty"))
        free_qty = parse_int(form.get("free_qty"))
        if buy_qty is None or free_qty is None:
            return None, "Enter valid deal values for buy/get quantities."
        if buy_qty <= 0 or free_qty <= 0:
            return None, "Buy/get quantities must be at least 1."

        group_size = buy_qty + free_qty
        full_groups = quantity // group_size
        remainder = quantity % group_size
        paid_units_int = (full_groups * buy_qty) + min(remainder, buy_qty)
        paid_units = Decimal(paid_units_int)
        free_units = Decimal(quantity - paid_units_int)
        deal_total = unit_price * paid_units

    elif deal_type == "x_for_y_items":
        bundle_size = parse_int(form.get("bundle_size"))
        pay_for_qty = parse_int(form.get("pay_for_qty"))
        if bundle_size is None or pay_for_qty is None:
            return None, "Enter valid deal values for bundle quantities."
        if bundle_size <= 0:
            return None, "Bundle size must be at least 1."
        if pay_for_qty < 0:
            return None, "Paid quantity cannot be negative."
        if pay_for_qty > bundle_size:
            return None, "Paid quantity cannot be greater than bundle size."

        full_groups = quantity // bundle_size
        remainder = quantity % bundle_size
        paid_units_int = (full_groups * pay_for_qty) + remainder
        paid_units = Decimal(paid_units_int)
        free_units = Decimal(quantity - paid_units_int)
        deal_total = unit_price * paid_units

    elif deal_type == "x_for_fixed_price":
        bundle_size = parse_int(form.get("bundle_size"))
        bundle_price = parse_decimal(form.get("bundle_price"))
        if bundle_size is None or bundle_price is None:
            return None, "Enter valid bundle size and fixed bundle price."
        if bundle_size <= 0:
            return None, "Bundle size must be at least 1."
        if bundle_price < 0:
            return None, "Fixed bundle price cannot be negative."

        full_groups = quantity // bundle_size
        remainder = quantity % bundle_size
        deal_total = (Decimal(full_groups) * bundle_price) + (Decimal(remainder) * unit_price)

    else:
        return None, "Select a valid multibuy deal type."

    savings = regular_total - deal_total
    effective_unit_price = deal_total / Decimal(quantity) if quantity else Decimal("0")

    result = {
        "deal_type": deal_type,
        "quantity": Decimal(quantity),
        "unit_price": money(unit_price),
        "regular_total": money(regular_total),
        "deal_total": money(deal_total),
        "savings": money(savings),
        "effective_unit_price": money(effective_unit_price),
        "paid_units": money(paid_units),
        "free_units": money(free_units),
        "bundle_price": money(bundle_price) if bundle_price is not None else None,
    }
    return result, None

def build_discount_form_from_request():
    return {
        "original_price": request.form.get("original_price", "").strip(),
        "discount_type": request.form.get("discount_type", "percent"),
        "discount_value": request.form.get("discount_value", "").strip(),
    }


def discount_result_payload(result):
    return {
        "discount_amount": f"${result['discount_amount']}",
        "final_price": f"${result['final_price']}",
    }


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
        form = build_discount_form_from_request()

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
    form = build_discount_form_from_request()
    result, error = calculate_discount(form)

    if error:
        return jsonify({"ok": False, "error": error}), 400

    if result is None:
        return jsonify({"ok": False, "error": "Calculation failed."}), 500

    try:
        save_history_entry(form, result)
    except OSError:
        pass

    return jsonify({"ok": True, **discount_result_payload(result)})


@app.route("/preview", methods=["POST"])
def preview():
    form = build_discount_form_from_request()
    result, error = calculate_discount(form)

    if error:
        return jsonify({"ok": False, "error": error}), 400

    if result is None:
        return jsonify({"ok": False, "error": "Calculation failed."}), 500

    return jsonify({"ok": True, **discount_result_payload(result)})


def build_multibuy_form_from_request():
    return {
        "unit_price": request.form.get("unit_price", "").strip(),
        "quantity": request.form.get("quantity", "").strip(),
        "deal_type": request.form.get("deal_type", "buy_x_get_y_free"),
        "buy_qty": request.form.get("buy_qty", "").strip(),
        "free_qty": request.form.get("free_qty", "").strip(),
        "bundle_size": request.form.get("bundle_size", "").strip(),
        "pay_for_qty": request.form.get("pay_for_qty", "").strip(),
        "bundle_price": request.form.get("bundle_price", "").strip(),
    }


@app.route("/multibuy/preview", methods=["POST"])
def multibuy_preview():
    form = build_multibuy_form_from_request()
    result, error = calculate_multibuy(form)

    if error:
        return jsonify({"ok": False, "error": error}), 400

    if result is None:
        return jsonify({"ok": False, "error": "Calculation failed."}), 500

    return jsonify(
        {
            "ok": True,
            "regular_total": f"${result['regular_total']}",
            "deal_total": f"${result['deal_total']}",
            "savings": f"${result['savings']}",
            "effective_unit_price": f"${result['effective_unit_price']}",
        }
    )


@app.route("/multibuy/calculate", methods=["POST"])
def multibuy_calculate():
    form = build_multibuy_form_from_request()
    result, error = calculate_multibuy(form)

    if error:
        return jsonify({"ok": False, "error": error}), 400

    if result is None:
        return jsonify({"ok": False, "error": "Calculation failed."}), 500

    try:
        save_multibuy_history_entry(form, result)
    except OSError:
        pass

    return jsonify(
        {
            "ok": True,
            "regular_total": f"${result['regular_total']}",
            "deal_total": f"${result['deal_total']}",
            "savings": f"${result['savings']}",
            "effective_unit_price": f"${result['effective_unit_price']}",
        }
    )


@app.route("/logic.js")
def serve_logic_js():
    return send_file("logic.js", mimetype="application/javascript")


@app.route("/history", methods=["GET"])
def history():
    entries = load_history_entries()
    if not isinstance(entries, list):
        entries = []

    return jsonify({"ok": True, "history": list(reversed(entries))})


@app.route("/history/delete", methods=["POST"])
def delete_history():
    payload = request.get_json(silent=True) or {}
    timestamp = payload.get("timestamp")

    if not timestamp:
        return jsonify({"ok": False, "error": "Missing history item timestamp."}), 400

    try:
        remaining = delete_history_entry(timestamp)
    except OSError:
        return jsonify({"ok": False, "error": "Could not delete history item."}), 500

    return jsonify({"ok": True, "history": list(reversed(remaining))})

@app.route("/template/pages/help")
def about_page():
    return render_template("about.html")
    
# Run the application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

