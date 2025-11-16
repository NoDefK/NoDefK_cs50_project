import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    return apology("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
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
    """Get stock quote."""
    return apology("TODO")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    #如果用户提交了表单
    if request.method =="POST":
        #保证用户名是被提交的
        if not request.form.get("username"):
            return apology("宝宝，我们需要你提供用户名哦",400)
        #保证密码是被提交的
        elif not request.form.get("password"):
            return apology("宝宝，我们需要你提供密码哦",400)
        elif not request.form.get("password")==request.form.get("confirmation"):
            return apology("宝宝太粗心啦，两次输入的密码不一样哦，请再尝试一次哦",400)
        #查询数据库，确保用户名未被注册
        rows=db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))#这句SQL语句现学现用
        if len(rows)>0:
            return apology("不好意思宝宝，这个用户名已经被其他宝宝抢先一步了，请再想一个哦",400)
        #获取hash密码
        hash_password=generate_password_hash(request.form.get("password"))
        new_user_id=db.execute("INSERT INTO users (username,hash) VALUES(?,?)",request.form.get("username"),hash_password)
        #注册成功后，自动为用户登录
        session["user_id"]=new_user_id
        flash("注册成功啦！欢迎你新来的宝宝，宝宝真棒！")
        #重新定向到首页
        return redirect("/")                      
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")
