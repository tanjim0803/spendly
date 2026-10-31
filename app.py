from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from database.db import init_db, seed_db, get_user_by_email, create_user, get_user_by_id, get_user_stats, get_top_category, get_recent_expenses, get_category_totals



app = Flask(__name__)
app.secret_key = "spendly-dev-secret-key"

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    if "user_id" in session:
        # For now, just render landing, but we know they are logged in
        pass
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("landing"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not name or not email or not password:
            return render_template("register.html", error="All fields are required.")

        if get_user_by_email(email):
            return render_template("register.html", error="Email already registered.")

        hashed_password = generate_password_hash(password)
        create_user(name, email, hashed_password)

        return redirect(url_for("login"))

    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("landing"))
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            return render_template("login.html", error="Email and password are required.")

        user = get_user_by_email(email)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            return redirect(url_for("landing"))

        return render_template("login.html", error="Invalid email or password.")

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/terms-and-conditions")
def terms_and_conditions():
    return render_template("terms.html")


@app.route("/privacy")
@app.route("/privacy-policy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    user_row = get_user_by_id(user_id)
    if not user_row:
        return redirect(url_for("logout"))

    # Date Filtering
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    valid_date_from = None
    valid_date_to = None

    if date_from:
        try:
            datetime.strptime(date_from, "%Y-%m-%d")
            valid_date_from = date_from
        except ValueError:
            date_from = None

    if date_to:
        try:
            datetime.strptime(date_to, "%Y-%m-%d")
            valid_date_to = date_to
        except ValueError:
            date_to = None

    if valid_date_from and valid_date_to and valid_date_from > valid_date_to:
        flash("Start date must be before end date.")
        valid_date_from = None
        valid_date_to = None

    # User Basic Info
    user = {
        "name": user_row["name"],
        "email": user_row["email"],
        "joined_date": user_row["created_at"][:10], # Simplest format YYYY-MM-DD
        "initials": "".join([n[0] for n in user_row["name"].split()])
    }

    # Summary Stats
    stats_row = get_user_stats(user_id, valid_date_from, valid_date_to)
    total_spent = stats_row.get("total_spent") or 0.0
    transaction_count = stats_row.get("transaction_count") or 0

    stats = {
        "total_spent": f"${total_spent:,.2f}",
        "transaction_count": str(transaction_count),
        "top_category": get_top_category(user_id, valid_date_from, valid_date_to) or "None"
    }

    # Recent Transactions
    recent_rows = get_recent_expenses(user_id, limit=5, date_from=valid_date_from, date_to=valid_date_to)
    recent_transactions = []
    for row in recent_rows:
        amount = row["amount"]
        recent_transactions.append({
            "date": row["date"],
            "desc": row["description"],
            "category": row["category"],
            "amount": f"-${amount:,.2f}"
        })

    # Category Breakdown
    category_rows = get_category_totals(user_id, valid_date_from, valid_date_to)
    category_breakdown = []
    for row in category_rows:
        cat_total = row["total"]
        percentage = (cat_total / total_spent * 100) if total_spent > 0 else 0
        category_breakdown.append({
            "category": row["category"],
            "amount": f"${cat_total:,.2f}",
            "percentage": int(percentage)
        })

    # Preset Date ranges for links
    today = datetime.now()
    first_of_month = today.replace(day=1).strftime("%Y-%m-%d")

    # Last 3 months: today - 90 days
    three_months_ago = (today - timedelta(days=90)).strftime("%Y-%m-%d")

    # Last 6 months: today - 180 days
    six_months_ago = (today - timedelta(days=180)).strftime("%Y-%m-%d")

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        recent_transactions=recent_transactions,
        category_breakdown=category_breakdown,
        date_from=valid_date_from,
        date_to=valid_date_to,
        presets={
            "this_month": {"from": first_of_month, "to": today.strftime("%Y-%m-%d")},
            "three_months": {"from": three_months_ago, "to": today.strftime("%Y-%m-%d")},
            "six_months": {"from": six_months_ago, "to": today.strftime("%Y-%m-%d")},
            "all_time": {"from": None, "to": None}
        }
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
