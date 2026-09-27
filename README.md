# Coupon Calculator

A lightweight Flask web app that helps users estimate the discount amount and final price before checkout. this is a link that will bring you directly to the live app:

[Open Coupon Calculator](https://coupon-calculator.up.railway.app)


## Why

This app was created to simplify the process of calculating discounts and final prices, ensuring accuracy and saving time during shopping. i am always pushing to become a carrer coder and engineer. i also finally got a job as a cashier and i have discalcula so i made this tool for work so i can get the most accurate calculations, which helps me help the older shoppers who dont understand technology well.

## Overview

This project lets a user:

- enter an original price
- choose either a percentage discount or a fixed amount discount
- validate the input values
- view the money saved and the final price

The app is designed to handle common checkout calculations with clear validation and currency-safe rounding.

## Features

- Percentage-off discounts up to 100%
- Fixed-amount discounts
- Negative-value validation
- Protection against invalid numeric input
- Rounded currency results to two decimal places

## Project structure

- `app.py` — Flask application logic and calculation rules
- `templates/index.html` — web form and rendered result display
- `static/styles.css` — page styling
- `requirements.txt` — Python dependencies


## Where to find the app

The app's source code is located in this repository. The main application logic is in `app.py`, the HTML template is in `templates/index.html`, and the CSS styling is in `static/styles.css`.

and this is a link that will bring you directly to the live app:

[Open Coupon Calculator](https://coupon-calculator.up.railway.app)


## Notes

- Input values are parsed using Python's `Decimal` type to reduce floating-point rounding errors.
- The app rounds monetary output to the nearest cent before displaying it.
- The calculator prevents invalid or impossible inputs such as negative prices or discounts above 100% for percentage deals.
