# Coupon Calculator

A lightweight Flask app designed to make checkout math faster, clearer, and more accurate. It helps users calculate the discount amount and final price before making a purchase, while keeping the logic strict enough to prevent bad input and messy rounding.

[The link to the live app is below:]
[Open Coupon Calculator](https://coupon-calculator.up.railway.app)

## Why I built it

I’ve been working toward becoming a better developer and engineer, and one of the biggest lessons I’ve learned and believe is that real problems often lead to the best projects. I recently started a job as a cashier, and Im not good at math in the slightest and i deal with descalcula, so discounts and price calculations can become confusing, especially during busy checkout moments or when helping older shoppers who are not comfortable with technology.

I needed something simple, reliable, and easy to use that could reduce mental math mistakes and make pricing more transparent. That idea became this calculator.

## What the app does

The app allows a user to:

- enter an original price
- choose a percentage discount or a fixed discount amount
- validate the inputs before calculating
- see exactly how much money is saved
- view the final price after the discount is applied

It is built for everyday shopping scenarios where the user needs a quick and trustworthy estimate.

## Key features

- Percentage discounts up to 100%
- Fixed-amount discounts
- Negative-value validation
- Protection against invalid numeric input
- Currency-safe rounding to two decimal places
- Clear, simple interface for fast use

## Technical details

This project is built with Flask and uses Python’s Decimal type to reduce floating-point precision issues when working with money. That helps avoid tiny calculation errors that can happen with standard float math.

The app also validates user inputs so values like negative prices or percentages above 100% are rejected before they can produce unrealistic results.

## Project structure

- `app.py` — Flask application logic and discount calculations
- `templates/index.html` — user form and displayed results
- `static/styles.css` — styling for the interface
- `requirements.txt` — Python dependencies

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Then open the app in your browser at `http://localhost:5000`.

## Why this project matters to me

This project is more than just a calculator. It is a practical tool built from a real-world need, and it reflects the kind of developer I want to become: someone who solves problems with simple, useful solutions.

It also reminds me that the best software often starts with a small pain point in everyday life.

## Final thoughts

This calculator may be small, but it solves a genuine problem in a straightforward and helpful way. It combines clean UI, safe validation, and money-focused logic into a tool that is useful in real-life situations.

If you’re learning to code, I think this is a great example of building something meaningful from a real-world need rather than just following tutorials. Sometimes the best projects are the ones that make a small part of everyday life easier.

You can try the app here: [Open Coupon Calculator](https://coupon-calculator.up.railway.app)
