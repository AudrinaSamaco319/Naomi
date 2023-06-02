import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")




@app.route("/")
@login_required
def index():
    rows = db.execute("SELECT symbol, SUM(shares) FROM transactions GROUP BY symbol HAVING user_id=? AND SUM(shares) > 0", session["user_id"])
    stocks = []
    grand_total = 0
    for row in rows:
        symbol = row['symbol']
        stock = lookup(symbol)
        name = stock['name']
        shares = row['SUM(shares)']
        price = stock['price']
        total = price * shares
        info = {
            'symbol': symbol,
            'name': name,
            'shares': shares,
            'price': price,
            'total': total
        }

        stocks.append(info)
        grand_total = grand_total + total
    data = db.execute("SELECT * FROM users WHERE id=?", session["user_id"])
    cash = data[0]['cash']
    grand_total = cash + grand_total
    return render_template("index.html",stocks = stocks, cash=cash, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "GET":
        return render_template("buy.html")
    else:
        symbol = request.form.get('symbol')
        if not symbol:
            return apology("You must provide symbol!")
        try:
            stock = lookup(symbol)
            price = stock['price']
        except:
            return apology("Incorrect Symbol!")
        shares = request.form.get('shares')
        if not shares:
            return apology("You must enter the number of shares to buy!")
        data = db.execute("SELECT cash FROM users WHERE id=?", session["user_id"])
        cash = data[0]['cash']
        if cash < price * int(shares):
            return apology("Insufficient funds!")
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (:user_id, :symbol, :shares, :price)", user_id=session["user_id"], symbol=symbol.upper(), shares=shares, price=price)
        db.execute("UPDATE users SET cash=? WHERE id=?", cash - price * int(shares), session["user_id"])
        flash("Bought")
        return redirect("/")


@app.route("/history")
@login_required
def history():
    rows = db.execute("SELECT * FROM transactions WHERE user_id=?", session["user_id"])
    return render_template("history.html", rows=rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "GET":
        return render_template("quote.html")
    else:
        symbol = request.form.get('symbol')
    try:
        stock = lookup(symbol)
        return render_template("quoted.html", stock=stock)
    except :
        return apology("Incorrect Symbol")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get('username')
        if not username:
            return apology("You must provide a username!!")
        password1 = request.form.get('password1')
        if not password1:
            return apology("You must enter a password!!!")
        password2 = request.form.get('password2')
        if not password2:
            return apology("You must retype your password!!!")
        if password1 != password2:
            return apology("Your passwords don't match!!")
        hash = generate_password_hash(password1)
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=hash)
        return redirect("/")





@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "GET":
        rows = db.execute("SELECT symbol, SUM(shares) FROM transactions GROUP BY symbol HAVING user_id=? AND SUM(shares) > 0", session['user_id'])
        return render_template("sell.html", rows=rows)
    else:
        symbol = request.form.get('symbol')
        if not symbol:
            return apology("You must select a symbol.")
        shares = request.form.get('shares')
        if not shares:
            return apology("You must enter the number of shares you want to sell!")
        rows = db.execute("SELECT symbol, SUM(shares) FROM transcations GROUP BY symbol HAVING user_id=? AND SUM(shares) > 0", session['user_id'])
        for row in rows:
            if symbol == row['symbol']:
                if shares > row['SUM(shares)']:
                    return apology("You don't have that many shares available!")
        data = db.execute("SELECT * FROM useres WHERE id=?", session["user_id"])
        cash = data[0]['cash']
        stock = lookup(symbol)
        price = stock['price']
        updated_cash = cash + int(shares) * price
        db.execute("UPDATE users cash=? WHERE id=?", updated_cash, session['user_id'])
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (:user_id, :symbol, :shares, :price)", user_id=session['user_id'], symbol=symbol, shares=-1*int(shares), price=price)
        return redirect("/")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
