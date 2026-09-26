from datetime import datetime
import os
import pandas as pd
import requests
from flask import Flask, jsonify, render_template, request, session

app = Flask(__name__)
app.secret_key = "anuaari_secure_secret_key"

GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1SK6S8tw4KWvwm_sQS6FHMGsSla7RkQ7XFkE7uuf9GRM/gviz/tq?tqx=out:csv&sheet=need+inventory+model+for+this+ANUAARI"
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyftApEC3eQJvJPF0tCSX7eFwAG52IinpEhQtlxhmVaOtpbc1J83zJZIhs9XRDRCezCZA/exec"


def load_inventory():
  try:
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
    df.columns = df.columns.astype(str).str.strip()
    products = []
    for _, row in df.iterrows():
      cat = str(row.iloc[1]).strip()
      if not cat or cat.lower() == "nan":
        cat = "General"

      # Collect all images from Column F onwards
      images = []
      for col_idx in range(5, len(row)):
        val = str(row.iloc[col_idx]).strip()
        if val and val.lower() != "nan":
          images.append(val)

      colors = (
          str(row.iloc[4]).strip()
          if len(row) > 4 and pd.notna(row.iloc[4])
          else ""
      )
      color_list = [
          c.strip() for c in colors.replace("&", ",").split(",") if c.strip()
      ]

      products.append({
          "id": str(row.iloc[0]).strip(),
          "name": str(row.iloc[2]).strip(),
          "category": cat,
          "price": str(row.iloc[3]).strip(),
          "colors": color_list,
          "images": images if images else ["default.jpg"],
      })
    return products
  except Exception:
    return [{
        "id": "AB0001",
        "name": "Sample Product",
        "category": "General",
        "price": "10",
        "colors": ["red", "blue"],
        "images": ["aari 1.JPG"],
    }]


@app.route("/")
def index():
  if "user" not in session:
    return render_template("login.html")

  products = load_inventory()
  categories = sorted(list(set(p["category"] for p in products)))
  selected_cat = request.args.get("category", categories[0] if categories else "General")
  filtered_products = [p for p in products if p["category"] == selected_cat]

  return render_template(
      "index.html",
      user=session["user"],
      categories=categories,
      selected_cat=selected_cat,
      products=filtered_products,
      cart_count=len(session.get("cart", [])),
  )


@app.route("/login", methods=["POST"])
def login():
  name = request.form.get("name")
  phone = request.form.get("phone")
  if name and phone and len(phone) == 10:
    session["user"] = {"name": name, "phone": phone}
    try:
      requests.post(
          GOOGLE_SCRIPT_URL,
          json={"Type": "Login", "Customer_Name": name, "Primary_Phone": phone},
      )
    except Exception:
      pass
  return jsonify({"success": True})


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
  data = request.json
  if "cart" not in session:
    session["cart"] = []
  session["cart"].append(data)
  session.modified = True
  return jsonify({"success": True, "cart_count": len(session["cart"])})


@app.route("/logout")
def logout():
  session.clear()
  return jsonify({"success": True})


if __name__ == "__main__":
  app.run(debug=True, port=5000)
