from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import init_db, seed_db, get_user_by_email, create_user


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

    # Hardcoded mock data for UI validation (Step 4)
    user = {
        "name": "Tanjim Ahmed",
        "email": "tanjim@example.com",
        "joined_date": "October 2023",
        "initials": "TA"
    }
    stats = {
        "total_spent": "$2,450.00",
        "transaction_count": "42",
        "top_category": "Dining"
    }
    recent_transactions = [
        {"date": "2023-10-25", "desc": "Starbucks Coffee", "category": "Dining", "amount": "-$6.50"},
        {"date": "2023-10-24", "desc": "Amazon - Books", "category": "Shopping", "amount": "-$24.99"},
        {"date": "2023-10-22", "desc": "Monthly Rent", "category": "Housing", "amount": "-$1,200.00"},
    ]
    category_breakdown = [
        {"category": "Housing", "amount": "$1,200", "percentage": 60},
        {"category": "Dining", "amount": "$450", "percentage": 20},
        {"category": "Shopping", "amount": "$300", "percentage": 15},
        {"category": "Other", "amount": "$100", "percentage": 5},
    ]

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        recent_transactions=recent_transactions,
        category_breakdown=category_breakdown
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
