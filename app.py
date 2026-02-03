from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import datetime
import database
import pandas as pd

app = Flask(__name__)
app.secret_key = "expense-secret"

database.init_db()

@app.route("/")
def dashboard():
    today = datetime.date.today()
    rows = database.fetch_expenses_by_month(today.month, today.year)

    df = pd.DataFrame(rows, columns=["ID", "Date", "Amount", "Category", "Note"]) if rows else pd.DataFrame()
    total = df["Amount"].sum() if not df.empty else 0

    category_data = (
        df.groupby("Category")["Amount"].sum().to_dict()
        if not df.empty else {}
    )

    return render_template(
        "dashboard.html",
        total=total,
        month=today.strftime("%B %Y"),
        chart_data=category_data
    )

@app.route("/add", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        try:
            database.add_expense(
                request.form["date"],
                float(request.form["amount"]),
                request.form["category"],
                request.form["note"]
            )
            flash("Expense added successfully!", "success")
            return redirect(url_for("add_expense"))
        except ValueError:
            flash("Invalid amount", "danger")

    return render_template("add_expense.html")

@app.route("/view")
def view_data():
    rows = database.fetch_all_expenses()
    return render_template("view_data.html", rows=rows)

@app.route("/delete/<int:id>")
def delete(id):
    database.delete_expense(id)
    flash("Record deleted", "info")
    return redirect(url_for("view_data"))

@app.route("/chart-data")
def chart_data():
    today = datetime.date.today()
    rows = database.fetch_expenses_by_month(today.month, today.year)

    df = pd.DataFrame(rows, columns=["ID", "Date", "Amount", "Category", "Note"])
    return jsonify(df.groupby("Category")["Amount"].sum().to_dict())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
