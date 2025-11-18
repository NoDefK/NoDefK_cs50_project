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
    # 查找cash
    users = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])
    # 用户持有的每一种股票和总数量
    stocks = db.execute( "SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = :user_id GROUP BY symbol HAVING total_shares > 0", user_id=session["user_id"])
    
    quotes = {} # 初始化一个空的字典
    
    cash_remaining = users[0]["cash"]
    grand_total = cash_remaining  # 初始化总资产为现金

    for stock in stocks: # 遍历
        quote = lookup(stock["symbol"])
        quotes[stock["symbol"]] = quote
        # 累加每支股票的总价值到 grand_total 中
        grand_total += stock["total_shares"] * quote["price"]

    # 注意：现在传递 grand_total 而不是旧的 total
    return render_template("portfolio.html", quotes=quotes, stocks=stocks, grand_total=grand_total, cash_remaining=cash_remaining)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    
    if request.method=="POST":
        symbol=request.form.get("symbol")
        # 增加一个检查，防止用户不输入就提交
        if not symbol:
            return apology("must provide symbol", 400)
            
        #查询股票数据
        quote=lookup(symbol)
        #没找到
        if quote==None:
            return apology("invalid symbol",400)
        #开始买了，记录要买多少
        try:
            #从表中读取的是字符串要转换
            shares=int(request.form.get("shares"))
        #如果是不正常的数
        except:
          return apology("shares must be normal",400)
        #判断shares是否>0
        if shares<=0:
            return apology("shares should be a positive number",400)
        #开始记录有多少钱
        rows=db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])
        cash_remaining=rows[0]["cash"]
        per_share_price=quote["price"]
        total=per_share_price*shares
        if total>cash_remaining:
            return apology("money is not enough")
        # 扣除用户现金
        db.execute("UPDATE users SET cash = cash - :price WHERE id = :user_id", price=total, user_id=session["user_id"])

        # 记录交易历史
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES(:user_id, :symbol, :shares, :price)", user_id=session["user_id"], symbol=symbol, shares=shares, price=per_share_price)
        flash("宝宝恭喜你购买成功！发大财哦！")
        #防止重复购买和扣款
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    a_list_of_my_trades = db.execute("SELECT symbol, shares, per_share_price, total,created_at FROM transactions WHERE user_id = :user_id ORDER BY created_at ASC", user_id=session["user_id"])
    return render_template("history.html", my_history=a_list_of_my_trades)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("宝宝，登录需要用户名哦", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("小笨蛋，忘记输密码啦", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("用户名或者密码不对哦，宝宝再试一次吧", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        flash(f"欢迎回来宝宝，{rows[0]["username"]}!")

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
    if request.method=="POST":
        #检查用户是否提交了空的表单
        symbol=request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol",400)
        stock=lookup(symbol)
        if stock==None:
            return apology("invalid symbol",400)
        #将值赋给对应的变量名,用usd格式化价格
        return render_template("quote.html",symbol=stock["symbol"],price=usd(stock["price"]))
    else:
      return render_template("quote.html")


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
