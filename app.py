from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from flask import Flask, render_template, request


app = Flask(__name__, template_folder="templates", static_folder="static")


def parse_decimal(value):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return None


def money(value):
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@app.route("/", methods=["GET", "POST"])
def index():
    defaults = {
        "original_price": "",
        "discount_type": "percent",
        "discount_value": "",
    }
    result = None
    error = None

    if request.method == "POST":
        form = {
            "original_price": request.form.get("original_price", "").strip(),
            "discount_type": request.form.get("discount_type", "percent"),
            "discount_value": request.form.get("discount_value", "").strip(),
        }

        defaults.update(form)

        original_price = parse_decimal(form["original_price"])
        discount_value = parse_decimal(form["discount_value"])

        if original_price is None or discount_value is None:
            error = "Enter valid numbers for price and discount."
        elif original_price < 0 or discount_value < 0:
            error = "Price and discount cannot be negative."
        elif form["discount_type"] == "percent" and discount_value > 100:
            error = "Percentage discount cannot be greater than 100."
        else:
            if form["discount_type"] == "percent":
                discount_amount = original_price * discount_value / Decimal("100")
            else:
                discount_amount = discount_value

            discount_amount = min(discount_amount, original_price)
            final_price = original_price - discount_amount

            result = {
                "original_price": money(original_price),
                "discount_amount": money(discount_amount),
                "final_price": money(final_price),
                "savings_percent": money((discount_amount / original_price * Decimal("100")) if original_price else Decimal("0")),
                "discount_label": "Percentage" if form["discount_type"] == "percent" else "Fixed amount",
            }

    return render_template("index.html", form=defaults, result=result, error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

